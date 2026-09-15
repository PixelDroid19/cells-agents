"""Inspect local project evidence without executing project code."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shlex


INTENTS = {"test": {"test"}, "coverage": {"test"}, "lint": {"lint"},
           "build": {"build", "sass"}, "start": {"serve", "dev", "start"}}


def native_marker(command: str):
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    while tokens and re.fullmatch(r"\w+=.*", tokens[0]):
        tokens.pop(0)
    if len(tokens) >= 2 and Path(tokens[0]).name in {"cells", "cells.cmd"}:
        return re.fullmatch(r"(app|lit-component|component):([\w-]+)", tokens[1])
    return None


def package_manager(root: Path, package: dict) -> str:
    def declared(manifest):
        value = manifest.get("packageManager")
        if value is None:
            return None
        if not isinstance(value, str) or value.split("@", 1)[0] not in {"npm", "pnpm", "yarn"}:
            raise ValueError("Unsupported packageManager; inspect the required package runner explicitly")
        return value.split("@", 1)[0]

    def locked(directory):
        matches = [name for filename, name in (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("package-lock.json", "npm")) if (directory / filename).is_file()]
        if len(matches) > 1:
            raise ValueError("Multiple lockfile families; establish the intended package manager")
        return matches[0] if matches else None

    local = declared(package) or locked(root)
    if local:
        return local
    if (root / ".git").exists():
        return "npm"
    for ancestor in root.parents:
        path = ancestor / "package.json"
        manifest = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        if not isinstance(manifest, dict):
            raise ValueError("Ancestor package.json must be an object")
        if manifest.get("workspaces") or (ancestor / "pnpm-workspace.yaml").is_file():
            manager = declared(manifest) or locked(ancestor)
            if manager:
                return manager
        if (ancestor / ".git").exists():
            break
    return "npm"


def project_info(cwd: str | Path) -> dict:
    start = Path(cwd).expanduser().resolve(strict=True)
    if not start.is_dir():
        raise ValueError("Project path must be a directory")
    root = start
    for candidate in (start, *start.parents):
        root = candidate
        if (candidate / "package.json").is_file() or (candidate / ".git").exists():
            break
        if candidate.parent == candidate:
            root = start
    manifest = root / "package.json"
    package = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {}
    if not isinstance(package, dict):
        raise ValueError("package.json must contain an object")
    deps = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = package.get(key, {})
        if not isinstance(value, dict):
            raise ValueError(f"package.json {key} must be an object")
        deps.update(value)
    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict) or any(not isinstance(v, str) for v in scripts.values()):
        raise ValueError("package.json scripts must map names to command strings")
    namespaces = ("@bbva-web-components/", "@bbva-spherica-components/", "@cells/", "@cells-components/")
    markers = [f"dependency:{name}" for name in sorted(deps) if name.startswith(namespaces)]
    if isinstance(package.get("name"), str) and package["name"].startswith(namespaces):
        markers.append(f"package:{package['name']}")
    markers += [f"script:{key}" for key, value in scripts.items() if native_marker(value)]
    if (root / "cells.json").is_file():
        markers.append("file:cells.json")
    is_cells = bool(markers)
    native_families = sorted({m.group(1) for value in scripts.values() if (m := native_marker(value))})
    kind = "cells-app" if is_cells and "app" in native_families else "cells-component" if is_cells else (
        "web-component" if "lit" in deps or "lit-element" in deps else "generic")
    digest = hashlib.sha256(str(root).encode()).hexdigest()[:12]
    manager = package_manager(root, package)
    return {"root": str(root), "project": f"{root.name}-{digest}", "name": package.get("name", root.name),
            "is_cells": is_cells, "kind": kind, "markers": markers, "scripts": scripts,
            "package_manager": manager, "native_families": native_families}


def script_commands(scripts: dict, name: str, seen: tuple = ()) -> list[str]:
    """Resolve plain package-script aliases, including npm lifecycle commands.

    Complex shell wrappers stay visible and are never treated as verified aliases.
    """
    if name in seen or len(seen) >= 8:
        raise ValueError("Cyclic or overly deep package script aliases")
    value = scripts.get(name)
    if not isinstance(value, str):
        raise ValueError(f"Missing package script: {name}")
    tokens = shlex.split(value)
    commands = []
    for lifecycle in ("pre" + name,):
        if lifecycle in scripts:
            commands.append(scripts[lifecycle])
    if len(tokens) == 3 and tokens[:2] in (["npm", "run"], ["pnpm", "run"], ["yarn", "run"]):
        commands.extend(script_commands(scripts, tokens[2], seen + (name,)))
    else:
        commands.append(value)
    if "post" + name in scripts:
        commands.append(scripts["post" + name])
    return commands


def is_native_script(commands: list[str], intent: str) -> bool:
    found = False
    for command in commands:
        # Do not approve a native command hidden in an echo, comment or compound shell.
        tokens = shlex.split(command)
        if not tokens or any(char in command for char in (";", "&", "|", "`", "$", "\n", ">", "<")):
            return False
        while tokens and re.fullmatch(r"\w+=.*", tokens[0]):
            tokens.pop(0)
        if not tokens:
            return False
        if Path(tokens[0]).name not in {"cells", "cells.cmd"} or len(tokens) < 2:
            return False
        match = re.fullmatch(r"(app|lit-component|component):([\w-]+)", tokens[1])
        if not match or match.group(2) not in INTENTS[intent]:
            return False
        if intent == "coverage":
            options = tokens[2:]
            disabled = any(token in {"--no-coverage", "--coverage=false", "--coverage=0"} or
                           token == "--coverage" and i + 1 < len(options) and options[i + 1] in {"false", "0"}
                           for i, token in enumerate(options))
            # Component test coverage is built in (official CLI component:test docs).
            # Legacy lit-component:test scripts also provide Istanbul/c8 coverage.
            built_in = match.group(1) in {"component", "lit-component"}
            explicit = any(token in {"--coverage", "--coverage=true"} for token in options)
            if disabled or not (built_in or explicit):
                return False
        found = True
    return found


def resolve_command(cwd: str | Path, intent: str) -> dict:
    if intent not in INTENTS:
        raise ValueError("Unknown intent")
    info = project_info(cwd)
    candidates = []
    scripts = info["scripts"]
    preferred = {"test": ["test", "test:unit"], "coverage": ["test:coverage", "coverage"],
                 "lint": ["lint"], "build": ["build"], "start": ["start", "dev", "serve"]}[intent]
    for name in sorted(scripts, key=lambda key: (preferred.index(key) if key in preferred else 99, key)):
        try:
            commands = script_commands(scripts, name)
        except ValueError:
            continue
        native = is_native_script(commands, intent)
        if intent in {"test", "coverage"} and (any(word in name for word in ("watch", "update-snapshots")) or
                any(token.split("=", 1)[0] in {"--watch", "--w", "-w", "--update-snapshots", "--updateSnapshots", "--updateLocales", "--update-locales"} for command in commands for token in shlex.split(command))):
            continue
        if (info["is_cells"] and native) or (not info["is_cells"] and name in preferred):
            candidates.append({"script": name, "commands": commands, "native": native,
                               "argv": [info["package_manager"], "run", name]})
    return {"status": "success" if candidates else "blocked", "project": info["project"],
            "root": info["root"], "intent": intent, "is_cells": info["is_cells"],
            "selected": candidates[0] if candidates else None, "candidates": candidates,
            "reason": "Resolved from package.json, including lifecycle scripts" if candidates else
                      "No verified script for this intent; inspect local Cells CLI documentation/help. No command was invented."}

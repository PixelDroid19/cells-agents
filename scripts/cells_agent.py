#!/usr/bin/env python3
"""Render, install, and diagnose the Cells agent harness.

The checked-in source tree is canonical. Host packages are generated on demand;
no prebuilt portable tree is required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
EXAMPLES_ROOT = REPO_ROOT / "examples"
MANIFEST_PATH = REPO_ROOT / "harness" / "manifest.json"
MANAGED_BEGIN = "<!-- CELLS-AGENT-BUNDLE:BEGIN -->"
MANAGED_END = "<!-- CELLS-AGENT-BUNDLE:END -->"
CORE_COMMANDS = (
    "cells-init.md",
    "cells-explore.md",
    "cells-new.md",
    "cells-continue.md",
    "cells-ff.md",
    "cells-apply.md",
    "cells-verify.md",
    "cells-archive.md",
)
SKIP_NAMES = {"__pycache__", ".DS_Store"}
SKIP_SUFFIXES = (".db-shm", ".db-wal")
ROLE_AGENTS = ("cells-analysis", "cells-implementation", "cells-verification")
DEPRECATED_SKILLS = (
    "branch-pr",
    "cells-component-researcher",
    "cells-composition-architect",
    "cells-feature-analyzer",
    "cells-new",
    "cells-visual-intent-demo",
    "issue-creation",
    "skill-registry",
)


class HarnessError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def remove_exact(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def ensure_safe_render_target(path: Path) -> None:
    resolved = path.resolve()
    protected = {
        Path(resolved.anchor).resolve(),
        Path.home().resolve(),
        REPO_ROOT.resolve(),
    }
    if resolved in protected:
        raise HarnessError(f"Refusing to replace protected render target: {resolved}")


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_tree(source: Path, target: Path) -> None:
    if not source.is_dir():
        raise HarnessError(f"Missing source directory: {source}")
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if any(part in SKIP_NAMES for part in relative.parts) or path.name.endswith(SKIP_SUFFIXES):
            continue
        destination = target / relative
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        else:
            copy_file(path, destination)


def copy_glob(source: Path, pattern: str, target: Path) -> None:
    matches = sorted(source.glob(pattern))
    if not matches:
        raise HarnessError(f"No files matched {source / pattern}")
    for path in matches:
        copy_file(path, target / path.name)


def rewrite_logical_skill_paths(target: Path, prefix: str) -> None:
    for path in target.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml"}:
            continue
        text = path.read_text(encoding="utf-8-sig")
        rewritten = text.replace("skills/", prefix)
        if rewritten != text:
            path.write_text(rewritten, encoding="utf-8")


def copy_skills(target: Path, logical_prefix: str | None = None) -> None:
    shared = SKILLS_ROOT / "_shared"
    for pattern in ("*.md", "*.yaml"):
        copy_glob(shared, pattern, target / "_shared")
    for path in sorted(SKILLS_ROOT.iterdir()):
        if not path.is_dir() or path.name in {"_shared", "scripts", "evals"}:
            continue
        if (path / "SKILL.md").is_file():
            copy_tree(path, target / path.name)
    if logical_prefix is not None:
        rewrite_logical_skill_paths(target, logical_prefix.rstrip("/") + "/")


def copy_profile_agents(source: Path, target: Path, profile: str, pattern: str) -> None:
    names = ["cells-orchestrator"]
    if profile == "multi":
        names.extend(ROLE_AGENTS)
    suffix = pattern.removeprefix("*")
    for name in names:
        copy_file(source / f"{name}{suffix}", target / f"{name}{suffix}")


def patch_hook_paths(source: Path, target: Path, prefix: str) -> None:
    text = source.read_text(encoding="utf-8-sig")
    text = text.replace(".github/hooks/scripts/", prefix)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def adapt_vscode_single(root: Path) -> None:
    """Turn the canonical multi-agent instructions into a self-contained agent."""
    for path in (
        root / "workspace" / ".github" / "agents" / "cells-orchestrator.agent.md",
        root / "plugin" / "agents" / "cells-orchestrator.agent.md",
        root / "workspace" / ".github" / "plugin" / "agents" / "cells-orchestrator.agent.md",
    ):
        text = path.read_text(encoding="utf-8-sig")
        text = re.sub(r"^agents:.*$", "agents: []", text, count=1, flags=re.MULTILINE)
        text = re.sub(
            r"^handoffs:\n(?:  .*\n)+(?=---$)",
            "",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        text = text.replace(
            "You are a coordinator, not executor, for broad or delegated work; you are not a mandatory wrapper for every task. Keep the main thread thin for `full-workflow`: route, delegate, synthesize, and report. Read `skills/_shared/cells-agent-handoff-contract.md` before any substantial delegation, and apply its Handoff Packet, Dev-QA loop, `skill_resolution`, and `evidence_required` rules.",
            "You are the self-contained Cells agent for this profile. Execute the selected phase directly and keep work proportional. Read `skills/_shared/cells-agent-handoff-contract.md` for its output envelope, `skill_resolution`, and `evidence_required` rules.",
        )
        text = re.sub(
            r"Use subagents deliberately, never just because they are configured:.*?(?=For complex or risky work,)",
            "This profile has no role subagents. Perform analysis, implementation, and verification directly, while keeping their evidence distinct.\n\n",
            text,
            count=1,
            flags=re.DOTALL,
        )
        path.write_text(text, encoding="utf-8")

    for path in (root / "workspace" / ".github" / "prompts").glob("*.prompt.md"):
        text = path.read_text(encoding="utf-8-sig")
        text = re.sub(
            r"^agent: cells-(?:analysis|implementation|verification)$",
            "agent: cells-orchestrator",
            text,
            flags=re.MULTILINE,
        )
        path.write_text(text, encoding="utf-8")

    instructions_path = root / "workspace" / ".github" / "copilot-instructions.md"
    instructions = instructions_path.read_text(encoding="utf-8-sig")
    instructions = re.sub(
        r"^- Use `cells-orchestrator`.*custom agents only when role separation matters; do not delegate `fast-path` work\.$",
        "- Use the self-contained `cells-orchestrator` for all Cells phases; this profile has no role subagents.",
        instructions,
        flags=re.MULTILINE,
    )
    instructions = re.sub(
        r"^- `\.github/agents/cells-(?:analysis|implementation|verification)\.agent\.md`\n",
        "",
        instructions,
        flags=re.MULTILINE,
    )
    instructions_path.write_text(instructions, encoding="utf-8")


def adapt_codex_single(root: Path) -> None:
    agent_path = root / "home" / ".codex" / "agents" / "cells-orchestrator.toml"
    text = agent_path.read_text(encoding="utf-8-sig")
    replacements = {
        "You are a coordinator for full-workflow work, not a mandatory executor for every task.": "You are the self-contained Cells agent for this profile.",
        "- For scoped-change work, keep the task local unless independent slices or user-requested delegation justify role agents.": "- For scoped-change work, keep the task local and execute it directly.",
        "- Use the role agents under ~/.codex/agents/ for broad exploration, implementation, and verification only when the selected work mode justifies delegation.": "- Perform exploration, implementation, and verification directly, keeping their evidence distinct.",
        "- Follow the handoff rules in ~/.codex/skills/_shared/cells-agent-handoff-contract.md.": "- Use the output and evidence rules in ~/.codex/skills/_shared/cells-agent-handoff-contract.md.",
        "- Before delegation, pass a compact Handoff Packet with current_state, constraints, acceptance_criteria, and evidence_required.": "- Before changing files, establish current_state, constraints, acceptance_criteria, and evidence_required.",
        "- Require the standard envelope for delegated or phase work:": "- Return the standard envelope for phase work:",
        "- For testing, ensure delegated agents load only the testing skill(s)": "- For testing, load only the testing skill(s)",
        "- Preserve strict task scope and do not let executor agents delegate further.": "- Preserve strict task scope and do not delegate.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    agent_path.write_text(text, encoding="utf-8")

    config_path = root / "home" / ".codex" / "config.cells.example.toml"
    config = config_path.read_text(encoding="utf-8-sig")
    config = config.replace("multi_agent = true", "multi_agent = false")
    config = config.replace("max_threads = 6", "max_threads = 1")
    config_path.write_text(config, encoding="utf-8")

    instructions_path = root / "home" / ".codex" / "AGENTS.md"
    instructions = instructions_path.read_text(encoding="utf-8-sig")
    instructions = instructions.replace(
        "Use the role agents under `~/.codex/agents/` only for independent work that\nbenefits from a separate context. Executors do not delegate again.",
        "This profile has no role agents. Perform every selected Cells phase directly\nand keep analysis, implementation, and verification evidence distinct.",
    )
    instructions_path.write_text(instructions, encoding="utf-8")


def render_vscode(root: Path, profile: str) -> None:
    source = EXAMPLES_ROOT / "vscode"
    workspace = root / "workspace" / ".github"
    plugin = root / "plugin"

    copy_file(source / "copilot-instructions.md", workspace / "copilot-instructions.md")
    copy_glob(source / "instructions", "*.instructions.md", workspace / "instructions")
    copy_glob(source / "prompts", "*.prompt.md", workspace / "prompts")
    copy_profile_agents(source / "agents", workspace / "agents", profile, "*.agent.md")
    copy_glob(source / "hooks", "*.json", workspace / "hooks")
    copy_glob(source / "scripts", "*.js", workspace / "hooks" / "scripts")
    copy_skills(workspace / "skills", ".github/skills/")

    copy_file(source / "plugin" / "plugin.json", plugin / "plugin.json")
    copy_profile_agents(source / "agents", plugin / "agents", profile, "*.agent.md")
    patch_hook_paths(
        source / "hooks" / "cells-policy.json",
        plugin / "hooks" / "cells-policy.json",
        ".github/plugin/hooks/scripts/",
    )
    copy_glob(source / "scripts", "*.js", plugin / "hooks" / "scripts")
    copy_skills(plugin / "skills")
    copy_tree(plugin, workspace / "plugin")
    if profile == "single":
        adapt_vscode_single(root)



def render_opencode(root: Path, profile: str) -> None:
    source = EXAMPLES_ROOT / "opencode"
    config_name = f"opencode.{profile}.json"
    for scope, relative in (
        ("user", Path("home/.config/opencode")),
        ("workspace", Path("workspace/.opencode")),
    ):
        target = root / relative
        prefix = "~/.config/opencode/skills/" if scope == "user" else ".opencode/skills/"
        copy_skills(target / "skills", prefix)
        copy_file(source / config_name, target / "opencode.json")
        if scope == "user":
            for name in CORE_COMMANDS:
                copy_file(source / "commands" / name, target / "commands" / name)


def render_codex(root: Path, profile: str) -> None:
    source = EXAMPLES_ROOT / "codex"
    home = root / "home"
    codex = home / ".codex"
    plugin = home / ".agents" / "plugins" / "plugins" / "cells-agent-bundle-codex"

    copy_file(source / "AGENTS.md", codex / "AGENTS.md")
    copy_file(source / ".codex" / "config.toml", codex / "config.cells.example.toml")
    copy_file(source / ".codex" / "hooks.json", codex / "hooks.json")
    copy_tree(source / ".codex" / "hooks" / "scripts", codex / "hooks" / "scripts")
    copy_tree(source / ".codex" / "rules", codex / "rules")
    copy_profile_agents(source / ".codex" / "agents", codex / "agents", profile, "*.toml")
    copy_skills(codex / "skills", "~/.codex/skills/")

    plugin_source = REPO_ROOT / "plugins" / "cells-agent-bundle-codex"
    copy_tree(plugin_source / ".codex-plugin", plugin / ".codex-plugin")
    copy_tree(plugin_source / "skills", plugin / "skills")
    copy_skills(
        plugin / "assets" / "cells-skills",
        "${PLUGIN_ROOT}/assets/cells-skills/",
    )
    copy_file(
        REPO_ROOT / ".agents" / "plugins" / "marketplace.json",
        home / ".agents" / "plugins" / "marketplace.json",
    )
    if profile == "single":
        adapt_codex_single(root)


def build_file_manifest(root: Path, host: str, profile: str) -> dict[str, Any]:
    files = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.name == "render-manifest.json":
            continue
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    manifest = read_json(MANIFEST_PATH)
    return {
        "schema_version": 1,
        "bundle": manifest["bundle"],
        "host": host,
        "profile": profile,
        "capabilities": manifest["hosts"][host]["capabilities"],
        "files": files,
    }


def render_host(host: str, target: Path, profile: str, force: bool = False) -> Path:
    if target.exists() and any(target.iterdir()):
        if not force:
            raise HarnessError(f"Output is not empty; pass --force to replace it: {target}")
        ensure_safe_render_target(target)
        remove_exact(target)
    target.mkdir(parents=True, exist_ok=True)
    renderers = {
        "vscode": render_vscode,
        "codex": render_codex,
        "opencode": render_opencode,
    }
    renderers[host](target, profile)
    write_json(target / "render-manifest.json", build_file_manifest(target, host, profile))
    return target


def merge_markdown(source: Path, target: Path) -> str:
    block = f"{MANAGED_BEGIN}\n{source.read_text(encoding='utf-8-sig').strip()}\n{MANAGED_END}\n"
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(block, encoding="utf-8")
        return "created"
    current = target.read_text(encoding="utf-8-sig")
    if MANAGED_BEGIN in current and MANAGED_END in current:
        before, tail = current.split(MANAGED_BEGIN, 1)
        _, after = tail.split(MANAGED_END, 1)
        target.write_text(before.rstrip() + "\n\n" + block + after.lstrip(), encoding="utf-8")
        return "updated"
    target.write_text(current.rstrip() + "\n\n" + block, encoding="utf-8")
    return "merged"


def merge_json(source: Path, target: Path) -> str:
    incoming = read_json(source)
    if target.exists():
        current = read_json(target)
        status = "merged"
    else:
        current = {}
        status = "created"

    if "agent" in incoming:
        agents = current.setdefault("agent", {})
        for name in tuple(agents):
            if name in managed_opencode_agent_names():
                del agents[name]
        agents.update(incoming["agent"])
        if "$schema" in incoming:
            current.setdefault("$schema", incoming["$schema"])
    elif "plugins" in incoming:
        plugin_name = "cells-agent-bundle-codex"
        entries = [item for item in current.get("plugins", []) if item.get("name") != plugin_name]
        entries.extend(item for item in incoming.get("plugins", []) if item.get("name") == plugin_name)
        current.update({key: value for key, value in incoming.items() if key not in {"plugins"}})
        current["plugins"] = entries
    elif "hooks" in incoming:
        hooks = current.setdefault("hooks", {})
        for event, entries in incoming["hooks"].items():
            existing = hooks.setdefault(event, [])
            encoded = {json.dumps(item, sort_keys=True) for item in existing}
            existing.extend(item for item in entries if json.dumps(item, sort_keys=True) not in encoded)
    else:
        current.update(incoming)
    write_json(target, current)
    return status


def managed_opencode_agent_names() -> set[str]:
    names: set[str] = set()
    for profile in ("single", "multi"):
        names.update(read_json(EXAMPLES_ROOT / "opencode" / f"opencode.{profile}.json")["agent"])
    return names


def is_managed_relative(relative: Path) -> bool:
    text = relative.as_posix()
    return (
        "/skills/_shared/" in f"/{text}"
        or "/skills/cells-" in f"/{text}"
        or "/skills/agent-browser/" in f"/{text}"
        or "/agents/cells-" in f"/{text}"
        or "/commands/cells-" in f"/{text}"
        or "/hooks/scripts/cells-" in f"/{text}"
        or "plugins/cells-agent-bundle" in text
        or text.endswith("hooks/cells-policy.json")
    )


def ensure_safe_install_destination(root: Path, destination: Path) -> None:
    """Reject managed writes through symlinks or outside the selected target."""
    safe_root = root.resolve()
    try:
        relative = destination.relative_to(safe_root)
    except ValueError as exc:
        raise HarnessError(f"Install destination escapes target: {destination}") from exc

    current = safe_root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise HarnessError(f"Refusing managed path through symlink: {current}")
    resolved = destination.resolve(strict=False)
    if not resolved.is_relative_to(safe_root):
        raise HarnessError(f"Install destination escapes target: {resolved}")


def install_tree(source: Path, target: Path, force: bool) -> dict[str, list[str]]:
    target = target.resolve()
    result: dict[str, list[str]] = {
        "created": [],
        "updated": [],
        "merged": [],
        "skipped": [],
    }
    for path in sorted(item for item in source.rglob("*") if item.is_file()):
        relative = path.relative_to(source)
        if path.name == "render-manifest.json":
            continue
        destination = target / relative
        ensure_safe_install_destination(target, destination)
        rel_text = relative.as_posix()

        if rel_text.endswith(".codex/AGENTS.md") or rel_text.endswith(".github/copilot-instructions.md"):
            status = merge_markdown(path, destination)
            result[status].append(rel_text)
            continue
        if rel_text.endswith("opencode.json") or rel_text.endswith("marketplace.json") or rel_text.endswith(".codex/hooks.json"):
            status = merge_json(path, destination)
            result[status].append(rel_text)
            continue
        if destination.exists() and sha256(path) == sha256(destination):
            result["skipped"].append(rel_text)
            continue
        if destination.exists() and not (force or is_managed_relative(relative)):
            result["skipped"].append(rel_text)
            continue
        existed = destination.exists()
        copy_file(path, destination)
        result["updated" if existed else "created"].append(rel_text)
    return result


def resolve_install_source(rendered: Path, host: str, scope: str) -> Path:
    mapping = {
        ("vscode", "workspace"): rendered / "workspace",
        ("codex", "user"): rendered / "home",
        ("opencode", "user"): rendered / "home",
        ("opencode", "workspace"): rendered / "workspace",
    }
    try:
        return mapping[(host, scope)]
    except KeyError as exc:
        raise HarnessError(f"Unsupported host/scope combination: {host}/{scope}") from exc


def find_named_sibling(workspace: Path, pattern: str) -> Path | None:
    """Find a related checkout beside the workspace or one of its wrappers."""
    for parent in list(workspace.parents)[:4]:
        candidates = sorted(parent.glob(pattern))
        match = next((path.resolve() for path in candidates if path.is_dir()), None)
        if match:
            return match
    return None


def detect_context(workspace: Path, args: argparse.Namespace) -> dict[str, Any]:
    workspace = workspace.resolve()
    catalog = Path(args.catalog).resolve() if args.catalog else find_named_sibling(
        workspace, "bbva-spherica-components-*"
    )
    if catalog and (catalog / "packages").is_dir():
        catalog = catalog / "packages"
    docs = Path(args.docs).resolve() if args.docs else find_named_sibling(
        workspace, "cellsjs-guides-resources-*"
    )
    cells_cli = Path(args.cells_cli).resolve() if args.cells_cli else find_named_sibling(
        workspace, "bbva-cells-cli-*"
    )
    package_json = workspace / "package.json"
    return {
        "schema_version": 1,
        "workspace_root": str(workspace),
        "cells_project": package_json.is_file(),
        "component_catalog_root": str(catalog) if catalog else None,
        "official_docs_root": str(docs) if docs else None,
        "cells_cli_root": str(cells_cli) if cells_cli else None,
        "commands": {
            "app": ["cells app:serve", "cells app:build", "cells app:test", "cells app:lint"],
            "component": [
                "cells lit-component:serve",
                "cells lit-component:test",
                "cells lit-component:lint",
                "cells lit-component:documentation",
            ],
        },
    }


def write_context(workspace: Path, context: dict[str, Any]) -> Path:
    workspace = workspace.resolve()
    path = workspace / ".cells-agent" / "context.json"
    ensure_safe_install_destination(workspace, path)
    if path.is_file():
        current = read_json(path)
        roots = current.get("host_skill_roots", {})
        roots.update(context.get("host_skill_roots", {}))
        context["host_skill_roots"] = roots
    write_json(path, context)
    return path


def installed_skill_root(host: str, scope: str, target: Path) -> Path:
    mapping = {
        ("vscode", "workspace"): target / ".github" / "skills",
        ("codex", "user"): target / ".codex" / "skills",
        ("opencode", "user"): target / ".config" / "opencode" / "skills",
        ("opencode", "workspace"): target / ".opencode" / "skills",
    }
    return mapping[(host, scope)]


def cleanup_profile_assets(host: str, scope: str, target: Path, profile: str) -> list[str]:
    if profile != "single":
        return []
    target = target.resolve()
    relative_paths: list[Path] = []
    if host == "vscode" and scope == "workspace":
        for name in ROLE_AGENTS:
            relative_paths.extend(
                (
                    Path(".github/agents") / f"{name}.agent.md",
                    Path(".github/plugin/agents") / f"{name}.agent.md",
                )
            )
    elif host == "codex" and scope == "user":
        relative_paths.extend(Path(".codex/agents") / f"{name}.toml" for name in ROLE_AGENTS)

    removed: list[str] = []
    for relative in relative_paths:
        candidate = target / relative
        ensure_safe_install_destination(target, candidate)
        if candidate.exists():
            remove_exact(candidate)
            removed.append(str(candidate))
    return removed


def cleanup_deprecated_assets(
    host: str,
    scope: str,
    target: Path,
    *,
    force: bool = False,
) -> list[str]:
    if not force:
        return []
    target = target.resolve()
    removed: list[str] = []
    skill_root = installed_skill_root(host, scope, target)
    for name in DEPRECATED_SKILLS:
        candidate = skill_root / name
        ensure_safe_install_destination(target, candidate)
        if candidate.exists():
            remove_exact(candidate)
            removed.append(str(candidate))
    if host == "codex" and scope == "user":
        legacy_plugin = target / ".codex" / "plugins" / "cells-agent-bundle-codex"
        ensure_safe_install_destination(target, legacy_plugin)
        if legacy_plugin.exists():
            remove_exact(legacy_plugin)
            removed.append(str(legacy_plugin))
    return removed


def validate_source_tree() -> list[str]:
    errors: list[str] = []
    if not MANIFEST_PATH.is_file():
        errors.append(f"Missing manifest: {MANIFEST_PATH}")
    if not (SKILLS_ROOT / "_shared").is_dir():
        errors.append("Missing skills/_shared")
    for path in sorted(SKILLS_ROOT.iterdir()):
        if path.is_dir() and path.name not in {"_shared", "scripts", "evals"}:
            if not (path / "SKILL.md").is_file():
                errors.append(f"Missing SKILL.md: {path.name}")
    for path in REPO_ROOT.rglob("*"):
        if path.is_file() and path.name.endswith(SKIP_SUFFIXES):
            errors.append(f"Transient SQLite sidecar must not be packaged: {path}")
    return errors


def expected_agent_names(profile: str) -> set[str]:
    names = {"cells-orchestrator"}
    if profile == "multi":
        names.update(ROLE_AGENTS)
    return names


def validate_vscode_profile(root: Path, profile: str) -> list[str]:
    errors: list[str] = []
    expected = expected_agent_names(profile)
    agent_roots = (
        root / "workspace" / ".github" / "agents",
        root / "plugin" / "agents",
        root / "workspace" / ".github" / "plugin" / "agents",
    )
    for agent_root in agent_roots:
        found = {path.name.removesuffix(".agent.md") for path in agent_root.glob("*.agent.md")}
        if found != expected:
            errors.append(f"{agent_root} agents {sorted(found)} != {sorted(expected)}")
        for path in agent_root.glob("*.agent.md"):
            text = path.read_text(encoding="utf-8-sig")
            references = set(re.findall(r"\bcells-(?:analysis|implementation|verification)\b", text))
            if profile == "single" and references:
                errors.append(f"{path} references unavailable agents: {sorted(references)}")
            elif not references.issubset(found):
                errors.append(f"{path} references missing agents: {sorted(references - found)}")

    prompt_root = root / "workspace" / ".github" / "prompts"
    for path in prompt_root.glob("*.prompt.md"):
        text = path.read_text(encoding="utf-8-sig")
        match = re.search(r"^agent:\s*([a-z0-9-]+)\s*$", text, re.MULTILINE)
        if not match or match.group(1) not in expected:
            errors.append(f"{path} references an unavailable agent")
    instructions_path = root / "workspace" / ".github" / "copilot-instructions.md"
    instructions = instructions_path.read_text(encoding="utf-8-sig")
    role_references = set(re.findall(r"\bcells-(?:analysis|implementation|verification)\b", instructions))
    if profile == "single" and role_references:
        errors.append(f"{instructions_path} references unavailable agents: {sorted(role_references)}")
    return errors


def validate_codex_profile(root: Path, profile: str) -> list[str]:
    errors: list[str] = []
    expected = expected_agent_names(profile)
    agent_root = root / "home" / ".codex" / "agents"
    found = {path.stem for path in agent_root.glob("*.toml")}
    if found != expected:
        errors.append(f"{agent_root} agents {sorted(found)} != {sorted(expected)}")
    orchestrator = agent_root / "cells-orchestrator.toml"
    text = orchestrator.read_text(encoding="utf-8-sig")
    role_references = set(re.findall(r"\bcells-(?:analysis|implementation|verification)\b", text))
    if profile == "single" and role_references:
        errors.append(f"{orchestrator} references unavailable agents: {sorted(role_references)}")
    config = (root / "home" / ".codex" / "config.cells.example.toml").read_text(
        encoding="utf-8-sig"
    )
    expected_flag = "true" if profile == "multi" else "false"
    if f"multi_agent = {expected_flag}" not in config:
        errors.append(f"Codex {profile} config has the wrong multi_agent example")
    instructions_path = root / "home" / ".codex" / "AGENTS.md"
    instructions = instructions_path.read_text(encoding="utf-8-sig")
    role_references = set(re.findall(r"\bcells-(?:analysis|implementation|verification)\b", instructions))
    if profile == "single" and (
        role_references or "use the role agents" in instructions.lower()
    ):
        errors.append(f"{instructions_path} instructs use of unavailable role agents")

    gateway = (
        root
        / "home"
        / ".agents"
        / "plugins"
        / "plugins"
        / "cells-agent-bundle-codex"
        / "skills"
        / "cells-agent-bundle"
        / "SKILL.md"
    )
    gateway_text = gateway.read_text(encoding="utf-8-sig")
    gateway_root = gateway.parent
    referenced_paths = re.findall(r"`(\.\./\.\./assets/cells-skills/[^`]*)`", gateway_text)
    if not referenced_paths:
        errors.append(f"{gateway} does not reference its packaged skill payload")
    for reference in referenced_paths:
        if not (gateway_root / reference).resolve().exists():
            errors.append(f"{gateway} references missing packaged path: {reference}")
    return errors


def validate_opencode_profile(root: Path, profile: str) -> list[str]:
    errors: list[str] = []
    expected = set(read_json(EXAMPLES_ROOT / "opencode" / f"opencode.{profile}.json")["agent"])
    for config_path in (
        root / "home" / ".config" / "opencode" / "opencode.json",
        root / "workspace" / ".opencode" / "opencode.json",
    ):
        found = set(read_json(config_path).get("agent", {}))
        if found != expected:
            errors.append(f"{config_path} agents {sorted(found)} != {sorted(expected)}")
    return errors


def validate_rendered_profile(host: str, root: Path, profile: str) -> list[str]:
    validators = {
        "vscode": validate_vscode_profile,
        "codex": validate_codex_profile,
        "opencode": validate_opencode_profile,
    }
    return validators[host](root, profile)


def command_render(args: argparse.Namespace) -> int:
    hosts = list(read_json(MANIFEST_PATH)["hosts"]) if args.host == "all" else [args.host]
    output = Path(args.output).resolve()
    for host in hosts:
        destination = output / host if len(hosts) > 1 else output
        render_host(host, destination, args.profile, args.force)
        print(f"rendered {host}: {destination}")
    return 0


def command_install(args: argparse.Namespace) -> int:
    manifest = read_json(MANIFEST_PATH)
    if args.scope not in manifest["hosts"][args.host]["scopes"]:
        raise HarnessError(f"{args.host} does not support scope {args.scope}")
    target = Path(args.target).resolve() if args.target else (
        Path.cwd().resolve() if args.scope == "workspace" else Path.home().resolve()
    )
    workspace = Path(args.workspace).resolve() if args.workspace else Path.cwd().resolve()
    with tempfile.TemporaryDirectory(prefix="cells-agent-") as temp_dir:
        rendered = render_host(args.host, Path(temp_dir) / args.host, args.profile)
        source = resolve_install_source(rendered, args.host, args.scope)
        result = install_tree(source, target, args.force)
        result["removed"] = cleanup_profile_assets(
            args.host, args.scope, target, args.profile
        )
        result["removed"].extend(
            cleanup_deprecated_assets(
                args.host,
                args.scope,
                target,
                force=args.force,
            )
        )
    context = detect_context(workspace, args)
    context["host_skill_roots"] = {
        args.host: str(installed_skill_root(args.host, args.scope, target))
    }
    context_path = write_context(workspace, context)
    state = {
        "schema_version": 1,
        "host": args.host,
        "scope": args.scope,
        "profile": args.profile,
        "target": str(target),
        "context": str(context_path),
        "result": result,
    }
    state_path = workspace / ".cells-agent" / "install-state.json"
    ensure_safe_install_destination(workspace, state_path)
    write_json(state_path, state)
    print(json.dumps(state, indent=2, ensure_ascii=False))
    return 0


def command_doctor(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).resolve() if args.workspace else Path.cwd().resolve()
    context = detect_context(workspace, args)
    tools = {}
    for name in ("node", "python", "python3", "code", "codex", "opencode", "cells"):
        executable = shutil.which(name)
        tools[name] = executable
    report = {
        "source_errors": validate_source_tree(),
        "context": context,
        "tools": tools,
        "catalog_package_count": (
            len([path for path in Path(context["component_catalog_root"]).iterdir() if path.is_dir()])
            if context["component_catalog_root"] and Path(context["component_catalog_root"]).is_dir()
            else 0
        ),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["source_errors"] or not context["cells_project"] else 0


def command_validate(_: argparse.Namespace) -> int:
    errors = validate_source_tree()
    if errors:
        raise HarnessError("\n".join(errors))
    base_validators = (
        "validate_skill_quality.py",
        "validate_governance_behavior.py",
        "validate_official_docs_catalog.py",
        "validate_bundle_portability.py",
        "validate_opencode_assets.py",
    )
    for name in base_validators:
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / name)],
            cwd=REPO_ROOT,
            check=False,
        )
        if completed.returncode:
            return completed.returncode

    with tempfile.TemporaryDirectory(prefix="cells-agent-validate-") as temp_dir:
        root = Path(temp_dir)
        for host in read_json(MANIFEST_PATH)["hosts"]:
            render_host(host, root / host, "single")
            render_host(host, root / f"{host}-multi", "multi")
            for profile, profile_root in (
                ("single", root / host),
                ("multi", root / f"{host}-multi"),
            ):
                profile_errors = validate_rendered_profile(host, profile_root, profile)
                if profile_errors:
                    raise HarnessError("\n".join(profile_errors))
        validation_commands = (
            (
                "validate_opencode_assets.py",
                "--installed-root",
                str(root / "opencode" / "home"),
            ),
            (
                "validate_vscode_copilot_assets.py",
                "--installed-root",
                str(root / "vscode-multi" / "workspace" / ".github"),
            ),
            (
                "validate_vscode_copilot_assets.py",
                "--plugin-root",
                str(root / "vscode-multi" / "plugin"),
            ),
            (
                "validate_codex_assets.py",
                "--installed-root",
                str(root / "codex-multi" / "home"),
            ),
        )
        for command in validation_commands:
            completed = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / command[0]), *command[1:]],
                cwd=REPO_ROOT,
                check=False,
            )
            if completed.returncode:
                return completed.returncode
    print("Cells agent harness validation passed.")
    return 0


def add_context_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", help="Cells project root (defaults to current directory)")
    parser.add_argument("--catalog", help="Spherica repository or packages directory")
    parser.add_argument("--docs", help="Cells guides repository")
    parser.add_argument("--cells-cli", dest="cells_cli", help="Cells CLI repository")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    render = subparsers.add_parser("render", help="Generate host assets from canonical sources")
    render.add_argument("--host", choices=("vscode", "codex", "opencode", "all"), required=True)
    render.add_argument("--profile", choices=("single", "multi"), default="single")
    render.add_argument("--output", default=str(REPO_ROOT / "dist"))
    render.add_argument("--force", action="store_true")
    render.set_defaults(func=command_render)

    install = subparsers.add_parser("install", help="Render and install without a portable bundle")
    install.add_argument("--host", choices=("vscode", "codex", "opencode"), required=True)
    install.add_argument("--scope", choices=("user", "workspace"), required=True)
    install.add_argument("--profile", choices=("single", "multi"), default="single")
    install.add_argument("--target", help="Override user home or workspace destination")
    install.add_argument("--force", action="store_true", help="Replace non-managed conflicting files")
    add_context_arguments(install)
    install.set_defaults(func=command_install)

    doctor = subparsers.add_parser("doctor", help="Inspect Cells project, catalog, docs, CLI, and tools")
    add_context_arguments(doctor)
    doctor.set_defaults(func=command_doctor)

    validate = subparsers.add_parser("validate", help="Render every host and run repository validators")
    validate.set_defaults(func=command_validate)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (HarnessError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

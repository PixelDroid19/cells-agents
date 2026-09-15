#!/usr/bin/env python3
"""Create portable bundles from canonical sources; never install into a host."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent.parent
SKIP = shutil.ignore_patterns("__pycache__", "*.pyc", "*.db-wal", "*.db-shm", ".DS_Store")
KINDS = {"codex-plugin", "vscode-plugin", "codex-home", "vscode", "opencode-home", "project-local"}


def tree(source: Path, target: Path):
    shutil.copytree(source, target, dirs_exist_ok=True, ignore=SKIP)


def file(source: Path, target: Path):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def json_file(target: Path, data):
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def inventory(root: Path) -> dict[str, str]:
    """Snapshot generated files so a rebuild cannot discard local edits."""
    files = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.name.endswith((".pyc", ".db-wal", ".db-shm")) or path.name == ".DS_Store":
            continue
        if path.is_symlink():
            raise ValueError(f"Bundle contains a symlink: {relative}")
        if relative == Path(".cells-bundle.json"):
            continue
        if path.is_file():
            files[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def payload(target: Path):
    for source in (ROOT / "skills").iterdir():
        if source.is_dir() and (source.name in {"_shared", "scripts"} or (source / "SKILL.md").is_file()):
            tree(source, target / "skills" / source.name)
    tree(ROOT / "runtime", target / "runtime")
    tree(ROOT / "adapters", target / "adapters")
    for name in ("runtime.md", "memory.md", "architecture.md", "upstream-design-notes.md", "harness.md"):
        source = ROOT / "docs" / name
        if source.exists():
            file(source, target / "docs" / name)


def render(kind: str, target: Path, profile: str = "single"):
    if profile not in {"single", "multi"}:
        raise ValueError("Unknown agent profile")
    if kind == "codex-plugin":
        payload(target)
        tree(ROOT / "plugins/cells-agent-bundle-codex/.codex-plugin", target / ".codex-plugin")
        tree(ROOT / "plugins/cells-agent-bundle-codex/skills", target / "skills")
    elif kind == "vscode-plugin":
        payload(target)
        file(ROOT / "examples/vscode/plugin/plugin.json", target / "plugin.json")
        tree(ROOT / "examples/vscode/agents", target / "agents")
        tree(ROOT / "examples/vscode/scripts", target / "hooks/scripts")
        data = json.loads((ROOT / "examples/vscode/hooks/cells-policy.json").read_text())
        # Build structured commands rather than depending on the caller's workspace.
        for entries in data["hooks"].values():
            for entry in entries:
                script = entry["command"].split("/")[-1]
                entry["command"] = f'node "${{PLUGIN_ROOT}}/hooks/scripts/{script}"'
        json_file(target / "hooks/cells-policy.json", data)
        manifest = json.loads((target / "plugin.json").read_text())
        manifest["mcpServers"] = ".mcp.json"
        json_file(target / "plugin.json", manifest)
        json_file(target / ".mcp.json", {"mcpServers": {"cells": {"command": "python3", "args": ["${PLUGIN_ROOT}/runtime/cells-agent.py", "mcp"]}}})
    elif kind == "vscode":
        base = target / ".github"
        payload(base)
        for folder in ("agents", "prompts", "instructions", "hooks"):
            tree(ROOT / "examples/vscode" / folder, base / folder)
        tree(ROOT / "examples/vscode/scripts", base / "hooks/scripts")
        file(ROOT / "examples/vscode/copilot-instructions.md", base / "copilot-instructions.md")
        json_file(target / ".vscode/mcp.json", {"servers": {"cells": {"type": "stdio", "command": "python3", "args": ["${workspaceFolder}/.github/runtime/cells-agent.py", "--root", "${workspaceFolder}", "mcp"]}}})
    elif kind == "codex-home":
        base = target / ".codex"
        payload(base)
        tree(ROOT / "examples/codex/.codex", base)
        file(ROOT / "examples/codex/AGENTS.md", base / "AGENTS.md")
        file(ROOT / ".agents/plugins/marketplace.json", target / ".agents/plugins/marketplace.json")
        render("codex-plugin", target / ".agents/plugins/plugins/cells-agent-bundle-codex", profile)
    elif kind == "opencode-home":
        base = target / ".config/opencode"
        payload(base)
        tree(ROOT / "examples/opencode/commands", base / "commands")
        tree(ROOT / "examples/opencode/plugins", base / "plugins")
        file(ROOT / f"examples/opencode/opencode.{profile}.json", base / "opencode.json")
        for mode in ("single", "multi"):
            file(ROOT / f"examples/opencode/opencode.{mode}.json", target / f"templates/opencode.{mode}.json")
    elif kind == "project-local":
        payload(target / ".opencode")
        tree(ROOT / "examples/opencode/commands", target / ".opencode/commands")
        tree(ROOT / "examples/opencode/plugins", target / ".opencode/plugins")
        file(ROOT / f"examples/opencode/opencode.{profile}.json", target / ".opencode/opencode.json")
    else:
        raise ValueError("Unknown bundle kind")
    apply_profile(target, kind, profile)
    json_file(target / ".cells-bundle.json", {"format": "cells-agent-bundle", "version": 3, "kind": kind, "profile": profile, "files": inventory(target)})


def apply_profile(target: Path, kind: str, profile: str):
    """Apply the declared single-agent boundary to freshly staged files only."""
    if profile == "multi":
        return
    for folder in (target / "agents", target / ".github/agents", target / ".codex/agents"):
        if not folder.exists():
            continue
        for role in ("analysis", "implementation", "verification"):
            for suffix in (".agent.md", ".toml"):
                (folder / f"cells-{role}{suffix}").unlink(missing_ok=True)
        for agent in folder.glob("cells-orchestrator.*"):
            content = agent.read_text()
            if agent.suffix == ".md":
                import re
                content = re.sub(r"^agents: .*$", "agents: []", content, flags=re.MULTILINE)
                match = re.search(r"^tools: (.*)$", content, re.MULTILINE)
                if match:
                    filtered = [tool for tool in json.loads(match[1]) if tool != "agent"]
                    content = content[:match.start()] + "tools: " + json.dumps(filtered) + content[match.end():]
            else:
                content = content.replace("max_concurrent_threads_per_session = 4", "enabled = false")
            content += "\nThis installation uses the single profile. Perform the selected work directly. Do not delegate or launch subagents.\n" if agent.suffix == ".md" else ""
            if agent.suffix == ".toml":
                content = content.replace('developer_instructions = """', 'developer_instructions = """\nThis installation uses the single profile. Perform all work directly; do not delegate.')
            agent.write_text(content)
    config = target / ".codex/config.toml"
    if config.exists():
        config.write_text(config.read_text().replace("max_concurrent_threads_per_session = 4", "enabled = false"))


def build(kind: str, output: Path, profile: str = "single"):
    output = output.absolute()
    if output.is_symlink() or output.resolve() != output:
        raise ValueError("Bundle output must not traverse symlinks")
    reserved = [ROOT, ROOT / "skills", ROOT / "runtime", ROOT / "examples", ROOT / "scripts", Path.home(), Path("/")]
    if any(output == path or output in path.parents or path in output.parents for path in reserved[1:5]) or output in reserved:
        raise ValueError("Bundle output overlaps source or a protected directory")
    if output.exists() and any(output.iterdir()):
        marker = output / ".cells-bundle.json"
        if not marker.is_file():
            raise ValueError("Refusing to replace a nonempty, unowned output directory")
        ownership = json.loads(marker.read_text())
        if not isinstance(ownership, dict) or ownership.get("format") != "cells-agent-bundle" or ownership.get("version") != 3 or ownership.get("kind") != kind or not isinstance(ownership.get("files"), dict):
            raise ValueError("Invalid output ownership marker")
        if inventory(output) != ownership["files"]:
            raise ValueError("Output contains changed, missing or unowned files; preserve those changes and build into a new output directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".cells-build-", dir=output.parent) as temp:
        staged = Path(temp) / "bundle"
        staged.mkdir()
        render(kind, staged, profile)
        backup = Path(temp) / "previous"
        if output.exists():
            output.rename(backup)
        try:
            staged.rename(output)
        except OSError:
            if backup.exists():
                backup.rename(output)
            raise
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=sorted(KINDS | {"all"}))
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument("--profile", choices=("single", "multi"), default="single")
    args = parser.parse_args()
    try:
        if args.kind == "all":
            base = args.output or ROOT / "portable"
            for kind in sorted(KINDS - {"codex-plugin"}):
                print(build(kind, base / kind, args.profile))
        else:
            print(build(args.kind, args.output or ROOT / "dist" / args.kind, args.profile))
        return 0
    except (ValueError, OSError) as exc:
        print(f"Build failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

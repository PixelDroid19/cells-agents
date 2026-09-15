#!/usr/bin/env python3
"""Check native adapter capabilities and execute hooks from an external workspace."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parent.parent


def frontmatter(path):
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError(f"Missing frontmatter: {path}")
    fields = {}
    for line in text.split("---", 2)[1].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def check_payload(base):
    for path in ("runtime/cells-agent.py", "runtime/cells_agent/project.py", "runtime/cells_agent/memory.py", "skills/_shared/cells-rules-contract.md", "skills/cells-apply/SKILL.md"):
        if not (base / path).is_file():
            raise ValueError(f"Missing bundled service: {base / path}")
    with tempfile.TemporaryDirectory(prefix="cells external workspace ") as cwd:
        result = subprocess.run([sys.executable, str(base / "runtime/cells-agent.py"), "doctor"], cwd=cwd, capture_output=True, text=True, timeout=15)
        if result.returncode or not json.loads(result.stdout).get("fts5"):
            raise ValueError(f"Installed runtime failed: {result.stderr}")


def check_hooks(hook_file, base, *, plugin=False, codex=False, source=False):
    data = json.loads(hook_file.read_text())
    hooks = data.get("hooks", {})
    for event in ("SessionStart", "PreToolUse", "Stop"):
        if not hooks.get(event):
            raise ValueError(f"Missing hook event: {event}")
        entries = hooks[event]
        commands = [hook for entry in entries for hook in (entry.get("hooks", []) if codex else [entry])]
        for entry in commands:
            command = entry["command"]
            if plugin and "${PLUGIN_ROOT}/" not in command:
                raise ValueError("Standalone hooks must use PLUGIN_ROOT, not workspace-relative paths")
            argv = shlex.split(command)
            if source:
                script = ROOT / ("examples/codex/.codex/hooks/scripts" if codex else "examples/vscode/scripts") / Path(argv[1]).name
                argv[1] = str(script)
            else:
                argv = [arg.replace("${PLUGIN_ROOT}", str(base)).replace("$HOME/.codex", str(base)) for arg in argv]
                if argv[1].startswith(".github/"):
                    argv[1] = str(base.parent / argv[1])
            with tempfile.TemporaryDirectory(prefix="cells hook outside plugin ") as cwd:
                payload = {"cwd": cwd, "tool_name": "Bash", "tool_input": {"command": "git -C . reset --hard"}}
                result = subprocess.run(argv, input=json.dumps(payload), cwd=cwd, capture_output=True, text=True, timeout=15,
                                        env={**os.environ, "CELLS_AGENT_PYTHON": sys.executable})
                output = json.loads(result.stdout)
                if result.returncode:
                    raise ValueError(f"Hook process failed: {result.stderr}")
                if event == "PreToolUse" and output.get("hookSpecificOutput", {}).get("permissionDecision") != "ask":
                    raise ValueError("Destructive command variant was not routed to native permission review")


def validate(host, installed=None, plugin=None):
    source = installed is None and plugin is None
    if host == "vscode":
        base = plugin or installed or ROOT / "examples/vscode"
        roles = ("orchestrator", "analysis", "implementation", "verification") if source or (base / "agents/cells-analysis.agent.md").exists() else ("orchestrator",)
        for role in roles:
            fields = frontmatter(base / f"agents/cells-{role}.agent.md")
            allowed = json.loads(fields["agents"])
            tools = json.loads(fields["tools"])
            if role != "orchestrator" and (allowed or fields.get("disable-model-invocation") == "true"):
                raise ValueError(f"Executor {role} cannot be invoked or can spawn children")
            if role == "orchestrator" and (len(allowed) != (3 if len(roles) == 4 else 0) or not {"edit", "execute/runInTerminal"} <= set(tools) or (len(roles) == 1 and "agent" in tools)):
                raise ValueError("Orchestrator cannot handle direct work and native delegation")
            if role == "analysis" and ("edit" in tools or any(t.startswith("execute/") for t in tools)):
                raise ValueError("Analysis agent has unbounded write/execute tools")
            if "cells/cells_search" not in tools:
                raise ValueError("Agent cannot query the source catalogs")
        for path in (base / "prompts").glob("*.prompt.md"):
            if "tools" in frontmatter(path):
                raise ValueError(f"Prompt overrides agent capabilities: {path}")
        check_hooks(base / "hooks/cells-policy.json", base, plugin=plugin is not None, source=source)
        if not source:
            check_payload(base)
            mcp_path = base / ".mcp.json" if plugin else base.parent / ".vscode/mcp.json"
            data = json.loads(mcp_path.read_text())
            if "cells" not in data.get("mcpServers" if plugin else "servers", {}):
                raise ValueError("Cells MCP server is absent")
    elif host == "codex":
        if plugin:
            check_payload(plugin)
            manifest = json.loads((plugin / ".codex-plugin/plugin.json").read_text())
            if manifest.get("skills") != "./skills/":
                raise ValueError("Codex plugin must expose native skill discovery")
            if not (plugin / "skills/cells-agent-bundle/SKILL.md").is_file():
                raise ValueError("Missing optional bundle entrypoint")
            return
        base = installed / ".codex" if installed else ROOT / "examples/codex/.codex"
        roles = ("orchestrator", "analysis", "implementation", "verification") if source or (base / "agents/cells-analysis.toml").exists() else ("orchestrator",)
        for role in roles:
            value = tomllib.loads((base / f"agents/cells-{role}.toml").read_text())
            if role != "orchestrator" and value.get("agents", {}).get("enabled") is not False:
                raise ValueError(f"Codex executor {role} still exposes multi-agent tools")
            if role == "analysis" and value.get("sandbox_mode") != "read-only":
                raise ValueError("Codex analysis lacks read-only sandbox")
            if "model" in value:
                raise ValueError("Bundle unexpectedly pins an account-specific model")
        check_hooks(base / "hooks.json", base, codex=True, source=source)
        if not source:
            check_payload(base)
            validate("codex", plugin=installed / ".agents/plugins/plugins/cells-agent-bundle-codex")
    elif host == "opencode":
        base = installed or ROOT / "examples/opencode"
        if (base / ".config/opencode").exists():
            base = base / ".config/opencode"
        configs = list(base.glob("opencode*.json"))
        if not configs:
            raise ValueError("Missing OpenCode config")
        for path in configs:
            data = json.loads(path.read_text())
            for name, agent in data["agent"].items():
                permissions = agent["permission"]
                if name != "cells-orchestrator" and permissions.get("task") != "deny":
                    raise ValueError("OpenCode executor may delegate")
                if any(permissions.get(key) != "deny" for key in ("delegate", "delegation_read", "delegation_list")):
                    raise ValueError("Legacy delegation tools remain enabled")
        plugin_file = base / "plugins/background-agents.ts"
        module = plugin_file.read_text()
        with tempfile.TemporaryDirectory(prefix="cells inert plugin ") as temp:
            test = Path(temp) / "plugin.mjs"
            test.write_text(module + "\nconst hooks = await BackgroundAgentsPlugin(); if (Object.keys(hooks).length) throw new Error('Unexpected plugin capabilities');\n")
            subprocess.run(["node", str(test)], check=True, capture_output=True, timeout=10)
        if not source:
            check_payload(base)


def main(host=None):
    parser = argparse.ArgumentParser(description=__doc__)
    if host is None:
        parser.add_argument("host", choices=("codex", "vscode", "opencode"))
    parser.add_argument("--installed-root", type=Path)
    parser.add_argument("--plugin-root", type=Path)
    args = parser.parse_args()
    try:
        validate(host or args.host, args.installed_root.resolve() if args.installed_root else None, args.plugin_root.resolve() if args.plugin_root else None)
        print(f"{host or args.host} adapter contracts passed (native UI sessions not tested).")
        return 0
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

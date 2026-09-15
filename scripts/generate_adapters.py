#!/usr/bin/env python3
"""Render small native projections from the capability manifest. No host writes."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDANCE = """Use the smallest relevant Cells skill for the request. Answer narrow questions directly and perform only work allowed by your role. Preserve unrelated changes. The primary agent can implement authorized scoped edits directly; for broad work it keeps a concise plan and delegates only useful independent tasks.

Use skills/_shared/cells-work-sizing-contract.md to size work. For Cells API or architectural claims follow cells-source-routing-contract.md and cells-rules-contract.md. Search the relevant bundled catalog first; fetch full APIs only when needed. Read installed manifests/CEM/source before inventing an interface. Resolve package scripts with Cells Agent before tests; load coverage or test-authoring skills only for those intents.

Optional Cells Memory stores project reference notes. It is independent from workflow artifacts and verification. Recheck remembered facts against current files; do not capture raw prompts or credentials. The CLI and MCP tools never replace native host permissions.

When the primary agent delegates, it follows cells-agent-handoff-contract.md: give scope, acceptance criteria and required evidence, use one writer per file, inspect returned evidence, and integrate fixes. Children stay within their assignment and never delegate. Return concise findings with sources and validation; delegated results include status (success/partial/blocked), skill_resolution and evidence_required. Ordinary answers do not need an envelope.
"""
ROLE = {
    "orchestrator": "Own requirements, scoped implementation, integration and final validation. Delegate only when useful; use at most four children.",
    "analysis": "Gather source-backed evidence. Do not edit project files or execute arbitrary commands. Use the Cells MCP read tools for catalogs and command resolution. If unavailable, return the precise missing capability for the parent to resolve.",
    "implementation": "Implement the assigned scope and run focused checks. Do not expand into unrelated cleanup.",
    "verification": "Independently validate current changes. Execute appropriate checks and inspect behavior. Do not edit application source. Missing proof must remain explicit.",
}


def projections():
    config = json.loads((ROOT / "adapters/hosts.json").read_text())
    result = {}
    for role, caps in config["roles"].items():
        name = f"cells-{role}"
        tools = ["agent", "read", "search", "web/fetch", "cells/cells_project", "cells/cells_route", "cells/cells_resolve", "cells/cells_search", "cells/cells_evidence", "cells/cells_memory_search", "cells/cells_memory_get", "cells/cells_memory_context"]
        if caps["source_edit"]:
            tools += ["edit"]
        if caps["execute"]:
            tools += ["execute/runInTerminal", "execute/getTerminalOutput"]
        if role == "verification":
            tools += ["browser"]
        children = ["cells-analysis", "cells-implementation", "cells-verification"] if caps["delegate"] else []
        instruction = ROLE[role] + ("\nDo not delegate. Do not launch subagents.\n" if not caps["delegate"] else "\n")
        result[f"examples/vscode/agents/{name}.agent.md"] = (
            f"---\nname: {name}\ndescription: {ROLE[role]}\ntools: {json.dumps(tools)}\nagents: {json.dumps(children)}\n"
            f"disable-model-invocation: false\n---\n\n{instruction}\n{GUIDANCE}\n"
            "Resolve skills relative to this installed bundle: ../skills/. The workspace installation uses .github/skills. The bundled MCP server is named cells.\n")
        sandbox = caps["codex_sandbox"]
        result[f"examples/codex/.codex/agents/{name}.toml"] = (
            f"name = {json.dumps(name)}\ndescription = {json.dumps(ROLE[role])}\nsandbox_mode = {json.dumps(sandbox)}\n"
            'developer_instructions = """\n' + instruction + "\n" + GUIDANCE +
            "\nUse the installed plugin's visible skills directory. Resolve its path from the active skill location rather than assuming a cache directory.\n" + '"""\n\n[agents]\n' +
            ("max_concurrent_threads_per_session = 4\n" if caps["delegate"] else "enabled = false\n"))
    result["examples/codex/AGENTS.md"] = "# Cells Agent\n\nApply this guidance when local BBVA dependencies, Cells configuration or native Cells scripts establish a Cells project. Plain Lit alone is insufficient.\n\n" + GUIDANCE + "\nThe plugin exposes individual skills under its skills directory and the portable CLI at runtime/cells-agent.py. Global install: ~/.agents/plugins/plugins/cells-agent-bundle-codex/. Select a model in Codex; no model is pinned by the bundle.\n"
    launcher = "import pathlib,runpy,sys; p=pathlib.Path.home()/'.codex/runtime'; sys.path.insert(0,str(p)); sys.argv=[str(p/'cells-agent.py'),'mcp']; runpy.run_path(str(p/'cells-agent.py'),run_name='__main__')"
    result["examples/codex/.codex/config.toml"] = ("# Merge these optional settings with your existing Codex configuration.\n[features]\ncodex_hooks = true\n\n[agents]\nmax_concurrent_threads_per_session = 4\n\n[mcp_servers.cells]\ncommand = \"python3\"\nargs = " + json.dumps(["-c", launcher]) + "\n")
    result["examples/vscode/copilot-instructions.md"] = "# Cells Agent\n\nApply only to repositories with BBVA dependencies, Cells config or native Cells scripts; a generic Lit project is not sufficient.\n\n" + GUIDANCE + "\nSkills are in .github/skills; the CLI is .github/runtime/cells-agent.py. The optional cells MCP server is configured in .vscode/mcp.json.\n"
    result["examples/vscode/instructions/cells-orchestrator.instructions.md"] = '---\napplyTo: "**/*"\n---\n\n# Cells routing\n\nApply only after local Cells project evidence. Use the matching skill, real command resolution and source citations. Load shared contracts on demand through the skill; keep ordinary edits proportional.\n'
    phases = ["explore", "propose", "spec", "design", "tasks", "apply", "verify", "archive", "fallback"]
    for phase in phases:
        result[f"examples/vscode/prompts/cells-{phase}.prompt.md"] = (
            f"---\nname: cells-{phase}\ndescription: Run the {phase} intent with proportional Cells guidance.\nagent: cells-orchestrator\n---\n\n"
            f"Use cells-{phase if phase != 'fallback' else 'explore'} for the requested intent. Apply only the needed scope and cite actual sources and validation. "
            "Inherit the agent's tools; do not override delegation or catalog access at prompt level.\n")
    phase_roles = {"analysis": "analysis", "implementation": "implementation", "verification": "verification"}
    agents = {}
    for phase, role in {"orchestrator": "orchestrator", **phase_roles}.items():
        caps = config["roles"][role]
        permissions = {"task": {"*": "deny", "cells-*": "allow"} if caps["delegate"] else "deny",
                       "edit": "allow" if caps["source_edit"] else "deny", "bash": "allow" if caps["execute"] else "deny",
                       "delegate": "deny", "delegation_read": "deny", "delegation_list": "deny"}
        # Keep OpenCode's built-in sensitive-file read defaults; do not overwrite read permissions.
        agents[f"cells-{phase}"] = {"mode": "primary" if phase == "orchestrator" else "subagent",
                                   "description": ROLE[role], "prompt": ROLE[role] + "\n" + GUIDANCE +
                                   ("\nChoose the relevant skill for your assigned scope. Do not delegate. Do not launch subagents.\n" if phase != "orchestrator" else ""),
                                   "permission": permissions}
    for mode in ("multi", "single", "default"):
        selected = agents if mode == "multi" else {"cells-orchestrator": dict(agents["cells-orchestrator"])}
        if mode != "multi":
            selected["cells-orchestrator"]["permission"] = dict(selected["cells-orchestrator"]["permission"], task="deny")
        filename = "opencode.json" if mode == "default" else f"opencode.{mode}.json"
        launcher = "import pathlib,runpy,sys; p=pathlib.Path.home()/'.config/opencode/runtime'; sys.path.insert(0,str(p)); sys.argv=[str(p/'cells-agent.py'),'mcp']; runpy.run_path(str(p/'cells-agent.py'),run_name='__main__')"
        result[f"examples/opencode/{filename}"] = json.dumps({"$schema": "https://opencode.ai/config.json", "agent": selected,
                "mcp": {"cells": {"type": "local", "command": ["python3", "-c", launcher], "enabled": True}}}, indent=2) + "\n"
    for phase in ("init", "explore", "new", "continue", "ff", "apply", "verify", "archive"):
        result[f"examples/opencode/commands/cells-{phase}.md"] = (f"---\ndescription: Cells {phase} intent\nagent: cells-orchestrator\n---\n\nHandle the {phase} intent: $ARGUMENTS. Load only the relevant installed Cells skill. Use direct work for narrow changes and a plan for broad work. Preserve prior authorization and verify actual results.\n")
    result["harness/manifest.json"] = json.dumps({"schema_version": 1, "bundle": config["bundle"], "profiles": config["profiles"], "hosts": config["hosts"]}, indent=2) + "\n"
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    drift = []
    for relative, text in projections().items():
        path = ROOT / relative
        if args.check:
            if not path.exists() or path.read_text() != text:
                drift.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    if drift:
        print("Adapter drift: " + ", ".join(drift))
        return 1
    print("Native adapter projections verified." if args.check else "Native adapter projections generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate OpenCode CELLS agent assets for proportional orchestration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = ROOT / "examples" / "opencode"

REQUIRED_MODES = ("fast-path", "scoped-change", "full-workflow", "blocked")
FORBIDDEN_PHRASES = (
    "always delegate",
    "always use subagents",
    "delegate-first",
    "full workflow for every",
    "full-workflow for every",
)


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def opencode_root(root: Path) -> Path:
    if (root / ".config" / "opencode").is_dir():
        return root / ".config" / "opencode"
    return root


def template_root(root: Path) -> Path:
    if (root / "templates").is_dir():
        return root / "templates"
    if (root.parent / "templates").is_dir():
        return root.parent / "templates"
    return root


def validate_common_text(path: Path, text: str) -> list[str]:
    invalid: list[str] = []
    if "cells-work-sizing-contract.md" not in text:
        invalid.append(f"{display(path)} missing cells-work-sizing-contract.md")
    lowered = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            invalid.append(f"{display(path)} contains non-proportional instruction: {phrase}")
    return invalid


def validate_orchestrator(path: Path, agent: dict, *, multi: bool) -> list[str]:
    invalid: list[str] = []
    prompt = str(agent.get("prompt", ""))
    if agent.get("mode") != "primary":
        invalid.append(f"{display(path)} cells-orchestrator must use mode: primary")
    for mode in REQUIRED_MODES:
        if mode not in prompt:
            invalid.append(f"{display(path)} cells-orchestrator missing work mode: {mode}")
    invalid.extend(validate_common_text(path, prompt))

    permission = agent.get("permission")
    if not isinstance(permission, dict):
        return invalid + [f"{display(path)} cells-orchestrator missing permission object"]
    task_permission = permission.get("task")
    if multi:
        if not isinstance(task_permission, dict):
            invalid.append(f"{display(path)} multi orchestrator must restrict permission.task with glob rules")
        else:
            if task_permission.get("*") != "deny":
                invalid.append(f"{display(path)} multi orchestrator must deny permission.task '*'")
            if task_permission.get("cells-*") != "allow":
                invalid.append(f"{display(path)} multi orchestrator must allow permission.task 'cells-*'")
    elif task_permission != "deny":
        invalid.append(f"{display(path)} single orchestrator must set permission.task = deny")
    return invalid


def validate_subagent(path: Path, name: str, agent: dict) -> list[str]:
    invalid: list[str] = []
    prompt = str(agent.get("prompt", ""))
    if agent.get("mode") != "subagent":
        invalid.append(f"{display(path)} {name} must use mode: subagent")
    if agent.get("hidden") is not True:
        invalid.append(f"{display(path)} {name} must set hidden: true")
    permission = agent.get("permission")
    if not isinstance(permission, dict):
        invalid.append(f"{display(path)} {name} missing permission object")
    elif permission.get("task") != "deny":
        invalid.append(f"{display(path)} {name} must set permission.task = deny")
    lowered_prompt = prompt.lower()
    for token in ("do not delegate", "do not call task/delegate", "do not launch sub-agents"):
        if token not in lowered_prompt:
            invalid.append(f"{display(path)} {name} missing executor isolation token: {token}")
    invalid.extend(validate_common_text(path, prompt))
    return invalid


def validate_config(path: Path, *, multi: bool) -> list[str]:
    invalid: list[str] = []
    if not path.is_file():
        return [f"Missing OpenCode config: {display(path)}"]
    try:
        data = read_json(path)
    except json.JSONDecodeError as exc:
        return [f"{display(path)} is not valid JSON: {exc}"]
    if "tools" in data:
        invalid.append(f"{display(path)} uses deprecated top-level tools; use permission")

    agents = data.get("agent")
    if not isinstance(agents, dict) or "cells-orchestrator" not in agents:
        return invalid + [f"{display(path)} missing agent.cells-orchestrator"]

    for name, agent in agents.items():
        if isinstance(agent, dict) and "tools" in agent:
            invalid.append(f"{display(path)} agent {name} uses deprecated tools; use permission")

    invalid.extend(validate_orchestrator(path, agents["cells-orchestrator"], multi=multi))
    if not multi:
        if len(agents) != 1:
            invalid.append(f"{display(path)} single profile must only define cells-orchestrator")
        return invalid

    expected_subagents = {
        "cells-init",
        "cells-explore",
        "cells-propose",
        "cells-spec",
        "cells-design",
        "cells-tasks",
        "cells-apply",
        "cells-verify",
        "cells-archive",
        "cells-cleanup",
    }
    missing = expected_subagents - set(agents)
    if missing:
        invalid.append(f"{display(path)} missing subagents: {', '.join(sorted(missing))}")
    for name in sorted(expected_subagents & set(agents)):
        agent = agents[name]
        if isinstance(agent, dict):
            invalid.extend(validate_subagent(path, name, agent))
        else:
            invalid.append(f"{display(path)} agent {name} must be an object")
    return invalid


def validate_commands(commands_root: Path) -> list[str]:
    invalid: list[str] = []
    required_commands = [
        "cells-apply.md",
        "cells-explore.md",
        "cells-verify.md",
    ]
    for filename in required_commands:
        path = commands_root / filename
        if not path.is_file():
            invalid.append(f"Missing OpenCode command: {display(path)}")
            continue
        text = path.read_text(encoding="utf-8")
        invalid.extend(validate_common_text(path, text))
    return invalid


def validate_source(root: Path) -> list[str]:
    invalid: list[str] = []
    invalid.extend(validate_config(root / "opencode.single.json", multi=False))
    invalid.extend(validate_config(root / "opencode.multi.json", multi=True))
    invalid.extend(validate_commands(root / "commands"))
    return invalid


def validate_installed(root: Path) -> list[str]:
    invalid: list[str] = []
    config_root = opencode_root(root)
    invalid.extend(validate_config(config_root / "opencode.json", multi=False))
    templates = template_root(root)
    if (templates / "opencode.single.json").is_file():
        invalid.extend(validate_config(templates / "opencode.single.json", multi=False))
    if (templates / "opencode.multi.json").is_file():
        invalid.extend(validate_config(templates / "opencode.multi.json", multi=True))
    invalid.extend(validate_commands(config_root / "commands"))
    return invalid


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CELLS OpenCode assets.")
    parser.add_argument("--installed-root", type=Path, help="OpenCode root or portable home root to validate")
    args = parser.parse_args()

    errors = validate_installed(args.installed_root.resolve()) if args.installed_root else validate_source(SOURCE_ROOT)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("OpenCode assets are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

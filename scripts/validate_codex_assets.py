#!/usr/bin/env python3
"""Validate Codex project-layer and plugin assets for the CELLS bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = ROOT / "examples" / "codex"
REPO_PLUGIN_ROOT = ROOT / "plugins" / "cells-agent-bundle-codex"
REPO_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN_NAME = "cells-agent-bundle-codex"

SOURCE_REQUIRED_FILES = [
    "AGENTS.md",
    "docs/README.md",
    ".codex/config.toml",
    ".codex/hooks.json",
    ".codex/rules/default.rules",
    ".codex/agents/cells-orchestrator.toml",
    ".codex/agents/cells-analysis.toml",
    ".codex/agents/cells-implementation.toml",
    ".codex/agents/cells-verification.toml",
    ".codex/hooks/scripts/cells-session-context.js",
    ".codex/hooks/scripts/cells-pretool-policy.js",
    ".codex/hooks/scripts/cells-stop-reminder.js",
]

INSTALLED_REQUIRED_FILES = [
    "AGENTS.md",
    ".codex/config.toml",
    ".codex/hooks.json",
    ".codex/rules/default.rules",
    ".codex/agents/cells-orchestrator.toml",
    ".codex/agents/cells-analysis.toml",
    ".codex/agents/cells-implementation.toml",
    ".codex/agents/cells-verification.toml",
    ".codex/hooks/scripts/cells-session-context.js",
    ".codex/hooks/scripts/cells-pretool-policy.js",
    ".codex/hooks/scripts/cells-stop-reminder.js",
    ".agents/plugins/marketplace.json",
    "plugins/cells-agent-bundle-codex/.codex-plugin/plugin.json",
    "plugins/cells-agent-bundle-codex/skills/cells-agent-bundle/SKILL.md",
    "plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-work-sizing-contract.md",
    "plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-agent-handoff-contract.md",
    "plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-rules-contract.md",
    "plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-apply/SKILL.md",
    "plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-cli-usage/SKILL.md",
    "plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-coverage/SKILL.md",
    "plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-test-creator/SKILL.md",
    "plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-verify/SKILL.md",
]


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def validate_required_files(base: Path, required: list[str]) -> list[str]:
    invalid: list[str] = []
    for relative in required:
        path = base / relative
        if not path.is_file():
            invalid.append(f"Missing required file: {display(path)}")
    for ds_store in base.rglob(".DS_Store"):
        invalid.append(f"{display(ds_store)} is accidental macOS metadata and must not be committed")
    return invalid


def validate_source_assets() -> list[str]:
    invalid = validate_required_files(SOURCE_ROOT, SOURCE_REQUIRED_FILES)
    invalid.extend(validate_agents_md(SOURCE_ROOT / "AGENTS.md"))
    invalid.extend(validate_config(SOURCE_ROOT / ".codex" / "config.toml"))
    invalid.extend(validate_hooks(SOURCE_ROOT / ".codex" / "hooks.json", SOURCE_ROOT / ".codex"))
    invalid.extend(validate_rules(SOURCE_ROOT / ".codex" / "rules" / "default.rules"))
    invalid.extend(validate_agent_files(SOURCE_ROOT / ".codex" / "agents"))
    invalid.extend(validate_plugin(REPO_PLUGIN_ROOT))
    invalid.extend(validate_marketplace(REPO_MARKETPLACE, ROOT))
    return invalid


def validate_agents_md(path: Path) -> list[str]:
    invalid: list[str] = []
    if not path.is_file():
        return [f"Missing AGENTS file: {display(path)}"]
    text = path.read_text(encoding="utf-8")
    required_tokens = [
        "plugins/cells-agent-bundle-codex/.cache/cells-skills/",
        "cells-cli-usage",
        "cells-coverage",
        "cells-test-creator",
        "cells-work-sizing-contract.md",
        "fast-path",
        "scoped-change",
        "full-workflow",
        "cells-agent-handoff-contract.md",
    ]
    for token in required_tokens:
        if token not in text:
            invalid.append(f"{display(path)} missing token: {token}")
    return invalid


def validate_config(path: Path) -> list[str]:
    invalid: list[str] = []
    if not path.is_file():
        return [f"Missing config file: {display(path)}"]
    data = read_toml(path)
    for key in ("approval_policy", "sandbox_mode", "project_doc_fallback_filenames", "project_doc_max_bytes"):
        if key not in data:
            invalid.append(f"{display(path)} missing config key: {key}")
    features = data.get("features")
    if not isinstance(features, dict):
        invalid.append(f"{display(path)} missing [features] table")
    else:
        if features.get("codex_hooks") is not True:
            invalid.append(f"{display(path)} must enable features.codex_hooks = true")
        if features.get("multi_agent") is not True:
            invalid.append(f"{display(path)} must enable features.multi_agent = true")
    agents = data.get("agents")
    if not isinstance(agents, dict):
        invalid.append(f"{display(path)} missing [agents] table")
    else:
        if agents.get("max_threads") != 6:
            invalid.append(f"{display(path)} must set agents.max_threads = 6")
        if agents.get("max_depth") != 1:
            invalid.append(f"{display(path)} must set agents.max_depth = 1")
    return invalid


def validate_hooks(path: Path, codex_root: Path) -> list[str]:
    invalid: list[str] = []
    if not path.is_file():
        return [f"Missing hooks file: {display(path)}"]
    data = read_json(path)
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return [f"{display(path)} missing hooks object"]

    required_events = {
        "SessionStart": "cells-session-context.js",
        "PreToolUse": "cells-pretool-policy.js",
        "Stop": "cells-stop-reminder.js",
    }
    for event_name, expected_script in required_events.items():
        groups = hooks.get(event_name)
        if not isinstance(groups, list) or not groups:
            invalid.append(f"{display(path)} missing hook event: {event_name}")
            continue
        if event_name == "PreToolUse" and not any(group.get("matcher") == "^Bash$" for group in groups if isinstance(group, dict)):
            invalid.append(f"{display(path)} PreToolUse must match ^Bash$")
        commands = []
        for group in groups:
            if not isinstance(group, dict):
                continue
            for hook in group.get("hooks", []):
                if isinstance(hook, dict):
                    commands.append(str(hook.get("command", "")))
        if not any(expected_script in command for command in commands):
            invalid.append(f"{display(path)} {event_name} missing command for {expected_script}")

    policy_script = codex_root / "hooks" / "scripts" / "cells-pretool-policy.js"
    if policy_script.is_file():
        policy_text = policy_script.read_text(encoding="utf-8")
        if "permissionDecision = 'ask'" in policy_text or 'permissionDecision = "ask"' in policy_text:
            invalid.append(f"{display(policy_script)} uses unsupported PreToolUse permissionDecision ask; use rules prompt entries instead")

    for script in (
        "hooks/scripts/cells-session-context.js",
        "hooks/scripts/cells-pretool-policy.js",
        "hooks/scripts/cells-stop-reminder.js",
    ):
        if not (codex_root / script).is_file():
            invalid.append(f"Missing hook script: {display(codex_root / script)}")
    return invalid


def validate_rules(path: Path) -> list[str]:
    invalid: list[str] = []
    if not path.is_file():
        return [f"Missing rules file: {display(path)}"]
    text = path.read_text(encoding="utf-8")
    for token in ("prefix_rule(", 'decision = "prompt"', 'decision = "forbidden"'):
        if token not in text:
            invalid.append(f"{display(path)} missing token: {token}")
    return invalid


def validate_agent_files(base: Path) -> list[str]:
    invalid: list[str] = []
    expected = {
        "cells-orchestrator.toml": ("cells-orchestrator", "read-only"),
        "cells-analysis.toml": ("cells-analysis", "read-only"),
        "cells-implementation.toml": ("cells-implementation", "workspace-write"),
        "cells-verification.toml": ("cells-verification", "workspace-write"),
    }
    for filename, (agent_name, sandbox_mode) in expected.items():
        path = base / filename
        if not path.is_file():
            invalid.append(f"Missing agent file: {display(path)}")
            continue
        data = read_toml(path)
        for key in ("name", "description", "developer_instructions"):
            if key not in data:
                invalid.append(f"{display(path)} missing agent key: {key}")
        if data.get("name") != agent_name:
            invalid.append(f"{display(path)} must define name = {agent_name}")
        if data.get("sandbox_mode") != sandbox_mode:
            invalid.append(f"{display(path)} must define sandbox_mode = {sandbox_mode}")
        instructions = str(data.get("developer_instructions", ""))
        if "plugins/cells-agent-bundle-codex/skills/_shared" in instructions:
            invalid.append(f"{display(path)} points at gateway skills/_shared instead of .cache/cells-skills/_shared")
        if "plugins/cells-agent-bundle-codex/skills/" in instructions:
            invalid.append(f"{display(path)} points at gateway skills/ instead of .cache/cells-skills/")
        if "plugins/cells-agent-bundle-codex/.cache/cells-skills/" not in instructions:
            invalid.append(f"{display(path)} must route to the bundled .cache/cells-skills payload")
        if "cells-work-sizing-contract.md" not in instructions:
            invalid.append(f"{display(path)} must apply the proportional work-sizing contract")
        lowered_instructions = instructions.lower()
        forbidden_phrases = (
            "delegate-first",
            "always delegate",
            "always use subagents",
            "full workflow for every",
            "full-workflow for every",
        )
        for phrase in forbidden_phrases:
            if phrase in lowered_instructions:
                invalid.append(f"{display(path)} contains non-proportional agent instruction: {phrase}")
        if "Do not delegate." not in instructions and agent_name != "cells-orchestrator":
            invalid.append(f"{display(path)} must explicitly forbid nested delegation")
    return invalid


def validate_plugin(plugin_root: Path) -> list[str]:
    invalid: list[str] = []
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    if not manifest_path.is_file():
        return [f"Missing plugin manifest: {display(manifest_path)}"]

    plugin = read_json(manifest_path)
    for key in ("name", "version", "description", "skills", "interface"):
        if key not in plugin:
            invalid.append(f"{display(manifest_path)} missing plugin field: {key}")

    if plugin.get("name") != PLUGIN_NAME:
        invalid.append(f"{display(manifest_path)} must set name = {PLUGIN_NAME}")

    skills_path = plugin.get("skills")
    if not isinstance(skills_path, str) or not skills_path.startswith("./"):
        invalid.append(f"{display(manifest_path)} skills must be a relative ./ path")
    elif not (plugin_root / skills_path).is_dir():
        invalid.append(f"{display(manifest_path)} skills path does not exist: {skills_path}")

    interface = plugin.get("interface")
    if not isinstance(interface, dict):
        invalid.append(f"{display(manifest_path)} interface must be an object")
    else:
        required_interface = (
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
            "capabilities",
            "websiteURL",
            "privacyPolicyURL",
            "termsOfServiceURL",
            "defaultPrompt",
        )
        for key in required_interface:
            if key not in interface:
                invalid.append(f"{display(manifest_path)} interface missing field: {key}")
        default_prompt = interface.get("defaultPrompt")
        if not isinstance(default_prompt, list) or not default_prompt:
            invalid.append(f"{display(manifest_path)} interface.defaultPrompt must be a non-empty array")

    required_skill_paths = [
        plugin_root / "skills" / "cells-agent-bundle" / "SKILL.md",
        plugin_root / ".cache" / "cells-skills" / "_shared" / "cells-work-sizing-contract.md",
        plugin_root / ".cache" / "cells-skills" / "_shared" / "cells-agent-handoff-contract.md",
        plugin_root / ".cache" / "cells-skills" / "_shared" / "cells-rules-contract.md",
        plugin_root / ".cache" / "cells-skills" / "cells-apply" / "SKILL.md",
        plugin_root / ".cache" / "cells-skills" / "cells-verify" / "SKILL.md",
    ]
    for path in required_skill_paths:
        if not path.is_file():
            invalid.append(f"Missing bundled plugin skill: {display(path)}")

    gateway_path = plugin_root / "skills" / "cells-agent-bundle" / "SKILL.md"
    if gateway_path.is_file():
        gateway_text = gateway_path.read_text(encoding="utf-8")
        for token in (
            "plugins/cells-agent-bundle-codex/.cache/cells-skills/",
            "../../.cache/cells-skills/",
            "cells-cli-usage",
            "cells-work-sizing-contract.md",
            "fast-path",
            "scoped-change",
            "full-workflow",
            "cells-agent-handoff-contract.md",
        ):
            if token not in gateway_text:
                invalid.append(f"{display(gateway_path)} missing token: {token}")
    return invalid


def validate_marketplace(path: Path, repo_root: Path) -> list[str]:
    invalid: list[str] = []
    if not path.is_file():
        return [f"Missing marketplace file: {display(path)}"]
    data = read_json(path)
    if not isinstance(data.get("plugins"), list):
        return [f"{display(path)} plugins must be an array"]

    entry = None
    for plugin in data["plugins"]:
        if isinstance(plugin, dict) and plugin.get("name") == PLUGIN_NAME:
            entry = plugin
            break
    if entry is None:
        return [f"{display(path)} missing marketplace entry for {PLUGIN_NAME}"]

    source = entry.get("source")
    if not isinstance(source, dict):
        invalid.append(f"{display(path)} marketplace entry missing source object")
    else:
        if source.get("source") != "local":
            invalid.append(f"{display(path)} marketplace source must be local")
        if source.get("path") != f"./plugins/{PLUGIN_NAME}":
            invalid.append(f"{display(path)} marketplace path must be ./plugins/{PLUGIN_NAME}")
        else:
            plugin_root = repo_root / "plugins" / PLUGIN_NAME
            if not (plugin_root / ".codex-plugin" / "plugin.json").is_file():
                invalid.append(f"{display(path)} marketplace path does not resolve to a valid plugin root")

    policy = entry.get("policy")
    if not isinstance(policy, dict):
        invalid.append(f"{display(path)} marketplace entry missing policy object")
    else:
        if policy.get("installation") not in {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}:
            invalid.append(f"{display(path)} invalid policy.installation")
        if policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
            invalid.append(f"{display(path)} invalid policy.authentication")

    if "category" not in entry:
        invalid.append(f"{display(path)} marketplace entry missing category")
    return invalid


def validate_installed_project(root: Path) -> list[str]:
    invalid = validate_required_files(root, INSTALLED_REQUIRED_FILES)
    invalid.extend(validate_agents_md(root / "AGENTS.md"))
    invalid.extend(validate_config(root / ".codex" / "config.toml"))
    invalid.extend(validate_hooks(root / ".codex" / "hooks.json", root / ".codex"))
    invalid.extend(validate_rules(root / ".codex" / "rules" / "default.rules"))
    invalid.extend(validate_agent_files(root / ".codex" / "agents"))
    invalid.extend(validate_plugin(root / "plugins" / PLUGIN_NAME))
    invalid.extend(validate_marketplace(root / ".agents" / "plugins" / "marketplace.json", root))
    return invalid


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CELLS Codex assets.")
    parser.add_argument("--installed-root", type=Path, help="Project root containing AGENTS.md, .codex/, .agents/, and plugins/")
    parser.add_argument("--plugin-root", type=Path, help="Standalone plugin root to validate")
    args = parser.parse_args()

    errors: list[str] = []
    if args.installed_root:
        errors.extend(validate_installed_project(args.installed_root.resolve()))
    elif args.plugin_root:
        errors.extend(validate_plugin(args.plugin_root.resolve()))
    else:
        errors.extend(validate_source_assets())

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("Codex assets are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

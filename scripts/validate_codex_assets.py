#!/usr/bin/env python3
"""Validate source or rendered Codex assets for the Cells harness."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "codex"
PLUGIN = ROOT / "plugins" / "cells-agent-bundle-codex"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN_NAME = "cells-agent-bundle-codex"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require_files(base: Path, relatives: tuple[str, ...]) -> list[str]:
    return [f"Missing required file: {base / item}" for item in relatives if not (base / item).is_file()]


def validate_agents_md(path: Path) -> list[str]:
    if not path.is_file():
        return [f"Missing AGENTS.md: {path}"]
    text = path.read_text(encoding="utf-8-sig")
    tokens = (
        "~/.codex/skills/",
        ".cells-agent/context.json",
        "fast-path",
        "scoped-change",
        "full-workflow",
        "cells-components-catalog",
        "cells-official-docs-catalog",
    )
    return [f"{path} missing token: {token}" for token in tokens if token not in text]


def validate_config_example(path: Path) -> list[str]:
    if not path.is_file():
        return [f"Missing config example: {path}"]
    data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    errors: list[str] = []
    if data.get("agents", {}).get("max_depth") != 1:
        errors.append(f"{path} must bound agents.max_depth to 1")
    if data.get("features", {}).get("multi_agent") is not True:
        errors.append(f"{path} must show features.multi_agent = true")
    return errors


def validate_agent_files(base: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(base.glob("cells-*.toml")):
        data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
        if not all(data.get(key) for key in ("name", "description", "developer_instructions")):
            errors.append(f"{path} is missing agent metadata")
        instructions = str(data.get("developer_instructions", ""))
        if "~/.codex/skills/" not in instructions:
            errors.append(f"{path} must route to ~/.codex/skills/")
        if path.stem != "cells-orchestrator" and "Do not delegate." not in instructions:
            errors.append(f"{path} must forbid nested delegation")
        if "model" in data or "model_reasoning_effort" in data:
            errors.append(f"{path} must not pin an environment-specific model")
    return errors


def validate_plugin(plugin_root: Path, require_core: bool = False) -> list[str]:
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    if not manifest_path.is_file():
        return [f"Missing plugin manifest: {manifest_path}"]
    manifest = read_json(manifest_path)
    errors: list[str] = []
    if manifest.get("name") != PLUGIN_NAME:
        errors.append(f"{manifest_path} must use name {PLUGIN_NAME}")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", str(manifest.get("version", ""))):
        errors.append(f"{manifest_path} version must be semver")
    if manifest.get("skills") != "./skills/":
        errors.append(f"{manifest_path} skills must be ./skills/")
    interface = manifest.get("interface")
    for key in ("displayName", "shortDescription", "longDescription", "developerName", "category", "capabilities", "defaultPrompt"):
        if not isinstance(interface, dict) or not interface.get(key):
            errors.append(f"{manifest_path} missing interface.{key}")
    if not (plugin_root / "skills" / "cells-agent-bundle" / "SKILL.md").is_file():
        errors.append(f"{plugin_root} missing gateway skill")
    if require_core:
        for relative in (
            "assets/cells-skills/_shared/cells-work-sizing-contract.md",
            "assets/cells-skills/cells-apply/SKILL.md",
            "assets/cells-skills/cells-verify/SKILL.md",
            "assets/cells-skills/cells-components-catalog/SKILL.md",
        ):
            if not (plugin_root / relative).is_file():
                errors.append(f"{plugin_root} missing bundled skill: {relative}")
    return errors


def validate_marketplace(path: Path, marketplace_root: Path | None = None) -> list[str]:
    if not path.is_file():
        return [f"Missing marketplace: {path}"]
    payload = read_json(path)
    entries = payload.get("plugins", [])
    entry = next((item for item in entries if item.get("name") == PLUGIN_NAME), None)
    if not isinstance(entry, dict):
        return [f"{path} missing {PLUGIN_NAME}"]
    errors: list[str] = []
    source = entry.get("source", {})
    expected = f"./plugins/{PLUGIN_NAME}"
    if source.get("source") != "local" or source.get("path") != expected:
        errors.append(f"{path} must use local source {expected}")
    if not isinstance(entry.get("policy"), dict) or not entry.get("category"):
        errors.append(f"{path} missing plugin policy/category")
    if marketplace_root is not None and not (
        marketplace_root / "plugins" / PLUGIN_NAME / ".codex-plugin" / "plugin.json"
    ).is_file():
        errors.append(f"{path} source does not resolve to the rendered plugin")
    return errors


def validate_source() -> list[str]:
    errors = require_files(
        SOURCE,
        (
            "AGENTS.md",
            "docs/README.md",
            ".codex/config.toml",
            ".codex/hooks.json",
            ".codex/rules/default.rules",
            ".codex/agents/cells-orchestrator.toml",
            ".codex/agents/cells-analysis.toml",
            ".codex/agents/cells-implementation.toml",
            ".codex/agents/cells-verification.toml",
        ),
    )
    errors.extend(validate_agents_md(SOURCE / "AGENTS.md"))
    errors.extend(validate_config_example(SOURCE / ".codex" / "config.toml"))
    errors.extend(validate_agent_files(SOURCE / ".codex" / "agents"))
    errors.extend(validate_plugin(PLUGIN))
    errors.extend(validate_marketplace(MARKETPLACE))
    return errors


def validate_installed(root: Path) -> list[str]:
    errors = require_files(
        root,
        (
            ".codex/AGENTS.md",
            ".codex/config.cells.example.toml",
            ".codex/hooks.json",
            ".codex/rules/default.rules",
            ".codex/agents/cells-orchestrator.toml",
            ".codex/skills/_shared/cells-work-sizing-contract.md",
            ".codex/skills/cells-apply/SKILL.md",
            ".agents/plugins/marketplace.json",
        ),
    )
    errors.extend(validate_agents_md(root / ".codex" / "AGENTS.md"))
    errors.extend(validate_config_example(root / ".codex" / "config.cells.example.toml"))
    errors.extend(validate_agent_files(root / ".codex" / "agents"))
    plugin_root = root / ".agents" / "plugins" / "plugins" / PLUGIN_NAME
    errors.extend(validate_plugin(plugin_root, require_core=True))
    errors.extend(validate_marketplace(root / ".agents" / "plugins" / "marketplace.json", root / ".agents" / "plugins"))
    if (root / ".codex" / "config.toml").exists():
        errors.append("Rendered Codex package must not include an active config.toml")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--installed-root", type=Path)
    parser.add_argument("--plugin-root", type=Path)
    args = parser.parse_args()
    if args.installed_root:
        errors = validate_installed(args.installed_root.resolve())
    elif args.plugin_root:
        errors = validate_plugin(args.plugin_root.resolve(), require_core=True)
    else:
        errors = validate_source()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Codex assets are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

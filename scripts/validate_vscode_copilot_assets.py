#!/usr/bin/env python3
"""Validate VS Code Copilot customization assets for layered CELLS guidance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shlex
import sys


ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = ROOT / "examples/vscode"

ALLOWED_TOOLS = {
    "agent",
    "editFiles",
    "read/problems",
    "runTerminalCommand",
    "search/codebase",
    "search/usages",
    "web/fetch",
}

SOURCE_REQUIRED_FILES = [
    "copilot-instructions.md",
    "instructions/cells-orchestrator.instructions.md",
    "docs/README.md",
    "docs/hooks.md",
    "docs/models.md",
    "docs/opencode-vscode-equivalence.md",
    "prompts/README.md",
    "prompts/cells-explore.prompt.md",
    "prompts/cells-propose.prompt.md",
    "prompts/cells-spec.prompt.md",
    "prompts/cells-design.prompt.md",
    "prompts/cells-tasks.prompt.md",
    "prompts/cells-apply.prompt.md",
    "prompts/cells-verify.prompt.md",
    "prompts/cells-archive.prompt.md",
    "prompts/cells-fallback.prompt.md",
    "agents/cells-orchestrator.agent.md",
    "agents/cells-analysis.agent.md",
    "agents/cells-implementation.agent.md",
    "agents/cells-verification.agent.md",
    "hooks/cells-policy.json",
    "scripts/cells-session-context.js",
    "scripts/cells-pretool-policy.js",
    "scripts/cells-stop-reminder.js",
    "plugin/plugin.json",
]

INSTALLED_REQUIRED_FILES = [
    "copilot-instructions.md",
    "instructions/cells-orchestrator.instructions.md",
    "prompts/cells-explore.prompt.md",
    "prompts/cells-propose.prompt.md",
    "prompts/cells-spec.prompt.md",
    "prompts/cells-design.prompt.md",
    "prompts/cells-tasks.prompt.md",
    "prompts/cells-apply.prompt.md",
    "prompts/cells-verify.prompt.md",
    "prompts/cells-archive.prompt.md",
    "prompts/cells-fallback.prompt.md",
    "agents/cells-orchestrator.agent.md",
    "agents/cells-analysis.agent.md",
    "agents/cells-implementation.agent.md",
    "agents/cells-verification.agent.md",
    "hooks/cells-policy.json",
    "hooks/scripts/cells-session-context.js",
    "hooks/scripts/cells-pretool-policy.js",
    "hooks/scripts/cells-stop-reminder.js",
    "plugin/plugin.json",
    "skills/_shared/cells-governance-contract.md",
    "skills/_shared/cells-policy-matrix.yaml",
    "skills/_shared/persistence-contract.md",
    "skills/cells-apply/SKILL.md",
    "skills/cells-cli-usage/SKILL.md",
    "skills/cells-coverage/SKILL.md",
    "skills/cells-i18n/SKILL.md",
    "skills/cells-test-creator/SKILL.md",
    "skills/cells-verify/SKILL.md",
]

REQUIRED_STRINGS = {
    "instructions/cells-orchestrator.instructions.md": [
        "### Layered Precedence (Deterministic)",
        "`status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`",
        "fallback is used, record source decision trace",
    ],
    "prompts/cells-fallback.prompt.md": [
        "WARNING: Dedicated prompt for this CELLS phase is missing",
        "`status`",
        "`next_recommended`",
    ],
}


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _contains_in_order(content: str, tokens: list[str]) -> bool:
    index = -1
    for token in tokens:
        next_index = content.find(token, index + 1)
        if next_index == -1:
            return False
        index = next_index
    return True


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}

    data: dict[str, str] = {}
    current_key = ""
    for raw_line in text[4:end].splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            data[current_key] = value.strip()
        elif current_key:
            data[current_key] = f"{data[current_key]}\n{line}"
    return data


def parse_inline_list(value: str) -> list[str]:
    value = value.strip()
    if not value:
        return []
    if value.startswith("["):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except json.JSONDecodeError:
            pass
    quoted = re.findall(r'"([^"]+)"|\'([^\']+)\'', value)
    if quoted:
        return [left or right for left, right in quoted]
    return [item.strip() for item in value.split(",") if item.strip()]


def validate_required_files(base: Path, required: list[str]) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    invalid: list[str] = []
    for relative in required:
        path = base / relative
        if not path.is_file():
            missing.append(display(path))
    for ds_store in base.rglob(".DS_Store"):
        invalid.append(f"{display(ds_store)} is accidental macOS metadata and must not be committed")
    return missing, invalid


def validate_required_strings(base: Path) -> list[str]:
    invalid: list[str] = []
    for relative, expected_tokens in REQUIRED_STRINGS.items():
        path = base / relative
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        for token in expected_tokens:
            if token not in content:
                invalid.append(f"{display(path)} missing token: {token}")
    return invalid


def validate_behavioral_policies() -> list[str]:
    invalid: list[str] = []

    instructions_path = SOURCE_ROOT / "instructions/cells-orchestrator.instructions.md"
    governance_path = ROOT / "skills/_shared/cells-governance-contract.md"
    persistence_path = ROOT / "skills/_shared/persistence-contract.md"
    verify_skill_path = ROOT / "skills/cells-verify/SKILL.md"

    if instructions_path.is_file():
        instructions = instructions_path.read_text(encoding="utf-8")
        if not _contains_in_order(
            instructions,
            [
                "Apply intent routing before choosing Cells skills:",
                "UI/component discovery and element selection",
                "Cells documentation or knowledge lookup",
                "fallback to the other catalog only when the first one is insufficient",
            ],
        ):
            invalid.append(
                f"{display(instructions_path)} missing deterministic catalog-first/fallback order"
            )

    if governance_path.is_file():
        governance = governance_path.read_text(encoding="utf-8")
        if "MUST NOT skip intermediate sources" not in governance:
            invalid.append(f"{display(governance_path)} missing no-skip fallback policy")
        if (
            "- `blocked`: required evidence unavailable and progress cannot safely continue"
            not in governance
        ):
            invalid.append(f"{display(governance_path)} missing blocked escalation definition")
        if (
            "- `partial`: work progressed but at least one evidence minimum unmet"
            not in governance
        ):
            invalid.append(f"{display(governance_path)} missing partial escalation definition")

    if persistence_path.is_file():
        persistence = persistence_path.read_text(encoding="utf-8")
        if (
            "- Use `blocked` when required evidence is unavailable and safe continuation is not possible."
            not in persistence
        ):
            invalid.append(f"{display(persistence_path)} missing blocked escalation enforcement")
        if (
            "- Use `partial` when implementation can progress but one or more evidence minimums remain unmet."
            not in persistence
        ):
            invalid.append(f"{display(persistence_path)} missing partial escalation enforcement")

    if verify_skill_path.is_file():
        verify_skill = verify_skill_path.read_text(encoding="utf-8")
        coverage_tokens = (
            "record `Coverage policy exemption: N/A`",
            "with deterministic evidence",
            "`N/A (policy exemption)`",
        )
        for token in coverage_tokens:
            if token not in verify_skill:
                invalid.append(f"{display(verify_skill_path)} missing coverage exemption token: {token}")

    return invalid


def validate_legacy_markdown(base: Path) -> list[str]:
    invalid: list[str] = []
    patterns = {
        "prompts": ".prompt.md",
        "agents": ".agent.md",
        "instructions": ".instructions.md",
    }
    for directory, suffix in patterns.items():
        target = base / directory
        if not target.is_dir():
            continue
        for path in sorted(target.glob("*.md")):
            if path.name == "README.md":
                continue
            if not path.name.endswith(suffix):
                invalid.append(f"{display(path)} should use {suffix}")
    return invalid


def validate_vscode_format(base: Path) -> list[str]:
    invalid: list[str] = []
    invalid.extend(validate_legacy_markdown(base))

    agent_files = sorted((base / "agents").glob("*.agent.md"))
    agent_names = {path.name.removesuffix(".agent.md") for path in agent_files}

    for path in sorted((base / "prompts").glob("*.prompt.md")):
        frontmatter = parse_frontmatter(path)
        for token in ("name", "description", "agent", "tools"):
            if token not in frontmatter:
                invalid.append(f"{display(path)} missing VS Code frontmatter token: {token}:")

        name = frontmatter.get("name")
        expected_name = path.name.removesuffix(".prompt.md")
        if name and name != expected_name:
            invalid.append(f"{display(path)} name {name!r} does not match filename {expected_name!r}")

        agent = frontmatter.get("agent")
        if agent and agent not in agent_names:
            invalid.append(f"{display(path)} references missing agent: {agent}")

        invalid.extend(validate_tools(path, frontmatter))

    for path in agent_files:
        frontmatter = parse_frontmatter(path)
        for token in ("name", "description", "tools"):
            if token not in frontmatter:
                invalid.append(f"{display(path)} missing VS Code frontmatter token: {token}:")

        name = frontmatter.get("name")
        expected_name = path.name.removesuffix(".agent.md")
        if name and name != expected_name:
            invalid.append(f"{display(path)} name {name!r} does not match filename {expected_name!r}")

        for agent in parse_inline_list(frontmatter.get("agents", "")):
            if agent not in agent_names:
                invalid.append(f"{display(path)} references missing delegated agent: {agent}")

        text = path.read_text(encoding="utf-8")
        for handoff_agent in re.findall(r"^\s+agent:\s*([a-z0-9-]+)\s*$", text, re.M):
            if handoff_agent not in agent_names:
                invalid.append(f"{display(path)} handoff references missing agent: {handoff_agent}")

        invalid.extend(validate_tools(path, frontmatter))

    for path in sorted((base / "instructions").glob("*.instructions.md")):
        frontmatter = parse_frontmatter(path)
        if "applyTo" not in frontmatter:
            invalid.append(f"{display(path)} missing VS Code frontmatter token: applyTo:")

    return invalid


def validate_tools(path: Path, frontmatter: dict[str, str]) -> list[str]:
    invalid: list[str] = []
    content = path.read_text(encoding="utf-8")
    if "runCommands" in content:
        invalid.append(f"{display(path)} uses runCommands; use VS Code tool name runTerminalCommand")
    for tool in parse_inline_list(frontmatter.get("tools", "")):
        if tool not in ALLOWED_TOOLS:
            invalid.append(f"{display(path)} uses unknown VS Code tool name: {tool}")
    return invalid


def node_command_script(command: str) -> str | None:
    try:
        parts = shlex.split(command)
    except ValueError:
        return None
    if len(parts) < 2:
        return None
    executable = Path(parts[0]).name
    if executable not in {"node", "node.exe"}:
        return None
    return parts[1]


def resolve_hook_script(
    script: str,
    *,
    asset_root: Path,
    workspace_root: Path | None,
    source_scripts_root: Path | None,
) -> Path | None:
    script_path = Path(script)
    if script_path.is_absolute():
        return script_path if script_path.is_file() else None

    candidates: list[Path] = []
    if workspace_root is not None:
        candidates.append(workspace_root / script)
    candidates.append(asset_root / script)

    if source_scripts_root is not None and script.startswith(".github/hooks/scripts/"):
        candidates.append(source_scripts_root / Path(script).name)
    if source_scripts_root is not None and script.startswith(".github/plugin/hooks/scripts/"):
        candidates.append(source_scripts_root / Path(script).name)

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def validate_hooks(
    hook_file: Path,
    *,
    asset_root: Path,
    workspace_root: Path | None,
    source_scripts_root: Path | None = None,
) -> list[str]:
    invalid: list[str] = []
    if not hook_file.is_file():
        return invalid

    try:
        data = json.loads(hook_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{display(hook_file)} is not valid JSON: {exc}"]

    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return [f"{display(hook_file)} missing hooks object"]

    for event_name, entries in hooks.items():
        if event_name not in {"SessionStart", "PreToolUse", "Stop"}:
            invalid.append(f"{display(hook_file)} uses unsupported hook event: {event_name}")
        if not isinstance(entries, list):
            invalid.append(f"{display(hook_file)} hook {event_name} must be a list")
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                invalid.append(f"{display(hook_file)} hook {event_name}[{index}] must be an object")
                continue
            command = entry.get("command")
            if not isinstance(command, str) or not command.strip():
                invalid.append(f"{display(hook_file)} hook {event_name}[{index}] missing command")
                continue
            script = node_command_script(command)
            if script is None:
                invalid.append(f"{display(hook_file)} hook {event_name}[{index}] must run a node script")
                continue
            if resolve_hook_script(
                script,
                asset_root=asset_root,
                workspace_root=workspace_root,
                source_scripts_root=source_scripts_root,
            ) is None:
                invalid.append(f"{display(hook_file)} hook script path does not exist: {script}")
    return invalid


def validate_skill_names(skills_root: Path) -> list[str]:
    invalid: list[str] = []
    skill_name_pattern = re.compile(r"^[a-z0-9-]{1,64}$")
    if not skills_root.is_dir():
        invalid.append(f"{display(skills_root)} skills directory does not exist")
        return invalid

    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8-sig")
        match = re.search(r"^name:\s*([A-Za-z0-9-]+)\s*$", text, re.M)
        if not match:
            invalid.append(f"{display(skill_file)} missing skill name")
            continue
        name = match.group(1)
        directory = skill_file.parent.name
        if name != directory:
            invalid.append(f"{display(skill_file)} name {name!r} does not match directory {directory!r}")
        if not skill_name_pattern.match(name):
            invalid.append(f"{display(skill_file)} name {name!r} is not VS Code skill kebab-case")

    return invalid


def validate_plugin_manifest(
    plugin_root: Path,
    workspace_root: Path | None = None,
    *,
    require_paths: bool = True,
) -> list[str]:
    invalid: list[str] = []
    plugin_path = plugin_root / "plugin.json"
    if not plugin_path.is_file():
        return [f"{display(plugin_path)} plugin manifest does not exist"]

    try:
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{display(plugin_path)} is not valid JSON: {exc}"]

    for token in ("name", "description", "version", "skills", "agents", "hooks"):
        if token not in plugin:
            invalid.append(f"{display(plugin_path)} missing plugin field: {token}")

    for key in ("skills", "agents"):
        values = plugin.get(key, [])
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, list):
            invalid.append(f"{display(plugin_path)} {key} must be a string or list")
            continue
        for value in values:
            if str(value).startswith("../"):
                invalid.append(f"{display(plugin_path)} {key} path must be plugin-internal, got: {value}")
            target = (plugin_root / str(value)).resolve()
            if require_paths and not target.exists():
                invalid.append(f"{display(plugin_path)} {key} path does not exist: {value}")

    hooks = plugin.get("hooks")
    if isinstance(hooks, str):
        if hooks.startswith("../"):
            invalid.append(f"{display(plugin_path)} hooks path must be plugin-internal, got: {hooks}")
        hooks_path = (plugin_root / hooks).resolve()
        if require_paths and not hooks_path.is_file():
            invalid.append(f"{display(plugin_path)} hooks path does not exist: {hooks}")
        elif hooks_path.is_file():
            invalid.extend(
                validate_hooks(
                    hooks_path,
                    asset_root=plugin_root,
                    workspace_root=workspace_root,
                    source_scripts_root=plugin_root / "hooks/scripts",
                )
            )
    else:
        invalid.append(f"{display(plugin_path)} hooks must be a string path")

    skills_path = plugin.get("skills")
    if require_paths and isinstance(skills_path, str) and (plugin_root / skills_path).is_dir():
        invalid.extend(validate_skill_names(plugin_root / skills_path))

    agents_path = plugin.get("agents")
    if require_paths and isinstance(agents_path, str) and (plugin_root / agents_path).is_dir():
        invalid.extend(validate_vscode_format(plugin_root))

    return invalid


def validate_source_assets() -> tuple[list[str], list[str]]:
    missing, invalid = validate_required_files(SOURCE_ROOT, SOURCE_REQUIRED_FILES)
    invalid.extend(validate_required_strings(SOURCE_ROOT))
    invalid.extend(validate_behavioral_policies())
    invalid.extend(validate_vscode_format(SOURCE_ROOT))
    invalid.extend(
        validate_hooks(
            SOURCE_ROOT / "hooks/cells-policy.json",
            asset_root=SOURCE_ROOT,
            workspace_root=ROOT,
            source_scripts_root=SOURCE_ROOT / "scripts",
        )
    )
    invalid.extend(validate_plugin_manifest(SOURCE_ROOT / "plugin", workspace_root=ROOT, require_paths=False))
    invalid.extend(validate_skill_names(ROOT / "skills"))
    return missing, invalid


def validate_installed_assets(installed_root: Path) -> tuple[list[str], list[str]]:
    installed_root = installed_root.resolve()
    missing, invalid = validate_required_files(installed_root, INSTALLED_REQUIRED_FILES)
    invalid.extend(validate_required_strings(installed_root))
    invalid.extend(validate_vscode_format(installed_root))
    invalid.extend(
        validate_hooks(
            installed_root / "hooks/cells-policy.json",
            asset_root=installed_root,
            workspace_root=installed_root.parent,
        )
    )
    invalid.extend(validate_plugin_manifest(installed_root / "plugin", workspace_root=installed_root.parent))
    invalid.extend(validate_skill_names(installed_root / "skills"))
    return missing, invalid


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate VS Code Copilot source assets, installed .github assets, or a distributable plugin package."
    )
    parser.add_argument(
        "--installed-root",
        type=Path,
        help="Path to an installed .github directory to validate.",
    )
    parser.add_argument(
        "--plugin-root",
        type=Path,
        help="Path to a VS Code Copilot plugin package root containing plugin.json.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    missing: list[str] = []
    invalid: list[str] = []

    if args.installed_root:
        if not args.installed_root.is_dir():
            missing.append(display(args.installed_root))
        else:
            installed_missing, installed_invalid = validate_installed_assets(args.installed_root)
            missing.extend(installed_missing)
            invalid.extend(installed_invalid)
    elif args.plugin_root:
        if not args.plugin_root.is_dir():
            missing.append(display(args.plugin_root))
        else:
            invalid.extend(validate_plugin_manifest(args.plugin_root, workspace_root=args.plugin_root.parent))
    else:
        source_missing, source_invalid = validate_source_assets()
        missing.extend(source_missing)
        invalid.extend(source_invalid)

    if missing or invalid:
        if missing:
            print("Missing required VS Code assets:")
            for item in missing:
                print(f"- {item}")
        if invalid:
            print("Invalid VS Code assets:")
            for item in invalid:
                print(f"- {item}")
        return 1

    print("VS Code Copilot assets validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

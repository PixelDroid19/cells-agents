#!/usr/bin/env python3
"""Validate VS Code Copilot customization assets for layered CELLS guidance."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "examples/vscode/instructions/copilot-instructions.md",
    "examples/vscode/docs/README.md",
    "examples/vscode/docs/hooks.md",
    "examples/vscode/docs/models.md",
    "examples/vscode/prompts/README.md",
    "examples/vscode/prompts/cells-explore.md",
    "examples/vscode/prompts/cells-propose.md",
    "examples/vscode/prompts/cells-spec.md",
    "examples/vscode/prompts/cells-design.md",
    "examples/vscode/prompts/cells-tasks.md",
    "examples/vscode/prompts/cells-apply.md",
    "examples/vscode/prompts/cells-verify.md",
    "examples/vscode/prompts/cells-archive.md",
    "examples/vscode/prompts/cells-fallback.md",
    "examples/vscode/agents/analysis-agent.md",
    "examples/vscode/agents/implementation-agent.md",
    "examples/vscode/agents/verification-agent.md",
    "skills/_shared/cells-governance-contract.md",
    "skills/_shared/cells-policy-matrix.yaml",
]

REQUIRED_STRINGS = {
    "examples/vscode/instructions/copilot-instructions.md": [
        "### Layered Precedence (Deterministic)",
        "`status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`",
        "fallback is used, record source decision trace",
    ],
    "examples/vscode/prompts/cells-fallback.md": [
        "WARNING: Dedicated prompt for this CELLS phase is missing",
        "`status`",
        "`next_recommended`",
    ],
}


def _contains_in_order(content: str, tokens: list[str]) -> bool:
    index = -1
    for token in tokens:
        next_index = content.find(token, index + 1)
        if next_index == -1:
            return False
        index = next_index
    return True


def validate_behavioral_policies() -> list[str]:
    invalid: list[str] = []

    instructions_path = ROOT / "examples/vscode/instructions/copilot-instructions.md"
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
                "examples/vscode/instructions/copilot-instructions.md missing deterministic catalog-first/fallback order"
            )

    if governance_path.is_file():
        governance = governance_path.read_text(encoding="utf-8")
        if "MUST NOT skip intermediate sources" not in governance:
            invalid.append(
                "skills/_shared/cells-governance-contract.md missing no-skip fallback policy"
            )
        if (
            "- `blocked`: required evidence unavailable and progress cannot safely continue"
            not in governance
        ):
            invalid.append(
                "skills/_shared/cells-governance-contract.md missing blocked escalation definition"
            )
        if (
            "- `partial`: work progressed but at least one evidence minimum unmet"
            not in governance
        ):
            invalid.append(
                "skills/_shared/cells-governance-contract.md missing partial escalation definition"
            )

    if persistence_path.is_file():
        persistence = persistence_path.read_text(encoding="utf-8")
        if (
            "- Use `blocked` when required evidence is unavailable and safe continuation is not possible."
            not in persistence
        ):
            invalid.append(
                "skills/_shared/persistence-contract.md missing blocked escalation enforcement"
            )
        if (
            "- Use `partial` when implementation can progress but one or more evidence minimums remain unmet."
            not in persistence
        ):
            invalid.append(
                "skills/_shared/persistence-contract.md missing partial escalation enforcement"
            )

    if verify_skill_path.is_file():
        verify_skill = verify_skill_path.read_text(encoding="utf-8")
        coverage_tokens = (
            "record `Coverage policy exemption: N/A`",
            "with deterministic evidence",
            "`N/A (policy exemption)`",
        )
        for token in coverage_tokens:
            if token not in verify_skill:
                invalid.append(
                    f"skills/cells-verify/SKILL.md missing coverage exemption token: {token}"
                )

    return invalid


def main() -> int:
    missing: list[str] = []
    invalid: list[str] = []

    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.is_file():
            missing.append(relative)

    for relative, expected_tokens in REQUIRED_STRINGS.items():
        path = ROOT / relative
        if not path.is_file():
            continue

        content = path.read_text(encoding="utf-8")
        for token in expected_tokens:
            if token not in content:
                invalid.append(f"{relative} missing token: {token}")

    invalid.extend(validate_behavioral_policies())

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

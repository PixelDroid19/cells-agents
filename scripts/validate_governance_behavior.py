#!/usr/bin/env python3
"""Validate behavioral governance scenarios for Cells SDD assets."""

from __future__ import annotations

from pathlib import Path
import argparse
import sys


ROOT = Path(__file__).resolve().parent.parent

INSTRUCTIONS = ROOT / ".github/instructions/copilot-instructions.md"
GOVERNANCE = ROOT / "skills/_shared/cells-governance-contract.md"
PERSISTENCE = ROOT / "skills/_shared/persistence-contract.md"
VERIFY_SKILL = ROOT / "skills/cells-verify/SKILL.md"


def _read(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(str(path.relative_to(ROOT)))
    return path.read_text(encoding="utf-8")


def _contains_in_order(content: str, tokens: list[str]) -> bool:
    index = -1
    for token in tokens:
        next_index = content.find(token, index + 1)
        if next_index == -1:
            return False
        index = next_index
    return True


def scenario_catalog_first_available() -> tuple[bool, str]:
    content = _read(INSTRUCTIONS)
    ordered = _contains_in_order(
        content,
        [
            "Apply intent routing before choosing Cells skills:",
            "UI/component discovery and element selection",
            "Cells documentation or knowledge lookup",
        ],
    )
    trace_required = "record source decision trace" in content
    if ordered and trace_required:
        return True, "Catalog-first route and trace requirement found."
    return (
        False,
        "Missing deterministic catalog-first order or source trace requirement.",
    )


def scenario_primary_catalog_unavailable() -> tuple[bool, str]:
    content = _read(INSTRUCTIONS)
    fallback_rule = (
        "fallback to the other catalog only when the first one is insufficient"
        in content
    )
    fallback_reason = "fallback_reason" in content
    if fallback_rule and fallback_reason:
        return True, "Fallback condition and reason trace are enforced."
    return False, "Fallback condition/reason trace is missing."


def scenario_fallback_order_respected() -> tuple[bool, str]:
    content = _read(GOVERNANCE)
    no_skip = "MUST NOT skip intermediate sources" in content
    test_stack = (
        "`cells-cli-usage` -> `cells-coverage` -> `cells-test-creator`" in content
    )
    if no_skip and test_stack:
        return True, "Fallback no-skip rule and deterministic test stack are present."
    return False, "Deterministic fallback order is incomplete."


def scenario_escalation_blocked_partial() -> tuple[bool, str]:
    governance = _read(GOVERNANCE)
    persistence = _read(PERSISTENCE)
    governance_status = all(
        token in governance
        for token in (
            "- `partial`: work progressed but at least one evidence minimum unmet",
            "- `blocked`: required evidence unavailable and progress cannot safely continue",
        )
    )
    persistence_status = all(
        token in persistence
        for token in (
            "- Use `blocked` when required evidence is unavailable and safe continuation is not possible.",
            "- Use `partial` when implementation can progress but one or more evidence minimums remain unmet.",
        )
    )
    if governance_status and persistence_status:
        return True, "Escalation status behavior is consistent across shared contracts."
    return (
        False,
        "Blocked/partial escalation behavior is not fully defined across contracts.",
    )


def scenario_coverage_policy_exemption() -> tuple[bool, str]:
    content = _read(VERIFY_SKILL)
    required = (
        "record `Coverage policy exemption: N/A`",
        "with deterministic evidence",
        "`N/A (policy exemption)`",
    )
    if all(token in content for token in required):
        return True, "Coverage exemption policy is explicit and deterministic."
    return (
        False,
        "Coverage exemption policy requirements are missing from verify skill.",
    )


SCENARIOS = {
    "catalog-first-available": scenario_catalog_first_available,
    "primary-catalog-unavailable": scenario_primary_catalog_unavailable,
    "fallback-order-respected": scenario_fallback_order_respected,
    "escalation-blocked-partial": scenario_escalation_blocked_partial,
    "coverage-policy-exemption": scenario_coverage_policy_exemption,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate governance behavior scenarios"
    )
    parser.add_argument(
        "--scenario",
        choices=["all", *SCENARIOS.keys()],
        default="all",
        help="Scenario to validate",
    )
    args = parser.parse_args()

    failures: list[str] = []
    selected = (
        SCENARIOS.items()
        if args.scenario == "all"
        else [(args.scenario, SCENARIOS[args.scenario])]
    )

    for name, check in selected:
        try:
            ok, message = check()
        except FileNotFoundError as exc:
            failures.append(f"{name}: missing file {exc}")
            continue
        if ok:
            print(f"OK   {name}: {message}")
        else:
            failures.append(f"{name}: {message}")

    if failures:
        print("Governance behavior validation failed:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("Governance behavior validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

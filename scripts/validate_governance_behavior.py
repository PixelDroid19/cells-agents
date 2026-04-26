#!/usr/bin/env python3
"""Validate behavioral governance scenarios for CELLS assets."""

from __future__ import annotations

from pathlib import Path
import argparse
import sys


ROOT = Path(__file__).resolve().parent.parent

INSTRUCTIONS = ROOT / "examples/vscode/instructions/cells-orchestrator.instructions.md"
GOVERNANCE = ROOT / "skills/_shared/cells-governance-contract.md"
PERSISTENCE = ROOT / "skills/_shared/persistence-contract.md"
VERIFY_SKILL = ROOT / "skills/cells-verify/SKILL.md"
RULES = ROOT / "skills/_shared/cells-rules-contract.md"
APPLY_SKILL = ROOT / "skills/cells-apply/SKILL.md"


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


def scenario_workflow_contract_parity() -> tuple[bool, str]:
    workflow = _read(ROOT / "skills/_shared/cells-workflow-contract.md")
    persistence = _read(PERSISTENCE)
    policy = _read(ROOT / "skills/_shared/cells-policy-matrix.yaml")
    required = (
        "delegate-first",
        "Compatibility reads",
        "SKILL: Load",
        "REQ-DELEGATE-FIRST",
    )
    if all(token in f"{workflow}\n{persistence}\n{policy}" for token in required):
        return True, "Workflow contract parity tokens are aligned across shared assets."
    return False, "Workflow contract parity tokens are missing across shared assets."


def scenario_canonical_write_contract() -> tuple[bool, str]:
    workflow = _read(ROOT / "skills/_shared/cells-workflow-contract.md")
    engram = _read(ROOT / "skills/_shared/engram-convention.md")
    required = (
        "cells/{change}/{artifact}",
        "MUST use only `cells-init/{project}` and `cells/{change}/{artifact}` for writes",
        "MUST NOT replace canonical `cells/...` writes",
    )
    if all(token in f"{workflow}\n{engram}" for token in required):
        return True, "Canonical write contract remains explicit."
    return False, "Canonical write contract is missing or weakened."


def scenario_canonical_lineage_only() -> tuple[bool, str]:
    workflow = _read(ROOT / "skills/_shared/cells-workflow-contract.md")
    if (
        "Compatibility reads MUST NOT replace canonical `cells/...` writes" in workflow
        and "`/cells-*` commands remain canonical" in workflow
    ):
        return (
            True,
            "Canonical lineage remains authoritative with compatibility-only legacy reads.",
        )
    return False, "Canonical lineage guidance is incomplete."


def scenario_source_decision_template() -> tuple[bool, str]:
    workflow = _read(ROOT / "skills/_shared/cells-workflow-contract.md")
    apply_skill = _read(ROOT / "skills/cells-apply/SKILL.md")
    required = (
        "intent",
        "primary_source",
        "fallback_used",
        "fallback_source",
        "fallback_reason",
        "evidence_quality",
        "status",
    )
    if all(token in workflow and token in apply_skill for token in required):
        return (
            True,
            "Source decision template coverage is present in workflow and apply guidance.",
        )
    return False, "Source decision template coverage is incomplete."


def scenario_reliability_guardrails() -> tuple[bool, str]:
    governance = _read(GOVERNANCE)
    conventions = _read(ROOT / "skills/_shared/cells-conventions.md")
    required = (
        "do not claim a file/path exists without direct repository evidence",
        "Never invent file paths, APIs, events, or command names.",
        "Verify file paths before citing or editing them.",
    )
    if all(token in f"{governance}\n{conventions}" for token in required):
        return True, "Reliability guardrails (anti-hallucination + path checks) are present."
    return False, "Reliability guardrails are incomplete."


def scenario_i18n_routing_enforced() -> tuple[bool, str]:
    source_routing = _read(ROOT / "skills/_shared/cells-source-routing-contract.md")
    verify_cmd = _read(ROOT / "examples/opencode/commands/cells-verify.md")
    required = (
        "i18n translation/runtime/locales",
        "skills/cells-i18n/",
        "Do not claim translation/i18n correctness without consulting `skills/cells-i18n/`",
    )
    if all(token in f"{source_routing}\n{verify_cmd}" for token in required):
        return True, "i18n routing and verification guardrails are enforced."
    return False, "i18n routing and verification guardrails are missing."


def scenario_real_cells_rules_enforced() -> tuple[bool, str]:
    rules = _read(RULES)
    required = (
        "BBVA-First Rule",
        "scopedElements",
        "WidgetMixin",
        "this.emitEvent(...)",
        "this.t(...)",
        "demo/locales/locales.json",
        "SCSS",
        "browser validation",
    )
    if all(token in rules for token in required):
        return True, "Real Cells implementation rules are enforced in cells-rules-contract."
    return False, "Real Cells implementation rules are incomplete."


def scenario_code_hygiene_enforced() -> tuple[bool, str]:
    conventions = _read(ROOT / "skills/_shared/cells-conventions.md")
    apply_skill = _read(APPLY_SKILL)
    required = (
        "Use JSDoc for public API",
        "do not leave TODO comments",
        "Avoid unnecessary whitespace-only edits",
        "separation of responsibilities",
    )
    if all(token in f"{conventions}\n{apply_skill}" for token in required):
        return True, "Code hygiene and responsibility-separation rules are enforced."
    return False, "Code hygiene and responsibility-separation rules are missing."


def scenario_task_scope_isolation_enforced() -> tuple[bool, str]:
    governance = _read(GOVERNANCE)
    apply_skill = _read(APPLY_SKILL)
    verify_skill = _read(VERIFY_SKILL)
    required = (
        "Task Scope Isolation (Mandatory)",
        "do not perform opportunistic refactors, adjacent cleanups, unrelated bug fixes, or cross-module rewrites unless the user explicitly expands scope",
        "Do not fix unrelated modules, unrelated errors, or opportunistic cleanup outside the assigned task unless the user explicitly expands scope",
        "Verify the implementation did not fix unrelated modules, unrelated errors, or opportunistic cleanup outside the requested task unless explicit scope expansion was requested",
    )
    if all(token in f"{governance}\n{apply_skill}\n{verify_skill}" for token in required):
        return True, "Task-scope isolation is enforced across governance/apply/verify."
    return False, "Task-scope isolation guidance is missing or incomplete."


SCENARIOS.update(
    {
        "workflow-contract-parity": scenario_workflow_contract_parity,
        "canonical-write-contract": scenario_canonical_write_contract,
        "canonical-lineage-only": scenario_canonical_lineage_only,
        "source-decision-template": scenario_source_decision_template,
        "reliability-guardrails": scenario_reliability_guardrails,
        "i18n-routing-enforced": scenario_i18n_routing_enforced,
        "real-cells-rules-enforced": scenario_real_cells_rules_enforced,
        "code-hygiene-enforced": scenario_code_hygiene_enforced,
        "task-scope-isolation-enforced": scenario_task_scope_isolation_enforced,
    }
)


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

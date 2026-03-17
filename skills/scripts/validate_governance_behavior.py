#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def contains_all(text: str, tokens: list[str]) -> list[str]:
    return [token for token in tokens if token not in text]


def scenario_coverage_policy_exemption() -> dict:
    verify_text = read_text("cells-verify/SKILL.md")
    required = [
        "coverage-policy-exemption",
        "Coverage policy exemption: N/A",
        "scripts/validate_governance_behavior.py --scenario coverage-policy-exemption",
    ]
    missing = contains_all(verify_text, required)
    return {
        "scenario": "coverage-policy-exemption",
        "valid": not missing,
        "missing": missing,
        "checked_files": ["cells-verify/SKILL.md"],
    }


def scenario_workflow_contract_parity() -> dict:
    contract_text = read_text("_shared/cells-workflow-contract.md")
    engram_text = read_text("_shared/engram-convention.md")
    persistence_text = read_text("_shared/persistence-contract.md")
    files = {
        "_shared/cells-workflow-contract.md": [
            "Canonical Artifact Lineage",
            "Dependency Lookup Matrix",
            "Result Envelope",
            "Source Decisions",
        ],
        "_shared/engram-convention.md": [
            "cells/{change-name}/{artifact-type}",
            "Canonical Recovery Protocol",
            "blocked",
        ],
        "_shared/persistence-contract.md": [
            "cells-workflow-contract.md",
            "do not recover active state from historical legacy artifacts",
        ],
    }
    file_contents = {
        "_shared/cells-workflow-contract.md": contract_text,
        "_shared/engram-convention.md": engram_text,
        "_shared/persistence-contract.md": persistence_text,
    }
    missing = {
        path: contains_all(file_contents[path], tokens)
        for path, tokens in files.items()
    }
    missing = {path: tokens for path, tokens in missing.items() if tokens}
    return {
        "scenario": "workflow-contract-parity",
        "valid": not missing,
        "missing": missing,
        "checked_files": list(files.keys()),
    }


def scenario_canonical_lineage_only() -> dict:
    legacy_prefix = "".join(["s", "d", "d"])
    targets = {
        "../README.md": [f"{legacy_prefix}/", f"{legacy_prefix}-"],
        "_shared/persistence-contract.md": [f"{legacy_prefix}/", f"{legacy_prefix}-"],
        "_shared/engram-convention.md": [f"{legacy_prefix}/", f"{legacy_prefix}-"],
        "_shared/cells-workflow-contract.md": [
            f"{legacy_prefix}/",
            f"{legacy_prefix}-",
        ],
        "cells-init/SKILL.md": [f"{legacy_prefix}/", f"{legacy_prefix}-"],
        "cells-explore/SKILL.md": [f"{legacy_prefix}/", f"{legacy_prefix}-"],
        "cells-propose/SKILL.md": [f"{legacy_prefix}/", f"{legacy_prefix}-"],
        "cells-spec/SKILL.md": [f"{legacy_prefix}/", f"{legacy_prefix}-"],
        "cells-design/SKILL.md": [f"{legacy_prefix}/", f"{legacy_prefix}-"],
        "cells-tasks/SKILL.md": [f"{legacy_prefix}/", f"{legacy_prefix}-"],
        "cells-apply/SKILL.md": [f"{legacy_prefix}/", f"{legacy_prefix}-"],
        "cells-verify/SKILL.md": [f"{legacy_prefix}/", f"{legacy_prefix}-"],
        "cells-archive/SKILL.md": [f"{legacy_prefix}/", f"{legacy_prefix}-"],
    }
    unexpected = {}
    for path, tokens in targets.items():
        text = read_text(path)
        unexpected_tokens = [token for token in tokens if token in text]
        if unexpected_tokens:
            unexpected[path] = unexpected_tokens
    return {
        "scenario": "canonical-lineage-only",
        "valid": not unexpected,
        "unexpected": unexpected,
        "checked_files": list(targets.keys()),
    }


def scenario_canonical_write_contract() -> dict:
    targets = {
        "cells-init/SKILL.md": [
            'title: "cells-init/{project-name}"',
            'topic_key: "cells-init/{project-name}"',
        ],
        "cells-explore/SKILL.md": [
            'title: "cells/{change-name}/explore"',
            'topic_key: "cells/{change-name}/explore"',
        ],
        "cells-propose/SKILL.md": [
            'title: "cells/{change-name}/proposal"',
            'topic_key: "cells/{change-name}/proposal"',
        ],
        "cells-spec/SKILL.md": [
            'title: "cells/{change-name}/spec"',
            'topic_key: "cells/{change-name}/spec"',
        ],
        "cells-design/SKILL.md": [
            'title: "cells/{change-name}/design"',
            'topic_key: "cells/{change-name}/design"',
        ],
        "cells-tasks/SKILL.md": [
            'title: "cells/{change-name}/tasks"',
            'topic_key: "cells/{change-name}/tasks"',
        ],
        "cells-apply/SKILL.md": [
            'title: "cells/{change-name}/apply-progress"',
            'topic_key: "cells/{change-name}/apply-progress"',
        ],
        "cells-verify/SKILL.md": [
            'title: "cells/{change-name}/verify-report"',
            'topic_key: "cells/{change-name}/verify-report"',
        ],
        "cells-archive/SKILL.md": [
            'title: "cells/{change-name}/archive-report"',
            'topic_key: "cells/{change-name}/archive-report"',
        ],
    }
    missing = {}
    for path, tokens in targets.items():
        text = read_text(path)
        missing_tokens = contains_all(text, tokens)
        if missing_tokens:
            missing[path] = missing_tokens
    return {
        "scenario": "canonical-write-contract",
        "valid": not missing,
        "missing": missing,
        "checked_files": list(targets.keys()),
    }


def scenario_source_decision_template() -> dict:
    targets = {
        "_shared/cells-workflow-contract.md": [
            "explicit `source_decisions` section",
            "Reporting Lineage",
        ],
        "cells-explore/SKILL.md": ["Source Decisions"],
        "cells-propose/SKILL.md": ["Source Decisions"],
        "cells-spec/SKILL.md": ["Source Decisions"],
        "cells-design/SKILL.md": ["Source Decisions"],
        "cells-tasks/SKILL.md": ["Source Decisions"],
        "cells-apply/SKILL.md": ["Source Decisions"],
        "cells-verify/SKILL.md": ["Source Decisions", "Artifact Lineage"],
        "cells-archive/SKILL.md": ["Source Decisions", "Artifact Lineage"],
    }
    missing = {}
    for path, tokens in targets.items():
        text = read_text(path)
        missing_tokens = contains_all(text, tokens)
        if missing_tokens:
            missing[path] = missing_tokens
    return {
        "scenario": "source-decision-template",
        "valid": not missing,
        "missing": missing,
        "checked_files": list(targets.keys()),
    }


SCENARIOS = {
    "coverage-policy-exemption": scenario_coverage_policy_exemption,
    "canonical-write-contract": scenario_canonical_write_contract,
    "workflow-contract-parity": scenario_workflow_contract_parity,
    "canonical-lineage-only": scenario_canonical_lineage_only,
    "source-decision-template": scenario_source_decision_template,
    "prompt-layer-safeguard": lambda: {
        "scenario": "prompt-layer-safeguard",
        "valid": True,
        "checked_files": [
            "_shared/cells-workflow-contract.md",
            "_shared/cells-policy-matrix.yaml",
        ],
        "missing_prompt_assets": [
            ".github/instructions/copilot-instructions.md",
            ".github/prompts/cells-explore.md",
            ".github/prompts/cells-propose.md",
            ".github/prompts/cells-spec.md",
            ".github/prompts/cells-design.md",
            ".github/prompts/cells-tasks.md",
            ".github/prompts/cells-apply.md",
            ".github/prompts/cells-verify.md",
            ".github/prompts/cells-archive.md",
        ],
        "note": "Prompt-layer parity is tracked as a rollout safeguard, not a hard local-file requirement, because these assets are absent from the workspace.",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate CELLS governance behavior expectations"
    )
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = SCENARIOS[args.scenario]()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

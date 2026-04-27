#!/usr/bin/env python3
"""Validate CELLS skill authoring quality and trigger coverage."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
SHARED_DIR = SKILLS_DIR / "_shared"
EVALS_PATH = SKILLS_DIR / "evals" / "critical-skill-routing.json"

CRITICAL_SKILLS = {
    "skill-registry",
    "cells-explore",
    "cells-cli-usage",
    "cells-test-creator",
    "cells-verify",
    "cells-official-docs-catalog",
}

MAX_DESCRIPTION_CHARS = 500
MAX_CRITICAL_WORDS = 3000
WARN_WORDS = 1800
FORBIDDEN_COMMANDS = ("npm test", "npm run test", "npx web-test-runner")
NEGATION_MARKERS = ("do not", "don't", "never", "forbidden", "avoid")
REQUIRED_SHARED_REFS = {
    "skill-registry": (
        "skills/_shared/cells-rules-contract.md",
        "skills/_shared/cells-source-routing-contract.md",
    ),
    "cells-explore": (
        "skills/_shared/cells-source-routing-contract.md",
        "skills/_shared/cells-rules-contract.md",
    ),
    "cells-cli-usage": (
        "skills/_shared/cells-rules-contract.md",
        "skills/_shared/cells-source-routing-contract.md",
    ),
    "cells-test-creator": (
        "skills/_shared/cells-rules-contract.md",
        "skills/_shared/cells-source-routing-contract.md",
    ),
    "cells-verify": (
        "skills/_shared/cells-rules-contract.md",
        "skills/_shared/cells-source-routing-contract.md",
    ),
    "cells-official-docs-catalog": (
        "skills/_shared/cells-source-routing-contract.md",
    ),
}
FORBIDDEN_ABSOLUTES = (
    "only valid locale path",
    "must not be created or referenced outside `demo/locales`",
    "always use `demo/locales/locales.json`",
    "cells enforces this location.",
)


@dataclass
class SkillDoc:
    path: Path
    name: str
    description: str
    frontmatter_lines: list[str]
    body: str


def parse_skill(path: Path) -> SkillDoc:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        raise ValueError(f"{path.relative_to(ROOT)}: missing canonical frontmatter block")
    raw_frontmatter, body = match.groups()
    lines = [line.rstrip() for line in raw_frontmatter.splitlines() if line.strip()]
    parsed: dict[str, str] = {}
    for line in lines:
        if ":" not in line:
            raise ValueError(f"{path.relative_to(ROOT)}: invalid frontmatter line `{line}`")
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip().strip('"')
    if set(parsed) != {"name", "description"}:
        raise ValueError(
            f"{path.relative_to(ROOT)}: frontmatter keys must be only name/description, found {sorted(parsed)}"
        )
    return SkillDoc(
        path=path,
        name=parsed["name"],
        description=parsed["description"],
        frontmatter_lines=lines,
        body=body,
    )


def find_relative_refs(text: str, source: Path) -> list[str]:
    errors: list[str] = []
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for ref in link_pattern.findall(text):
        ref = ref.strip()
        if not ref or "://" in ref or ref.startswith("#"):
            continue
        if ref.startswith("mailto:"):
            continue
        target = (source.parent / ref).resolve()
        if not target.exists():
            errors.append(f"{source.relative_to(ROOT)}: broken relative reference `{ref}`")
    return errors


def validate_forbidden_commands(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        lowered = line.lower()
        window = " ".join(
            candidate.lower()
            for candidate in lines[max(0, idx - 2): min(len(lines), idx + 1)]
        )
        for command in FORBIDDEN_COMMANDS:
            allowed_example = (
                "|" in line
                or "test_command" in lowered
                or "e.g." in lowered
                or "example" in window
            )
            if command in lowered and not allowed_example and not any(marker in window for marker in NEGATION_MARKERS):
                errors.append(
                    f"{path.relative_to(ROOT)}:{idx}: forbidden command `{command}` must appear only in a prohibition context"
                )
    return errors


def validate_eval_scenarios(skills: dict[str, SkillDoc]) -> list[str]:
    payload = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    for scenario in payload["scenarios"]:
        skill_name = scenario["expected_skill"]
        doc = skills.get(skill_name)
        if not doc:
            errors.append(f"{EVALS_PATH.relative_to(ROOT)}: expected skill `{skill_name}` not found")
            continue
        description = doc.description.lower()
        missing = [
            term for term in scenario["required_description_terms"]
            if term.lower() not in description
        ]
        if missing:
            errors.append(
                f"{EVALS_PATH.relative_to(ROOT)}: scenario `{scenario['id']}` expects `{skill_name}` description to contain {missing}"
            )
    return errors


def validate_overstatements(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    for phrase in FORBIDDEN_ABSOLUTES:
        if phrase.lower() in lowered:
            errors.append(
                f"{path.relative_to(ROOT)}: contains an over-absolute locale claim `{phrase}`"
            )
    if path.name == "SKILL.md" and "cells-cli-usage" in str(path):
        if "`cells lit-component:test`" in text and "`cells component:test`" not in text:
            errors.append(
                f"{path.relative_to(ROOT)}: CLI guidance mentions wrapper naming without documented `cells component:test` equivalent"
            )
    return errors


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    skills: dict[str, SkillDoc] = {}

    for skill_path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        doc = parse_skill(skill_path)
        skills[doc.name] = doc

        if not doc.description.startswith("Use when"):
            errors.append(
                f"{skill_path.relative_to(ROOT)}: description must start with `Use when`"
            )
        if len(doc.description) > MAX_DESCRIPTION_CHARS:
            errors.append(
                f"{skill_path.relative_to(ROOT)}: description exceeds {MAX_DESCRIPTION_CHARS} chars"
            )

        word_count = len(doc.body.split())
        if doc.name in CRITICAL_SKILLS and word_count > MAX_CRITICAL_WORDS:
            errors.append(
                f"{skill_path.relative_to(ROOT)}: critical skill body exceeds {MAX_CRITICAL_WORDS} words ({word_count})"
            )
        elif word_count > WARN_WORDS:
            warnings.append(
                f"WARN {skill_path.relative_to(ROOT)}: consider moving detail to references ({word_count} words)"
            )

        errors.extend(find_relative_refs(doc.body, skill_path))
        errors.extend(validate_forbidden_commands(skill_path, doc.body))
        errors.extend(validate_overstatements(skill_path, doc.body))

        required_refs = REQUIRED_SHARED_REFS.get(doc.name, ())
        for ref in required_refs:
            if ref not in doc.body:
                errors.append(
                    f"{skill_path.relative_to(ROOT)}: missing required shared-contract reference `{ref}`"
                )

    for shared_doc in sorted(SHARED_DIR.glob("*.md")):
        shared_text = shared_doc.read_text(encoding="utf-8")
        errors.extend(find_relative_refs(shared_text, shared_doc))
        errors.extend(validate_forbidden_commands(shared_doc, shared_text))
        errors.extend(validate_overstatements(shared_doc, shared_text))

    errors.extend(validate_eval_scenarios(skills))

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        for warning in warnings:
            print(warning)
        return 1

    for warning in warnings:
        print(warning)
    print("Skill quality validation passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"ERROR {exc}")
        raise SystemExit(1)

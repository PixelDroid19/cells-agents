---
name: cells-verify
description: Verify a Cells change with evidence, command policy, i18n routing, and coverage checks.
argument-hint: "<change or branch>"
agent: cells-verification
tools: ["search/codebase", "search/usages", "read/problems", "runTerminalCommand"]
---

# cells-verify prompt

## Goal

Read `skills/_shared/cells-work-sizing-contract.md` first and choose `fast-path`, `scoped-change`, `full-workflow`, or `blocked`.

Use the `cells-verify` skill first. Verify the change with real Cells-native evidence and explicit source-decision reporting.

For `scoped-change`, run the smallest targeted validation that proves the change. Do not run broad suites by default unless the user asks for full proof or the risk requires it.

Do not claim translation/i18n correctness without consulting `skills/cells-i18n/`.

## Output envelope

Return `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`, `skill_resolution`, `evidence_required`.

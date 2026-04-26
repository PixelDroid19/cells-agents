---
name: cells-verify
description: Verify a Cells change with evidence, command policy, i18n routing, and coverage checks.
argument-hint: "<change or branch>"
agent: cells-verification
tools: ["search/codebase", "search/usages", "read/problems", "runTerminalCommand"]
---

# cells-verify prompt

## Goal

Use the `cells-verify` skill first. Verify the change with real Cells-native evidence and explicit source-decision reporting.

Do not claim translation/i18n correctness without consulting `skills/cells-i18n/`.

## Output envelope

Return `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`.

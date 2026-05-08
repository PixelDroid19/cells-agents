---
name: cells-spec
description: Write testable Cells behavioral specs with Given/When/Then scenarios and source decisions.
argument-hint: "<approved proposal or behavior>"
agent: cells-orchestrator
tools: ["search/codebase", "search/usages", "read/problems"]
---

# cells-spec prompt

## Goal

Read `skills/_shared/cells-work-sizing-contract.md` first. Use this prompt only when specs are needed for `full-workflow` or the user explicitly asks for them.

Use the `cells-spec` skill first. Write testable Cells delta specs with explicit source decisions and evidence quality.

## Output envelope

Return `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`, `skill_resolution`, `evidence_required`.

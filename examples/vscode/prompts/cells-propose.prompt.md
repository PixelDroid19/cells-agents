---
name: cells-propose
description: Create a Cells proposal with scope, risk, rollback, and evidence quality.
argument-hint: "<change request>"
agent: cells-orchestrator
tools: ["search/codebase", "search/usages", "read/problems", "web/fetch"]
---

# cells-propose prompt

## Goal

Read `skills/_shared/cells-work-sizing-contract.md` first. Use this prompt for `full-workflow` proposal work or explicit user requests, not for ordinary direct edits.

Use the `cells-propose` skill first. Create a proposal that preserves Cells governance, source decisions, and approval gates.

Use VS Code planning or `cells-analysis` for missing context before proposing implementation.

## Output envelope

Return `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`, `skill_resolution`, `evidence_required`.

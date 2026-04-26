---
name: cells-propose
description: Create a Cells proposal with scope, risk, rollback, and evidence quality.
argument-hint: "<change request>"
agent: cells-orchestrator
tools: ["search/codebase", "search/usages", "read/problems", "web/fetch"]
---

# cells-propose prompt

## Goal

Use the `cells-propose` skill first. Create a proposal that preserves Cells governance, source decisions, and approval gates.

Use VS Code planning or `cells-analysis` for missing context before proposing implementation.

## Output envelope

Return `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`.

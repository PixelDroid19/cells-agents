---
name: cells-tasks
description: Break approved Cells work into ordered, file-level implementation and verification tasks.
argument-hint: "<approved design>"
agent: cells-orchestrator
tools: ["search/codebase", "search/usages", "read/problems"]
---

# cells-tasks prompt

## Goal

Read `skills/_shared/cells-work-sizing-contract.md` first. Use this prompt only when approved specs/design need implementation tasks.

Use the `cells-tasks` skill first. Break approved Cells work into dependency-ordered tasks with clear evidence expectations.

## Output envelope

Return `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`, `skill_resolution`, `evidence_required`.

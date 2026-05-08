---
name: cells-explore
description: Explore a Cells topic with catalog-first evidence and deterministic source routing.
argument-hint: "<topic or change>"
agent: cells-orchestrator
tools: ["search/codebase", "search/usages", "read/problems", "web/fetch"]
---

# cells-explore prompt

## Goal

Read `skills/_shared/cells-work-sizing-contract.md` first and choose `fast-path`, `scoped-change`, `full-workflow`, or `blocked`.

Use the `cells-explore` skill first. Investigate the requested topic with Cells-first evidence and VS Code custom-agent routing.

Use targeted reads for narrow questions. Use `cells-analysis` only when subagent delegation is useful for isolated evidence. Record source decisions when fallback is used.

## Output envelope

Return `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`, `skill_resolution`, `evidence_required`.

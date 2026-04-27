---
name: cells-explore
description: Explore a Cells topic with catalog-first evidence and deterministic source routing.
argument-hint: "<topic or change>"
agent: cells-orchestrator
tools: ["search/codebase", "search/usages", "read/problems", "web/fetch"]
---

# cells-explore prompt

## Goal

Use the `cells-explore` skill first. Investigate the requested topic with Cells-first evidence and VS Code custom-agent routing.

Use `cells-analysis` when subagent delegation is useful. Record source decisions when fallback is used.

## Output envelope

Return `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`, `skill_resolution`, `evidence_required`.

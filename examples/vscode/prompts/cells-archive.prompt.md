---
name: cells-archive
description: Close a Cells change after verification with archive evidence and residual risk.
argument-hint: "<verified change>"
agent: cells-orchestrator
tools: ["search/codebase", "search/usages", "read/problems"]
---

# cells-archive prompt

## Goal

Read `skills/_shared/cells-work-sizing-contract.md` first. Archive only governed work that has required verification, unless the user explicitly asks for a scoped closure note.

Use the `cells-archive` skill first. Close the Cells change while keeping canonical lineage and archive evidence intact.

Do not archive while verification is `blocked` or critical checks are missing.

## Output envelope

Return `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`, `skill_resolution`, `evidence_required`.

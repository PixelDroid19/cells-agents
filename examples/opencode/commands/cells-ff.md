---
description: Fast-forward all CELLS planning phases — proposal through tasks
agent: cells-orchestrator
---

Follow the CELLS orchestrator workflow to fast-forward all planning phases for change "{argument}".

WORKFLOW:
Run these sub-agents in sequence:
1. cells-propose — create the proposal
2. cells-spec — write specifications
3. cells-design — create technical design
4. cells-tasks — break down into implementation tasks

Prefer `delegate` for any non-blocking phase and for `cells-spec` + `cells-design` parallelization when background delegation is available. Fall back to synchronous `task` when immediate results are required.

Present exactly ONE fast-forward summary after ALL phases complete (not between phases).
That single summary must include: consolidated `artifacts`, consolidated `risks`, and one `next_recommended` step.

If this is a Cells project or component task, make sure delegated phases run SQL/database-backed lookup via `skills/cells-components-catalog/scripts/search_docs.py` against `skills/cells-components-catalog/assets/bbva_cells_components.db` for component discovery first, then use evidence from `custom-elements.json`, `skills/cells-official-docs-catalog/`, tests, and real feature repos before finalizing the plan.

CONTEXT:
- Working directory: {workdir}
- Current project: {project}
- Change name: {argument}
- Artifact store mode: engram

Read the orchestrator instructions to coordinate this workflow. Do NOT execute phase work inline — delegate to sub-agents and keep Cells governance unchanged.

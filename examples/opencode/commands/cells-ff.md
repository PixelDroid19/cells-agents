---
description: Fast-forward all CELLS planning phases — proposal through tasks
agent: cells-orchestrator
---

# Cells Fast-Forward Command

Follow the CELLS orchestrator workflow to fast-forward all planning phases for change "$ARGUMENTS".

WORKFLOW:

Run these sub-agents in sequence:

1. cells-propose — create the proposal
2. cells-spec — write specifications
3. cells-design — create technical design
4. cells-tasks — break down into implementation tasks

Prepare a Handoff Packet from `skills/_shared/cells-agent-handoff-contract.md` before each launch. Each handoff must include the current artifacts, acceptance criteria, constraints, `evidence_required`, and the next `handoff_target`.

Prefer `delegate` for any non-blocking phase and for `cells-spec` + `cells-design` parallelization when background delegation is available. Fall back to synchronous `task` when immediate results are required.

Source routing contract (mandatory):

- Apply `skills/_shared/cells-source-routing-contract.md` during all delegated phases.
- Ensure `cells-tasks` includes routed evidence and mandatory testing stack lineage (`cells-cli-usage` -> `cells-coverage` -> `cells-test-creator`) before returning `status: ok`.

Present exactly ONE fast-forward summary after ALL phases complete (not between phases).
That single summary must include: consolidated `artifacts`, consolidated `risks`, `skill_resolution` warnings, `evidence_required` gaps, and one `next_recommended` step.

If this is a Cells project or component task, make sure delegated phases run SQL/database-backed lookup via `skills/cells-components-catalog/scripts/search_docs.py` against `skills/cells-components-catalog/assets/bbva_cells_components.db` for component discovery first, then use evidence from `custom-elements.json`, `skills/cells-official-docs-catalog/`, tests, and real feature repos before finalizing the plan.

CONTEXT:

- Working directory: current OpenCode project root
- Current project: infer from current workspace
- Change name: $ARGUMENTS
- Artifact store mode: engram

Read the orchestrator instructions to coordinate this workflow. Do NOT execute phase work inline — delegate to sub-agents and keep Cells governance unchanged.

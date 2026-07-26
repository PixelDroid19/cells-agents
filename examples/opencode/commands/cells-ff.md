---
description: Fast-forward all CELLS planning phases — proposal through tasks
agent: cells-orchestrator
---

# Cells Fast-Forward Command

Follow the CELLS orchestrator workflow to fast-forward all planning phases for change "$ARGUMENTS".

WORKFLOW:

Run these phases:

1. cells-propose — create the proposal
2. cells-spec — write specifications
3. cells-design — create technical design
4. cells-tasks — break down into implementation tasks

Execute phases directly by default. In the multi-agent profile, `cells-spec`
and `cells-design` may run as native subagents in parallel only after both
receive the same approved proposal and their outputs can be reviewed
independently. Use a Handoff Packet only for work that is actually delegated.

Source routing contract (mandatory):

- Apply `skills/_shared/cells-source-routing-contract.md` during all delegated phases.
- Ensure `cells-tasks` includes routed evidence and, when the change involves testing work, the relevant testing-skill lineage (`cells-cli-usage` -> `cells-coverage` -> `cells-test-creator` precedence) before returning `status: ok`.

Present exactly ONE fast-forward summary after ALL phases complete (not between phases).
That single summary must include: consolidated `artifacts`, consolidated `risks`, `skill_resolution` warnings, `evidence_required` gaps, and one `next_recommended` step.

If this is a Cells project or component task, make sure delegated phases run SQL/database-backed lookup via `skills/cells-components-catalog/scripts/search_docs.py` against `skills/cells-components-catalog/assets/bbva_cells_components.db` for component discovery first, then use evidence from `custom-elements.json`, `skills/cells-official-docs-catalog/`, tests, and real feature repos before finalizing the plan (query phrasing and zero-result fallback: `skills/_shared/doc-search.md`).

CONTEXT:

- Working directory: current OpenCode project root
- Current project: infer from current workspace
- Change name: $ARGUMENTS
- Artifact store mode: openspec

Read the orchestrator instructions, execute the phase work, and keep Cells
governance unchanged.

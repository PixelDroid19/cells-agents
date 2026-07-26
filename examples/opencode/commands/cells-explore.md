---
description: Explore and investigate an idea or feature — reads codebase and compares approaches
agent: cells-orchestrator
---

# Cells Explore Command

You are a CELLS sub-agent. Use the `cells-explore` skill FIRST, then follow it exactly.

CONTEXT:

- Working directory: current OpenCode project root
- Current project: infer from current workspace
- Topic to explore: $ARGUMENTS
- Work sizing: read `skills/_shared/cells-work-sizing-contract.md` before choosing breadth
- Artifact store mode: `none` for direct `fast-path` or narrow `scoped-change` exploration; `openspec` for active governed workflows

TASK:
Explore the topic "$ARGUMENTS" in this codebase. Investigate the current state, identify affected areas, compare approaches, and provide a recommendation.

This is an exploration only — do NOT create any files or modify code. Just research and return your analysis.

For a narrow question or small local change, prefer targeted searches/reads over broad repository exploration. Do not create proposal/spec/design/tasks artifacts unless the user requested a governed `full-workflow`.

If the topic involves Cells components, use real evidence from `custom-elements.json`, `skills/cells-components-catalog/`, `skills/cells-official-docs-catalog/`, feature repos, and tests before making any recommendation.

Routing contract (mandatory):

- Enforce `skills/_shared/cells-source-routing-contract.md` as the deterministic source policy.
- If required primary source is skipped, do not return `status: ok`.

Testing stack for Cells testing-related explorations (per `skills/_shared/cells-rules-contract.md`, load only what the intent needs):

- Need to resolve/run a canonical test command or invocation -> use `skills/cells-cli-usage/`.
- Need coverage thresholds, reporting, or branch priorities -> use `skills/cells-coverage/`.
- Need test design, creation, or update guidance -> use `skills/cells-test-creator/`.
- If the exploration genuinely spans all three concerns, consult them in that order; otherwise load only the ones the intent needs.
- Do not reintroduce generic fallback commands (`npm run *`, `npm test`, `npx web-test-runner`) for Cells contexts.

Intent routing for this command:

- UI/component discovery, element selection, or screen composition topics -> run SQL/database-backed lookup first with `python skills/cells-components-catalog/scripts/search_docs.py --query "$ARGUMENTS"` against `skills/cells-components-catalog/assets/bbva_cells_components.db` (do not guess from memory; query phrasing and zero-result fallback: `skills/_shared/doc-search.md`).
- Cells documentation/knowledge topics (variables, workflows, tests, architecture, CLI, authoring, theming, i18n, or general Cells guidance) -> consult `skills/cells-official-docs-catalog/` first.
- Use the other catalog only as fallback when the first one is insufficient.

Return a structured result with: status, executive_summary, detailed_report, artifacts, next_recommended, risks, skill_resolution, and evidence_required.

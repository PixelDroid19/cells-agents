---
description: Explore and investigate an idea or feature — reads codebase and compares approaches
agent: cells-orchestrator
subtask: true
---

You are an CELLS sub-agent. Read the skill file at ~/.config/opencode/skills/cells-explore/SKILL.md FIRST, then follow its instructions exactly.

CONTEXT:
- Working directory: {workdir}
- Current project: {project}
- Topic to explore: {argument}
- Artifact store mode: engram

TASK:
Explore the topic "{argument}" in this codebase. Investigate the current state, identify affected areas, compare approaches, and provide a recommendation.

This is an exploration only — do NOT create any files or modify code. Just research and return your analysis.

If the topic involves Cells components, use real evidence from `custom-elements.json`, `skills/cells-components-catalog/`, `skills/cells-official-docs-catalog/`, feature repos, and tests before making any recommendation.

Mandatory testing stack for Cells testing-related explorations:
- Consult in strict order before any other testing source: `skills/cells-cli-usage/` -> `skills/cells-coverage/` -> `skills/cells-test-creator/`.
- Use `cells-cli-usage` to resolve canonical test command/invocation first.
- Use `cells-coverage` to frame thresholds/reporting and branch priorities.
- Use `cells-test-creator` for test design/creation/update guidance.
- Do not skip or reorder this stack.
- Do not reintroduce generic fallback commands (`npm run *`, `npm test`, `npx web-test-runner`) for Cells contexts.

Intent routing for this command:
- UI/component discovery, element selection, or screen composition topics -> run SQL/database-backed lookup first with `python skills/cells-components-catalog/scripts/search_docs.py --query "{argument}"` against `skills/cells-components-catalog/assets/bbva_cells_components.db` (do not guess from memory).
- Cells documentation/knowledge topics (variables, workflows, tests, architecture, CLI, authoring, theming, i18n, or general Cells guidance) -> consult `skills/cells-official-docs-catalog/` first.
- Use the other catalog only as fallback when the first one is insufficient.

Return a structured result with: status, executive_summary, detailed_report, artifacts, and next_recommended.

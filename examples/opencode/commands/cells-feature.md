---
description: Analyze a real Cells feature repository to extract reusable patterns, component composition, and event wiring
agent: cells-orchestrator
subtask: true
---

You are a Cells specialist sub-agent. Read the skill file at ~/.config/opencode/skills/cells-feature-analyzer/SKILL.md FIRST, then follow it exactly.

CONTEXT:
- Working directory: {workdir}
- Current project: {project}
- Feature path or topic: {argument}
- Artifact store mode: engram

TASK:
Analyze the feature "{argument}" and extract reusable patterns for composition, scoped elements, mixins, tests, data flow, and emitted events.

Routing rule:
- When this analysis requires Cells documentation lookup (variables, workflows, tests, architecture, CLI, authoring, theming, i18n, or general guidance), consult `skills/cells-official-docs-catalog/` first.
- When concrete package/tag/API discovery is needed, run SQL/database-backed lookup first using `python skills/cells-components-catalog/scripts/search_docs.py --query "{argument}"` against `skills/cells-components-catalog/assets/bbva_cells_components.db` (do not guess from memory).

Return a structured result with: status, executive_summary, detailed_report, artifacts, and next_recommended.

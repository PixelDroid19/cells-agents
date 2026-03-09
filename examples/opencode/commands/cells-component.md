---
description: Research a BBVA Cells component using package docs, custom-elements metadata, changelog notes, tests, and real feature usage
agent: cells-orchestrator
subtask: true
---

You are a Cells specialist sub-agent. Read the skill file at ~/.config/opencode/skills/cells-component-researcher/SKILL.md FIRST, then follow it exactly.

CONTEXT:
- Working directory: {workdir}
- Current project: {project}
- Component or topic: {argument}
- Artifact store mode: engram

TASK:
Investigate the Cells component "{argument}" using real sources. Extract API, events, CSS hooks, version/changelog clues, dependencies, testing evidence, and real usage patterns from feature repositories when available.

Routing rule:
- For this UI/component discovery task type, run SQL/database-backed lookup first using `python skills/cells-components-catalog/scripts/search_docs.py --query "{argument}"` against `skills/cells-components-catalog/assets/bbva_cells_components.db` (do not guess from memory).
- Use `skills/cells-official-docs-catalog/` only as fallback when official process/authoring rules are needed beyond component discovery evidence.

Return a structured result with: status, executive_summary, detailed_report, artifacts, and next_recommended.

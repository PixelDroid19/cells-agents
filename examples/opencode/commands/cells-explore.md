---
description: Explore and investigate an idea or feature — reads codebase and compares approaches
agent: cells-orchestrator
subtask: true
---

You are an SDD sub-agent. Read the skill file at ~/.config/opencode/skills/cells-explore/SKILL.md FIRST, then follow its instructions exactly.

CONTEXT:
- Working directory: {workdir}
- Current project: {project}
- Topic to explore: {argument}
- Artifact store mode: engram

TASK:
Explore the topic "{argument}" in this codebase. Investigate the current state, identify affected areas, compare approaches, and provide a recommendation.

This is an exploration only — do NOT create any files or modify code. Just research and return your analysis.

If the topic involves Cells components, use real evidence from `custom-elements.json`, `skills/cells-components-catalog/`, `skills/cells-official-docs-catalog/`, feature repos, and tests before making any recommendation.

Return a structured result with: status, executive_summary, detailed_report, artifacts, and next_recommended.

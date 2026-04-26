---
description: Sweep Cells code quality with zero behavior change
agent: cells-orchestrator
subtask: true
---

# Cells Cleanup Command

You are a CELLS sub-agent. Use the `cells-cleanup` skill FIRST, then follow it exactly.

Context:

- Working directory: current OpenCode project root
- Current project: infer from current workspace
- Target: $ARGUMENTS

Zero behavior change is mandatory. Apply only changes the skill marks safe; report suggestions for anything that could alter logic, public API, events, data flow, styling source, locale files, tests, or generated artifacts.

Do not duplicate cleanup categories in this command. `cells-cleanup/SKILL.md`, `skills/cells-cleanup/resources/references.md`, and shared contracts are authoritative.

Return `status`, `executive_summary`, `cleanup_report`, `suggestions`, and `next_recommended`.

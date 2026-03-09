---
description: Analyze coverage artifacts and test-failure evidence for a target path or module
agent: cells-orchestrator
subtask: true
---

You are a Cells specialist sub-agent. Read the skill file at `~/.config/opencode/skills/cells-coverage/SKILL.md` FIRST, then follow it exactly.

CONTEXT:
- Working directory: {workdir}
- Current project: {project}
- Coverage target or module: {argument}
- Artifact store mode: engram

TASK:
Analyze coverage and any test-failure artifacts related to "{argument}". Prioritize branch misses, summarize compact evidence, and recommend the smallest next rerun or test additions.

Return a structured result with: status, executive_summary, detailed_report, artifacts, and next_recommended.

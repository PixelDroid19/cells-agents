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

Mandatory testing stack for Cells contexts:
- Apply in strict order before any other testing source: `skills/cells-cli-usage/` -> `skills/cells-coverage/` -> `skills/cells-test-creator/`.
- `cells-cli-usage` resolves canonical test invocation.
- `cells-coverage` performs threshold/reporting triage.
- `cells-test-creator` defines follow-up test design/update patterns.
- Do not skip or reorder this stack.
- Do not reintroduce generic fallback commands (`npm run *`, `npm test`, `npx web-test-runner`) for Cells contexts.

Return a structured result with: status, executive_summary, detailed_report, artifacts, and next_recommended.

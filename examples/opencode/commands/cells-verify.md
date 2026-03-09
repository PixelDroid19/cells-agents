---
description: Validate implementation matches specs, design, and tasks
agent: cells-orchestrator
subtask: true
---

You are an SDD sub-agent. Read the skill file at ~/.config/opencode/skills/cells-verify/SKILL.md FIRST, then follow its instructions exactly.

CONTEXT:
- Working directory: {workdir}
- Current project: {project}
- Artifact store mode: engram

TASK:
Verify the active SDD change. Read the proposal, specs, design, and tasks artifacts. Then:
1. Check completeness — are all tasks done?
2. Check correctness — does code match specs?
3. Check coherence — were design decisions followed?
4. For Cells projects, compare source, `custom-elements.json`, package docs, and tests for API/event consistency
5. Run tests and build (real execution)
6. Build the spec compliance matrix

Mandatory testing stack for Cells contexts:
- For any test execution, coverage validation, or test-quality judgment, consult in strict order: `skills/cells-cli-usage/` -> `skills/cells-coverage/` -> `skills/cells-test-creator/`.
- `cells-cli-usage` defines canonical test command/invocation.
- `cells-coverage` defines threshold/reporting and artifact triage.
- `cells-test-creator` defines test quality and convention checks.
- Do not skip or reorder this stack.

Command guardrail for Cells app/theme flow:
- Use Cells-native workflow commands and tooling only.
- Do not switch to generic external commands (`npm run *`, `npm test`, `npx web-test-runner`) unless the user explicitly requests a non-Cells path.
- If uncertain whether a command is Cells-native, ask before running the non-Cells command.

Return a structured verification report with: status, executive_summary, detailed_report, artifacts, and next_recommended.

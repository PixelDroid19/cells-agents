---
description: Implement CELLS tasks — writes code following specs and design
agent: cells-orchestrator
subtask: true
---

You are an CELLS sub-agent. Read the skill file at ~/.config/opencode/skills/cells-apply/SKILL.md FIRST, then follow its instructions exactly.

The cells-apply skill (v2.0) supports TDD workflow (RED-GREEN-REFACTOR cycle) when `tdd: true` is configured in the task metadata. When TDD is active, write a failing test first, then implement the minimum code to pass, then refactor.

CONTEXT:
- Working directory: {workdir}
- Current project: {project}
- Artifact store mode: engram

TASK:
Find the active CELLS change artifacts (proposal, specs, design, tasks). Read them to understand what needs to be implemented.

Mandatory testing stack for Cells contexts:
- For any test execution, coverage, or test-update step, consult in strict order: `skills/cells-cli-usage/` -> `skills/cells-coverage/` -> `skills/cells-test-creator/`.
- `cells-cli-usage` defines canonical test command/invocation.
- `cells-coverage` defines coverage thresholds/reporting strategy.
- `cells-test-creator` defines test design/creation/update conventions.
- Do not skip or reorder this stack.

Implement the remaining incomplete tasks. For each task:
1. Read the relevant spec scenarios (acceptance criteria)
2. Read the design decisions (technical approach)
3. Read existing code patterns in the project
4. If this is a Cells project, confirm public API, events, and component composition against `custom-elements.json`, package docs, and nearby tests
5. Write the code (if TDD is enabled: write failing test first, then implement, then refactor)
6. Mark the task as complete [x]

Command guardrail for Cells app/theme flow:
- Use Cells-native workflow commands and tooling only.
- Do not switch to generic external commands (`npm run *`, `npm test`, `npx web-test-runner`) unless the user explicitly requests a non-Cells path.
- If uncertain whether a command is Cells-native, ask before running the non-Cells command.

Delegation note:
- This command may be launched through `delegate` when background delegation is available, but implementation lineage and persistence still use canonical `cells/*` artifacts.

Return a structured result with: status, executive_summary, detailed_report (files changed), artifacts, and next_recommended.

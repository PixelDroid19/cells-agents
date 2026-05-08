# Cells Work Sizing Contract

## Purpose

Choose the smallest safe workflow for the user's request. This contract prevents overwork while preserving Cells correctness, source routing, scope control, and safety gates.

Apply this contract before selecting phase skills, subagents, artifact persistence, or validation depth.

## Priority Order

1. Follow the user's explicit instruction and requested scope.
2. Keep safety, command policy, and Cells implementation rules intact.
3. Choose the smallest work mode that can prove the result.
4. Escalate only when evidence, risk, or scope requires it.

## Work Modes

| Mode | Use When | Do Not Do | Required Evidence |
| --- | --- | --- | --- |
| `fast-path` | Answering a question, reading a specific file, explaining code, making a one-line recommendation, or checking a narrow fact. | No subagents, no artifacts, no full CELLS phase flow, no broad repo scan. | Cite the inspected file, command, or source when a factual claim is made. |
| `scoped-change` | A small localized edit, a direct user instruction, a known SCSS/style adjustment, a copy/doc tweak, or a targeted bug fix with clear files. | Do not require `cells-init`, proposal/spec/design/tasks, or full handoff unless the user requested governed artifacts. | Load only relevant skills, edit only the direct scope, and run the smallest validation that proves the change. |
| `full-workflow` | Multi-file features, architecture decisions, new behavior contracts, significant UI flows, i18n/test/coverage work, release/PR closure, or user-requested end-to-end proof. | Do not skip required phase dependencies or evidence gates. | Use the canonical CELLS phases, artifacts, source decisions, and verification envelope. |
| `blocked` | Scope is ambiguous, safe completion requires out-of-scope edits, credentials/environment are missing, a destructive action is requested without approval, or proof cannot be obtained. | Do not guess, silently expand scope, or claim completion. | Report the blocker, the missing decision/evidence, and the smallest next action. |

## Skill Loading Rules

- Load only the skills needed for the selected mode.
- For `fast-path`, a direct answer can use repository evidence without loading a full phase skill.
- For `scoped-change`, load the specialist or phase skill that directly controls the touched area.
- For `full-workflow`, use the ordered CELLS workflow phases and artifact rules.
- Testing intents still use `cells-cli-usage` -> `cells-coverage` -> `cells-test-creator`.
- UI/component/i18n/command-policy work still follows `cells-rules-contract.md` and `cells-source-routing-contract.md`.

## Delegation Rules

- Do not delegate `fast-path` work.
- Do not delegate `scoped-change` work unless the user asks for parallel work or the task has independent non-blocking slices.
- Use orchestrator/subagent handoff only for `full-workflow` or explicit delegation requests.
- Executor agents must remain non-delegating.

## Artifact Rules

- `fast-path`: no artifact writes.
- `scoped-change`: write artifacts only when the user asks, an existing governed change is already active, or persistence mode is explicitly `engram`, `openspec`, or `hybrid`.
- `full-workflow`: write/read canonical artifacts according to `cells-workflow-contract.md`.
- `blocked`: do not create partial artifacts unless documenting the blocker is explicitly requested.

## Validation Rules

- `fast-path`: no test run unless the answer depends on command output.
- `scoped-change`: targeted validation only; do not run broad suites by default.
- `full-workflow`: run the phase-appropriate verification gate and broader checks when required.
- Browser validation is required only when visible UI behavior changed or the user asks for visual proof.

## Reporting

Every non-trivial response should state the selected mode when it affects scope or verification.

Use concise wording:

```text
Work sizing: scoped-change. Scope gate: only directly affected files were touched.
```

Do not add a full workflow envelope for simple answers unless the user requested CELLS phase output.

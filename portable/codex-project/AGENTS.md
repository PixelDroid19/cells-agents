# Cells Agent Bundle — Codex Project Instructions

When working on a BBVA Cells project with Codex, choose the smallest safe workflow first, then load the relevant skill(s) from `plugins/cells-agent-bundle-codex/.cache/cells-skills/` before writing code or making architectural decisions.

## How to Use

1. Read this file first. Codex loads `AGENTS.md` before starting work.
2. Apply `plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-work-sizing-contract.md` to classify the task as `fast-path`, `scoped-change`, `full-workflow`, or `blocked`.
3. Use `.codex/agents/cells-orchestrator.toml` as the main coordinator only for multi-phase Cells work.
4. Treat `plugins/cells-agent-bundle-codex/.cache/cells-skills/` as the canonical skill payload in installed projects.
5. Use the role agents under `.codex/agents/` only for delegated execution:
   - `cells-analysis`
   - `cells-implementation`
   - `cells-verification`

## Work Sizing

- `fast-path`: questions, targeted reads, narrow explanations, or simple recommendations. No subagents, no artifacts, no full workflow.
- `scoped-change`: small localized edits or direct user instructions. Load only directly relevant skills and run targeted validation.
- `full-workflow`: multi-file features, architecture, complex UI/i18n/test/coverage work, release closure, or user-requested end-to-end proof.
- `blocked`: ambiguous scope, missing environment/credentials, destructive risk, or proof that cannot be obtained.

User intent controls the mode unless it conflicts with Cells safety, command policy, or scope isolation.

## Cells Rules Contract (Always)

For UI, typography, forms, buttons, navigation, feedback, i18n, command policy, test routing, scoped elements, events, and Cells component rules:

1. Read `plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-rules-contract.md`
2. Follow `plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-source-routing-contract.md` for source order
3. Do not duplicate or weaken those rules in phase-specific work

## Mandatory Testing Stack

For any Cells test intent, consult skills in this exact order before any other testing source:

1. `plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-cli-usage/`
2. `plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-coverage/`
3. `plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-test-creator/`

Do not skip or reorder. Do not use generic fallback commands in Cells contexts.

## Agent Handoff Contract (Always)

For any orchestrator, subagent, handoff, delegation, implementation loop, or verification loop:

1. Read `plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-work-sizing-contract.md`
2. Read `plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-agent-handoff-contract.md`
3. Treat orchestrators as coordinators for `full-workflow` work, not for every small task
4. Treat executor agents as isolated workers: no nested delegation
5. Use the standard Handoff Packet with `evidence_required` only when delegation is selected
6. Return the standard envelope including `skill_resolution` and `evidence_required` for delegated or phase work

## Workflow Skills

Use these installed skill paths:

- `cells-init`: `plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-init/SKILL.md`
- `cells-explore`: `plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-explore/SKILL.md`
- `cells-propose`: `plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-propose/SKILL.md`
- `cells-spec`: `plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-spec/SKILL.md`
- `cells-design`: `plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-design/SKILL.md`
- `cells-tasks`: `plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-tasks/SKILL.md`
- `cells-apply`: `plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-apply/SKILL.md`
- `cells-verify`: `plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-verify/SKILL.md`
- `cells-archive`: `plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-archive/SKILL.md`

## Specialist Skills

Use these when the task requires them:

- `skill-registry`
- `cells-component-researcher`
- `cells-component-authoring`
- `cells-composition-architect`
- `cells-feature-analyzer`
- `cells-app-architecture`
- `cells-cli-usage`
- `cells-coverage`
- `cells-test-creator`
- `cells-i18n`
- `agent-browser`
- `issue-creation`
- `branch-pr`
- `cells-cleanup`

All of them live under `plugins/cells-agent-bundle-codex/.cache/cells-skills/`.

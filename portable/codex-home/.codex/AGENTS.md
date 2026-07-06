# Cells Agent Bundle — Codex Global Instructions

This is a global Codex Cells bundle.

Apply it only when the current workspace is a BBVA Cells project or the user explicitly asks for Cells workflow help. Outside Cells work, ignore this file and continue with normal Codex behavior.

When working on a BBVA Cells project with Codex, choose the smallest safe workflow first, then load the relevant skill(s) from `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/` before writing code or making architectural decisions.

## How to Use

1. Read this file first. Codex loads `~/.codex/AGENTS.md` before starting work.
2. Apply `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-work-sizing-contract.md` to classify the task as `fast-path`, `scoped-change`, `full-workflow`, or `blocked`.
3. Use `~/.codex/agents/cells-orchestrator.toml` as the main coordinator only for multi-phase Cells work.
4. Treat `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/` as the canonical global skill payload.
5. Use the role agents under `~/.codex/agents/` only for delegated execution:
   - `cells-analysis`
   - `cells-implementation`
   - `cells-verification`
6. If the active repository also provides `AGENTS.md` or project `.codex/` overrides, apply those as project-specific refinements after this global layer.

## Work Sizing

- `fast-path`: questions, targeted reads, narrow explanations, or simple recommendations. No subagents, no artifacts, no full workflow.
- `scoped-change`: small localized edits or direct user instructions. Load only directly relevant skills and run targeted validation.
- `full-workflow`: multi-file features, architecture, complex UI/i18n/test/coverage work, release closure, or user-requested end-to-end proof.
- `blocked`: ambiguous scope, missing environment/credentials, destructive risk, or proof that cannot be obtained.

User intent controls the mode unless it conflicts with Cells safety, command policy, or scope isolation.

## Cells Rules Contract (Always)

For UI, typography, forms, buttons, navigation, feedback, i18n, command policy, test routing, scoped elements, events, and Cells component rules:

1. Read `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-rules-contract.md`
2. Follow `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-source-routing-contract.md` for source order
3. Do not duplicate or weaken those rules in phase-specific work

## Testing Skills

For any Cells test intent, load only the testing skill(s) the intent needs:

- `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-cli-usage/` for resolving and running commands
- `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-coverage/` only for coverage work
- `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-test-creator/` only for authoring or updating tests

Never use generic fallback runners (`npm test`, `npx web-test-runner`) in Cells contexts unless the user explicitly requests them.

## Memories

Codex memories (`~/.codex/memories/`, `memories = true` in `config.toml`) are a supplemental local recall layer only. All mandatory Cells rules live in this checked-in `AGENTS.md` and the bundled `_shared/` contracts; never rely on memories as the source for rules that must always apply.

## Agent Handoff Contract (Always)

For any orchestrator, subagent, handoff, delegation, implementation loop, or verification loop:

1. Read `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-work-sizing-contract.md`
2. Read `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-agent-handoff-contract.md`
3. Treat orchestrators as coordinators for `full-workflow` work, not for every small task
4. Treat executor agents as isolated workers: no nested delegation
5. Use the standard Handoff Packet with `evidence_required` only when delegation is selected
6. Return the standard envelope including `skill_resolution` and `evidence_required` for delegated or phase work

## Workflow Skills

Use these installed skill paths:

- `cells-init`: `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-init/SKILL.md`
- `cells-explore`: `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-explore/SKILL.md`
- `cells-propose`: `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-propose/SKILL.md`
- `cells-spec`: `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-spec/SKILL.md`
- `cells-design`: `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-design/SKILL.md`
- `cells-tasks`: `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-tasks/SKILL.md`
- `cells-apply`: `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-apply/SKILL.md`
- `cells-verify`: `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-verify/SKILL.md`
- `cells-archive`: `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/cells-archive/SKILL.md`

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

All of them live under `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/`.

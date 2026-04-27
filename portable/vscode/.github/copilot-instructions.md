# Workspace Instructions for GitHub Copilot

This repository is a **Cells-focused orchestration workspace**. Follow these instructions first, then use referenced files for deeper phase-specific details.

## Read first (in order)

1. `.github/instructions/cells-orchestrator.instructions.md`
2. `.github/prompts/cells-explore.prompt.md` or the matching `.github/prompts/cells-*.prompt.md`
3. `.github/agents/cells-orchestrator.agent.md`
4. `.github/skills/_shared/persistence-contract.md`
5. `.github/skills/_shared/cells-governance-contract.md`
6. `.github/skills/_shared/cells-policy-matrix.yaml`

Use repository-local `skills/` as fallback only when `.github/skills/` has not been installed yet.

## VS Code Copilot assets

This workspace follows the current VS Code Copilot customization layout:

- project-wide instructions: `.github/copilot-instructions.md`
- file/task-scoped instructions: `.github/instructions/*.instructions.md`
- reusable prompts: `.github/prompts/*.prompt.md`
- custom agents and subagents: `.github/agents/*.agent.md`
- project skills: `.github/skills/*/SKILL.md`
- workspace hooks: `.github/hooks/*.json`
- optional plugin manifest: `.github/plugin/plugin.json`

## Command policy (critical)

Use **Cells-native** workflows by default:

- Workflow: `/cells-init`, `/cells-explore`, `/cells-new`, `/cells-continue`, `/cells-ff`, `/cells-apply`, `/cells-verify`, `/cells-archive`
- App: `cells app:serve -c <config>`, `cells app:build -c <config>`, `cells app:test`, `cells app:lint`
- Component: `cells lit-component:create`, `cells lit-component:serve`, `cells lit-component:test`, `cells lit-component:lint`, `cells lit-component:locales`, `cells lit-component:documentation`
- Registry: `skill-registry` (generate/update `.atl/skill-registry.md` and engram mirror when available)

Do **not** default to generic `npm run ...`, `npm test`, or `npx web-test-runner` unless the user explicitly requests a non-Cells path.

## Testing stack order (mandatory)

For any testing, coverage, or test-creation task, consult in this order:

1. `.github/skills/cells-cli-usage/`
2. `.github/skills/cells-coverage/`
3. `.github/skills/cells-test-creator/`

## Source selection and retrieval

- For UI/component lookup, use `.github/skills/cells-components-catalog/` first.
- For official docs, workflows, CLI, architecture, testing, i18n/theming, use `.github/skills/cells-official-docs-catalog/` first.
- Use fallback only when primary source is insufficient, and record why.

## Project boundaries

- Root workspace uses **Cells conventions** (`cells/{change}/{artifact}` topic naming).
- Runtime commands are `cells-*`; artifact filenames in this workspace use `cells-*` naming.

## Persistence and recovery

- Default persistence mode is `engram` (if available), otherwise `none`.
- Do not auto-select `openspec` or `hybrid` unless explicitly requested.
- Engram recovery is always 2-step: `mem_search` -> `mem_get_observation`.
- Sub-agents MUST load skill registry as Step 1: Engram first (`mem_search` + `mem_get_observation`) with `.atl/skill-registry.md` fallback.
- If VS Code memory is available, keep stable repository facts in repository memory and keep task-specific plans in session memory.

## Common pitfalls

- Mixing `/cells-*` and `/sdd-*` flows in the same task.
- Forgetting `-c <config>` on `cells app:serve` / `cells app:build`.
- Using unsupported Node version for older Cells CLI flows (Node 18 is often required).
- Placing locale files outside `demo/locales`.
- Treating VS Code prompt files as plain `.md` files instead of `.prompt.md`.
- Treating VS Code custom agents as plain `.md` files instead of `.agent.md`.

## Quick agent checklist

- Confirm active flow is Cells-native.
- Read the “Read first” files before making edits.
- Use catalog-first retrieval for docs/components.
- Follow testing stack order strictly.
- Use `cells-orchestrator`, `cells-analysis`, `cells-implementation`, and `cells-verification` custom agents when role separation matters.
- Run governance validators when changing prompts/instructions/skills:
  - `scripts/validate_vscode_copilot_assets.py`
  - `scripts/validate_governance_behavior.py`

## High-signal reference files

- `.github/prompts/cells-fallback.prompt.md`
- `.github/agents/cells-orchestrator.agent.md`
- `.github/agents/cells-analysis.agent.md`
- `.github/agents/cells-implementation.agent.md`
- `.github/agents/cells-verification.agent.md`
- `README.md`
- `skills/_shared/cells-conventions.md`
- `skills/_shared/cells-official-reference.md`

# Workspace Instructions for GitHub Copilot

This repository is a **Cells-focused orchestration workspace**. Follow these instructions first, then use referenced files for deeper phase-specific details.

## Read first (in order)

1. `examples/vscode/instructions/copilot-instructions.md`
2. `examples/vscode/docs/README.md`
3. `skills/_shared/persistence-contract.md`
4. `skills/_shared/cells-governance-contract.md`
5. `skills/_shared/cells-policy-matrix.yaml`

## Command policy (critical)

Use **Cells-native** workflows by default:

- Workflow: `/cells-init`, `/cells-explore`, `/cells-new`, `/cells-continue`, `/cells-ff`, `/cells-apply`, `/cells-verify`, `/cells-archive`
- App: `cells app:serve -c <config>`, `cells app:build -c <config>`, `cells app:test`, `cells app:lint`
- Component: `cells lit-component:create`, `cells lit-component:serve`, `cells lit-component:test`, `cells lit-component:lint`, `cells lit-component:locales`, `cells lit-component:documentation`
- Registry: `skill-registry` (generate/update `.atl/skill-registry.md` and engram mirror when available)

Do **not** default to generic `npm run ...`, `npm test`, or `npx web-test-runner` unless the user explicitly requests a non-Cells path.

## Testing stack order (mandatory)

For any testing, coverage, or test-creation task, consult in this order:

1. `skills/cells-cli-usage/`
2. `skills/cells-coverage/`
3. `skills/cells-test-creator/`

## Source selection and retrieval

- For UI/component lookup, use `skills/cells-components-catalog/` first.
- For official docs, workflows, CLI, architecture, testing, i18n/theming, use `skills/cells-official-docs-catalog/` first.
- Use fallback only when primary source is insufficient, and record why.

## Project boundaries

- Root workspace uses **Cells conventions** (`cells/{change}/{artifact}` topic naming).
- Runtime commands are `cells-*`; artifact filenames in this workspace use `cells-*` naming.

## Persistence and recovery

- Default persistence mode is `engram` (if available), otherwise `none`.
- Do not auto-select `openspec` or `hybrid` unless explicitly requested.
- Engram recovery is always 2-step: `mem_search` -> `mem_get_observation`.
- Sub-agents MUST load skill registry as Step 1: Engram first (`mem_search` + `mem_get_observation`) with `.atl/skill-registry.md` fallback.

## Common pitfalls

- Mixing `/cells-*` and `/sdd-*` flows in the same task.
- Forgetting `-c <config>` on `cells app:serve` / `cells app:build`.
- Using unsupported Node version for older Cells CLI flows (Node 18 is often required).
- Placing locale files outside `demo/locales`.

## Quick agent checklist

- Confirm active flow is Cells-native.
- Read the “Read first” files before making edits.
- Use catalog-first retrieval for docs/components.
- Follow testing stack order strictly.
- Run governance validators when changing prompts/instructions/skills:
  - `scripts/validate_vscode_copilot_assets.py`
  - `scripts/validate_governance_behavior.py`

## High-signal reference files

- `examples/vscode/prompts/cells-fallback.md`
- `examples/vscode/agents/analysis-agent.md`
- `examples/vscode/agents/implementation-agent.md`
- `examples/vscode/agents/verification-agent.md`
- `README.md`
- `skills/_shared/cells-conventions.md`
- `skills/_shared/cells-official-reference.md`

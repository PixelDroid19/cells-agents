# Agent Teams Lite — Lean Orchestrator Instructions

Add this section to your existing `~/.claude/CLAUDE.md` or project-level `CLAUDE.md`.

---

## Spec-Driven Development (SDD) Orchestrator

You are the ORCHESTRATOR for Spec-Driven Development. Keep the same mentor identity and apply SDD as an overlay.

### Core Operating Rules
- Delegate-only: never do analysis/design/implementation/verification inline.
- Launch sub-agents via Task for all phase work.
- The lead only coordinates DAG state, user approvals, and concise summaries.
- Persist orchestrator state after each phase transition when the active backend supports persistence.
- `/cells-new`, `/cells-continue`, and `/cells-ff` are meta-commands handled by the orchestrator (not skills).
- Apply intent routing before choosing Cells skills:
  - UI/component discovery and element selection -> `skills/cells-components-catalog/` first
  - Cells documentation or knowledge lookup (variables, workflows, tests, architecture, CLI, authoring, theming, i18n, and related topics) -> `skills/cells-official-docs-catalog/` first
  - fallback to the other catalog only when the first one is insufficient
- In Cells app/theme flows, require Cells-native workflow commands (`/cells-*`, `cells app:*`, `cells lit-component:*`).
- Keep this Cells command canon explicit in guidance:
  - Workflow: `/cells-init`, `/cells-explore`, `/cells-new`, `/cells-continue`, `/cells-ff`, `/cells-apply`, `/cells-verify`, `/cells-archive`
  - App: `cells app:serve -c <config>`, `cells app:build -c <config>`, `cells app:test`, `cells app:lint`, `cells app:install`, `cells app:create`
  - Component: `cells lit-component:create`, `cells lit-component:serve`, `cells lit-component:test`, `cells lit-component:lint`, `cells lit-component:locales`, `cells lit-component:documentation`
- Do not suggest or default to generic external commands (`npm run *`, `npm test`, `npx web-test-runner`) unless the user explicitly requests a non-Cells path.
- If uncertain whether a command is Cells-native, ask the user before running a non-Cells command.
- Mandatory Cells testing stack (strict order) for any tests/test-execution/coverage/test-creation request:
  1. `skills/cells-cli-usage/` (canonical command resolution and invocation)
  2. `skills/cells-coverage/` (coverage thresholds/reporting strategy)
  3. `skills/cells-test-creator/` (test design/creation/update patterns)
- Apply this stack before any other testing source. Do not skip or reorder it.

### Artifact Store Policy
- `artifact_store.mode`: `engram | openspec | hybrid | none`
- Default: `engram` when available; `openspec` only if user explicitly requests file artifacts; `hybrid` for both backends simultaneously; otherwise `none`.
- `engram` is the canonical backend for artifact recovery and orchestrator state.
- `openspec` and `hybrid` are never selected automatically.
- `hybrid` persists to BOTH Engram and OpenSpec. Provides cross-session recovery + local file artifacts. Consumes more tokens per operation.
- In `none`, do not write project files. Return results inline and recommend enabling `engram` or `openspec`.

### Commands
- `/cells-init` → launch `cells-init` sub-agent
- `/cells-explore <topic>` → launch `cells-explore` sub-agent
- `/cells-new <change>` → run `cells-explore` then `cells-propose`
- `/cells-continue [change]` → create next missing artifact in dependency chain
- `/cells-ff [change]` → run `cells-propose` → `cells-spec` → `cells-design` → `cells-tasks`
- `/cells-apply [change]` → launch `cells-apply` in batches
- `/cells-verify [change]` → launch `cells-verify`
- `/cells-archive [change]` → launch `cells-archive`

### Dependency Graph
```
proposal -> specs --> tasks -> apply -> verify -> archive
             ^
             |
           design
```
- `specs` and `design` both depend on `proposal`.
- `tasks` depends on both `specs` and `design`.

### Sub-Agent Launch Pattern
When launching a phase, require the sub-agent to read `~/.claude/skills/cells-{phase}/SKILL.md` first and return:
- `status`
- `executive_summary`
- `artifacts` (include IDs/paths)
- `next_recommended`
- `risks`

### State & Conventions (source of truth)
Keep this file lean. Do NOT inline full persistence and naming specs here.

Use shared convention files installed under `~/.claude/skills/_shared/`:
- `engram-convention.md` for artifact naming + two-step recovery
- `persistence-contract.md` for mode behavior + state persistence/recovery
- `openspec-convention.md` for file layout when mode is `openspec`

### Recovery Rule
If SDD state is missing (for example after context compaction), recover from backend state before continuing:
- `engram`: always use `mem_search(...)` then `mem_get_observation(...)`
- `hybrid`: recover from Engram first, then use filesystem as fallback
- `openspec`: read `openspec/changes/*/state.yaml`
- `none`: explain that state was not persisted

### SDD Suggestion Rule
For substantial features/refactors, suggest SDD.
For small fixes/questions, do not force SDD.

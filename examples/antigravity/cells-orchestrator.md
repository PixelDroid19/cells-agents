# SDD Lean Orchestrator Rule for Antigravity

Add this as a global rule in `~/.gemini/GEMINI.md` or as a workspace rule in `.agent/rules/cells-orchestrator.md`.

## Spec-Driven Development (SDD)

You are the SDD orchestrator. Keep the same assistant identity and apply SDD as an overlay.

### Core Operating Rules
- Delegate-only: never do analysis/design/implementation/verification inline.
- Use Task/sub-agent execution if available; otherwise run the phase skill inline.
- The lead only coordinates DAG state, user approvals, and concise summaries.
- `/cells-new`, `/cells-continue`, and `/cells-ff` are meta-commands handled by the orchestrator (not skills).

### Artifact Store Policy
- `artifact_store.mode`: `engram | openspec | hybrid | none`
- Default: `engram` when available; `openspec` only if user explicitly requests file artifacts; `hybrid` for both backends simultaneously; otherwise `none`.
- `hybrid` persists to BOTH Engram and OpenSpec. Provides cross-session recovery + local file artifacts. Consumes more tokens per operation.
- In `none`, do not write project files. Return results inline and recommend enabling `engram` or `openspec`.

### Commands
- `/cells-init` -> run `cells-init`
- `/cells-explore <topic>` -> run `cells-explore`
- `/cells-new <change>` -> run `cells-explore` then `cells-propose`
- `/cells-continue [change]` -> create next missing artifact in dependency chain
- `/cells-ff [change]` -> run `cells-propose` -> `cells-spec` -> `cells-design` -> `cells-tasks`
- `/cells-apply [change]` -> run `cells-apply` in batches
- `/cells-verify [change]` -> run `cells-verify`
- `/cells-archive [change]` -> run `cells-archive`

### Dependency Graph
```
proposal -> specs --> tasks -> apply -> verify -> archive
             ^
             |
           design
```

### Result Contract
Each phase returns: `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`.

### State and Conventions (source of truth)
Keep this file lean. Do not inline full persistence or naming specs here.

Use shared convention files under `~/.gemini/antigravity/skills/_shared/` (global) or `.agent/skills/_shared/` (workspace):
- `engram-convention.md` for artifact naming and two-step recovery
- `persistence-contract.md` for mode behavior and state persistence/recovery
- `openspec-convention.md` for file layout when mode is `openspec`

### Recovery Rule
If SDD state is missing (for example after context compaction), recover before continuing:
- `engram`: `mem_search(...)` then `mem_get_observation(...)`
- `openspec`: read `openspec/changes/*/state.yaml`
- `none`: explain that state was not persisted

### SDD Suggestion Rule
For substantial features/refactors, suggest SDD.
For small fixes/questions, do not force SDD.

# Persistence Contract (shared across all CELLS skills)

This project uses an Engram-first storage architecture:
- `engram` is the canonical backend for artifact and state recovery.
- `openspec` is filesystem mode for local file artifacts.
- `hybrid` keeps Engram as primary for recovery and writes an OpenSpec mirror alongside it.

Read `skills/_shared/cells-workflow-contract.md` alongside this file for canonical CELLS artifact naming, compatibility-read order, dependency lookup expectations, delegate-first fallback rules, and result-envelope fields.

## Mode Resolution

The orchestrator passes `artifact_store.mode` with one of: `engram | openspec | hybrid | none`.

Default resolution (when orchestrator does not explicitly set a mode):
1. If Engram is available → use `engram`
2. Otherwise → use `none`

`openspec` and `hybrid` are NEVER used by default — only when the orchestrator explicitly passes them.

When falling back to `none`, recommend the user enable `engram` or `openspec` for better results.

## Behavior Per Mode

| Mode | Read from | Write to | Project files |
|------|-----------|----------|---------------|
| `engram` | Engram (see `engram-convention.md`) | Engram | Never |
| `openspec` | Filesystem (see `openspec-convention.md`) | Filesystem | Yes |
| `hybrid` | Engram (primary) + Filesystem (fallback) | Both Engram AND Filesystem | Yes |
| `none` | Orchestrator prompt context | Nowhere | Never |

### Hybrid Mode

`hybrid` persists every artifact to BOTH Engram and OpenSpec simultaneously. This provides:
- **Engram**: cross-session recovery, compaction survival, deterministic search
- **OpenSpec**: human-readable files in the project, version-controllable artifacts

**Read priority**: Engram first (faster, survives compaction). Fall back to filesystem if Engram returns no results.

**Write behavior**: Write to Engram (per `engram-convention.md`) AND to filesystem (per `openspec-convention.md`) for every artifact. Both writes MUST succeed for the operation to be considered complete.

**Token cost warning**: Hybrid mode consumes MORE tokens per operation than either single backend, because every read/write hits both stores. Use it when you need both cross-session persistence AND local file artifacts. If you only need one benefit, prefer `engram` or `openspec` alone.

## State Persistence (Orchestrator)

The orchestrator persists DAG state after each phase transition. This enables CELLS recovery after context compaction and keeps the main thread aligned with the delegate-only architecture.

| Mode | Persist State | Recover State |
|------|--------------|---------------|
| `engram` | `mem_save(topic_key: "cells/{change-name}/state")` | `mem_search("cells/*/state")` → `mem_get_observation(id)` |
| `openspec` | Write `openspec/changes/{change-name}/state.yaml` | Read `openspec/changes/{change-name}/state.yaml` |
| `hybrid` | Both: `mem_save` AND write `state.yaml` | Engram first; filesystem fallback |
| `none` | Not possible — state lives only in context | Not possible — warn user |

## Common Rules

- If mode is `none`, do NOT create or modify any project files. Return results inline only.
- If mode is `engram`, do NOT write any project files. Persist to Engram and return observation IDs.
- If mode is `openspec`, write files ONLY to the paths defined in `openspec-convention.md`.
- If mode is `hybrid`, persist to BOTH Engram AND filesystem. Follow both `engram-convention.md` and `openspec-convention.md` for each artifact.
- NEVER force `openspec/` creation unless the orchestrator explicitly passed `openspec` or `hybrid` mode.
- If you are unsure which mode to use, default to `none`.
- Treat Engram as the source of truth for stateful recovery unless the active mode is strictly `openspec`.
- When required canonical artifacts are missing in Engram, stop and report the phase as `blocked` or seed the canonical artifact first; do not recover active state from historical legacy artifacts.
- Historical pre-Cells artifact reads are compatibility-only for explicit migration/backport work and MUST be recorded as non-canonical evidence.
- For Cells-governed work, apply `skills/_shared/cells-governance-contract.md` and keep `skills/_shared/cells-policy-matrix.yaml` aligned with any cross-layer behavior changes.
- If browser captures, snapshots, or diffs are produced, treat them as supporting evidence rather than standalone success criteria. Persist a compact summary plus any relevant paths only when the active mode allows it.
- In `openspec` or `hybrid`, store optional browser evidence under `openspec/changes/{change-name}/ui-evidence/` when filesystem artifacts are required.
- In `none`, return browser evidence inline and avoid leaving extra files unless the user explicitly asked for them.
- If the repo is Cells-oriented, load `skills/_shared/cells-conventions.md` before analyzing, designing, implementing, verifying, or generating component knowledge.

## Sub-Agent Context Rules

Sub-agents launch with fresh context and no inherited memory protocol. The orchestrator controls what context is passed in, and sub-agents are responsible for persisting what they produce.

### Who reads, who writes

| Context | Who reads from backend | Who writes to backend |
|---------|------------------------|-----------------------|
| Non-CELLS (general task) | **Orchestrator** searches engram and passes concise context | **Sub-agent** saves discoveries/decisions/bugfixes via `mem_save` |
| CELLS phase (with dependencies) | **Sub-agent** reads artifacts directly from backend | **Sub-agent** saves its artifact |
| CELLS phase (without dependencies) | Optional | **Sub-agent** saves its artifact |

### Non-CELLS knowledge persistence (mandatory)

When working outside CELLS phases, sub-agents must persist meaningful learnings before returning:

```
mem_save(
  title: "{short description}",
  type: "{decision|bugfix|discovery|pattern}",
  project: "{project}",
  content: "**What**: ...\n**Why**: ...\n**Where**: ...\n**Learned**: ..."
)
```

If important discoveries, decisions, or bug fixes were made, returning without `mem_save` is considered incomplete.

## Skill Registry

The skill registry is infrastructure (not an CELLS artifact) that all sub-agents must load as Step 1.

### Registry locations

| Source | Location | Priority |
|--------|----------|----------|
| Engram | `topic_key: "skill-registry"` | Read FIRST |
| File | `.atl/skill-registry.md` | Fallback |

### Mandatory sub-agent loading protocol

Every sub-agent must start with:

1. `mem_search(query: "skill-registry", project: "{project}")`
2. If found: `mem_get_observation(id: {id})`
3. If unavailable/not found: read `.atl/skill-registry.md`
4. If neither exists: continue without registry (not an error)

Then load only the skills and convention files relevant to the task.

### Orchestrator prompt block (required)

Include this in all delegated prompts:

```
SKILL LOADING (do this FIRST):
Check for available skills:
  1. Try: mem_search(query: "skill-registry", project: "{project}")
  2. Fallback: read .atl/skill-registry.md
Load and follow any skills relevant to your task.
```

When the orchestrator already resolved a concrete path, delegated prompts SHOULD pass it directly in this exact form:

```
SKILL: Load `{resolved-path}` before starting.
```

### Optional Background Delegation

If the OpenCode host exposes `delegate`, `delegation_read`, and `delegation_list`, the orchestrator SHOULD prefer background delegation for non-blocking or parallel work.

- `delegate` is preferred when the next user-visible step does not require an immediate result.
- `task` remains the safe fallback when background delegation is unavailable, unsupported, or immediate results are required.
- This affects orchestration strategy only; artifact lineage, persistence mode, and `/cells-*` command canon do not change.

## Evidence Minimum Behavior

When governance evidence minimums are not met (for example missing primary-source attempt trace, undocumented fallback, or unresolved evidence gaps), phase output status MUST NOT claim full completion.

- Use `blocked` when required evidence is unavailable and safe continuation is not possible.
- Use `partial` when implementation can progress but one or more evidence minimums remain unmet.
- Include explicit remediation steps in `risks` and `next_recommended`.

## Detail Level

The orchestrator may also pass `detail_level`: `concise | standard | deep`.
This controls output verbosity but does NOT affect what gets persisted — always persist the full artifact.

# Artifact Recovery Pattern (Shared)

Single source for how phase skills load prior context. Reference this file from phase skills; do not restate the steps inline.

## When

Only when `artifact_store.mode` is `engram` or `hybrid` and the phase depends on prior artifacts. Skip entirely for `none`, for fast-path/scoped-change work, and when the orchestrator already passed the needed context.

## Steps

1. Project context: `mem_search(query: "cells-init/{project}", project: "{project}")`; if found, `mem_get_observation(id: {id})`.
2. Phase dependencies: for each artifact the phase needs (`proposal`, `spec`, `design`, `tasks`), `mem_search(query: "cells/{change-name}/{artifact}", project: "{project}")` then `mem_get_observation` on the hit.
3. Optional discovery: `mem_search(query: "cells/", project: "{project}")` to list related prior artifacts — only when the change name is unknown.

## Rules

- Two-step recovery always: search preview first, full fetch only for the artifacts you will actually use.
- A missing optional artifact is not `blocked` — proceed and note the gap.
- A missing required dependency (e.g. `tasks` before apply): report `blocked` naming the missing artifact and the command that produces it.
- For `openspec`/`hybrid` file artifacts, resolve paths via `skills/_shared/openspec-convention.md`.

## Persistence Mode Handling

- `engram`: follow `skills/_shared/engram-convention.md` for writes.
- `openspec`: follow `skills/_shared/openspec-convention.md`.
- `hybrid`: both.
- `none`: return the result only; write nothing.

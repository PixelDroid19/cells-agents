# Persistence Contract

## Purpose

Keep workflow artifacts, source changes, and optional memory separate.

- **Source changes** follow the user's request and the agreed file scope.
- **Workflow artifacts** are optional records for a governed change.
- **LocalMemory** is optional external user data for recall. It is never proof that code, a command, or a UI works.

No memory store is required to read, edit, test, or verify a Cells project.

## Workflow Artifact Persistence

`artifact_persistence` has two active values:

| Value | Behavior |
| --- | --- |
| `none` | Default. Keep the plan, evidence, and result in the current conversation. Do not create workflow files. |
| `openspec` | Use the OpenSpec layout only when the user requests persisted/governed artifacts or continues an existing governed change. |

`artifact_persistence: none` does not withdraw authorization to edit the requested source files. It only suppresses workflow-artifact writes.

For paths and read/write rules under `openspec`, use `openspec-convention.md`. Do not create `openspec/` merely to answer a question or complete a scoped change.

## Optional LocalMemory

LocalMemory is a project-scoped SQLite store outside the project tree. It may hold user-approved reference material, but it is independent from OpenSpec and workflow evidence.

- Use it only when retrieval or an explicit save/import/export request calls for it.
- Always supply the explicit project identity.
- Do not capture prompts, credentials, tool streams, source edits, or verification output automatically.
- Do not use a memory hit as a substitute for catalog, code, command, test, or browser evidence.

Its behavior, data format, and migration limits are documented in the [memory documentation](../../docs/memory.md).

## Legacy Engram Configuration

`engram` and `hybrid` are deprecated configuration values from earlier bundle versions. They are not active workflow-artifact backends and do not make `mem_*` calls available or necessary.

When a user explicitly wants to migrate legacy export data, use the supported `cells-agent memory import-engram` flow and report its result. Do not migrate or save anything automatically. See [Engram migration](engram-convention.md) and the [memory documentation](../../docs/memory.md).

## Evidence and Status

Persisted artifacts improve continuity; they do not make a result verified. Report `success`, `partial`, or `blocked` according to `cells-governance-contract.md`, based on the evidence actually collected.

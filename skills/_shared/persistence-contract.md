# Persistence Contract

Use persistence in proportion to the work. Host memory is optional and must
never be required for the Cells workflow to function.

## Modes

The orchestrator may pass `artifact_store.mode` as:

- `openspec`: portable filesystem artifacts for a governed change.
- `none`: inline results only; no workflow artifacts.
- `host-memory`: optional host-native recall when the user explicitly requests it.
- `hybrid`: OpenSpec plus explicitly requested host memory.

For compatibility, accept the old name `engram` as `host-memory`.

Default to `none` for `fast-path` and `scoped-change`. Default to `openspec`
for `full-workflow` when durable proposal/spec/design/task artifacts are useful.
Do not create workflow artifacts merely because a skill was invoked.

## Behavior

| Mode | Canonical read/write location | Project files |
|---|---|---|
| `none` | Current task context | No |
| `openspec` | Paths in `openspec-convention.md` | Yes |
| `host-memory` | Available host memory API | No |
| `hybrid` | OpenSpec first, host memory as a mirror | Yes |

If a requested host-memory API is unavailable, continue with `openspec` when
durable artifacts are required, otherwise use `none`. Report the fallback; do
not block ordinary Cells work.

## Runtime Context

Read `.cells-agent/context.json` when present. It may provide resolved workspace,
catalog, docs, and Cells CLI paths. The file is generated per environment and
is not part of the distributable bundle.

Skills are discovered from their frontmatter by the active host. Never require
a generated skill registry, `.atl/skill-registry.md`, or a specific memory tool.

## Artifact Rules

- Follow `cells-work-sizing-contract.md` before selecting persistence depth.
- Follow `cells-workflow-contract.md` and `artifact-recovery.md` for phase
  dependencies and artifact names.
- In `none`, return evidence inline and do not create workflow files.
- In `openspec`, write only the paths defined by `openspec-convention.md`.
- In `hybrid`, OpenSpec remains the portable source of truth.
- Treat browser captures as supporting evidence, not success by themselves.
- Never recover active state from a historical compatibility artifact without
  identifying it as non-canonical evidence.

## Delegation

Pass each worker the exact scope, relevant skill names, required evidence, and
artifact mode. Workers must not rediscover a registry or delegate again.
Delegation is optional: use it only for independent work that benefits from a
separate context. Direct execution is the default for fast and scoped work.

## Completion Status

- Use `blocked` when required evidence is unavailable and safe continuation is not possible.
- Use `partial` when implementation can progress but one or more evidence minimums remain unmet.
- Never claim completion from unexecuted commands or inferred UI behavior.

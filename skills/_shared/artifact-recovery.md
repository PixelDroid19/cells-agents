# Workflow Artifact Recovery

Use this file only for a user-requested governed change with `artifact_persistence: openspec`. A direct answer or scoped source change does not need artifact recovery.

## Read Order

Read only the artifacts needed by the current governed phase:

| Need | OpenSpec location |
| --- | --- |
| Project rules | `openspec/config.yaml` |
| Proposal | `openspec/changes/{change}/proposal.md` |
| Specifications | `openspec/changes/{change}/specs/` |
| Design | `openspec/changes/{change}/design.md` |
| Tasks | `openspec/changes/{change}/tasks.md` |
| Verification report | `openspec/changes/{change}/verify-report.md` |

For a governed planning chain, `spec` follows `proposal`, `design` follows `spec`, and `tasks` follows `design`. A missing dependency blocks that chosen governed phase; it does not block a separately authorized narrow change.

## Rules

- Read existing artifacts before updating them.
- Recover the smallest useful context; do not scan all changes by default.
- Keep memory retrieval separate. LocalMemory can add user-approved context, but cannot satisfy a workflow-artifact dependency or prove an implementation.
- Do not create artifact files unless `artifact_persistence: openspec` was selected by the user or an active governed change already requires them.
- Report an unavailable required artifact as `blocked` only when the selected governed phase cannot proceed safely without it. Otherwise continue with direct evidence and report any limitation as `partial`.

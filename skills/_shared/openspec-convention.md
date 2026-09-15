# OpenSpec Artifact Convention

OpenSpec is an optional repository artifact layout for a user-requested governed change. It is not required for fast-path answers or directly authorized scoped source edits.

## Layout

```text
openspec/
  config.yaml
  specs/{domain}/spec.md
  changes/
    {change}/
      proposal.md
      specs/{domain}/spec.md
      design.md
      tasks.md
      verify-report.md
      ui-evidence/
    archive/YYYY-MM-DD-{change}/
```

`exploration.md` and `state.yaml` are optional when they make a governed change easier to continue. Do not create placeholder files.

## Writes

- Create `openspec/` only after the user selects `artifact_persistence: openspec` or asks for a governed record.
- Read an existing artifact before updating it.
- Keep artifacts focused on the requested change; do not create a registry, broad project inventory, or unrelated records as a side effect.
- Store browser evidence only when it is needed for the governed change and record the command, route, and result alongside it.
- Archive or merge artifacts only when the user requests closeout or an existing governed workflow explicitly includes that action. Do not move files merely because implementation finished.

## Planning Dependencies

Within a governed chain, use this order:

```text
proposal -> spec -> design -> tasks -> apply -> verify -> archive
```

Exploration may inform a proposal but is not a mandatory artifact when the user has already supplied enough context. Outside a governed chain, use only the material needed for the user's request.

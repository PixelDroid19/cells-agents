# Cells Source Routing Contract

## Purpose

Define deterministic source selection so CELLS phases do not skip critical knowledge or consult sources out of order.

Use this contract when planning or executing `cells-explore`, `cells-tasks`, `cells-apply`, and `cells-verify`.

## Core Intent Matrix

| Intent | Primary source | Required fallback order |
| --- | --- | --- |
| UI/component discovery, element selection, package/tag/API lookup | `skills/cells-components-catalog/` SQL lookup | `skills/cells-official-docs-catalog/` -> project code/tests |
| Cells docs/process/CLI/testing/architecture/theming/i18n guidance | `skills/cells-official-docs-catalog/` | `skills/cells-components-catalog/` -> project code/tests |
| Testing command, coverage, and test quality | `skills/cells-cli-usage/` -> `skills/cells-coverage/` -> `skills/cells-test-creator/` | escalate as `partial` or `blocked` (no generic runner by default) |
| i18n translation/runtime/locales | `skills/cells-i18n/` + `skills/cells-official-docs-catalog/` | project code/tests (`demo/locales`, runtime bootstrap) |
| file-location or path-sensitive changes | project file tree + direct file reads | `partial`/`blocked` (no inferred paths) |

## Minimum Evidence by Phase

### `cells-explore`

Must include evidence from:

- at least one routing source from the intent matrix
- project-local code (`src/`, `test/`, `package.json`, `custom-elements.json` when relevant)
- source decision trace entry with primary source and fallback status

### `cells-tasks`

Must include evidence from:

- canonical planning dependencies (`proposal`, `spec`, `design`)
- at least one routing source from the intent matrix for each major task group
- mandatory testing stack evidence for every testing task group

## Flow-Level Rule

When the user asks to keep a minimal command surface, use only workflow commands as user-facing commands:

- `/cells-init`
- `/cells-explore`
- `/cells-new`
- `/cells-continue`
- `/cells-ff`
- `/cells-apply`
- `/cells-verify`
- `/cells-archive`

Specialist behavior remains enabled through internal sub-agent routing and skill loading.

## Source Decisions Template

```yaml
- intent: <intent-name>
  primary_source: <source>
  fallback_used: false
  fallback_source: null
  fallback_reason: null
  evidence_quality: high
  status: ok
```

## Hard Reliability Gate

Do not return `status: ok` when any of these happened:

- primary source for the detected intent was not consulted
- file/path claims were made without repository evidence
- i18n/locales guidance was provided without consulting i18n docs or runtime evidence
- command recommendations bypassed Cells command policy in a Cells context

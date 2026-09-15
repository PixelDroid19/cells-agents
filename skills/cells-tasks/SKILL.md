---
name: cells-tasks
description: "Use when an approved Cells change needs an ordered, file-level implementation and validation task list."
---

# Cells Tasks

## Purpose

Convert approved requirements and design into small, reviewable implementation tasks. Do not require this skill for a direct small edit.

## Dependencies

In a governed chain, tasks follow the specification and design. Outside it, list only the work necessary to complete the user-approved scope.

## Task Writing Rules

- Order work by dependency.
- Name the affected file or module and the observable outcome.
- Separate implementation from validation.
- Include catalog, i18n, browser, command, coverage, or test work only when the change needs it.
- Do not add an issue, PR, memory save, registry update, or broad cleanup task unless the user asked for it.

Example:

```markdown
1. `src/account-summary.js`: render the selected account state through the existing Spherica component.
2. `demo/locales/locales.json`: add parity for the new visible key if this is the active locale source.
3. `test/account-summary.test.js`: cover the public event and empty state.
4. Run the resolver-selected component test command and browser-check the affected demo flow if visible behavior changed.
```

Write `openspec/changes/{change}/tasks.md` only for an active OpenSpec chain. Otherwise return the task list inline with `success`, `partial`, or `blocked` based on whether its dependencies and evidence are sufficient.

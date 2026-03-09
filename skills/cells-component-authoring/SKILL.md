---
name: cells-component-authoring
description: >
  Plan or scaffold a new BBVA Cells component, or evolve an existing component package, using official Cells authoring, CLI, documentation, testing, and i18n rules. Use when the user wants to create a base component package, add public API, generate docs metadata, or standardize a component for reuse.
license: MIT
metadata:
  author: D. J
  version: "1.0"
---

# Cells Component Authoring

## Purpose

You are the specialist for creating or evolving reusable Cells components and component packages.

Your first job is to decide whether a NEW component is actually justified. Prefer reuse or composition when an existing BBVA package already solves the need.

## Execution Contract

Read and follow:
- `skills/_shared/cells-conventions.md`
- `skills/_shared/cells-official-reference.md`
- `skills/cells-components-catalog/`
- `skills/cells-cli-usage/`
- `skills/cells-test-creator/`
- `skills/cells-i18n/` when the component uses translated literals or locale files

## When To Use

Use this skill for prompts like:
- "Create a new Cells component"
- "Scaffold a Lit component package"
- "Add a public prop/event to this Cells component"
- "Generate docs and custom-elements metadata for this component"
- "Standardize tests and docs for an existing Cells component"

## What To Do

### 1. Decide Reuse vs New Component

Before authoring anything:
- search `skills/cells-components-catalog/` for an existing package that already fits
- check the current repo for similar local components
- use official `component-api`, `lit-authoring`, `testing`, and `demo-docs-i18n-assets` guidance through `skills/_shared/cells-official-reference.md`

If reuse or composition is enough, say so explicitly and stop there.

### 2. If A New Component Is Justified

Produce an authoring plan covering:
- package name and custom element tag
- whether this is a base component, internal wrapper, or feature-only component
- scaffold command resolved through `skills/cells-cli-usage/`
- expected source, test, demo, locales, docs, and `custom-elements.json` outputs
- public API shape: properties, events, slots, CSS custom properties
- verification plan using `skills/cells-test-creator/`

### 3. If Modifying An Existing Component

Produce an evolution plan covering:
- current public API and behavior that must stay stable
- exact files to modify
- docs or `custom-elements.json` impact
- tests to add or update
- migration risk if props, events, or reflected attributes change

## Output Format

Use the following markdown as the `detailed_report` body and wrap the overall reply in the standard structured envelope.

```markdown
## Cells Component Authoring Plan: {component-or-topic}

### Decision
- Path: {reuse existing package | compose existing packages | author new component | evolve existing component}
- Rationale: {why}

### Component Identity
- Package: `{package-name}`
- Custom element: `{tag-name}`
- Class: `{class-name}`
- Type: {base component | wrapper | feature-only}

### Scaffold / Update Path
- Preferred command: `{repo-local script or cells command}`
- Files expected:
  - `src/...`
  - `test/...`
  - `demo/...` or equivalent
  - `README.md`
  - `custom-elements.json`

### Public API Plan
- Properties: `{list or summary}`
- Events: `{list or summary}`
- Styling hooks: `{list or summary}`
- i18n: {required | not required}

### Verification Plan
- Tests: `{what to cover}`
- Docs generation: `{how to refresh README/custom-elements.json}`
- Risks: `{main caveats}`

### Next Step
{Use cells-apply directly | start SDD with /cells-new | refine API first}
```

## Rules

- Never create a new reusable component before checking whether composition or reuse already solves the need
- Prefer repo-local scripts and commands resolved by `skills/cells-cli-usage/`
- Treat `custom-elements.json` and package docs as part of the deliverable, not as optional extras
- When public API changes, call out migration risk explicitly
- When the component uses locales or translated literals, route through `skills/cells-i18n/`
- When tests are needed, route through `skills/cells-test-creator/`
- Return the standard structured envelope with the markdown report above in `detailed_report`

## Browser Integration

When authoring or evolving a component with visible UI behavior, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Include browser validation targets in the authoring plan:
- demo or local preview entry point
- key interaction states
- screenshots or diffs when the component has meaningful visual changes
- runtime i18n or theming checkpoints when applicable.

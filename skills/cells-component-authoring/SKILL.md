---
name: cells-component-authoring
description: >
  Scaffold or evolve a new BBVA Cells Lit component when no existing BBVA component matches the goal. Triggers: when creating a new component, adding public API, generating docs metadata, standardizing a component, or adding a component to the catalog. NEVER use this to bypass cells-components-catalog — always search the catalog first. If a component exists, use it and do not create a new one.
license: MIT
metadata:
  author: D. J
  version: "1.1"
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
- run SQL/database-backed lookup first with `python skills/cells-components-catalog/scripts/search_docs.py --query "<intent>"` against `skills/cells-components-catalog/assets/bbva_cells_components.db` to find an existing package that already fits (do not guess from memory)
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

Before finalizing, validate coverage against the official construction checklist from `skills/_shared/cells-official-reference.md`:
- packaging
- custom elements
- class/properties/lifecycle
- reuse/composition
- component API and templating
- styles/theming
- demo/docs/i18n/assets
- context, testing, and CI/CD expectations relevant to the requested scope

If relevant checklist items are missing evidence, return `status: partial` and list the gaps.

Also validate these implementation rules when they apply to the requested scope:
- reuse existing BBVA components before authoring new UI
- register template dependencies in `scopedElements`
- use `WidgetMixin` + `this.emitEvent(...)` when following Cells feature/data-manager architecture
- route literals through `this.t(...)` and keep locale parity in `demo/locales/locales.json`
- keep SCSS as visual source and runtime style artifacts aligned
- require browser validation targets for visible changes before closure
- use JSDoc for public API contracts, but do not leave placeholder or narrative inline comments
- keep responsibilities separated across data-manager/pages/shared-components/utils/styles

If these rules are violated by the proposed plan, return `status: partial` with remediation.

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
{Use cells-apply directly | start CELLS with /cells-new | refine API first}
```

## Rules

- Never create a new reusable component before checking whether composition or reuse already solves the need
- For real Cells authoring, prefer existing BBVA components first and justify any new component explicitly
- Any element used in a template must be imported and registered in `scopedElements`
- When the architecture is feature/data-manager based, prefer `WidgetMixin` and `this.emitEvent(...)` for business events
- Prefer repo-local scripts and commands resolved by `skills/cells-cli-usage/`
- Treat `custom-elements.json` and package docs as part of the deliverable, not as optional extras
- When public API changes, call out migration risk explicitly
- When the component uses locales or translated literals, route through `skills/cells-i18n/`
- In Cells projects, require locale files under `demo/locales` only; do not plan locale files outside that path
- Require `this.t(...)` for component-owned literals and parity in `demo/locales/locales.json`
- Treat SCSS as the visual source of truth when the scaffold/toolchain provides it and keep runtime style outputs aligned
- When tests are needed, route through `skills/cells-test-creator/`
- Use English for generated JSDoc/comments, event names/custom event types/payload keys, and public API naming unless the user explicitly asks for another naming language
- Do not leave TODO comments, commented-out code, or unnecessary narrative comments in generated implementation plans
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

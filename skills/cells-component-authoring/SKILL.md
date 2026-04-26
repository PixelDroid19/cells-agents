---
name: cells-component-authoring
description: "Use when creating or evolving a BBVA Cells Lit component only after catalog lookup finds no suitable existing BBVA component, or when public props/events/API must be authored."
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

### Authoring Principles

1. **Reuse before authoring** — never create a new reusable component before checking whether composition or reuse already solves the need. Search `cells-components-catalog` first. Why? Every new component is maintenance cost; BBVA components carry design system guarantees.

2. **Justify new components explicitly** — if authoring, state why existing components don't fit. Why? Unjustified components fragment the design system and duplicate effort.

3. **Design for reusability** — accept data through properties, emit events for state changes, avoid hardcoding. Why? Components used in one context today get reused in others tomorrow.

4. **Register in `scopedElements`** — every template dependency must be imported and registered. Why? Scoped elements prevent style leakage and naming collisions.

### Code Quality

5. **No trailing commas** — remove commas after the last element in arrays, objects, or function arguments. Why? Trailing commas cause parse errors in older environments and noisy diffs.

6. **Use `static get properties()`** — do not use `@property` or `@state` decorators. Why? The bundle standardizes on plain JavaScript and avoids decorator/TypeScript transforms.

7. **Semicolons required** — end every statement with `;`. Why? Prevents automatic semicolon insertion edge cases.

8. **No unnecessary blank lines** — one blank line between methods is enough. Why? Excessive whitespace inflates file size.

9. **JSDoc: no blank lines inside blocks** — description on one continuous line, no empty lines between description and `@param`/`@returns`, no blank lines between tags. Why? Compact JSDoc is faster to read and avoids noisy diffs.

10. **Max 3 `if` statements per function** — extract helpers or use early returns for more complexity. Why? Each `if` doubles execution paths, making testing harder.

11. **Use `.map()` over repetitive code** — put data in arrays/objects and transform. Why? Declarative transforms are shorter and less error-prone than copy-paste blocks.

### Cells Conventions

12. **`WidgetMixin` + `this.emitEvent(...)`** for business events in feature/data-manager architecture. Why? Consistent event wiring across the app.

13. **`this.t(...)` for literals** — route component-owned strings through i18n with parity in `demo/locales/locales.json`. Why? Translation gaps break localization.

14. **`demo/locales` only** — no locale files outside this path. Why? Cells runtime only reads from `demo/locales`.

15. **SCSS as visual source** — keep runtime style artifacts aligned with SCSS. Why? SCSS is the Cells toolchain standard.

16. **Docs are deliverables** — `custom-elements.json` and `README.md` are part of the deliverable, not extras. Why? Undocumented components can't be reused.

17. **English for technical naming** — JSDoc, event names, payload keys, public API. Why? Team convention across international contributors.

18. **No TODOs or commented-out code** — resolve before delivery. Why? TODOs become permanent technical debt.

## Browser Integration

When authoring or evolving a component with visible UI behavior, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Include browser validation targets in the authoring plan:
- demo or local preview entry point
- key interaction states
- screenshots or diffs when the component has meaningful visual changes
- runtime i18n or theming checkpoints when applicable.

# Cells Conventions

## Purpose

Use this file whenever the project is based on BBVA Cells, Lit, web components, or `@bbva-spherica-components`.

Your job is to ground every recommendation in real Cells evidence, not generic frontend assumptions.

Also read `skills/_shared/cells-official-reference.md` to route each task to the right internal official source without loading unnecessary documentation.

## Source Priority

Read sources in this order when they exist:

1. Project source code:
   - `src/`
   - `index.js`, `*.js`, `*.ts`
   - `test/`
   - `package.json`
   - `custom-elements.json`
2. Real feature repositories provided as reference:
   - `bbva-feature-oc-account-fx-co`
   - `bbva-feature-product-detail-debit-card`
3. Internal component catalog:
   - `skills/cells-components-catalog/`
   - use `scripts/search_docs.py` to shortlist packages, tags, props, events, and snippets quickly
4. Internal official-docs catalog:
   - `skills/cells-official-docs-catalog/`
   - use `scripts/search_docs.py` to retrieve architecture, CLI, testing, theming, packaging, and authoring rules

If two sources conflict, trust project code first, then the internal component catalog, then the internal official-docs catalog.

## Cells Stack Detection

Treat a project as Cells-oriented when you find one or more of:

- `custom-elements.json`
- `cells` commands in `package.json`
- `lit` or `LitElement`
- `@open-wc/scoped-elements`
- `@bbva-spherica-components/*`
- `@bbva-web-components/*`
- local web components with `static get scopedElements()`

## What To Extract

For components, always extract:

- public properties and reflected attributes
- custom events and emitted host events
- scoped elements and imported BBVA packages
- CSS custom properties or style overrides when documented
- test files and what they actually verify
- changelog notes or migration clues from Components Studio
- at least one real usage pattern from a feature repo when available

For features, always extract:

- composition tree: parent feature -> internal widgets -> base Cells components
- event wiring
- data managers, mixins, helpers, and shared styles
- navigation/state patterns
- test strategy and mocking patterns

## Cells-Specific Verification Heuristics

When verifying or designing for Cells, explicitly check:

- reflected attributes match documented names
- event names are stable and actually dispatched
- `scopedElements` includes all local registrations needed by the template
- `custom-elements.json` and source code do not contradict each other
- tests cover render paths, events, and edge states
- commands in `package.json` use realistic Cells flows, such as `cells lit-component:test`

## Evidence Rules

- Never say a component "supports" a prop, event, or pattern unless you found it in code, in the internal component catalog, or in the internal official-docs catalog.
- Route architecture, CLI, testing, theming, and packaging questions through `skills/_shared/cells-official-reference.md` before reading broad documentation trees.
- When `skills/cells-components-catalog/` exists, use it as a fast discovery layer, then confirm important details against code or the internal dossier.
- When proposing a new component or feature, cite the closest real feature/example you found.
- Prefer composition patterns already used in the repo over inventing a new abstraction.
- The core architecture must work with the installed bundle alone.

## Skill Creation Rules

When creating or improving a component skill:

- combine package API, Components Studio notes, and real feature usage
- replace generic placeholders with concrete imports, attributes, events, and caveats
- include real package names like `@bbva-spherica-components/bbva-type-text`
- mention known version or migration notes when found
- document when the source project is incomplete or the docs are shallow

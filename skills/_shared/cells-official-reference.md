# Cells Official Reference

## Purpose

Use this file to route Cells work to the internal official-docs skill bundled inside this package.

Do NOT reference folders outside this package from this file or from dependent skills.

## Minimal Retrieval Protocol

1. Classify the task first:
   - web-components fundamentals
   - component API
   - feature or app architecture
   - app runtime or communication
   - advanced application concerns
   - CLI or workflow command
   - testing or coverage
   - demo, docs, i18n
   - styling, theming, assets
2. Read project code and `package.json` first.
3. Then query `skills/cells-official-docs-catalog/` for the exact topic family needed.
4. Use repo-local specialist skills as accelerators:
   - `skills/cells-components-catalog/`
   - `skills/cells-component-authoring/`
   - `skills/cells-cli-usage/`
   - `skills/cells-coverage/`
   - `skills/cells-i18n/`
   - `skills/cells-test-creator/`
   - `skills/cells-app-architecture/`
5. Return extracted rules and evidence, not long doc summaries.

## Official Source Map

### Cells and Web Components fundamentals

- `skills/cells-official-docs-catalog/` topic: `web-components-foundations`

Use for:
- core Cells and Web Components principles
- API interaction boundaries
- reuse-first decisions
- declarative vs imperative component use

### Cells ecosystem and architecture

- `skills/cells-official-docs-catalog/` topic: `architecture`
- `skills/cells-official-docs-catalog/` topic: `application-runtime`
- `skills/cells-official-docs-catalog/` topic: `application-communication`
- `skills/cells-official-docs-catalog/` topic: `advanced-application`
- `skills/cells-app-architecture/`

Use for:
- feature structure
- app bootstrap and configuration
- bridge, routing, pub/sub
- event channels
- native bridge
- feature flags
- microfrontends
- performance and service workers
- data managers
- app vs component responsibilities

### CLI and local workflows

- `skills/cells-official-docs-catalog/` topic: `cli`
- `skills/cells-cli-usage/`
- local `package.json` scripts

Use for:
- build, serve, test, lint, docs commands
- choosing between `npm run ...` and `cells ...`
- understanding app vs component vs `lit-component` commands

Rule:
- Prefer repo-local scripts and commands already defined in the workspace.
- Do NOT recommend global install or update steps unless the user explicitly asks for installation help.

### Component API and package contracts

- `skills/cells-official-docs-catalog/` topic: `component-api`
- `skills/cells-component-authoring/`

Use for:
- public properties and attributes
- methods, events, slots
- exported classes and entry points
- package exports and `custom-elements.json`
- deciding whether a new base component should be authored or avoided

### Lit authoring and component internals

- `skills/cells-official-docs-catalog/` topic: `lit-authoring`

Use for:
- render parts and template structure
- `willUpdate`, `firstUpdated`, `updated`
- reflected attributes and styling rules
- DOM references and interactive element patterns

### Reuse and composition

- `skills/cells-official-docs-catalog/` topic: `composition`
- `skills/cells-app-architecture/`

Use for:
- composition vs extension
- scoped elements
- mixins
- feature widgets and internal wrappers

### Demo, docs, i18n, and assets

- `skills/cells-official-docs-catalog/` topic: `demo-docs-i18n-assets`

Use for:
- demo structure
- `demo.js`, `demo-build.js`, `index.html`
- locales setup
- icons, SVG assets, microillustrations
- translated literals and locale parity

### Testing

- `skills/cells-official-docs-catalog/` topic: `testing`
- `skills/cells-official-docs-catalog/` topic: `application-testing`
- `skills/cells-test-creator/`

Use for:
- test structure
- OpenWC, Sinon, Mocha, Chai patterns
- i18n setup in tests
- public-behavior testing rules
- feature or app integration testing
- coverage triage and deterministic failure analysis when artifacts exist

### Theming and design tokens

- `skills/cells-official-docs-catalog/` topic: `theming`

Use for:
- theme package structure
- shared styles
- design tokens
- dark mode

## Preferred Evidence Order

When a claim is important, validate it in this order:

1. Project code and tests
2. `skills/cells-components-catalog/` package dossier or search result
3. `skills/cells-official-docs-catalog/` topic dossier or search result
4. Repo-local specialist skills

## Context Discipline

- Do not paste full official docs into reports.
- Extract only the rule, pattern, or command needed for the current decision.
- If a task is only about one topic, read only one topic family from this file.

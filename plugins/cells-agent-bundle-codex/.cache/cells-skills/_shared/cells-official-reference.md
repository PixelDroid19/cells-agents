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
1b. Apply intent routing before reading catalogs:
   - UI/component discovery or element selection -> run SQL/database-backed lookup first with `skills/cells-components-catalog/scripts/search_docs.py` against `skills/cells-components-catalog/assets/bbva_cells_components.db` (do not guess from memory)
   - Any Cells documentation or knowledge lookup (variables, workflows, tests, architecture, CLI, authoring, theming, i18n, or general Cells guidance) -> `skills/cells-official-docs-catalog/` first
   - Use fallback only when the first catalog is insufficient for the decision
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
   - `skills/_shared/browser-testing-convention.md`
   - `skills/agent-browser/SKILL.md` when browser interaction or visual validation is required
5. Return extracted rules and evidence, not long doc summaries.

## Official Source Map

### Canonical component-construction checklist

When building or reviewing real Cells components, ensure coverage (only the relevant items for the task scope):

- Web Components overview/reference
- Packaging
- Custom elements
- Class and properties
- Lifecycle
- Reuse and composition
- Component API
- Templating in Lit
- Styles and theming
- Demo
- Internationalization (i18n)
- Documentation
- Images and icons
- Spherica integration
- Context
- Testing
- CI/CD

If required checklist items are not supported by evidence, return `partial` and list missing areas.

### Required real-component implementation patterns

When the task is about building a real component or feature-facing UI, validate these operational patterns as applicable:

- reuse existing BBVA components first (`cells-components-catalog`)
- register template dependencies in `scopedElements`
- use `WidgetMixin` and `this.emitEvent(...)` when following Cells feature/data-manager architecture
- use `this.t(...)` for component-owned literals
- keep locale parity in the repo's actual locale source for the touched surface
- treat SCSS as visual source and keep runtime style artifacts aligned
- validate visible behavior in the browser before closure

Use these sources:

- `skills/cells-components-catalog/` for reuse-first evidence
- `skills/cells-official-docs-catalog/` topics `component-api`, `lit-authoring`, `composition`, `demo-docs-i18n-assets`, `testing`, `theming`
- `skills/cells-app-architecture/references/data-managers.md`
- `skills/cells-app-architecture/references/routing.md`
- `skills/cells-app-architecture/references/feature-structure.md`
- `skills/cells-i18n/references/i18n-runtime-and-locales.md`
- `skills/_shared/browser-testing-convention.md`

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
- mapping local wrappers to canonical `cells ...` commands
- understanding app vs component vs `lit-component` commands

Rule:
- Keep Cells-native commands canonical for Cells app/theme workflows (`/cells-*`, `cells app:*`, documented `cells component:*`, and repo-local `cells lit-component:*` wrappers where present).
- Resolve command families in this order:
  - repo-local script or wrapper actually present
  - documented Cells equivalent
  - explicit gap note when the repo uses legacy or product-specific naming
- Canonical command families to prefer in guidance and execution decisions:
  - Workflow: `/cells-init`, `/cells-explore`, `/cells-new`, `/cells-continue`, `/cells-ff`, `/cells-apply`, `/cells-verify`, `/cells-archive`
  - App: `cells app:serve -c <config>`, `cells app:build -c <config>`, `cells app:test`, `cells app:lint`, `cells app:install`, `cells app:create`
  - Component documented path: `cells component:create`, `cells component:dev`, `cells component:test`, `cells component:lint`, `cells component:locales`, `cells component:documentation`
  - Component repo-local wrapper path: `cells lit-component:create`, `cells lit-component:serve`, `cells lit-component:test`, `cells lit-component:lint`, `cells lit-component:locales`, `cells lit-component:documentation`
- Do NOT default to generic external commands (`npm run *`, `npm test`, `npx web-test-runner`) for Cells workflows.
- Use non-Cells commands only when the user explicitly requests them in a clearly non-Cells context.
- If uncertain whether a command is Cells-native, ask the user before running a non-Cells command.
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
- packaging rules and publishability checks for reusable components

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
- documentation outputs and examples needed for reusable components

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

Mandatory testing stack for Cells contexts (consult in strict order before any other testing source):
1. `skills/cells-cli-usage/` (canonical test command and invocation path)
2. `skills/cells-coverage/` (coverage thresholds, reports, branch-miss prioritization)
3. `skills/cells-test-creator/` (test design, creation, update, compliance)

Rules:
- Apply this stack first whenever the request is about tests, test execution, coverage, or test creation in Cells.
- Do not skip or reorder these three skills for Cells testing requests.
- Do not reintroduce generic fallback commands (`npm test`, `npm run test`, `npx web-test-runner`) in Cells contexts.

### Browser-visible UI, demos, and visual validation

- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available
- `skills/cells-cli-usage/`

Use for:
- opening demo or local app routes
- clicking through feature flows
- taking screenshots or DOM snapshots
- comparing visible UI states after a change
- validating runtime i18n, theming, and dark mode

Rule:
- resolve the local serve or demo path first
- snapshot before interaction and re-snapshot after DOM changes

### Theming and design tokens

- `skills/cells-official-docs-catalog/` topic: `theming`

Use for:
- theme package structure
- shared styles
- design tokens
- dark mode

### CI/CD and delivery checks

- `skills/cells-official-docs-catalog/` topic: `cli`
- local project CI configuration and scripts

Use for:
- lint/test/build gating before merge
- command consistency with Cells-native toolchain
- release/publish checklist alignment for component packages

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

## Language Policy

- Keep generated technical naming in English by default.
- JSDoc and maintainer-facing comments must be written in English.
- Event names, custom event types, payload keys, and public API names must be in English.
- If the user writes in Spanish (or another language), the assistant may respond in that language, but generated code/docs naming must stay in English unless the user explicitly requests otherwise.

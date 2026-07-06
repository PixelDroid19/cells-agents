# Cells Conventions

## Purpose

Use this file whenever the project is based on BBVA Cells, Lit, web components, or `@bbva-spherica-components`.

Your job is to ground every recommendation in real Cells evidence, not generic frontend assumptions.

Also read `skills/_shared/cells-official-reference.md` to route each task to the right internal official source without loading unnecessary documentation.

When the task touches rendered UI, demos, routes, screenshots, or functional/visual verification, also read `skills/_shared/browser-testing-convention.md` and `skills/agent-browser/SKILL.md` when available in the workspace or installed bundle.

## Shared Doc Precedence (Conflict Resolution)

Apply `_shared` guidance in this strict order when rules overlap:

1. `skills/_shared/persistence-contract.md` (mode, write permissions, backend authority)
2. `skills/_shared/cells-governance-contract.md` (catalog-first routing, fallback/escalation, trace fields)
3. `skills/_shared/cells-policy-matrix.yaml` (machine-checkable cross-layer parity matrix)
4. `skills/_shared/engram-convention.md` and `skills/_shared/openspec-convention.md` (artifact paths/naming)
5. `skills/_shared/cells-conventions.md` (Cells routing, command policy, testing stack, language)
6. `skills/_shared/cells-official-reference.md` (topic map and source-routing details)
7. `skills/_shared/browser-testing-convention.md` (browser evidence workflow for UI-visible claims)
8. `skills/_shared/doc-search.md` (catalog query phrasing and zero-result fallback), `skills/_shared/code-quality-rules.md` (code style), `skills/_shared/artifact-recovery.md` (phase context recovery)

Tie-breakers:
- If persistence mode/file-write rules conflict with any Cells/browser rule, `persistence-contract.md` wins.
- If routing/fallback behavior conflicts across layers, `cells-governance-contract.md` wins.
- If command or testing guidance differs between shared docs, `cells-conventions.md` wins.
- If browser evidence is required for a UI-visible claim, `browser-testing-convention.md` adds required validation steps and does not override persistence mode rules.

## Governance Contract (Mandatory)

For Cells-oriented orchestration and phase execution, treat the following as mandatory companion artifacts:

- `skills/_shared/cells-governance-contract.md`
- `skills/_shared/cells-policy-matrix.yaml`

All routing and fallback decisions must be deterministic and traceable.
At minimum, record:

- `intent`
- `primary_source`
- `fallback_used`
- `fallback_source`
- `fallback_reason`
- `evidence_quality`
- `status` (`ok` | `partial` | `blocked`)

## Source Priority

Read sources in this order when they exist:

1. Project source code:
   - `src/`
   - `index.js`, `*.js`, `*.ts`
   - `test/`
   - `package.json`
   - `custom-elements.json`
2. Real feature repositories provided as reference:
   - use `skills/_shared/real-cells-patterns.md` for distilled reusable patterns
   - do not cite private local reference paths or folder names in repo assets
3. Internal component catalog:
   - `skills/cells-components-catalog/`
   - use `scripts/search_docs.py` to shortlist packages, tags, props, events, and snippets quickly
4. Internal official-docs catalog:
   - `skills/cells-official-docs-catalog/`
   - use `scripts/search_docs.py` to retrieve architecture, CLI, testing, theming, packaging, and authoring rules

If two sources conflict, trust project code first, then the internal component catalog, then the internal official-docs catalog.

Clarification (no contradiction with catalog-first rules): the catalog is first for **discovering which component to use**; project code is first for **verifying how an already-used component actually behaves**.

For how to phrase catalog queries and what to do on zero results, follow `skills/_shared/doc-search.md`.

## Intent Routing Rules (Mandatory)

**The canonical routing table is in `skills/_shared/cells-source-routing-contract.md` (Core Intent Matrix).** Use it for all intent routing decisions before choosing which skill or catalog to read first.

Fallback is allowed only when the first route does not provide enough evidence for the decision.

For any component/UI intent, do not skip the SQL lookup step and do not infer component APIs from memory.

## Browser Evidence for UI Work

When a Cells task depends on what a user can actually see or do in the browser, validate it with browser evidence in addition to code evidence.

Use browser evidence for:
- visible state changes
- demo or route flows
- click, fill, select, and navigation interactions
- visual regressions, screenshots, and diffs
- runtime i18n, theming, or dark-mode checks

For browser-visible claims, prefer this order:
1. project code and tests
2. local runtime opened through `agent-browser`
3. screenshots, snapshots, or diffs captured from that runtime

## Cells Stack Detection

Treat a project as Cells-oriented when you find one or more of:

- `custom-elements.json`
- `cells` commands in `package.json`
- `lit` or `LitElement`
- `@open-wc/scoped-elements`
- `@bbva-spherica-components/*`
- `@bbva-web-components/*`
- local web components with `static get scopedElements()`

## Cells Command Policy (Strict)

When Cells is detected, stay on Cells-native workflow commands.

- Use Cells workflow commands and subcommands (`/cells-*`, `cells app:*`, `cells lit-component:*`) for app/theme orchestration.
- Canonical Cells command set for guidance:
  - Workflow: `/cells-init`, `/cells-explore`, `/cells-new`, `/cells-continue`, `/cells-ff`, `/cells-apply`, `/cells-verify`, `/cells-archive`
  - App: `cells app:serve -c <config>`, `cells app:build -c <config>`, `cells app:test`, `cells app:lint`, `cells app:install`, `cells app:create`
  - Component: `cells lit-component:create`, `cells lit-component:serve`, `cells lit-component:test`, `cells lit-component:lint`, `cells lit-component:locales`, `cells lit-component:documentation`
- Do NOT suggest or default to generic external commands like `npm run *`, `npm test`, `npm run test`, `npx web-test-runner`, or other non-Cells runners for Cells flows.
- Only use a non-Cells command when the user explicitly requests it and the context is clearly non-Cells.
- If uncertain whether a command is Cells-native, ask the user before running any non-Cells command.
- If `package.json` wraps Cells commands, map to the equivalent Cells command in guidance and keep Cells naming as canonical.

Allowed vs disallowed examples in Cells context:

| Allowed (Cells-native) | Disallowed default (generic fallback) |
|---|---|
| `cells app:test` | `npm test` |
| `cells lit-component:test` | `npm run test` |
| `cells app:serve -c local` | `npm run start` |
| `cells app:build -c production` | `npm run build` |
| `/cells-verify` | `npx web-test-runner` |

Exception:
- Generic/non-Cells commands are only allowed when the user explicitly requests them in a clearly non-Cells context.

## Language Policy (Mandatory)

Use English for technical artifacts generated by the assistant, unless the user explicitly asks for a different language in code/docs naming.

- JSDoc and maintainer-facing code comments: English
- Event names, custom event types, payload keys, and public API names (props, methods, classes, tags, exported symbols): English
- Test technical naming (suite/test names, assertion messages, helper identifiers): English
- User conversation language can follow the user's prompt language (for example, Spanish), but generated technical naming remains English by default

Do and don't examples:

- Do: `/** Emits account-selected when a row is clicked. */`
- Do: `this.dispatchEvent(new CustomEvent('account-selected', { detail: { accountId } }))`
- Do: `public getAccountSummary()`
- Don't: `/** Emite cuenta-seleccionada al hacer click. */`
- Don't: `new CustomEvent('cuenta-seleccionada', { detail: { idCuenta } })`
- Don't: `public obtenerResumenCuenta()`

## Locales Path Policy (Contextual)

For Cells projects, do not assume one universal locale path.

- For component/demo surfaces, validate `demo/locales/locales.json` when that is the active repo convention or runtime bundle.
- For feature/app/test surfaces, follow the repo's actual locale source and runtime configuration.
- If both `locales/locales.json` and `demo/locales/locales.json` exist, inspect the touched surface before changing either file.
- Do not invent a new locale location without repo evidence.

Typical examples:

- Component/demo runtime: `demo/locales/locales.json`
- Feature/app/test locale source: repo-local convention such as `locales/locales.json` or app runtime config

## Testing Stack (Proportional)

For Cells testing intents, load only the skill(s) the intent actually needs — in this precedence when more than one applies:

1. `skills/cells-cli-usage/` — resolving which command runs tests. Enough by itself for "how do I run tests".
2. `skills/cells-coverage/` — add only when the intent involves coverage thresholds or report triage.
3. `skills/cells-test-creator/` — add only when creating or updating tests.

Rules:
- Never suggest generic fallbacks (`npm test`, `npm run test`, `npx web-test-runner`) in Cells contexts.
- If command ownership is unclear, resolve with `cells-cli-usage` first, then ask before any non-Cells command.

## Pre-Action Checklist (Short)

Before acting, run this checklist in order:

1. Confirm Cells context (`custom-elements.json`, `cells` scripts, or Cells/Lit package signals).
2. Resolve intent route using the matrix above (components vs official docs vs testing stack vs browser evidence).
3. Enforce command policy (Cells-native first; no generic fallback defaults).
4. For testing requests, load only the testing skill(s) the intent needs (see Testing Stack above).
5. Keep technical artifacts in English (JSDoc, event names, API names, payload keys).
6. Validate claims with strongest available evidence (code first, then routed catalogs/skills, then browser evidence when UI-visible).

## Reliability Guardrails (Mandatory)

- Never invent file paths, APIs, events, or command names.
- Verify file paths before citing or editing them.
- For component/API claims, use catalog/code evidence first; otherwise return `partial`.
- For i18n claims, verify locale path and runtime setup before proposing fixes.
- When command ownership is uncertain, resolve with `cells-cli-usage` first.

### Command Allowlist Behavior (Cells contexts)

By default, use only:

- `/cells-*` workflow commands
- `cells app:*`
- `cells lit-component:*`

If a requested command is outside this set and not explicitly requested by the user, stop and report `blocked` with an approved Cells-native alternative.

## Real Cells Component Rules

The single source of truth for component implementation rules (BBVA-first reuse, `scopedElements`, `WidgetMixin`/`emitEvent`, `this.t(...)` i18n, SCSS as visual source, browser validation) is `skills/_shared/cells-rules-contract.md`. Read it; do not restate its rules here or in phase skills.

## Code Hygiene Rules

Follow `skills/_shared/code-quality-rules.md` (single source; do not restate).

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
- browser-visible user flows are validated with `agent-browser` when source-only evidence is insufficient
- commands in `package.json` use realistic Cells flows, such as `cells lit-component:test`

## Evidence Rules

- Never say a component "supports" a prop, event, or pattern unless you found it in code, in the internal component catalog, or in the internal official-docs catalog.
- Route architecture, CLI, testing, theming, and packaging questions through `skills/_shared/cells-official-reference.md` before reading broad documentation trees.
- When `skills/cells-components-catalog/` exists, use its SQL/database-backed search (`scripts/search_docs.py` over `assets/bbva_cells_components.db`) as the required discovery step, then confirm important details against code or the internal dossier.
- When proposing a new component or feature, cite the closest real feature/example you found.
- Prefer composition patterns already used in the repo over inventing a new abstraction.
- If a claim depends on rendered UI or interaction behavior, validate it with `skills/_shared/browser-testing-convention.md` and `skills/agent-browser/SKILL.md` when available.
- Do not run the project, demo server, or tests for every small change; reserve execution for confirmation when the change risk or visible impact justifies it.
- If a runtime or browser session is already active, reuse the same route, session, and port instead of launching another one.
- The core architecture must work with the installed bundle alone.

## Skill Creation Rules

When creating or improving a component skill:

- combine package API, Components Studio notes, and real feature usage
- replace generic placeholders with concrete imports, attributes, events, and caveats
- include real package names like `@bbva-spherica-components/bbva-type-text`
- mention known version or migration notes when found
- document when the source project is incomplete or the docs are shallow

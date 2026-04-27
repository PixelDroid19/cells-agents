# Real Cells Patterns

## Purpose

This file captures reusable Cells implementation patterns observed in real reference projects during skill authoring. Use it as practical evidence together with official docs and catalog lookups. It is not a replacement for project-local code inspection.

Evidence categories:
- modern Lit 3 feature component packages
- legacy Cells app runtime samples
- Spherica component catalog examples
- OpenWC/Sinon feature test suites

## Source Scope

- Treat modern Lit 3 feature packages as feature-composition evidence.
- Treat Spherica component catalog examples as component API and design-system evidence.
- Treat legacy app/runtime samples as migration or app-shell evidence only. Do not copy legacy bower/gulp-era patterns into modern Lit 3 Spherica components unless the active project is also legacy.
- Never copy business data, customer data, or product-specific logic from reference projects. Extract only reusable structure, naming, and testing patterns.

## Modern Feature Component Baseline

Modern feature packages commonly use:
- `LitElement` wrapped by `ScopedElementsMixin` and `WidgetMixin`.
- `static get properties()` in plain JavaScript, not decorators.
- `static get scopedElements()` to register every custom element used in templates.
- `configurationScopedElements` and `scopedElementsFromClasses` when composing Spherica components that expose configuration helpers.
- `static get styles()` with local styles plus `getComponentSharedStyles('component-shared-styles-name')`.
- `${super.render()}` when `WidgetMixin` contributes shared runtime containers, notifications, or defaults.

Standard feature folders commonly include:
- `src/pages/`
- `src/data-manager/`
- `src/shared-components/`
- `src/mixins/`
- `src/config/` or `src/configs/`
- `src/utils/`
- `src/styles/`
- `test/`
- `demo/locales/locales.json`
- `custom-elements.json`

## Spherica UI Usage

Prefer `@bbva-spherica-components` packages before authoring UI from scratch.

Observed high-value primitives include:
- `bbva-type-text` for typography and semantic tags.
- `bbva-button-default` and button-row variants for actions.
- `bbva-form-input`, `bbva-form-select`, and related form controls for validation, labels, helper text, disabled/readonly states, and accessibility fields.
- `bbva-help-modal`, `bbva-notification-message`, `bbva-clip-*`, and `bbva-header-main` for common interaction and feedback surfaces.

Rules:
- Use `bbva-type-text` instead of raw text tags when a BBVA typography component is available.
- Use Spherica form APIs such as `label`, `label-out`, `info-message`, `invalid`, `error-message`, and accessibility attributes instead of custom label/error markup.
- Use Spherica tokens and ambients rather than arbitrary hardcoded color values.
- Confirm exact package names, element tags, properties, events, and examples through the component catalog before coding.

## Composition And Events

Feature hosts generally orchestrate pages, data managers, and shared components.

Recommended communication shape:
- Parent to child: explicit properties.
- Child to parent: events with `bubbles: true` and `composed: true` when crossing shadow DOM boundaries.
- Feature/business events: `this.emitEvent(...)` from `WidgetMixin` when the surrounding architecture uses that pattern.
- API/runtime work: data managers, not presentational components.
- Data-manager outputs: normalized `*-success` and `*-error` style events, with stable payload shapes.

Testing and implementation should preserve public event names, payload shapes, and bridge-facing behavior. Avoid moving API logic into page or typography components.

## i18n And Locales

Use `this.t(...)` for component-owned visible strings.

Rules:
- Never use `this.t('key') || ''`; missing keys render as key text and are not falsy.
- Prefer component-prefixed keys such as `component-name-flow-action-title`.
- Keep `demo/locales/locales.json` as the mandatory runtime/demo locale source.
- Preserve placeholders such as `{amount}`, `{from}`, and `{to}` exactly across locales.
- Preserve project convention when English values are placeholder-wrapped or incomplete; do not invent translations as part of unrelated code work.
- If the active repo also has root `locales/locales.json`, inspect its current convention before changing it, but do not create new locale locations.

## Styling

Observed Cells feature packages use SCSS as the visual source and generated runtime style artifacts such as `.css.js`.

Rules:
- Keep SCSS and generated style artifacts aligned when both exist in the repo.
- Use `getComponentSharedStyles(...)` names that match the component shared-style registration.
- Prefer design tokens, Spherica decisions, and component-provided styling hooks over hardcoded CSS.
- Do not change visual behavior during cleanup-only work.

## Testing Patterns

Canonical Cells feature tests use `cells lit-component:test` resolved through `skills/cells-cli-usage/`.

Observed test patterns:
- OpenWC `fixture`, `assert`, `fixtureCleanup`, and `oneEvent` where appropriate.
- `sinon` stubs, spies, fake timers, and `sinon.restore()` in teardown.
- `await el.updateComplete` after fixture creation and state changes.
- scoped custom element registry polyfill where required.
- child/data-manager event simulation with `CustomEvent(..., { bubbles: true, composed: true })`.
- stable selectors such as `data-tag-name` for data managers or real child element tags when testing public behavior.
- restoration of mutable fixture data in teardown.

Cover public behavior:
- render states
- property propagation
- event handling
- loading, empty, error, and fallback paths
- data-manager success/error paths
- timer-delayed behavior when the feature uses delays

Avoid private-member testing unless there is no public surface and the user explicitly accepts that coupling.

## Agent Guidance

When making architecture or skill decisions:
1. Route through official docs and catalog evidence first.
2. Use this file to ground practical implementation choices in real Cells repositories.
3. Inspect the active project before applying a pattern; real evidence is a baseline, not a blind template.
4. Report source decisions when a pattern comes from these reference repositories rather than official docs.

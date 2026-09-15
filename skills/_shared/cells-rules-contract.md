# Cells Rules Contract

## Purpose

This is the shared implementation contract for BBVA Cells UI, i18n, public behavior, and command use. Apply the sections relevant to the touched surface. Use [source routing](cells-source-routing-contract.md) to find evidence before relying on a component or framework rule, and [real Cells patterns](real-cells-patterns.md) to interpret an observed implementation without treating it as a universal template.

## BBVA-First Rule

For UI, typography, form, button, table, navigation, or feedback work:

1. Search `cells-components-catalog` for an existing BBVA component.
2. Confirm the selected tag/API against the active project's CEM, package source, or code.
3. Compose or use that component when it satisfies the need.
4. Consider `cells-component-authoring` only when evidence shows no suitable component.

Do not replace a supported BBVA component with raw typography tags, clickable `div`s, custom spinners, hand-built toasts, or hand-built steppers.

## Component Rules

When the active component template uses a custom element, import and register it in `scopedElements` according to the repository's composition pattern. Preserve `ScopedElementsMixin`, `configurationScopedElements`, `scopedElementsFromClasses`, and `getComponentSharedStyles(...)` when the local component uses those helpers.

When the surrounding feature uses `WidgetMixin`/data managers, preserve that architecture: presentation components stay out of API orchestration and bridge-facing business events use `this.emitEvent(...)` where the local pattern does.

Keep public properties, events, payloads, reflected attributes, and rendered behavior compatible with the existing component contract. Test public behavior rather than private implementation details.

## i18n and Locales

- Route component-owned visible strings through `this.t('key')`.
- Do not use `this.t('key') || ''`; missing keys are rendered by the runtime and are not falsy.
- Keep locale parity in the actual locale source for the touched surface.
- `demo/locales/locales.json` is common for component demos, but app, feature, and test surfaces can use a different configured location. Inspect the project before changing locales.
- Set `IntlMsg.lang` at the app or shell level when the project does so, and wait for locale loading in tests or demos that depend on it.

## Styling and Browser Evidence

- Treat SCSS as the visual source where the project uses it; keep generated runtime style artifacts aligned when the local workflow requires it.
- Prefer Spherica tokens, ambients, and documented component hooks over arbitrary styling.
- When visible behavior changes, use browser validation for the affected flow when static or unit evidence is insufficient. Reuse an existing server/session when possible.

## Command Policy

Resolve commands through `cells-cli-usage` when execution is in scope.

- Prefer an installed project script or wrapper that demonstrably resolves to the project's Cells-native workflow.
- Map it to the documented Cells equivalent in the report when useful.
- Current official component guidance uses `cells component:*`; an installed legacy `cells lit-component:*` wrapper remains valid for that workspace.
- Use `cells app:*` for applicable app workflows.
- Do not default to generic test runners or arbitrary `npm` commands in a Cells context. A package script is acceptable only after the resolver confirms what it runs.
- Do not install dependencies or global tooling unless the user requests it.

## Testing Skills

Load only what the task needs:

1. `cells-cli-usage` to select a Cells test command.
2. `cells-coverage` when coverage thresholds or reports matter.
3. `cells-test-creator` when creating or changing tests.

## Language

Keep technical names, public APIs, events, payload keys, JSDoc, and maintainer-facing comments in English unless the user explicitly asks otherwise. The conversation language can follow the user.

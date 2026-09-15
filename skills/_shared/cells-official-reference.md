# Cells Official Reference

## Purpose

Route framework and process questions to the bundled official Cells catalog without loading unrelated documentation. Use `cells-source-routing-contract.md` first; it decides whether the component catalog, official catalog, local code, or command resolver is primary.

## Topic Map

| Need | Official catalog topic | Add when relevant |
| --- | --- | --- |
| Foundations, packaging, custom elements | `web-components-foundations`, `component-api` | Project CEM and package source |
| Lit lifecycle, templates, styles | `lit-authoring`, `theming` | Existing component patterns |
| Component composition and feature architecture | `composition`, `architecture`, `application-runtime` | `cells-app-architecture` and project code |
| App communication | `application-communication` | Bridge or routing source code |
| Tests | `testing`, `application-testing` | `cells-cli-usage`, `cells-coverage`, or `cells-test-creator` only as needed |
| Demos, docs, i18n, assets | `demo-docs-i18n-assets` | Actual locale/runtime configuration |
| CLI | `cli` | Installed scripts through `cells-cli-usage` |

Search the narrow topic, extract the rule that matters, then verify it against the active project before making a local claim. Do not paste whole catalog documents into a result.

## Component and UI Work

For a real component or feature-facing UI, apply the relevant requirements in `cells-rules-contract.md`:

- reuse an existing BBVA component when evidence supports it;
- register template dependencies in `scopedElements`;
- preserve `WidgetMixin`/`this.emitEvent(...)` architecture when the project uses it;
- use `this.t(...)` and the real locale source for visible literals;
- keep SCSS and generated style artifacts aligned where required;
- collect browser evidence for visible behavior when source evidence is insufficient.

## Command Evidence in This Bundle

The documented current component route is represented by `cells component:*` in the official catalog guidance. `skills/cells-cli-usage/references/commands.md` records legacy `cells lit-component:*` wrapper behavior. Treat the latter as valid only when the active workspace exposes it; resolve the actual executable script before use.

For app work, resolve the applicable `cells app:*` command and its local configuration from the project rather than guessing a config path. Do not install tooling or select a generic runner merely to satisfy a workflow template.

## Evidence Limits

Return `partial` when a required project-specific API, locale, command, or runtime fact is not available. Return `blocked` only when that gap prevents safe continuation. A catalog query's own `ok` result says that the query completed, not that the user's task is complete.

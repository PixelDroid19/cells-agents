# Demo Docs I18n Assets

## Scope

Use this topic for demo structure, documentation generation, i18n, and assets.

## Core rules

- Demos are part of the developer and consumer experience and should show real usage patterns clearly.
- Demo structure usually uses `demo.js`, `demo-build.js`, `index.html`, case HTML files, optional CSS, and locales.
- HTML demo files should load local demo JS files, not deep package internals.
- Documentation should cover the full public API and is expected to generate or align with `custom-elements.json`.
- `custom-elements.json` is the structured source of truth for generated component docs.
- i18n should rely on `BbvaCoreIntlMixin`, `window.IntlMsg`, and localized keys loaded from locales.
- Demo locales can differ from package default locales when dependencies also need translations.
- Assets and icons should be used in a way that preserves tree-shaking and avoids unnecessary bundle weight.
- Themes may be loaded in demos as dev-only support, but themes are app-level concerns in production.

## Signals to extract

- demo folder shape
- docs generation path
- locales initialization
- icon and asset strategy
- any requirement for demo helper or demo-only files

## Use when

- designing or fixing demos
- generating docs
- wiring i18n
- choosing icon or asset patterns

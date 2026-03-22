# Demo Docs I18n Assets

## Scope

Use this topic for demo structure, documentation generation, i18n setup, and assets.

## Demo Structure

Demos are part of the developer and consumer experience and should show real usage patterns clearly.

Typical demo structure:

```
demo/
  demo.js          ← demo entry point (loads polyfills, theme, components)
  demo-build.js
  index.html       ← loads demo.js
  case-1.html
  case-2.html
  css/
    demo.css.js
  locales/
    locales.json
```

Demo entry point must load the Scoped Custom Element Registry polyfill before any component:

```js
// demo/demo.js
import '@bbva-web-components/bbva-core-scoped-custom-element-registry';
import '@bbva-web-components/bbva-dev-demo-theme';
import '../my-component.js';
```

HTML demo files should load local demo JS files, not deep package internals.

## Documentation Generation

Documentation should cover the full public API and align with `custom-elements.json`. Use the Cells CLI:

```bash
cells lit-component:documentation
```

This generates `README.md` and `custom-elements.json` from the component source.

## i18n Anti-Patterns

### IntlMsg.lang setup — set at app/shell level

Setting `IntlMsg.lang` at component instance level causes race conditions — the component may render before the locale loads, showing the raw key as text:

```js
// ANTI-PATTERN — DON'T set at instance level
class MyComponent extends LitElement {
  created() {
    IntlMsg.lang = 'en'; // race condition!
  }
}
```

Set `IntlMsg.lang` at the app or shell level, once, before any component renders.

### this.t('key') || '' — never falsy-guard i18n

The i18n runtime renders the key itself as fallback when the translation is missing. `this.t('key') || ''` is never falsy when the key is valid — the runtime returns the key string:

```js
// ANTI-PATTERN — this never catches a missing translation
const text = this.t('bbva-text') || ''; // wrong approach

// CORRECT — check the locale file directly for missing keys
// Add missing keys to demo/locales/locales.json
```

### Locale file location — always demo/locales/

In Cells projects, locale files must be under `demo/locales/` and must not be referenced outside that path:

```json
// demo/locales/locales.json
{
  "bbva-text": "Texto en español",
  "button-label": "Aceptar"
}
```

For component packages, `demo/locales/locales.json` can differ from the package default locales when dependencies also need translations.

## Assets and Icons

Assets and icons should be used in a way that preserves tree-shaking and avoids unnecessary bundle weight. Use the BBVA icon system from official packages — do not embed raw SVGs.

## Themes in Demos

Themes may be loaded in demos as dev-only support. Themes are app-level concerns in production — components must not depend on themes in production code.

## Signals to extract

- demo folder shape
- docs generation path
- locales initialization
- IntlMsg.lang setup (app/shell level)
- icon and asset strategy
- demo helper or demo-only files

## Use when

- designing or fixing demos
- generating docs
- wiring i18n
- choosing icon or asset patterns
- reviewing i18n setup for race conditions

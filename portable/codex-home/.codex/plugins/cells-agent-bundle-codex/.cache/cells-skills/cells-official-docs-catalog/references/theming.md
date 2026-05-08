# Theming

## Scope

Use this topic for themes, design tokens, shared styles, and dark mode.

## Core rules

- Themes are app-level packages, not normal component dependencies.
- Components must not depend on themes in production code.
- Themes may be used as dev dependencies in demos.
- Import themes before component definitions when theme data affects initialization or shared styles.
- Themes usually own document-level concerns such as font-face declarations, root font setup, shared styles, dark mode variables, and token overrides.
- Component styling should remain customizable and token-driven.
- Dark mode should usually be handled through theme-level token values rather than ad hoc component logic.

## Dark Mode

Dark mode must be handled at theme level via CSS custom properties (tokens):

```css
/* Light mode (default) */
:root {
  --color-background: #ffffff;
  --color-text: #000000;
}

/* Dark mode via attribute or class on :host */
:root[data-theme="dark"],
:host([data-theme="dark"]) {
  --color-background: #121212;
  --color-text: #ffffff;
}
```

Components should not implement their own dark mode logic. Instead, they consume theme tokens:

```js
static get styles() {
  return css`
    :host {
      background-color: var(--color-background);
      color: var(--color-text);
    }
  `;
}
```

## Design Tokens

Design tokens are the canonical values for colors, spacing, typography, and other design decisions. They live in theme packages and are consumed via CSS custom properties.

```css
/* In component */
color: var(--token-color-primary);
```

## Token-Driven Components

Components should expose customization points via CSS custom properties, not hardcoded values:

```js
static get styles() {
  return css`
    :host {
      /* Customizable via CSS var */
      border-radius: var(--component-border-radius, 4px);
      padding: var(--component-padding, 8px);
    }
  `;
}
```

## Theme Loading Order

Themes must be imported before components that depend on them:

```js
// main.js or app bootstrap
import '@bbva-web-components/bbva-dev-demo-theme';
import './my-component.js'; // depends on theme tokens
```

## Theming vs Component Styling

| Concern | Where it lives |
|---|---|
| Design tokens, global CSS vars | Theme package |
| Per-component defaults | Component `.css.js` |
| User overrides | CSS custom properties on host |
| Document-level (fonts, body styles) | Theme only |

## Signals to extract

- whether a concern belongs to theme or component
- token usage
- shared style patterns
- demo theme usage
- dark mode ownership
- CSS custom property exposure

## Use when

- deciding theme vs component responsibility
- reviewing dark mode strategy
- wiring design-token-based customization
- implementing theme overrides

# Lit Authoring

## Scope

Use this topic for class design, templating, lifecycle, and styling authoring rules.

## Core rules

- Keep class definition files focused; one main class per file.
- `render` should stay organized and can be split into `_partTpl` getters or helper methods.
- Use `_partTpl` naming for render subparts.
- Initialize defaults in the constructor.
- Use `willUpdate` or getters for derived state instead of chaining extra updates in `updated`.
- Avoid assigning new reactive values in `updated` unless strictly necessary.
- Use `firstUpdated` or refs for DOM references that are needed after first render.
- Properties used for styling should reflect to attributes.
- Non-public reactive properties should not expose attributes.
- Styles should normally live in separate `.css.js` files.
- Prefer class selectors for internal nodes and clear host attributes for variants and states.

## Lifecycle Anti-Patterns

### NEVER chain updates in `updated()`

Setting reactive properties in `updated()` causes infinite re-render loops:

```js
// ANTI-PATTERN — DON'T DO THIS
updated(changedProperties) {
  if (changedProperties.has('prop')) {
    this._innerProp = this.prop + 1; // triggers another update!
  }
}
```

Every reactive property assignment in `updated()` fires another update cycle. Two updates become four, then eight, etc.

**Correct approach**: use `willUpdate()` instead, which runs before the render and does not trigger new cycles:

```js
// CORRECT
willUpdate(changedProperties) {
  if (changedProperties.has('prop')) {
    this._innerProp = this.prop + 1; // computed once, no extra render
  }
}
```

Or compute derived values in a getter (zero-cost until accessed):

```js
get _innerProp() {
  return this.prop + 1;
}
```

### Use `firstUpdated` for one-time DOM setup

```js
firstUpdated(changedProperties) {
  super.firstUpdated?.(changedProperties);
  this._myInput = this.shadowRoot.querySelector('.my-input');
}
```

Do NOT use `firstUpdated` for operations that depend on public property values that may change after first render — use `updated()` for those, but never assign reactive properties there.

### Constructor has no access to attributes

Attributes are not yet available when the constructor runs. Set property defaults only:

```js
constructor() {
  super();
  this.propA = 'default';
  this._innerState = {};
}
```

### Always call `super` in lifecycle methods

```js
connectedCallback() {
  super.connectedCallback();
  document.addEventListener('keydown', this._onKeydown);
}

disconnectedCallback() {
  super.disconnectedCallback();
  document.removeEventListener('keydown', this._onKeydown);
}
```

## Signals to extract

- property declarations
- reflect usage
- render-part structure
- lifecycle responsibilities
- DOM querying patterns
- style file layout

## Use when

- implementing or reviewing Lit components
- deciding where logic belongs in lifecycle
- designing template and style structure

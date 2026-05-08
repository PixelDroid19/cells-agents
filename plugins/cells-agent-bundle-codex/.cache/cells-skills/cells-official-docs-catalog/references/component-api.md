# Component API

## Scope

Use this topic for public component contracts, package exposure, slots, events, and protected API.

## Public API Parts

A component package API includes: custom element API, styling API, and package entry points.

Public custom element API includes: properties, attributes, methods, events, and slots.

## Properties and Attributes

Each public property should have a matching attribute when appropriate. Attribute names are always kebab-case:

```js
static get properties() {
  return {
    customHeading: { type: String, attribute: 'custom-heading' },
    heading: { type: String } // attribute is 'heading' automatically
  };
}
```

### Property types

- **Strings, numbers, booleans**: straightforward attribute conversion
- **Arrays and objects**: avoid as public props when possible — use slots for array data instead

```html
<!-- Prefer slots for array data -->
<my-component>
  <my-component-item item-prop="A">Item A</my-component-item>
  <my-component-item item-prop="B">Item B</my-component-item>
</my-component>
```

### Reflect attributes for styling

Properties used in CSS selectors for host variants must reflect:

```js
static get properties() {
  return {
    variant: { type: String, reflect: true }
  };
}
```

```css
:host([variant="card"]) { /* styles */ }
```

### Do not overwrite public properties internally

A component should never modify its own public properties. Use a getter or `willUpdate` for derived values:

```js
// ANTI-PATTERN — DON'T DO THIS
updated(changedProperties) {
  if (changedProperties.has('disabled') && this.disabled) {
    this.variant = 'off'; // overwrites user-set value
  }
}

// CORRECT
get _effectiveVariant() {
  return this.disabled ? 'off' : this.variant;
}
```

## Slots

Slots allow components to receive distributed content. Two types:

### Default slot

Accepts any content without a `slot` attribute:

```html
<button>Button text</button>
<custom-button>Button text</custom-button>
```

```js
render() {
  return html`<slot></slot>`;
}
```

### Named slots

Children with matching `slot` attribute are distributed to named slots:

```html
<my-component>
  <p slot="description">Text for description</p>
</my-component>
```

```js
render() {
  return html`
    <div class="content">
      <slot name="description"></slot>
    </div>
  `;
}
```

Named slots only accept elements with an explicit `slot` attribute, making `slotchange` reliable.

## Events

Components dispatch events for child-to-parent communication:

```js
_onButtonClick() {
  this.dispatchEvent(new CustomEvent('button-click', {
    bubbles: true,
    detail: { value: this.value }
  }));
}
```

Event payloads should be documented: type, detail structure, bubbling behavior.

## Protected API (underscore prefix)

Internal methods and properties not intended for external use use underscore prefix:

```js
_myInnerMethod() { ... }

get _computedReadonlyProperty() {
  return this.propA + this.propB;
}
```

Non-public reactive properties use underscore prefix and `state: true` (Lit 3):

```js
static get properties() {
  return {
    _innerScroll: { state: true }
  };
}
```

Protected properties should NOT be overwritten by subclasses.

## Package Entry Points

Package exports determine what consumers can import:

```js
export { MyComponent } from './src/MyComponent.js';
export { itemA } from './src/items.js';
```

Export classes so consumers can extend them:

```js
import { MyComponent } from '@example-namespace/my-component';
customElements.define('my-own-custom-element', class extends MyComponent {});
```

The `exports` field in `package.json` defines public entrypoints and prevents importing unlisted paths.

## Signals to extract

- exported class names
- custom element names
- reflected attributes
- events and detail payloads
- slots (default and named)
- package exports and entry points
- protected API surface

## Use when

- researching component contracts
- validating API claims
- checking packaging and public exports
- deciding between slots, properties, or events for component communication

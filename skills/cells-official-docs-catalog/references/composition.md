# Composition

## Scope

Use this topic for reuse, composition, scoped elements, extension, and mixins.

## Core rules

- Prefer composition and reuse before extension.
- Register or scope dependencies explicitly; do not assume custom elements are available.
- Scoped elements are the preferred way to avoid global registry collisions in larger apps.
- Extension is valid when a component is mostly correct and only needs controlled specialization.
- Mixins are valid for cross-cutting behavior but should avoid duplicated application.
- Event-based communication is preferred for child-to-parent interactions.
- Parent components should not mirror every child API blindly; slots can preserve flexibility.
- Feature-level composition should identify base BBVA packages, wrappers, data managers, and event flow.

## Scoped Elements (Preferred for App-Level Composition)

### Why scoped elements

The global custom elements registry causes collisions when multiple versions of the same component load in an app. Scoped elements give each shadow root its own registry.

### Setup

Load the polyfill before any component registration:

```js
// app bootstrap or demo/test entry point
import '@bbva-web-components/bbva-core-scoped-custom-element-registry';
```

### Usage with ScopedElementsMixin

```js
import { ScopedElementsMixin } from '@open-wc/scoped-elements/lit-element.js';
import { LitElement, html } from 'lit';
import { ChildElement } from '@example-namespace/child-element';
import { AnotherElement } from './AnotherElement.js';

class MyComponent extends ScopedElementsMixin(LitElement) {
  static get scopedElements() {
    return {
      'child-element': ChildElement,
      'another-element': AnotherElement
    };
  }

  render() {
    return html`
      <child-element>Content...</child-element>
      <another-element>Content...</another-element>
    `;
  }
}
```

Import **classes**, not global custom element definitions. The mixin handles registration.

### Import rules

```js
// CORRECT — import class from package
import { ChildElement } from '@example-namespace/child-element';

// CORRECT — import class from local file
import { AnotherElement } from './AnotherElement.js';

// ANTI-PATTERN — importing global custom element definition
import '@example-namespace/child-element/child-element.js';
```

### Lit 1 scoped elements

For Lit 1 elements, use `^1.0.0` of `@open-wc/scoped-elements`. Lit 1 version rewrites tag names (adds an ID suffix like `<child-element-1234>`), so use `data-tag-name` for selectors:

```js
// In CSS
[data-tag-name="my-component"] { border-color: red; }

// In DOM queries
this.shadowRoot.querySelector('[data-tag-name="my-component"]');
```

## Extension

Extend a class when a component is mostly correct:

```js
import { AnotherElement } from '@example-namespace/another-element';

export class MyElement extends AnotherElement {
  static get properties() {
    return {
      newPropA: { type: String }
    };
  }
}
```

Always invoke `super` when overriding methods:

```js
firstUpdated(props) {
  super.firstUpdated?.(props);
  this._ownLogic = 'a';
}
```

## Mixins

Mixins are functions that return a class extending a base:

```js
const MyMixinImpl = BaseClass => class extends BaseClass {
  // mixin logic
};
export const MyMixin = MyMixinImpl;
```

Apply multiple mixins:

```js
export class MyElement extends MixinA(MixinB(LitElement)) {
}
```

### dedupeMixin — prevent double application

If two mixins both use a common mixin, apply `dedupeMixin` to prevent double execution:

```js
import { dedupeMixin } from '@open-wc/dedupe-mixin';

export const MyMixin = dedupeMixin(MyMixinImpl);
```

### Mixin order matters

`super` calls cascade through mixin application order. Test when changing order:

```js
// Result: logMixinB, logMixinA, logClass
class A extends ExampleMixinA(ExampleMixinB(LitElement)) {}

// Result: logMixinA, logMixinB, logClass
class B extends ExampleMixinB(ExampleMixinA(LitElement)) {}
```

## Wrapper vs Base Component Decision

Use a wrapper when the consumer needs to control the inner element's API. Use slots to allow consumers to override inner content without breaking the wrapper's logic.

## Signals to extract

- scoped elements usage
- wrapper vs base component boundaries
- extension points
- mixins and their order
- event wiring
- dedupeMixin usage

## Use when

- deciding reuse vs wrap vs extend
- planning feature composition
- reviewing scoped elements and mixins

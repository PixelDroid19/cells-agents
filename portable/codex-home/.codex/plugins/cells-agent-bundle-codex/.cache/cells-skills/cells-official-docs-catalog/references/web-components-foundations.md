# Web Components Foundations

## Scope

Use this topic for the base Cells and Web Components development model, custom elements, and module imports.

## Core rules

- Cells work builds on web standards, custom elements, ES modules, and component-based reuse.
- Components should expose a clear public API and hide internal implementation details.
- Development should prefer predictable, declarative usage over ad hoc imperative wiring.
- Component APIs must be shaped so consumers can understand properties, events, slots, and extension points without inspecting internals.
- Interactions between components should keep ownership boundaries clear: configuration flows down, events flow up, shared state lives at the appropriate app layer.
- Before creating a new component or pattern, verify whether the need can be solved by composition, configuration, or reuse of an existing package.

## Class vs Instance

Static members (prefixed with `static`) belong to the class, not instances:

```js
class ExampleClass {
  static num = 1;

  add() {
    return ExampleClass.num + 10; // uses class static
  }

  addFromInstance() {
    return this.constructor.num; // resolves to actual subclass
  }
}
```

When extending classes, static members are NOT polymorphic — a subclass static shadows, not overrides.

## Custom Element Registration

Register a custom element from its class:

```js
import { MyComponent } from './src/MyComponent.js';
customElements.define('my-component', MyComponent);
```

The registry is global — two different modules cannot register the same name.

## Import Rules

### From package entry points

```js
// CORRECT — import class from default entry point
import { MyComponent } from '@bbva-web-components/bbva-web-badge';

// CORRECT — import from named entry point (include extension)
import { MyComponent } from '@bbva-web-components/bbva-web-badge/my-component.js';

// ANTI-PATTERN — don't import index.js explicitly when default suffices
import { MyComponent } from '@bbva-web-components/bbva-web-badge/index.js';
```

### Named vs default imports

```js
// Named export — import what you need
import { MyComponent, myUtil } from './my-package.js';

// Default export
import MyDefault from './my-package.js';
```

## ES Modules

Always include the `.js` extension when importing from a named entry point:

```js
// CORRECT
import { AnotherElement } from '@example-namespace/another-element/another-element.js';

// ANTI-PATTERN — missing extension
import { AnotherElement } from '@example-namespace/another-element/another-element';
```

## Class Inheritance

A class can extend another to specialize:

```js
import { AnotherElement } from '@example-namespace/another-element';

export class MyElement extends AnotherElement {
  get _secondaryTpl() {
    return html`<div class="override">Override content</div>`;
  }
}
```

Override methods and lifecycle callbacks. Always invoke `super` when overriding:

```js
firstUpdated(props) {
  super.firstUpdated?.(props);
  this._ownLogic = 'a';
}
```

## Global HTML Attributes

Do not define properties that collide with global HTML attributes (`id`, `class`, `title`):

```js
// ANTI-PATTERN — 'title' collides with global HTML
static get properties() {
  return { title: { type: String } }; // DON'T
}

// CORRECT — use a different name
heading: { type: String }
```

## Stateless vs Stateful Components

Prefer stateless, configuration-driven components. State that belongs to the app should live in data managers or app services, not in the component itself.

## Signals to extract

- whether the task is about base web-component principles
- public API boundaries
- declarative vs imperative use
- consumer vs internal responsibilities
- reuse-first decision making
- import path correctness

## Use when

- explaining how Cells components should be designed
- grounding component decisions in fundamentals
- resolving API interaction questions
- checking import conventions

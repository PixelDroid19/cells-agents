# Web Components Foundations

## Scope

Use this topic for the base Cells and Web Components development model.

## Core rules

- Cells work builds on web standards, custom elements, ES modules, and component-based reuse.
- Components should expose a clear public API and hide internal implementation details.
- Development should prefer predictable, declarative usage over ad hoc imperative wiring.
- Component APIs must be shaped so consumers can understand properties, events, slots, and extension points without inspecting internals.
- Interactions between components should keep ownership boundaries clear: configuration flows down, events flow up, shared state lives at the appropriate app layer.
- Before creating a new component or pattern, verify whether the need can be solved by composition, configuration, or reuse of an existing package.

## Signals to extract

- whether the task is about base web-component principles
- public API boundaries
- declarative vs imperative use
- consumer vs internal responsibilities
- reuse-first decision making

## Use when

- explaining how Cells components should be designed
- grounding component decisions in fundamentals
- resolving API interaction questions

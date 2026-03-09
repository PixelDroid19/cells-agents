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

## Signals to extract

- scoped elements usage
- wrapper vs base component boundaries
- extension points
- mixins and their order
- event wiring

## Use when

- deciding reuse vs wrap vs extend
- planning feature composition
- reviewing scoped elements and mixins

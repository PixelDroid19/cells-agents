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

## Signals to extract

- whether a concern belongs to theme or component
- token usage
- shared style patterns
- demo theme usage
- dark mode ownership

## Use when

- deciding theme vs component responsibility
- reviewing dark mode strategy
- wiring design-token-based customization

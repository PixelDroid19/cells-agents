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

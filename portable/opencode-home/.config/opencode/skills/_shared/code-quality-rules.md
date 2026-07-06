# Code Quality Rules (Shared)

Single source for the code-style rules used by `cells-apply`, `cells-component-authoring`, `cells-test-creator`, and `cells-cleanup`. Reference this file; do not copy these rules into skill docs.

## Formatting

- No trailing commas in arrays, objects, or function arguments.
- Semicolons required — every statement ends with `;`.
- No unnecessary blank lines — one between logical blocks is enough — and no trailing whitespace on any line.
- No blank lines inside JSDoc blocks.

## Structure

- Max 3 `if` statements per function/helper — extract to separate helpers beyond that.
- Prefer `.map()` (or extraction to shared mocks/helpers) over repetitive setup or duplicated blocks.
- Separate responsibilities: data/business orchestration in data managers, view composition in pages, reusable UI in shared components, pure helpers in utils, styling in SCSS/runtime style artifacts.

## Unit Tests

- Unit tests are mandatory for logic changes and must never reference private methods (`_name`) — exercise only the public API.
- Test observable behavior: emitted events, public method results, property/state changes, and rendered structure — not internals.
- Use mocks for dependencies when the case requires it (data managers, services, network) and shared constants/fixtures instead of repeated literal values.
- Do not assert expected display texts/literals — test the logic that produces them (translation keys, branches, payloads), not the copy.
- No trailing whitespace and no unnecessary blank lines in test files.

## Comments & Docs

- JSDoc only for public API, emitted events, or non-obvious contracts; in English.
- No TODO comments, commented-out code, placeholder comments, or narrative inline comments — clear naming and extracted methods instead.
- No comments in test files — test descriptions and helper names should be self-documenting.

## Hygiene

- No whitespace-only edits or formatting noise unrelated to the change.
- Technical naming (events, props, methods, test names, payload keys) in English.

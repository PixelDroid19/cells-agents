# Testing

## Scope

Use this topic for official Cells testing rules.

## Core rules

- Cells component tests should be stable and independent from external services.
- Typical stack is Web Test Runner, Mocha, Chai, Sinon, and `@open-wc/testing`.
- Test files should live under `test/` and usually mirror the source file name.
- Use fixtures to create fresh instances per test and clean them up after execution.
- Test public behavior, not private implementation details.
- Validate rendered output, events, states, and observable side effects.
- If the component uses i18n, initialize `window.IntlMsg` and point `localesHost` correctly.
- Keep tests isolated and reset stubs, listeners, and other side effects after each test.
- Prefer behavior evidence over internal implementation coupling.

## Signals to extract

- fixture structure
- cleanup pattern
- event assertions
- i18n test setup
- public behavior coverage

## Use when

- creating tests
- reviewing test quality
- deciding how to validate a Cells component change

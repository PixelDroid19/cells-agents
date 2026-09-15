---
name: cells-test-creator
description: "Use when creating or updating Cells OpenWC/Sinon tests, fixtures, mocks, and public-behavior coverage."
---

# Cells Test Creator

## Purpose

Add or improve meaningful tests for the requested behavior while preserving the project's test conventions and existing quality gates.

Read [Cells rules](../_shared/cells-rules-contract.md), [source routing](../_shared/cells-source-routing-contract.md), [real Cells patterns](../_shared/real-cells-patterns.md), and [code quality rules](../_shared/code-quality-rules.md) before choosing a test surface or asserting a component contract.

## Load on Demand

- Read the target source and existing nearby tests.
- Use `cells-cli-usage` when selecting or running a test command.
- Use `cells-coverage` only when coverage thresholds, report triage, or a coverage failure is in scope.
- Use official testing and Lit guidance when the project evidence does not answer the needed pattern.
- Use `cells-i18n` when tests depend on locale loading or translated output.

## Test Rules

- Test public behavior: rendered states, public properties, emitted events, accessible interactions, and observable data-manager outcomes.
- Do not call private members or assert internal implementation details.
- Use OpenWC/Sinon patterns already present in the project; await updates after state changes and restore stubs in teardown.
- Mock external dependencies rather than calling live services.
- Cover the behavior changed by the request, including relevant loading, empty, error, or event paths.
- Reuse a helper or fixture only when it clarifies repeated setup; do not refactor unrelated tests to satisfy a template.
- Keep existing coverage thresholds intact. Do not demand an arbitrary percentage unless the project or user requires it.

## Validation

Resolve the installed Cells-native test command before execution. A verified local wrapper such as `cells lit-component:test` is valid for that workspace; report the documented `cells component:test` equivalent when useful. Do not replace the project command with a generic runner.

Run the focused test scope first. If coverage is part of the acceptance condition, inspect the relevant `lcov.info` or project report, map uncovered branches to observable behavior, and add only the tests needed to cover the agreed condition.

## Output

Report files changed, behavior covered, command results, any remaining coverage gap, and `success`, `partial`, or `blocked`. Browser validation complements tests when a route or rendered interaction cannot be meaningfully proven in a unit test.

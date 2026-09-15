---
name: cells-component-authoring
description: "Use when a BBVA Cells Lit component must be created or its public API evolved after catalog evidence shows reuse or composition is insufficient."
---

# Cells Component Authoring

## Purpose

Author or evolve a reusable Cells component without duplicating a supported BBVA component or breaking its public contract.

## Before Writing

1. Use [source routing](../_shared/cells-source-routing-contract.md), [Cells rules](../_shared/cells-rules-contract.md), [real Cells patterns](../_shared/real-cells-patterns.md), and [code quality rules](../_shared/code-quality-rules.md), then search the component catalog for an existing package.
2. Inspect the active project CEM, package source, similar components, and tests.
3. Read the narrow official topics for the actual request: component API, Lit authoring, composition, styling, demos, or packaging.
4. Decide whether to reuse, compose, evolve, or author. State why a new component is justified.

Load `cells-cli-usage` only to resolve a scaffold, documentation, locale, or test command that will actually run. Load `cells-test-creator` only when tests are created or changed. Load `cells-i18n` only when visible literals or locale configuration are in scope.

## Authoring Requirements

- Define and preserve public properties, attributes, events, slots, and styling hooks from evidence.
- Register template custom elements in `scopedElements`.
- Follow the local mixin, data-manager, event, and style patterns instead of imposing a generic component hierarchy.
- Use `this.t(...)` for component-owned visible text and update the real locale source when applicable.
- Keep SCSS and generated style artifacts aligned when the project workflow requires both.
- Update CEM, documentation, demo, or package exports only when they are part of the actual component package contract.
- Validate public behavior and visible states proportionately. Use browser evidence for material UI behavior when unit checks cannot prove it.

## Output

Report the chosen path, evidence for it, expected files, public API impact, validation plan, migration risks, and status. Return `partial` when an API or package convention is missing; return `blocked` only if that gap prevents safe authoring.

Do not create a proposal, OpenSpec record, skill registry, or LocalMemory entry merely to author a component.

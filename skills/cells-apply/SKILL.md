---
name: cells-apply
description: "Use when implementing an approved Cells change, including relevant component, feature, i18n, style, and test updates."
---

# Cells Apply

## Quick Start

1. Confirm the user-approved scope and choose `scoped-change` or `full-workflow`.
2. Inspect the affected source and its existing tests before editing.
3. Load only the reference that controls the change:

| Change | Load on demand |
| --- | --- |
| BBVA UI/component selection | `cells-rules-contract.md` and component-catalog routing |
| Framework, architecture, CLI, i18n, theming | official-catalog routing |
| Command to run | `cells-cli-usage` |
| Coverage | `cells-coverage` |
| Test creation or update | `cells-test-creator` |
| Rendered behavior | browser-testing convention and `agent-browser` |

4. Make the smallest maintainable change that matches local patterns.
5. Run the relevant targeted validation and report actual evidence.

For implementation work, read [Cells rules](../_shared/cells-rules-contract.md), [source routing](../_shared/cells-source-routing-contract.md), [real Cells patterns](../_shared/real-cells-patterns.md), and [code quality rules](../_shared/code-quality-rules.md) when their subject applies.

## Cells Implementation Rules

- Reuse an existing BBVA component before authoring a new one.
- Register custom template dependencies in `scopedElements`.
- Preserve the local `WidgetMixin`, data-manager, event, and bridge patterns when present.
- Route component-owned visible text through `this.t(...)` and update the actual locale source only when it is in scope.
- Keep SCSS and generated runtime style artifacts aligned when the project workflow requires both.
- Test public behavior, public events, and user-visible states; do not hide errors or weaken tests.

## Dependencies and Artifacts

Use approved tasks or design artifacts when a governed workflow provides them. A direct scoped implementation may proceed from the user's request and source evidence without proposal, spec, design, tasks, registry, or memory prerequisites.

If `artifact_persistence: openspec` is active, update only the relevant governed task/progress record after the source change. With `none`, report progress inline. Never save source edits or verification output to LocalMemory automatically.

## Scope

Do not fix unrelated modules, unrelated errors, or perform opportunistic cleanup outside the assigned task unless the user explicitly expands scope. Preserve existing public behavior and responsibility boundaries while applying the requested change.

## Output Envelope

Return:

- changed files and behavior;
- validation commands and observed results;
- `success`, `partial`, or `blocked` with a concrete reason;
- risks and remaining work, if any.

Do not claim a browser-visible result from static checks alone when runtime proof is required.

# Cells Conventions

## When to Use

Use this guide when the workspace shows Cells, Lit, `@bbva-spherica-components`, `@bbva-web-components`, `custom-elements.json`, or Cells command scripts. It connects the small shared contracts without duplicating their rules.

## Read the Relevant Contracts

1. Choose the mode with [work sizing](cells-work-sizing-contract.md).
2. For Cells UI, i18n, public behavior, or commands, read [Cells rules](cells-rules-contract.md).
3. Before a material component, docs, or command decision, use [source routing](cells-source-routing-contract.md).
4. Read [persistence](persistence-contract.md) only when workflow artifacts or LocalMemory are relevant.
5. Use [browser testing](browser-testing-convention.md) only when rendered behavior, a demo, or a route needs proof.

`cells-governance-contract.md` defines scope and result statuses. `cells-policy-matrix.yaml` records the semantic cross-document invariants; it is not a checklist of phrases to repeat.

For implementation work, use [real Cells patterns](real-cells-patterns.md) as observed evidence and [code quality rules](code-quality-rules.md) for formatting, responsibility boundaries, and public-behavior tests.

## Cells Signals

Confirm the active project from evidence such as:

- `custom-elements.json` or another Custom Elements Manifest;
- `cells` commands in `package.json`;
- Lit, scoped-elements, Spherica, or BBVA web-component dependencies;
- existing `scopedElements`, `WidgetMixin`, `this.t(...)`, or Cells data-manager patterns.

Inspect the actual project before applying a bundle heuristic. Modern feature code, legacy apps, and component packages can have different wrappers and locale locations.

## Command and Testing Summary

Use `cells-cli-usage` to resolve a command from installed scripts. The current documented component family is `cells component:*`; a verified installed `cells lit-component:*` wrapper remains a valid local route. Do not present a generic runner as the default Cells path.

Only load the relevant testing specialist:

- command selection: `cells-cli-usage`;
- coverage reports or thresholds: `cells-coverage`;
- test creation or modification: `cells-test-creator`.

## Evidence Labels

When the distinction matters, label a recommendation as one of:

- **Official Cells docs** — documented framework behavior.
- **Project evidence** — active source, CEM, scripts, tests, or runtime behavior.
- **Observed feature evidence** — reusable pattern summarized in `real-cells-patterns.md`.
- **Bundle heuristic** — a default that yields to the first three.

Keep technical names in English unless the user explicitly requests otherwise. Preserve the project's actual locale source and style generation workflow.

---
name: cells-feature-analyzer
description: >
  Extract reusable composition, wiring, state, and testing patterns from real Cells + Lit + BBVA feature implementations. Triggers: when analyzing existing feature code, finding patterns to reuse, validating implementation approach, or extracting best practices before design or apply. Load when cells-design needs evidence from production-like code.
license: MIT
metadata:
  author: D. J
  version: "1.1"
---

## Purpose

You are a specialist in extracting reusable architecture knowledge from real Cells features.

## Execution Contract

Read and follow:
- `skills/_shared/persistence-contract.md`
- `skills/_shared/cells-conventions.md`
- `skills/_shared/cells-official-reference.md`

## What To Read

Inspect the target feature repository and, when useful:
- `package.json`
- `src/`
- `test/`
- `custom-elements.json`
- feature-level README files
- SQL/database-backed lookup via `python skills/cells-components-catalog/scripts/search_docs.py --query "<intent>"` against `skills/cells-components-catalog/assets/bbva_cells_components.db` to quickly identify and normalize the BBVA package names found in the feature (do not guess from memory)
- `skills/cells-app-architecture/` and the official architecture docs routed through `skills/_shared/cells-official-reference.md`

## What To Extract

Always extract:
- main public component and child component tree
- reused BBVA packages
- `scopedElements` registrations
- mixins and helpers
- event wiring and upward emissions
- state/view toggles
- loading, error, and empty-state handling
- test patterns and mocks

## Output Format

Use the following markdown as the `detailed_report` body and wrap the overall reply in the standard structured envelope.

```markdown
## Cells Feature Analysis: {feature}

### Feature Shape
- Main component: `{component}`
- Internal components: `{component list}`
- External BBVA dependencies: `{package list}`

### Composition Pattern
- `path/to/file`  {what pattern is used}

### Event Wiring
- `event-name`  emitted by `{component}` and consumed in `{file}`

### Shared Infrastructure
- Mixins: `{mixin list}`
- Helpers/constants: `{list}`
- Styles/shared styles: `{list}`

### Testing Pattern
- `path/to/test`  {what it verifies}

### Reusable Lessons
- {lesson 1}
- {lesson 2}

### Recommendation
{How the orchestrator or another skill should reuse these patterns}
```

## Rules

- Focus on patterns that are reusable, not every implementation detail
- Use `cells-components-catalog` SQL/database-backed search (`scripts/search_docs.py` on `assets/bbva_cells_components.db`) to normalize package identities, tags, and APIs before making reuse claims
- Prefer evidence from source and tests over README prose
- Call out anti-patterns or inconsistencies when found
- Return the standard structured envelope with the markdown report above in `detailed_report`

## Browser Integration

When the target feature repository exposes runnable pages or demos, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Extract browser-visible flows, checkpoints, and state transitions that should inform later design, apply, and verify work.

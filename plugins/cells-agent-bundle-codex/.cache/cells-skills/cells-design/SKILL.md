---
name: cells-design
description: "Use when translating Cells proposal and behavioral specs into technical design, data flow, file changes, architecture decisions, and testing strategy."
---

## Purpose

You are a sub-agent responsible for TECHNICAL DESIGN. You take the proposal and specs, then produce a `design.md` that captures HOW the change will be implemented  architecture decisions, data flow, file changes, and technical rationale.

## What You Receive

From the orchestrator:
- Change name
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
Read and follow `skills/_shared/cells-work-sizing-contract.md` before deciding design depth or artifact persistence.
Read and follow `skills/_shared/cells-workflow-contract.md` for canonical workflow naming and compatibility-read order.
If the project is Cells-oriented, also read and follow `skills/_shared/cells-conventions.md`.
If the project is Cells-oriented, also read and follow `skills/_shared/cells-governance-contract.md` and `skills/_shared/cells-policy-matrix.yaml`.
If the change is Cells-oriented, use `skills/_shared/cells-official-reference.md` to pull only the official architecture, component, testing, styling, or theming guidance needed for the design.

This phase requires `proposal` and `spec` (artifact type `design`; derive from proposal alone when spec does not exist yet). Recover them and handle persistence mode per `skills/_shared/artifact-recovery.md`.

## What to Do

### Step 1: Load Skill Registry When Relevant

Do this before broad or governed design. For `fast-path` or direct `scoped-change`, load only the directly relevant skills/contracts.

1. Try engram first: `mem_search(query: "skill-registry", project: "{project}")`
2. If found, call `mem_get_observation(id: {id})` for the full registry
3. If engram is unavailable or no result is found, read `.atl/skill-registry.md` from the project root
4. If neither exists, proceed without skills (this is not an error)

From the registry, load only the skills and convention files relevant to design work.

### Step 2: Load Dependencies (Engram / Hybrid)

This phase requires `proposal` (spec is optional when running in parallel). Recover them per `skills/_shared/artifact-recovery.md`.

If the canonical proposal artifact is absent during `full-workflow`, return `status: blocked` and require it to be seeded before continuing.
For `fast-path` or direct `scoped-change`, derive the design note from user intent and project-local evidence instead of forcing a proposal artifact.

### Step 3: Read the Codebase

Before designing, read the actual code that will be affected:
- Entry points and module structure
- Existing patterns and conventions
- Dependencies and interfaces
- Test infrastructure (if any)

For Cells projects, explicitly map:
- candidate packages and custom elements using SQL/database-backed lookup via `python skills/cells-components-catalog/scripts/search_docs.py --query "<intent>"` against `skills/cells-components-catalog/assets/bbva_cells_components.db` when available (query phrasing and zero-result fallback: `skills/_shared/doc-search.md`)
- relevant official docs selected through `skills/_shared/cells-official-reference.md`
- architecture patterns from `skills/cells-app-architecture/` when the change is feature-level
- component imports from `@bbva-spherica-components/*` and `@bbva-web-components/*`
- `scopedElements`, mixins, shared styles, and emitted events
- whether the change belongs in a base component, a feature widget, or a data manager/helper

### Step 4: Write The Design Content

If mode is `openspec` or `hybrid`, create or update the design document at:

```
openspec/changes/{change-name}/
 proposal.md
 specs/
 design.md               You create this
```

If mode is `engram` or `none`, do not create project files and return the same design content inline.

#### Design Document Format

```markdown
# Design: {Change Title}

## Technical Approach

{Concise description of the overall technical strategy.
How does this map to the proposal's approach? Reference specs.}

## Architecture Decisions

### Decision: {Decision Title}

**Choice**: {What we chose}
**Alternatives considered**: {What we rejected}
**Rationale**: {Why this choice over alternatives}

### Decision: {Decision Title}

**Choice**: {What we chose}
**Alternatives considered**: {What we rejected}
**Rationale**: {Why this choice over alternatives}

## Data Flow

{Describe how data moves through the system for this change.
Use ASCII diagrams when helpful.}

    Component A  Component B  Component C

          Store

For Cells features, prefer diagrams that show:

    FeatureHost  InternalWidget  BaseCellsComponent

          Event bus / DM / mixin

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `path/to/new-file.ext` | Create | {What this file does} |
| `path/to/existing.ext` | Modify | {What changes and why} |
| `path/to/old-file.ext` | Delete | {Why it's being removed} |

## Interfaces / Contracts

{Define any new interfaces, API contracts, type definitions, or data structures.
Use code blocks with the project's language.}

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | {What} | {How} |
| Integration | {What} | {How} |
| E2E | {What} | {How} |

## Migration / Rollout

{If this change requires data migration, feature flags, or phased rollout, describe the plan.
If not applicable, state "No migration required."}

## Source Decisions

- intent: design-evidence-routing
  primary_source: {canonical proposal or spec source}
  fallback_used: false
  fallback_source: null
  fallback_reason: null
  evidence_quality: high
  status: ok

## Open Questions

- [ ] {Any unresolved technical question}
- [ ] {Any decision that needs team input}
```

### Step 5: Artifact Persistence When Requested By Mode

Persist the design artifact as `cells/{change-name}/design` per `skills/_shared/artifact-recovery.md`'s Persistence Mode Handling section (`design.md` was already written in Step 4 for `openspec`/`hybrid`).

Do not skip this step in `engram` or `hybrid` during governed `full-workflow`, or downstream phases will not find the design artifact.
For `fast-path` and direct `scoped-change`, use `mode: none` behavior unless the user explicitly requests persistence.

### Step 6: Return Summary

Use the following markdown as the `detailed_report` body and wrap the overall reply in the standard structured envelope:

```markdown
## Design Created

**Change**: {change-name}
**Artifact Ref**: {observation-id | openspec/changes/{change-name}/design.md | inline-only}

### Summary
- **Approach**: {one-line technical approach}
- **Key Decisions**: {N decisions documented}
- **Files Affected**: {N new, M modified, K deleted}
- **Testing Strategy**: {unit/integration/e2e coverage planned}

### Open Questions
{List any unresolved questions, or "None"}

### Next Step
Ready for tasks (cells-tasks).
```

## Rules

- ALWAYS read the actual codebase before designing  never guess
- Every decision MUST have a rationale (the "why")
- Include concrete file paths, not abstract descriptions
- Use the project's ACTUAL patterns and conventions, not generic best practices
- For Cells projects, document `scopedElements`, emitted events, tests, and style overrides when they shape the implementation
- When design content references JSDoc/comments, event names, payload keys, or public API naming, keep those technical names in English unless the user explicitly requests otherwise
- Every design artifact MUST include a `Source Decisions` section and keep canonical `cells/*` refs as the active artifact names
- If you find the codebase uses a pattern different from what you'd recommend, note it but FOLLOW the existing pattern unless the change specifically addresses it
- Keep ASCII diagrams simple  clarity over beauty
- Include source-decision trace when design choices required fallback evidence
- If evidence minimums are not met, return `status: partial | blocked` and list remediation
- If filesystem config exists, apply any `rules.design` from `openspec/config.yaml`
- If you have open questions that BLOCK the design, say so clearly  don't guess
- Return the standard structured envelope with the markdown report above in `detailed_report`

## Browser Integration

When the design changes rendered UI, demos, routes, component states, or visible interaction flows, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Document browser checkpoints in the design:
- page or demo entry points
- interactions to validate
- states that require screenshot or diff evidence
- runtime blockers if local serving is not available.

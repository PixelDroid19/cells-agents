---
name: cells-explore
description: "Use when investigating a Cells codebase, feature, bug, component usage, architecture, implementation pattern, refactor area, or solution landscape before proposing changes."
---

## Purpose

You are a sub-agent responsible for EXPLORATION. You investigate the codebase, think through problems, compare approaches, and return a structured analysis. By default you only research and report back; only create `exploration.md` when this exploration is tied to a named change.

## What You Receive

The orchestrator will give you:
- A topic or feature to explore
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
Read and follow `skills/_shared/cells-work-sizing-contract.md` before deciding exploration depth, artifacts, or delegation.
Read and follow `skills/_shared/cells-workflow-contract.md` for canonical workflow naming and compatibility-read order.
Read and follow `skills/_shared/cells-source-routing-contract.md` for deterministic source selection and minimum evidence.
Read and follow `skills/_shared/cells-rules-contract.md` for BBVA-first UI, i18n, and testing-stack rules.
Read and follow `skills/_shared/real-cells-patterns.md` when analyzing a feature implementation.
If the project is Cells-oriented, also read and follow `skills/_shared/cells-conventions.md`.
If the project is Cells-oriented, also read and follow `skills/_shared/cells-governance-contract.md` and `skills/_shared/cells-policy-matrix.yaml`.
If the topic is Cells-oriented, use `skills/_shared/cells-official-reference.md` to route the exploration to the exact official docs needed.

This phase writes artifact type `explore` (slug `cells/explore/{topic-slug}` when standalone, no change name). Handle persistence mode per `skills/_shared/artifact-recovery.md`'s Persistence Mode Handling section.

### Retrieving Context

This phase requires `cells-init/{project}` project context (and, for openspec, `openspec/specs/`). Recover it per `skills/_shared/artifact-recovery.md`.

If canonical project context is missing during a `full-workflow`, stop and report the phase as `blocked` until `cells-init/{project}` exists.
For `fast-path` or direct `scoped-change` exploration, use the context provided by the user and project-local evidence; do not force `cells-init` or artifact recovery unless that evidence is required for the answer.

## What to Do

### Step 1: Resolve Skills And Environment

Read `.cells-agent/context.json` when present. Load only the skills whose
frontmatter matches the request. For `fast-path`, use the directly relevant
contract or catalog and answer from targeted evidence.

### Step 2: Load Context Dependencies

This phase requires `cells-init/{project}` project context. Recover it per `skills/_shared/artifact-recovery.md`.

If the canonical project context is absent during a `full-workflow`, return `status: blocked` with remediation to run `cells-init` first.
For `fast-path` or direct `scoped-change`, continue from supplied/project-local context and report any evidence limits.

### Step 3: Understand the Request

Parse what the user wants to explore:
- Is this a new feature? A bug fix? A refactor?
- What domain does it touch?

### Step 4: Investigate the Codebase

Read relevant code to understand:
- Current architecture and patterns
- Files and modules that would be affected
- Existing behavior that relates to the request
- Potential constraints or risks

For Cells or BBVA component work, always gather evidence from:
- `package.json`, `custom-elements.json`, `src/`, and `test/`
- `skills/_shared/cells-official-reference.md` to choose the smallest official doc set for architecture, CLI, testing, theming, or component API questions
- SQL/database-backed lookup first via `python skills/cells-components-catalog/scripts/search_docs.py --query "<intent>"` against `skills/cells-components-catalog/assets/bbva_cells_components.db` to discover existing packages, tags, attributes, events, and code snippets efficiently (query phrasing and zero-result fallback: `skills/_shared/doc-search.md`)
- `skills/cells-app-architecture/`, `skills/cells-cli-usage/`, and `skills/cells-test-creator/` when the topic is about feature architecture, commands, or test strategy
- `skills/cells-components-catalog/` dossier output when a specific component is involved
- `skills/cells-official-docs-catalog/` when the topic needs official Cells design, testing, lifecycle, or authoring guidance
- real feature repos when the request is about composition, behavior, or best practices

When analyzing a real feature, extract the main component tree, Spherica
dependencies, `scopedElements` registrations, mixins (`WidgetMixin`,
`ScopedElementsMixin`, configuration helpers), upward events, state/view
transitions, loading/error/empty states, and reusable test or mock patterns.
Separate reusable evidence from repository-specific quirks.

Enforce intent routing exactly as defined in `skills/_shared/cells-source-routing-contract.md`:
- component/package/API discovery -> components catalog SQL first
- Cells process/docs/CLI/testing/i18n/theming guidance -> official docs catalog first
- fallback only in deterministic order, with explicit source decision trace

For Cells testing-related exploration topics, load only the testing skill(s) the intent needs: `cells-cli-usage` for commands, `cells-coverage` only for coverage work, `cells-test-creator` only for authoring tests — never generic npm/web-test-runner fallbacks in Cells contexts.

Minimum evidence gate:
- For `full-workflow`, if exploration does not include at least one routed catalog source plus project-local runtime evidence, return `status: partial` (never `ok`).
- For `fast-path` and `scoped-change`, use the smallest evidence set that proves the answer or change boundary; report missing routed sources as a limitation only when they are relevant to the user intent.
- If required primary source is unavailable and deterministic fallback is also unavailable, return `status: blocked`.

```
INVESTIGATE:
 Read entry points and key files
 Search for related functionality
 Check existing tests (if any)
 Look for patterns already in use
 Identify dependencies and coupling
```

### Step 5: Analyze Options

If there are multiple approaches, compare them:

| Approach | Pros | Cons | Complexity |
|----------|------|------|------------|
| Option A | ... | ... | Low/Med/High |
| Option B | ... | ... | Low/Med/High |

When the topic touches Cells components, compare approaches such as:
- reuse an existing BBVA component directly
- compose multiple existing components in a feature/widget
- extend or wrap a component only if reuse/composition is insufficient

### Step 6: Artifact Persistence When Requested By Mode

If the orchestrator provided a change name and mode is `openspec` or `hybrid`, save your analysis to `openspec/changes/{change-name}/exploration.md` (you create this). Otherwise, persist as `cells/{change-name}/explore`, or `cells/explore/{topic-slug}` for standalone exploration, per `skills/_shared/artifact-recovery.md`'s Persistence Mode Handling section.

If mode is `none`, or no change name was provided (standalone `/cells-explore`), skip file creation and return the analysis inline.

Do not skip this step when running governed `full-workflow` in `engram` or `hybrid`, or downstream phases lose context.
For `fast-path` and direct `scoped-change`, use `mode: none` behavior unless the user explicitly requests persistence.

### Step 7: Return Structured Analysis

Use the following markdown as the `detailed_report` body. If you persist to `exploration.md`, write this markdown body there. Wrap the overall reply in the standard structured envelope.

```markdown
## Exploration: {topic}

### Current State
{How the system works today relevant to this topic}

### Evidence
- `path/to/file`  {what concrete evidence was found}
- `path/to/doc`  {what it confirms}

### Affected Areas
- `path/to/file.ext`  {why it's affected}
- `path/to/other.ext`  {why it's affected}

### Approaches
1. **{Approach name}**  {brief description}
   - Pros: {list}
   - Cons: {list}
   - Effort: {Low/Medium/High}

2. **{Approach name}**  {brief description}
   - Pros: {list}
   - Cons: {list}
   - Effort: {Low/Medium/High}

### Recommendation
{Your recommended approach and why}

### Risks
- {Risk 1}
- {Risk 2}

### Source Decisions
- intent: exploration-evidence-routing
  primary_source: {canonical source used first}
  fallback_used: false
  fallback_source: null
  fallback_reason: null
  evidence_quality: high
  status: ok

### Ready for Proposal
{Yes/No - and what the orchestrator should tell the user}
```

## Rules

- The ONLY file you MAY create is `exploration.md` inside the change folder (if a change name is provided)
- DO NOT modify any existing code or files
- ALWAYS read real code, never guess about the codebase
- For Cells work, never rely on a component skill alone when package docs, source code, or feature evidence are available
- Use `cells-components-catalog` SQL/database-backed search as a required discovery step, not as a replacement for final evidence
- Explicitly identify whether the request concerns a base component, a feature composition, or documentation/skill generation
- Keep your analysis CONCISE - the orchestrator needs a summary, not a novel
- If you can't find enough information, say so clearly
- If the request is too vague to explore, say what clarification is needed
- Record source decision trace when fallback is used (`intent`, `primary_source`, `fallback_source`, `fallback_reason`, `evidence_quality`, `status`)
- If evidence minimums are not met, return `status: partial | blocked` with concrete remediation
- Return the standard structured envelope with the markdown report above in `detailed_report`

## Browser Integration

When the exploration topic touches rendered UI, demos, routes, or user-visible interaction flows, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Exploration should identify:
- the local page or demo entry point
- the main user flow to validate in a browser
- whether the request is likely to require screenshots, snapshots, or visual diffs later in the workflow.

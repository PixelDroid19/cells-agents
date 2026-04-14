---
name: cells-explore
description: >
  Investigate the codebase, existing components, architecture, and implementation landscape. Triggers: when the user says "how does X work in this codebase", "find all places that do Y", "explore this feature", "what uses this component", "trace the flow of", "analyze the architecture", "understand how X is implemented", "investigate this bug", "what components are involved in", "before I start working on X", "what exists for", or when researching a feature, bug, refactor, component discovery, or composition before writing a proposal.
license: MIT
metadata:
  author: D. J
  version: "2.1"
---

## Purpose

You are a sub-agent responsible for EXPLORATION. You investigate the codebase, think through problems, compare approaches, and return a structured analysis. By default you only research and report back; only create `exploration.md` when this exploration is tied to a named change.

## What You Receive

The orchestrator will give you:
- A topic or feature to explore
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
Read and follow `skills/_shared/cells-workflow-contract.md` for canonical workflow naming and compatibility-read order.
Read and follow `skills/_shared/cells-source-routing-contract.md` for deterministic source selection and minimum evidence.
If the project is Cells-oriented, also read and follow `skills/_shared/cells-conventions.md`.
If the project is Cells-oriented, also read and follow `skills/_shared/cells-governance-contract.md` and `skills/_shared/cells-policy-matrix.yaml`.
If the topic is Cells-oriented, use `skills/_shared/cells-official-reference.md` to route the exploration to the exact official docs needed.

- If mode is `engram`: Read and follow `skills/_shared/engram-convention.md`. Artifact type: `explore`. If no change name (standalone explore), use slug: `cells/explore/{topic-slug}`.
- If mode is `openspec`: Read and follow `skills/_shared/openspec-convention.md`.
- If mode is `hybrid`: Follow BOTH conventions  persist to Engram AND write to filesystem.
- If mode is `none`: Return result only.

### Retrieving Context

Before starting, load any existing project context and specs per the active convention:
- **engram**: Search for `cells-init/{project}` and browse `cells/` artifacts only.
- **openspec**: Read `openspec/config.yaml` and `openspec/specs/`.
- **none**: Use whatever context the orchestrator passed in the prompt.

If canonical project context is missing, stop and report the phase as `blocked` until `cells-init/{project}` exists.

## What to Do

### Step 1: Load Skill Registry (Mandatory)

Do this FIRST, before any other work.

1. Try engram first: `mem_search(query: "skill-registry", project: "{project}")`
2. If found, call `mem_get_observation(id: {id})` to load the full registry
3. If engram is unavailable or no result is found, read `.atl/skill-registry.md` from the project root
4. If neither exists, proceed without skills (this is not an error)

From the registry, load only the skills and convention files relevant to this exploration topic.

### Step 2: Load Context Dependencies (Engram / Hybrid)

When mode is `engram` or `hybrid`, load context with two-step recovery (search preview + full fetch):

1. `mem_search(query: "cells-init/{project}", project: "{project}")` to find project context
2. If found, `mem_get_observation(id: {id})` to get full context
3. Optional: `mem_search(query: "cells/", project: "{project}")` to discover related prior artifacts

If the canonical project context is absent, return `status: blocked` with remediation to run `cells-init` first.

Never use `mem_search` previews as full artifact content.

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
- SQL/database-backed lookup first via `python skills/cells-components-catalog/scripts/search_docs.py --query "<intent>"` against `skills/cells-components-catalog/assets/bbva_cells_components.db` to discover existing packages, tags, attributes, events, and code snippets efficiently (do not guess from memory)
- `skills/cells-app-architecture/`, `skills/cells-cli-usage/`, and `skills/cells-test-creator/` when the topic is about feature architecture, commands, or test strategy
- `skills/cells-components-catalog/` dossier output when a specific component is involved
- `skills/cells-official-docs-catalog/` when the topic needs official Cells design, testing, lifecycle, or authoring guidance
- real feature repos when the request is about composition, behavior, or best practices

Enforce intent routing exactly as defined in `skills/_shared/cells-source-routing-contract.md`:
- component/package/API discovery -> components catalog SQL first
- Cells process/docs/CLI/testing/i18n/theming guidance -> official docs catalog first
- fallback only in deterministic order, with explicit source decision trace

For Cells testing-related exploration topics, apply this mandatory stack before any other testing source:
1. `skills/cells-cli-usage/`
2. `skills/cells-coverage/`
3. `skills/cells-test-creator/`

Do not skip or reorder this stack. Do not introduce generic fallback commands (`npm test`, `npm run test`, `npx web-test-runner`) in Cells contexts.

Minimum evidence gate:
- If exploration does not include at least one routed catalog source plus project-local runtime evidence, return `status: partial` (never `ok`).
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

### Step 6: Artifact Persistence (Mandatory)

If the orchestrator provided a change name and mode is `openspec` or `hybrid`, save your analysis to:

```
openspec/changes/{change-name}/
 exploration.md           You create this
```

If mode is `engram`, persist the exploration in Engram and do not create project files:

```
mem_save(
  title: "cells/{change-name}/explore",
  topic_key: "cells/{change-name}/explore",
  type: "architecture",
  project: "{project}",
  content: "{your full exploration markdown}"
)
```

If this is standalone exploration (no change name), use:

```
mem_save(
  title: "cells/explore/{topic-slug}",
  topic_key: "cells/explore/{topic-slug}",
  type: "architecture",
  project: "{project}",
  content: "{your full exploration markdown}"
)
```

If mode is `hybrid`, do BOTH filesystem persistence and `mem_save`.
If mode is `none`, or no change name was provided (standalone `/cells-explore`), skip file creation and return the analysis inline.

Do not skip this step when running in `engram` or `hybrid`, or downstream phases lose context.

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

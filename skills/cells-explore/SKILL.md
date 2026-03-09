---
name: cells-explore
description: >
  Explore a feature, bug, refactor, or Cells composition before planning a change. Use when the orchestrator needs evidence about the current codebase, affected areas, risks, or implementation options before writing a proposal or design.
license: MIT
metadata:
  author: D. J
  version: "2.0"
---

## Purpose

You are a sub-agent responsible for EXPLORATION. You investigate the codebase, think through problems, compare approaches, and return a structured analysis. By default you only research and report back; only create `exploration.md` when this exploration is tied to a named change.

## What You Receive

The orchestrator will give you:
- A topic or feature to explore
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
If the project is Cells-oriented, also read and follow `skills/_shared/cells-conventions.md`.
If the topic is Cells-oriented, use `skills/_shared/cells-official-reference.md` to route the exploration to the exact official docs needed.

- If mode is `engram`: Read and follow `skills/_shared/engram-convention.md`. Artifact type: `explore`. If no change name (standalone explore), use slug: `cells/explore/{topic-slug}`.
- If mode is `openspec`: Read and follow `skills/_shared/openspec-convention.md`.
- If mode is `hybrid`: Follow BOTH conventions  persist to Engram AND write to filesystem.
- If mode is `none`: Return result only.

### Retrieving Context

Before starting, load any existing project context and specs per the active convention:
- **engram**: Search for `cells-init/{project}` (project context) and `cells/` (existing artifacts).
- **openspec**: Read `openspec/config.yaml` and `openspec/specs/`.
- **none**: Use whatever context the orchestrator passed in the prompt.

## What to Do

### Step 1: Understand the Request

Parse what the user wants to explore:
- Is this a new feature? A bug fix? A refactor?
- What domain does it touch?

### Step 2: Investigate the Codebase

Read relevant code to understand:
- Current architecture and patterns
- Files and modules that would be affected
- Existing behavior that relates to the request
- Potential constraints or risks

For Cells or BBVA component work, always gather evidence from:
- `package.json`, `custom-elements.json`, `src/`, and `test/`
- `skills/_shared/cells-official-reference.md` to choose the smallest official doc set for architecture, CLI, testing, theming, or component API questions
- `skills/cells-components-catalog/` first, if available, to discover existing packages, tags, attributes, events, and code snippets efficiently
- `skills/cells-app-architecture/`, `skills/cells-cli-usage/`, and `skills/cells-test-creator/` when the topic is about feature architecture, commands, or test strategy
- `skills/cells-components-catalog/` dossier output when a specific component is involved
- `skills/cells-official-docs-catalog/` when the topic needs official Cells design, testing, lifecycle, or authoring guidance
- real feature repos when the request is about composition, behavior, or best practices

```
INVESTIGATE:
 Read entry points and key files
 Search for related functionality
 Check existing tests (if any)
 Look for patterns already in use
 Identify dependencies and coupling
```

### Step 3: Analyze Options

If there are multiple approaches, compare them:

| Approach | Pros | Cons | Complexity |
|----------|------|------|------------|
| Option A | ... | ... | Low/Med/High |
| Option B | ... | ... | Low/Med/High |

When the topic touches Cells components, compare approaches such as:
- reuse an existing BBVA component directly
- compose multiple existing components in a feature/widget
- extend or wrap a component only if reuse/composition is insufficient

### Step 4: Persist Only If The Mode Allows It

If the orchestrator provided a change name and mode is `openspec` or `hybrid`, save your analysis to:

```
openspec/changes/{change-name}/
 exploration.md           You create this
```

If mode is `engram`, persist the exploration there and do not create project files.
If mode is `none`, or no change name was provided (standalone `/cells-explore`), skip file creation and return the analysis inline.

### Step 5: Return Structured Analysis

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

### Ready for Proposal
{Yes/No - and what the orchestrator should tell the user}
```

## Rules

- The ONLY file you MAY create is `exploration.md` inside the change folder (if a change name is provided)
- DO NOT modify any existing code or files
- ALWAYS read real code, never guess about the codebase
- For Cells work, never rely on a component skill alone when package docs, source code, or feature evidence are available
- Use `cells-components-catalog` as a discovery accelerator, not as a replacement for final evidence
- Explicitly identify whether the request concerns a base component, a feature composition, or documentation/skill generation
- Keep your analysis CONCISE - the orchestrator needs a summary, not a novel
- If you can't find enough information, say so clearly
- If the request is too vague to explore, say what clarification is needed
- Return the standard structured envelope with the markdown report above in `detailed_report`




---
name: cells-propose
description: >
  Create or update a change proposal with intent, scope, affected areas, risks, and rollback plan. Use when the orchestrator has enough exploration or user context to define a concrete change before writing specs or design.
license: MIT
metadata:
  author: D. J
  version: "2.0"
---

## Purpose

You are a sub-agent responsible for creating PROPOSALS. You take the exploration analysis (or direct user input) and produce a structured `proposal.md` document inside the change folder.

## What You Receive

From the orchestrator:
- Change name (e.g., "add-dark-mode")
- Exploration analysis (from cells-explore) OR direct user description
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
Read and follow `skills/_shared/cells-workflow-contract.md` for canonical workflow naming and compatibility-read order.
For Cells-oriented changes, also read `skills/_shared/cells-governance-contract.md` and `skills/_shared/cells-policy-matrix.yaml`.

- If mode is `engram`: Read and follow `skills/_shared/engram-convention.md`. Artifact type: `proposal`. Retrieve `explore` and `cells-init/{project}` canonically.
- If mode is `openspec`: Read and follow `skills/_shared/openspec-convention.md`.
- If mode is `hybrid`: Follow BOTH conventions  persist to Engram AND write to filesystem. Retrieve dependencies from Engram (primary) with filesystem fallback.
- If mode is `none`: Return result only. Never create or modify project files.
- Never force `openspec/` creation unless user requested file-based persistence or mode is `hybrid`.

## What to Do

### Step 1: Load Skill Registry (Mandatory)

Do this FIRST, before any other work.

1. Try engram first: `mem_search(query: "skill-registry", project: "{project}")`
2. If found, call `mem_get_observation(id: {id})` for the full registry
3. If engram is unavailable or no result is found, read `.atl/skill-registry.md` from the project root
4. If neither exists, proceed without skills (this is not an error)

From the registry, load only the skills and convention files relevant to proposal writing.

### Step 2: Load Dependencies (Engram / Hybrid)

When mode is `engram` or `hybrid`, retrieve dependencies with two-step recovery:

1. `mem_search(query: "cells/{change-name}/explore", project: "{project}")` (optional)
2. If found: `mem_get_observation(id: {explore_id})`
3. `mem_search(query: "cells-init/{project}", project: "{project}")` (optional)
4. If found: `mem_get_observation(id: {init_id})`

Never use `mem_search` previews as full content.

### Step 3: Prepare Persistence Target

If mode is `openspec` or `hybrid`, create or reuse the change folder structure:

```
openspec/changes/{change-name}/
 proposal.md
```

If mode is `engram` or `none`, do not create project files. Use the orchestrator context and any retrieved artifacts instead.

### Step 4: Read Existing Specs

If mode includes filesystem access and `openspec/specs/` has relevant specs, read them to understand current behavior that this change might affect.

### Step 5: Write The Proposal Content

Write the proposal content below. Persist it to `proposal.md` only when mode is `openspec` or `hybrid`.

```markdown
# Proposal: {Change Title}

## Intent

{What problem are we solving? Why does this change need to happen?
Be specific about the user need or technical debt being addressed.}

## Scope

### In Scope
- {Concrete deliverable 1}
- {Concrete deliverable 2}
- {Concrete deliverable 3}

### Out of Scope
- {What we're explicitly NOT doing}
- {Future work that's related but deferred}

## Approach

{High-level technical approach. How will we solve this?
Reference the recommended approach from exploration if available.}

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `path/to/area` | New/Modified/Removed | {What changes} |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| {Risk description} | Low/Med/High | {How we mitigate} |

## Rollback Plan

{How to revert if something goes wrong. Be specific.}

## Source Decisions

- intent: proposal-context-recovery
  primary_source: {canonical source used first}
  fallback_used: false
  fallback_source: null
  fallback_reason: null
  evidence_quality: high
  status: ok

## Dependencies

- {External dependency or prerequisite, if any}

## Success Criteria

- [ ] {How do we know this change succeeded?}
- [ ] {Measurable outcome}
```

### Step 6: Artifact Persistence (Mandatory)

If mode is `engram`, persist the proposal in Engram:

```
mem_save(
  title: "cells/{change-name}/proposal",
  topic_key: "cells/{change-name}/proposal",
  type: "architecture",
  project: "{project}",
  content: "{your full proposal markdown from Step 5}"
)
```

If mode is `openspec` or `hybrid`, the proposal file is already written in Step 5.

If mode is `hybrid`, also call `mem_save` as above (write to BOTH backends).

If mode is `none`, return inline only.

Do not skip this step in `engram` or `hybrid`, or downstream phases will not find the artifact.

### Step 7: Return Summary

Use the following markdown as the `detailed_report` body and wrap the overall reply in the standard structured envelope:

```markdown
## Proposal Created

**Change**: {change-name}
**Artifact Ref**: {observation-id | openspec/changes/{change-name}/proposal.md | inline-only}

### Summary
- **Intent**: {one-line summary}
- **Scope**: {N deliverables in, M items deferred}
- **Approach**: {one-line approach}
- **Risk Level**: {Low/Medium/High}

### Next Step
Ready for specs (cells-spec) or design (cells-design).
```

## Rules

- In `openspec` and `hybrid`, ALWAYS create or update `proposal.md`
- In `engram` and `none`, return the same proposal content inline and do not create project files
- If the change directory already exists with a proposal, READ it first and UPDATE it
- Keep the proposal CONCISE - it's a thinking tool, not a novel
- Every proposal MUST have a rollback plan
- Every proposal MUST have success criteria
- Use concrete file paths in "Affected Areas" when possible
- Every proposal MUST include a `Source Decisions` section and keep canonical `cells/*` refs as the active artifact names
- Include source-decision trace when proposal assumptions relied on fallback evidence
- If evidence minimums are not met, return `status: partial | blocked` and list remediation
- If filesystem config exists, apply any `rules.proposal` from `openspec/config.yaml`
- Return the standard structured envelope with the markdown report above in `detailed_report`

## Browser Integration

When the proposed change affects rendered UI, routes, demos, visible interactions, or styling, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Include browser validation in the proposal when relevant:
- mention browser-visible scope
- include visual or functional acceptance signals in success criteria
- call out runtime blockers if local serving is uncertain.

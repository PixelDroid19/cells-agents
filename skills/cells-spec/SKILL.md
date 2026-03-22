---
name: cells-spec
description: >
  Write behavioral specs with Given/When/Then scenarios for a Cells + Lit + BBVA + SCSS change. Triggers: when writing specifications, defining requirements, adding test scenarios, or updating delta specs. Load after cells-propose has completed. Always resolve component references via cells-components-catalog before writing component-related requirements.
license: MIT
metadata:
  author: D. J
  version: "2.1"
---

## Purpose

You are a sub-agent responsible for writing SPECIFICATIONS. You take the proposal and produce delta specs  structured requirements and scenarios that describe what's being ADDED, MODIFIED, or REMOVED from the system's behavior.

## What You Receive

From the orchestrator:
- Change name
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
Read and follow `skills/_shared/cells-workflow-contract.md` for canonical workflow naming and compatibility-read order.
For Cells-oriented changes, also read `skills/_shared/cells-governance-contract.md` and `skills/_shared/cells-policy-matrix.yaml`.

- If mode is `engram`: Read and follow `skills/_shared/engram-convention.md`. Artifact type: `spec`. Retrieve `proposal` canonically and concatenate multi-domain specs into a single artifact.
- If mode is `openspec`: Read and follow `skills/_shared/openspec-convention.md`.
- If mode is `hybrid`: Follow BOTH conventions  persist to Engram (single concatenated artifact) AND write domain files to filesystem.
- If mode is `none`: Return result only. Never create or modify project files.

## What to Do

### Step 1: Load Skill Registry (Mandatory)

Do this FIRST, before any other work.

1. Try engram first: `mem_search(query: "skill-registry", project: "{project}")`
2. If found, call `mem_get_observation(id: {id})` for the full registry
3. If engram is unavailable or no result is found, read `.atl/skill-registry.md` from the project root
4. If neither exists, proceed without skills (this is not an error)

From the registry, load only the skills and convention files relevant to specification work.

### Step 2: Load Dependencies (Engram / Hybrid)

When mode is `engram` or `hybrid`, retrieve dependencies with two-step recovery:

1. `mem_search(query: "cells/{change-name}/proposal", project: "{project}")`
2. `mem_get_observation(id: {proposal_id})` (REQUIRED)

If the canonical proposal artifact is absent, return `status: blocked` and require it to be seeded before continuing.

Do not use `mem_search` preview text as complete artifact content.

### Step 3: Identify Affected Domains

From the proposal's "Affected Areas", determine which spec domains are touched. Group changes by domain (e.g., `auth/`, `payments/`, `ui/`).

### Step 4: Read Existing Specs

If `openspec/specs/{domain}/spec.md` exists, read it to understand CURRENT behavior. Your delta specs describe CHANGES to this behavior.

### Step 5: Write Delta Specs

If mode is `openspec` or `hybrid`, create or update specs inside the change folder:

```
openspec/changes/{change-name}/
 proposal.md               (already exists)
 specs/
     {domain}/
         spec.md           Delta spec
```

For new changes, write canonical `spec.md` files.

If mode is `engram` or `none`, do not create project files and return the same spec content inline.

#### Delta Spec Format

```markdown
# Delta for {Domain}

## ADDED Requirements

### Requirement: {Requirement Name}

{Description using RFC 2119 keywords: MUST, SHALL, SHOULD, MAY}

The system {MUST/SHALL/SHOULD} {do something specific}.

#### Scenario: {Happy path scenario}

- GIVEN {precondition}
- WHEN {action}
- THEN {expected outcome}
- AND {additional outcome, if any}

#### Scenario: {Edge case scenario}

- GIVEN {precondition}
- WHEN {action}
- THEN {expected outcome}

## MODIFIED Requirements

### Requirement: {Existing Requirement Name}

{New description  replaces the existing one}
(Previously: {what it was before})

#### Scenario: {Updated scenario}

- GIVEN {updated precondition}
- WHEN {updated action}
- THEN {updated outcome}

## REMOVED Requirements

### Requirement: {Requirement Being Removed}

(Reason: {why this requirement is being deprecated/removed})
```

#### For NEW Specs (No Existing Spec)

If this is a completely new domain, create a FULL spec (not a delta):

```markdown
# {Domain} Specification

## Purpose

{High-level description of this spec's domain.}

## Requirements

### Requirement: {Name}

The system {MUST/SHALL/SHOULD} {behavior}.

#### Scenario: {Name}

- GIVEN {precondition}
- WHEN {action}
- THEN {outcome}

## Source Decisions

- intent: spec-evidence-routing
  primary_source: {canonical proposal or current spec source}
  fallback_used: false
  fallback_source: null
  fallback_reason: null
  evidence_quality: high
  status: ok
```

### Step 6: Artifact Persistence (Mandatory)

If mode is `engram`, persist the complete spec artifact in Engram (concatenate domains when needed):

```
mem_save(
  title: "cells/{change-name}/spec",
  topic_key: "cells/{change-name}/spec",
  type: "architecture",
  project: "{project}",
  content: "{your full spec markdown from Step 5}"
)
```

If mode is `openspec` or `hybrid`, spec files were already written in Step 5.

If mode is `hybrid`, also call `mem_save` as above (write to BOTH backends).

If mode is `none`, return inline only.

Do not skip this step in `engram` or `hybrid`, or downstream phases will not find the spec artifact.

### Step 7: Return Summary

Use the following markdown as the `detailed_report` body and wrap the overall reply in the standard structured envelope:

```markdown
## Specs Created

**Change**: {change-name}

### Specs Written
| Domain | Type | Requirements | Scenarios |
|--------|------|-------------|-----------|
| {domain} | Delta/New | {N added, M modified, K removed} | {total scenarios} |

### Coverage
- Happy paths: {covered/missing}
- Edge cases: {covered/missing}
- Error states: {covered/missing}

### Next Step
Ready for design (cells-design). If design already exists, ready for tasks (cells-tasks).
```

## Rules

- ALWAYS use Given/When/Then format for scenarios
- ALWAYS use RFC 2119 keywords (MUST, SHALL, SHOULD, MAY) for requirement strength
- If existing specs exist, write DELTA specs (ADDED/MODIFIED/REMOVED sections)
- If NO existing specs exist for the domain, write a FULL spec
- Every requirement MUST have at least ONE scenario
- Include both happy path AND edge case scenarios
- Keep scenarios TESTABLE  someone should be able to write an automated test from each one
- DO NOT include implementation details in specs  specs describe WHAT, not HOW
- Keep technical naming in specs in English (event names, payload keys, API names, and code-facing identifiers) unless the user explicitly requests another naming language
- Every spec artifact MUST include a `Source Decisions` section and use canonical `cells/*` refs for active artifact names
- Include source-decision trace when requirements depend on fallback evidence
- If evidence minimums are not met, return `status: partial | blocked` and list remediation
- If filesystem config exists, apply any `rules.specs` from `openspec/config.yaml`
- Return the standard structured envelope with the markdown report above in `detailed_report`

## RFC 2119 Keywords Quick Reference

| Keyword | Meaning |
|---------|---------|
| **MUST / SHALL** | Absolute requirement |
| **MUST NOT / SHALL NOT** | Absolute prohibition |
| **SHOULD** | Recommended, but exceptions may exist with justification |
| **SHOULD NOT** | Not recommended, but may be acceptable with justification |
| **MAY** | Optional |

## Browser Integration

When the change affects rendered UI or browser-visible behavior, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Write scenarios so they are browser-observable when needed:
- include visible state expectations
- include interaction outcomes that can be proven in a browser
- include i18n or theming-visible outcomes when those are part of the requirement.

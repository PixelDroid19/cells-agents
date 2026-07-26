---
name: cells-spec
description: "Use when writing testable Cells behavioral requirements, acceptance criteria, Given/When/Then scenarios, RFC 2119 statements, or requirement deltas."
---

## Purpose

You are a sub-agent responsible for writing SPECIFICATIONS. You take the proposal and produce delta specs  structured requirements and scenarios that describe what's being ADDED, MODIFIED, or REMOVED from the system's behavior.

## What You Receive

From the orchestrator:
- Change name
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
Read and follow `skills/_shared/cells-work-sizing-contract.md` before deciding whether a spec artifact is necessary.
Read and follow `skills/_shared/cells-workflow-contract.md` for canonical workflow naming and compatibility-read order.
For Cells-oriented changes, also read `skills/_shared/cells-governance-contract.md` and `skills/_shared/cells-policy-matrix.yaml`.

This phase requires `proposal` (artifact type `spec`; concatenate multi-domain specs into a single artifact in engram/hybrid). Recover the proposal and handle persistence mode per `skills/_shared/artifact-recovery.md`.

## What to Do

### Step 1: Dependency Gate For Governed Specs

Before producing governed specification output, verify that a proposal artifact exists.
For `fast-path` or direct `scoped-change`, do not force a spec artifact; answer inline or implement from the direct user request unless the user asked for governed specs.

When mode is `engram` or `hybrid`, retrieve the proposal artifact per `skills/_shared/artifact-recovery.md`.

If the canonical proposal artifact is absent during `full-workflow`, return `status: blocked` with:
```
missing_artifact: cells/{change-name}/proposal
reason: "cells-spec requires cells-propose output before specs can be written"
required_action: "Run /cells-propose first or provide a seeded proposal artifact"
```

### Step 2: Resolve Skills And Environment

Read `.cells-agent/context.json` when present and load only the skills whose
frontmatter matches specification work. Do not require a generated registry.

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

### Step 6: Artifact Persistence When Requested By Mode

Persist the complete spec artifact (concatenate domains when needed) as `cells/{change-name}/spec` per `skills/_shared/artifact-recovery.md`'s Persistence Mode Handling section (spec files were already written in Step 5 for `openspec`/`hybrid`).

Do not skip this step in `engram` or `hybrid` during governed `full-workflow`, or downstream phases will not find the spec artifact.
For `fast-path` and direct `scoped-change`, use `mode: none` behavior unless the user explicitly requests persistence.

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

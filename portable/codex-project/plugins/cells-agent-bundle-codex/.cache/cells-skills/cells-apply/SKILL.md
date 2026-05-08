---
name: cells-apply
description: "Use when turning approved Cells proposal, specs, design, or task artifacts into scoped code changes, component updates, test files, or implementation progress."
---

# Cells Apply

## Purpose

Implement the assigned Cells task batch with real code changes, strict scope control, and evidence-backed source routing.

Use [implementation-playbook.md](references/implementation-playbook.md) for the detailed TDD loop, browser validation checklist, and response template.

## What You Receive

- change name
- task batch or phase scope
- artifact store mode: `engram | openspec | hybrid | none`

## Execution and Persistence Contract

Read and follow:

- `skills/_shared/persistence-contract.md`
- `skills/_shared/cells-workflow-contract.md`
- `skills/_shared/cells-source-routing-contract.md`
- `skills/_shared/cells-rules-contract.md`
- `skills/_shared/cells-conventions.md`
- `skills/_shared/cells-governance-contract.md`
- `skills/_shared/cells-policy-matrix.yaml`
- `skills/_shared/real-cells-patterns.md`
- `skills/_shared/cells-official-reference.md`

For Cells testing or test-execution decisions during implementation, apply the mandatory testing stack from `skills/_shared/cells-rules-contract.md` and `skills/_shared/cells-source-routing-contract.md`.

Mode handling:

- `engram`: use `skills/_shared/engram-convention.md` and persist `apply-progress`
- `openspec`: use `skills/_shared/openspec-convention.md` and update `tasks.md`
- `hybrid`: do both
- `none`: return progress only

## Workflow

### Step 1: Load Skill Registry

Before any other work:

1. `mem_search(query: "skill-registry", project: "{project}")`
2. `mem_get_observation(id: {id})` when available
3. fallback: read `.atl/skill-registry.md`
4. if neither exists, proceed without it

### Step 2: Load Canonical Dependencies

When mode is `engram` or `hybrid`, retrieve:

1. `mem_search(query: "cells/{change-name}/proposal", project: "{project}")`
2. `mem_search(query: "cells/{change-name}/spec", project: "{project}")`
3. `mem_search(query: "cells/{change-name}/design", project: "{project}")`
4. `mem_search(query: "cells/{change-name}/tasks", project: "{project}")`
5. `mem_get_observation(...)` for each result

If any required canonical dependency is absent, return `status: blocked`.

### Step 3: Read Context Before Editing

Always read:

1. spec or acceptance criteria
2. design decisions
3. affected code and nearby patterns
4. project-local conventions

For Cells work, also inspect:

5. `custom-elements.json`
6. relevant tests
7. `package.json`
8. real feature usage when composition or architecture is involved
9. `python skills/cells-components-catalog/scripts/search_docs.py --query "<intent>"` when component identity is not already certain
10. `skills/cells-cli-usage/` for command resolution
11. `skills/cells-coverage/` when coverage or test artifacts are relevant
12. `skills/cells-test-creator/` when adding or changing tests
13. `skills/_shared/browser-testing-convention.md` and `skills/agent-browser/SKILL.md` for browser-visible changes

Before coding real Cells UI/component work, enforce these implementation checks:

- reuse existing BBVA components first
- register every template dependency in `scopedElements`
- when the surrounding architecture uses feature/data-manager patterns, prefer `WidgetMixin` and `this.emitEvent(...)`
- route component-owned literals through `this.t(...)` and keep parity in the correct locale source for the touched surface
- treat SCSS as visual source and keep runtime style artifacts aligned
- require a browser validation target when the change is visible in the UI

### Step 3b: Scope Restriction Gate

Before editing any file:

- identify the exact module, feature slice, or task boundary
- touch only files directly required by that work
- justify every dependency edit explicitly
- stop if safe completion requires broader edits than requested

If the assigned batch is tests-only:

- allowed: `test/**`, `test/mocks/**`, and test-only fixtures
- forbidden: `src/**`, repo locale source paths, and runtime source paths
- do not "just fix source quickly" during this batch

Absolute scope rule:

- Do not fix unrelated modules, unrelated errors, or opportunistic cleanup outside the assigned task unless the user explicitly expands scope

Use one of these gate notes in the implementation report:

- `Scope gate: strict task scope enforced; only directly affected files were touched`
- `Scope gate: direct dependency edit justified for assigned task`
- `Scope gate: tests-only enforced (no src/** or repo locale source edits)`
- `Scope gate: transitioned after explicit scope expansion confirmation`

### Step 4: Implement

Detect whether the project is running TDD. Use the detailed RED/GREEN/REFACTOR flow from [implementation-playbook.md](references/implementation-playbook.md) when TDD is active.

Standard mode minimum:

- read task
- read relevant specs
- read design decisions
- match existing code patterns
- make the smallest working change
- note deviations or issues

When the change is browser-visible, use the browser validation checklist from [implementation-playbook.md](references/implementation-playbook.md).

### Step 5: Persist Progress

If mode is `openspec` or `hybrid`, update `tasks.md` from `[ ]` to `[x]`.

If mode is `engram`, update the tasks artifact and save progress:

```text
mem_update(id: {tasks_observation_id}, content: "{updated tasks markdown with [x] marks}")
mem_save(
   title: "cells/{change-name}/apply-progress",
   topic_key: "cells/{change-name}/apply-progress",
   type: "architecture",
   project: "{project}",
   content: "{implementation progress report}"
)
```

If mode is `hybrid`, do both filesystem and Engram persistence.

### Step 6: Return Summary

Use the response template from [implementation-playbook.md](references/implementation-playbook.md).

The report must include:

- completed tasks
- files changed
- remaining tasks
- status
- scope gate note

Include a `Source Decisions` section with these exact fields:

- `intent`
- `primary_source`
- `fallback_used`
- `fallback_source`
- `fallback_reason`
- `evidence_quality`
- `status`

## Rules

### Core implementation rules

- Specs are acceptance criteria.
- Follow design decisions unless you explicitly record a deviation.
- Match existing patterns before introducing new abstractions.
- Scope isolation is mandatory.

### Cells-specific rules

- BBVA-first: search `cells-components-catalog` before inventing UI.
- Register every custom element used in templates in `scopedElements`.
- Use `static get properties()` for Lit properties. Do not use `@property`, `@state`, or `@attribute`.
- Route component-owned visible literals through `this.t(...)`.
- Keep locale parity in the correct locale source for the touched surface.
- Keep public technical naming in English.
- Use Cells-native commands only unless the user explicitly requests otherwise.

### Code hygiene rules

- Use JSDoc for public API and non-obvious contracts.
- do not leave TODO comments, commented-out code, or placeholder implementation notes.
- Avoid unnecessary whitespace-only edits.
- preserve separation of responsibilities across data-manager, pages, shared-components, utils, and styles.
- use semicolons and avoid trailing commas.
- keep SCSS/runtime style artifacts aligned when both exist.

### Verification handoff rules

- If the change affects rendered UI, do minimal browser validation before claiming implementation complete.
- If tests changed, resolve commands through `skills/cells-cli-usage/` first.
- If evidence is missing, return `partial` or `blocked`, never certainty by memory.

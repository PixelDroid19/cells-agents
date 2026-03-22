---
name: cells-apply
description: >
  Implement planned Cells + Lit + BBVA + SCSS tasks by editing real code against proposal, specs, and design. Triggers: when implementing code, writing components, applying changes, or generating tests. Load cells-cli-usage, cells-coverage, and cells-test-creator before starting. NEVER use HTML elements like <p>, <h3>, <span> — always search cells-components-catalog first for BBVA components. If no matching component exists, use cells-component-authoring to create one correctly.
license: MIT
metadata:
  author: D. J
  version: "2.1"
---

## Purpose

You are a sub-agent responsible for IMPLEMENTATION. You receive specific tasks from `tasks.md` and implement them by writing actual code. You follow the specs and design strictly.

## What You Receive

From the orchestrator:
- Change name
- The specific task(s) to implement (e.g., "Phase 1, tasks 1.1-1.3")
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
Read and follow `skills/_shared/cells-workflow-contract.md` for canonical workflow naming and compatibility-read order.
If the project is Cells-oriented, also read and follow `skills/_shared/cells-conventions.md`.
If the project is Cells-oriented, also read and follow `skills/_shared/cells-governance-contract.md` and `skills/_shared/cells-policy-matrix.yaml`.
For Cells implementation work, use `skills/_shared/cells-official-reference.md` to fetch only the official guidance needed for the touched area.

For Cells testing or test-execution decisions during implementation, apply this mandatory stack first and in order:
1. `skills/cells-cli-usage/` (canonical command resolution)
2. `skills/cells-coverage/` (threshold/reporting and artifact triage)
3. `skills/cells-test-creator/` (test design/update/compliance)

Do not skip or reorder this stack. Do not use generic fallback commands (`npm test`, `npm run test`, `npx web-test-runner`) in Cells contexts.

- If mode is `engram`: Read and follow `skills/_shared/engram-convention.md`. Artifact type: `apply-progress`. Retrieve `proposal`, `spec`, `design`, and `tasks` canonically, and use `mem_update` to mark completed tasks in the `tasks` artifact.
- If mode is `openspec`: Read and follow `skills/_shared/openspec-convention.md`. Update `tasks.md` with `[x]` marks.
- If mode is `hybrid`: Follow BOTH conventions  persist progress to Engram (`mem_update` for tasks) AND update `tasks.md` with `[x]` marks on filesystem.
- If mode is `none`: Return progress only. Do not update project artifacts.

## What to Do

### Step 1: Load Skill Registry (Mandatory)

Do this FIRST, before any other work.

1. Try engram first: `mem_search(query: "skill-registry", project: "{project}")`
2. If found, call `mem_get_observation(id: {id})` for the full registry
3. If engram is unavailable or no result is found, read `.atl/skill-registry.md` from the project root
4. If neither exists, proceed without skills (this is not an error)

From the registry, load only the coding skills and convention files relevant to the assigned implementation batch.

### Step 2: Load Dependencies (Engram / Hybrid)

When mode is `engram` or `hybrid`, retrieve dependencies with two-step recovery:

1. `mem_search(query: "cells/{change-name}/proposal", project: "{project}")`
2. `mem_search(query: "cells/{change-name}/spec", project: "{project}")`
3. `mem_search(query: "cells/{change-name}/design", project: "{project}")`
4. `mem_search(query: "cells/{change-name}/tasks", project: "{project}")`
5. `mem_get_observation(id: {proposal_id})`
6. `mem_get_observation(id: {spec_id})`
7. `mem_get_observation(id: {design_id})`
8. `mem_get_observation(id: {tasks_id})`

If any required canonical dependency is absent, return `status: blocked` and require canonical artifact seeding before implementation.

Do not use `mem_search` preview text as complete artifact content.

### Step 3: Read Context

Before writing ANY code:
1. Read the specs  understand WHAT the code must do
2. Read the design  understand HOW to structure the code
3. Read existing code in affected files  understand current patterns
4. Check the project's coding conventions from the active workspace config (`openspec/config.yaml` if it exists, otherwise repo conventions and orchestrator context)

For Cells projects, also inspect:
5. `custom-elements.json` and public API docs for touched components
6. nearby tests covering events, render states, and reflected attributes
7. real feature usage before introducing new composition patterns
8. SQL/database-backed lookup via `python skills/cells-components-catalog/scripts/search_docs.py --query "<intent>"` against `skills/cells-components-catalog/assets/bbva_cells_components.db`, when available, to confirm exact package names, tags, attributes, and usage snippets before coding (do not guess from memory)
9. `skills/cells-cli-usage/` first when resolving any test command path
10. `skills/cells-coverage/` second when coverage thresholds, reports, or test-failure artifacts exist
11. `skills/cells-test-creator/` third when adding or modifying tests
12. `skills/cells-cli-usage/` when you need the correct local lint, docs, locales, or serve command
13. `skills/_shared/browser-testing-convention.md` and `skills/agent-browser/SKILL.md` when the task changes rendered UI, demos, routes, interaction flows, or visual states

Before coding real Cells UI/component work, enforce these implementation checks:
- reuse existing BBVA components first; do not reinvent existing UI primitives
- register every template dependency in `scopedElements`
- when the surrounding architecture uses feature/data-manager patterns, prefer `WidgetMixin` and `this.emitEvent(...)` for business events
- route component-owned literals through `this.t(...)` and keep parity in `demo/locales/locales.json`
- treat SCSS as visual source and keep runtime style artifacts aligned
- require a browser validation target when the change is visible in the UI

### Step 3b: Scope Restriction Gate (Mandatory)

Before editing any file, enforce the assigned scope explicitly:

```
For every assigned batch:
 - Identify the exact module, feature slice, or task boundary requested by the user/orchestrator
 - Touch only files directly required to complete that assigned work
 - Do not fix unrelated errors, neighboring modules, or "while I'm here" issues by default

If another file or module must be touched:
 - Prove it is a direct dependency of the assigned task
 - Keep the edit limited to the minimum surface needed for the requested outcome
 - Record the reason in the implementation report

If safe completion requires broader edits than the assigned scope:
 - STOP before making those extra changes
 - Request an explicit scope expansion confirmation
 - Resume only after that confirmation is recorded

If the assigned batch is tests-only:
 - Allowed paths: `test/**`, `test/mocks/**`, and test-only fixtures
 - Forbidden paths: `src/**`, `demo/locales/**`, and any runtime source path
 - Do not "just fix source quickly" during this batch
```

Use one of these one-line gate evidence entries in `detailed_report`:
- `Scope gate: strict task scope enforced; only directly affected files were touched`
- `Scope gate: direct dependency edit justified for assigned task`
- `Scope gate: tests-only enforced (no src/** or demo/locales/** edits)`
- `Scope gate: transitioned after explicit scope expansion confirmation`

### Step 4: Detect Implementation Mode

Before writing code, determine if the project uses TDD:

```
Detect TDD mode from (in priority order):
 openspec/config.yaml  rules.apply.tdd (true/false  if filesystem config exists)
 User's installed skills (e.g., tdd/SKILL.md exists)
 Existing test patterns in the codebase (test files alongside source)
 Default: standard mode (write code first, then verify)

IF TDD mode is detected  use Step 2a (TDD Workflow)
IF standard mode  use Step 2b (Standard Workflow)
```

### Step 4a: Implement Tasks (TDD Workflow  RED  GREEN  REFACTOR)

When TDD is active, EVERY task follows this cycle:

```
FOR EACH TASK:
 1. UNDERSTAND
    Read the task description
    Read relevant spec scenarios (these are your acceptance criteria)
    Read the design decisions (these constrain your approach)
    Read existing code and test patterns

 2. RED  Write a failing test FIRST
    Write test(s) that describe the expected behavior from the spec scenarios
    Run tests  confirm they FAIL (this proves the test is meaningful)
    If test passes immediately  the behavior already exists or the test is wrong

 3. GREEN  Write the minimum code to pass
    Implement ONLY what's needed to make the failing test(s) pass
    Run tests  confirm they PASS
    Do NOT add extra functionality beyond what the test requires

 4. REFACTOR  Clean up without changing behavior
    Improve code structure, naming, duplication
    Run tests again  confirm they STILL PASS
    Match project conventions and patterns

 5. Mark the task as complete in the active tasks artifact
 6. Note any issues or deviations
```

Detect the test runner for execution:

```
Detect test runner from:
 openspec/config.yaml  rules.apply.test_command (if filesystem config exists)
 `skills/cells-cli-usage/` first for the correct Cells-native command path
 `skills/cells-coverage/` second for coverage/reporting constraints when applicable
 `skills/cells-test-creator/` third for test-design and convention constraints
 package.json  scripts.test (wrapper mapping only after Cells command resolution)
 pyproject.toml / pytest.ini  pytest
 Makefile  make test
 Fallback: report that tests couldn't be run automatically
```

**Important**: If any user coding skills are installed (e.g., `tdd/SKILL.md`, `pytest/SKILL.md`, `vitest/SKILL.md`), read and follow those skill patterns for writing tests.

### Step 4b: Implement Tasks (Standard Workflow)

When TDD is not active:

```
FOR EACH TASK:
 Read the task description
 Read relevant spec scenarios (these are your acceptance criteria)
 Read the design decisions (these constrain your approach)
 Read existing code patterns (match the project's style)
 Write the code
 Mark the task as complete in the active tasks artifact
 Note any issues or deviations
```

For small, low-risk changes:

- do not automatically start the full project
- do not automatically run the full test suite
- prefer code-local reasoning, targeted edits, and minimal confirmation only when the change needs proof

### Step 4c: Browser Validation For Visible UI Changes

When a task changes rendered UI, demos, routes, interaction flows, styling, or other browser-visible states:

```
Resolve the local serve/demo command and target URL through `skills/cells-cli-usage/`
Reuse an already running dev server, route, browser session, or CDP port when available
Open or connect with `agent-browser` using that existing runtime first
Capture a snapshot before interaction
Perform the minimum interaction needed to prove the changed behavior
Re-snapshot after DOM changes
Capture screenshot or diff evidence when the change is visual
If runtime validation cannot be executed locally, report it as blocked evidence
```

This browser step complements implementation confidence for UI work and does not replace full verification in `cells-verify`.

### Step 5: Artifact Persistence (Mandatory)

If mode is `openspec` or `hybrid`, update `tasks.md` and change `- [ ]` to `- [x]` for completed tasks.
If mode is `engram`, update the Engram `tasks` artifact and the `apply-progress` artifact, but do not modify project files.
If mode is `none`, report completed tasks inline only.

For Engram persistence use explicit calls:

```
mem_update(id: {tasks_observation_id}, content: "{updated tasks markdown with [x] marks}")
mem_save(
   title: "cells/{change-name}/apply-progress",
   topic_key: "cells/{change-name}/apply-progress",
   type: "architecture",
   project: "{project}",
   content: "{implementation progress report}"
)
```

If mode is `hybrid`, do BOTH filesystem updates and Engram calls.

Do not skip this step in `engram` or `hybrid`, or `cells-verify` will not have complete execution lineage.

```markdown
## Phase 1: Foundation

- [x] 1.1 Create `internal/auth/middleware.go` with JWT validation
- [x] 1.2 Add `AuthConfig` struct to `internal/config/config.go`
- [ ] 1.3 Add auth routes to `internal/server/server.go`   still pending
```

### Step 6: Return Summary

Use the following markdown as the `detailed_report` body and wrap the overall reply in the standard structured envelope:

```markdown
## Implementation Progress

**Change**: {change-name}
**Mode**: {TDD | Standard}

### Completed Tasks
- [x] {task 1.1 description}
- [x] {task 1.2 description}

### Files Changed
| File | Action | What Was Done |
|------|--------|---------------|
| `path/to/file.ext` | Created | {brief description} |
| `path/to/other.ext` | Modified | {brief description} |

### Source Decisions
- intent: apply-dependency-recovery
  primary_source: {canonical dependency used first}
  fallback_used: false
  fallback_source: null
  fallback_reason: null
  evidence_quality: high
  status: ok

### Tests (TDD mode only)
| Task | Test File | RED (fail) | GREEN (pass) | REFACTOR |
|------|-----------|------------|--------------|----------|
| 1.1 | `path/to/test.ext` |  Failed as expected |  Passed |  Clean |
| 1.2 | `path/to/test.ext` |  Failed as expected |  Passed |  Clean |

{Omit this section if standard mode was used.}

### Deviations from Design
{List any places where the implementation deviated from design.md and why.
If none, say "None  implementation matches design."}

### Issues Found
{List any problems discovered during implementation.
If none, say "None."}

### Remaining Tasks
- [ ] {next task}
- [ ] {next task}

### Status
{N}/{total} tasks complete. {Ready for next batch / Ready for verify / Blocked by X}
```

## Rules

- ALWAYS read specs before implementing  specs are your acceptance criteria
- ALWAYS follow the design decisions  don't freelance a different approach
- ALWAYS match existing code patterns and conventions in the project
- For Cells projects, preserve public attributes, event names, scoped registrations, and package import conventions unless the task explicitly changes them
- For Cells projects, use existing BBVA components before creating new UI primitives or wrappers unless specs/design explicitly justify otherwise
- For Cells projects, every custom element used in template output must be imported and registered in `scopedElements`
- For Cells feature/data-manager architecture, prefer `WidgetMixin` plus `this.emitEvent(...)` for business events when consistent with surrounding code
- For Cells projects, keep locale files under `demo/locales` only; do not create or reference locale files outside `demo/locales`
- For Cells projects, use `this.t(...)` for component-owned literals and keep key parity in `demo/locales/locales.json`
- When the scaffold/toolchain uses SCSS, keep SCSS as the visual source and keep runtime style files aligned
- Use English for generated JSDoc/comments, event names/custom event types/payload keys, and public API naming unless the user explicitly requests a different naming language
- Use JSDoc for public API/events and non-obvious contracts; do not leave TODO comments, placeholder comments, or commented-out code
- Avoid unnecessary whitespace-only edits and extra blank lines unrelated to the task
- Preserve separation of responsibilities across data-manager, pages, shared-components, utils, and styles
- In `openspec` mode, mark tasks complete in `tasks.md` AS you go, not at the end
- If you discover the design is wrong or incomplete, NOTE IT in your return summary  don't silently deviate
- If a task is blocked by something unexpected, STOP and report back
- NEVER implement tasks that weren't assigned to you
- Do not fix unrelated modules, unrelated errors, or opportunistic cleanup outside the assigned task unless the user explicitly expands scope
- When the assigned scope is tests-only, do not edit `src/**` or `demo/locales/**` unless an explicit mid-session scope transition is confirmed
- Load and follow any relevant Cells specialist skills (e.g., `cells-component-authoring`, `cells-cli-usage`, `cells-test-creator`) when available in the active skill set; do not inject generic stack skills (React, Django, etc.) unless the user explicitly requests a non-Cells context
- If filesystem config exists, apply any `rules.apply` from `openspec/config.yaml`
- If TDD mode is detected (Step 2), ALWAYS follow the RED  GREEN  REFACTOR cycle  never skip RED (writing the failing test first)
- When running tests during TDD, run ONLY the relevant test file/suite, not the entire test suite (for speed)
- For Cells app/theme work, do NOT switch to generic external runners (`npm run *`, `npm test`, `npx web-test-runner`) unless the user explicitly requests a non-Cells path
- If uncertain whether a command is Cells-native, ask the user before running a non-Cells command
- Do not run project-wide runtime or test commands for every small change; execute only what is needed to confirm the assigned task
- If browser confirmation is needed, reuse the existing runtime, browser session, and port before starting a new one
- When implementation changes browser-visible UI, run a minimal browser validation loop if a local runtime can be served safely; do not claim closure without browser evidence for visible changes
- Every apply-progress artifact MUST include a `Source Decisions` section and refer to canonical `cells/*` artifacts as the active lineage
- Record task-level source decision trace and fallback reason when non-primary evidence is used
- If evidence minimums are unmet, return `status: partial | blocked` with remediation steps
- Return the standard structured envelope with the markdown report above in `detailed_report`



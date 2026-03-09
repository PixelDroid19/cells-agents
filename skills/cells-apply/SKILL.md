---
name: cells-apply
description: >
  Implement one or more planned change tasks by editing real code to match proposal, specs, design, and project conventions. Use when the orchestrator has a task batch ready for implementation, including Cells-specific component work and test updates.
license: MIT
metadata:
  author: D. J
  version: "2.0"
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
If the project is Cells-oriented, also read and follow `skills/_shared/cells-conventions.md`.
For Cells implementation work, use `skills/_shared/cells-official-reference.md` to fetch only the official guidance needed for the touched area.

For Cells testing or test-execution decisions during implementation, apply this mandatory stack first and in order:
1. `skills/cells-cli-usage/` (canonical command resolution)
2. `skills/cells-coverage/` (threshold/reporting and artifact triage)
3. `skills/cells-test-creator/` (test design/update/compliance)

Do not skip or reorder this stack. Do not use generic fallback commands (`npm test`, `npm run test`, `npx web-test-runner`) in Cells contexts.

- If mode is `engram`: Read and follow `skills/_shared/engram-convention.md`. Artifact type: `apply-progress`. Retrieve `proposal`, `spec`, `design`, and `tasks` as dependencies. Also use `mem_update` to mark completed tasks in the `tasks` artifact.
- If mode is `openspec`: Read and follow `skills/_shared/openspec-convention.md`. Update `tasks.md` with `[x]` marks.
- If mode is `hybrid`: Follow BOTH conventions  persist progress to Engram (`mem_update` for tasks) AND update `tasks.md` with `[x]` marks on filesystem.
- If mode is `none`: Return progress only. Do not update project artifacts.

## What to Do

### Step 1: Read Context

Before writing ANY code:
1. Read the specs  understand WHAT the code must do
2. Read the design  understand HOW to structure the code
3. Read existing code in affected files  understand current patterns
4. Check the project's coding conventions from the active workspace config (`openspec/config.yaml` if it exists, otherwise repo conventions and orchestrator context)

For Cells projects, also inspect:
5. `custom-elements.json` and public API docs for touched components
6. nearby tests covering events, render states, and reflected attributes
7. real feature usage before introducing new composition patterns
8. `skills/cells-components-catalog/`, when available, to confirm exact package names, tags, attributes, and usage snippets before coding
9. `skills/cells-cli-usage/` first when resolving any test command path
10. `skills/cells-coverage/` second when coverage thresholds, reports, or test-failure artifacts exist
11. `skills/cells-test-creator/` third when adding or modifying tests
12. `skills/cells-cli-usage/` when you need the correct local lint, docs, locales, or serve command
13. `skills/_shared/browser-testing-convention.md` and `skills/agent-browser/SKILL.md` when the task changes rendered UI, demos, routes, interaction flows, or visual states

### Step 2: Detect Implementation Mode

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

### Step 2a: Implement Tasks (TDD Workflow  RED  GREEN  REFACTOR)

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

### Step 2b: Implement Tasks (Standard Workflow)

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

### Step 2c: Browser Validation For Visible UI Changes

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

### Step 3: Persist Task Progress Correctly

If mode is `openspec` or `hybrid`, update `tasks.md` and change `- [ ]` to `- [x]` for completed tasks.
If mode is `engram`, update the Engram `tasks` artifact and the `apply-progress` artifact, but do not modify project files.
If mode is `none`, report completed tasks inline only.

```markdown
## Phase 1: Foundation

- [x] 1.1 Create `internal/auth/middleware.go` with JWT validation
- [x] 1.2 Add `AuthConfig` struct to `internal/config/config.go`
- [ ] 1.3 Add auth routes to `internal/server/server.go`   still pending
```

### Step 4: Return Summary

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
- Use English for generated JSDoc/comments, event names/custom event types/payload keys, and public API naming unless the user explicitly requests a different naming language
- In `openspec` mode, mark tasks complete in `tasks.md` AS you go, not at the end
- If you discover the design is wrong or incomplete, NOTE IT in your return summary  don't silently deviate
- If a task is blocked by something unexpected, STOP and report back
- NEVER implement tasks that weren't assigned to you
- Load and follow any relevant coding skills for the project stack (e.g., react-19, typescript, django-drf, tdd, pytest, vitest) if available in the user's skill set
- If filesystem config exists, apply any `rules.apply` from `openspec/config.yaml`
- If TDD mode is detected (Step 2), ALWAYS follow the RED  GREEN  REFACTOR cycle  never skip RED (writing the failing test first)
- When running tests during TDD, run ONLY the relevant test file/suite, not the entire test suite (for speed)
- For Cells app/theme work, do NOT switch to generic external runners (`npm run *`, `npm test`, `npx web-test-runner`) unless the user explicitly requests a non-Cells path
- If uncertain whether a command is Cells-native, ask the user before running a non-Cells command
- Do not run project-wide runtime or test commands for every small change; execute only what is needed to confirm the assigned task
- If browser confirmation is needed, reuse the existing runtime, browser session, and port before starting a new one
- When implementation changes browser-visible UI, run a minimal browser validation loop if a local runtime can be served safely
- Return the standard structured envelope with the markdown report above in `detailed_report`



---
name: cells-tasks
description: "Use when breaking Cells design and specs into ordered, file-level implementation tasks, task groups, dependency sequencing, and verification-ready checklists."
---

## Purpose

You are a sub-agent responsible for creating the TASK BREAKDOWN. You take the proposal, specs, and design, then produce a `tasks.md` with concrete, actionable implementation steps organized by phase.

## What You Receive

From the orchestrator:
- Change name
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
Read and follow `skills/_shared/cells-work-sizing-contract.md` before deciding whether a task artifact is necessary.
Read and follow `skills/_shared/cells-workflow-contract.md` for canonical workflow naming and compatibility-read order.
Read and follow `skills/_shared/cells-source-routing-contract.md` for deterministic source selection and minimum evidence.
For Cells-oriented changes, also read `skills/_shared/cells-governance-contract.md` and `skills/_shared/cells-policy-matrix.yaml`.

This phase requires `proposal`, `spec`, and `design` (artifact type `tasks`). Recover them and handle persistence mode per `skills/_shared/artifact-recovery.md`.

## What to Do

### Step 1: Dependency Gate For Governed Task Planning

Before producing governed task planning output, verify that all required canonical artifacts exist.
For `fast-path` or direct `scoped-change`, do not force proposal/spec/design/task artifacts; use a short inline task list only if it helps execute the requested change.

When mode is `engram` or `hybrid`, retrieve all three required artifacts (proposal, spec, design) per `skills/_shared/artifact-recovery.md`.

If any required canonical dependency is absent during `full-workflow`, return `status: blocked` with:
```
missing_artifact: cells/{change-name}/<missing-phase>
reason: "cells-tasks requires proposal, spec, and design artifacts before tasks can be generated"
required_action: "Run the missing phase(s) first or provide the required canonical artifact"
```

### Step 2: Resolve Skills And Environment

Read `.cells-agent/context.json` when present and load only the skills whose
frontmatter matches task planning. Do not require a generated registry.

### Step 3: Analyze the Design

From the design document, identify:
- All files that need to be created/modified/deleted
- The dependency order (what must come first)
- Testing requirements per component

Before writing tasks, validate source coverage by intent:
- UI/component/package/API task groups -> run `skills/cells-components-catalog/scripts/search_docs.py` SQL lookup first and then confirm against project evidence (`custom-elements.json`, `src/`, `test/`) (query phrasing and zero-result fallback: `skills/_shared/doc-search.md`).
- Cells docs/process/CLI/testing/theming/i18n task groups -> consult `skills/cells-official-docs-catalog/` first (query phrasing and zero-result fallback: `skills/_shared/doc-search.md`).
- Any testing task group should load only the testing skill(s) the intent needs: `skills/cells-cli-usage/` for commands, `skills/cells-coverage/` only for coverage work, `skills/cells-test-creator/` only for authoring tests  never generic npm/web-test-runner fallbacks in Cells contexts unless explicitly requested by the user.

### Step 4: Write The Task Content

If mode is `openspec` or `hybrid`, create or update the task file:

```
openspec/changes/{change-name}/
 proposal.md
 specs/
 design.md
 tasks.md                You create this
```

If mode is `engram` or `none`, do not create project files and return the same task content inline.

#### Task File Format

```markdown
# Tasks: {Change Title}

## Phase 1: {Phase Name} (e.g., Infrastructure / Foundation)

- [ ] 1.1 {Concrete action  what file, what change}
- [ ] 1.2 {Concrete action}
- [ ] 1.3 {Concrete action}

## Phase 2: {Phase Name} (e.g., Core Implementation)

- [ ] 2.1 {Concrete action}
- [ ] 2.2 {Concrete action}
- [ ] 2.3 {Concrete action}
- [ ] 2.4 {Concrete action}

## Phase 3: {Phase Name} (e.g., Testing / Verification)

- [ ] 3.1 {Write tests for ...}
- [ ] 3.2 {Write tests for ...}
- [ ] 3.3 {Verify integration between ...}

## Phase 4: {Phase Name} (e.g., Cleanup / Documentation)

- [ ] 4.1 {Update docs/comments}
- [ ] 4.2 {Remove temporary code}

## Source Decisions

- intent: task-planning-evidence
  primary_source: {canonical proposal/spec/design source}
  fallback_used: false
  fallback_source: null
  fallback_reason: null
  evidence_quality: high
  status: ok
```

### Task Writing Rules

Each task MUST be:

| Criteria | Example  | Anti-example  |
|----------|-----------|----------------|
| **Specific** | "Add `icon-left='transfer'` to transfer button in `src/account-actions.js`" | "Add icon to button" |
| **Actionable** | "Register `bbva-button-default` in `static get scopedElements()`" | "Register button" |
| **Verifiable** | "Test: transfer button renders `icon-left='transfer'`" | "Make sure icon works" |
| **Small** | One file or one logical unit of work | "Implement the feature" |

### Phase Organization Guidelines

```
Phase 1: Foundation / Infrastructure
   New types, interfaces, database changes, config
   Things other tasks depend on

Phase 2: Core Implementation
   Main logic, business rules, core behavior
   The meat of the change

Phase 3: Integration / Wiring
   Connect components, routes, UI wiring
   Make everything work together

Phase 4: Testing
   Unit tests, integration tests, e2e tests
   Verify against spec scenarios

Phase 5: Cleanup (if needed)
   Documentation, remove dead code, polish
```

### Step 5: Artifact Persistence When Requested By Mode

Persist the tasks artifact as `cells/{change-name}/tasks` per `skills/_shared/artifact-recovery.md`'s Persistence Mode Handling section (`tasks.md` was already written in Step 4 for `openspec`/`hybrid`).

Do not skip this step in `engram` or `hybrid` during governed `full-workflow`, or downstream phases will not find the tasks artifact.
For `fast-path` and direct `scoped-change`, use `mode: none` behavior unless the user explicitly requests persistence.

### Step 6: Return Summary

Use the following markdown as the `detailed_report` body and wrap the overall reply in the standard structured envelope:

```markdown
## Tasks Created

**Change**: {change-name}
**Artifact Ref**: {observation-id | openspec/changes/{change-name}/tasks.md | inline-only}

### Breakdown
| Phase | Tasks | Focus |
|-------|-------|-------|
| Phase 1 | {N} | {Phase name} |
| Phase 2 | {N} | {Phase name} |
| Phase 3 | {N} | {Phase name} |
| Total | {N} | |

### Implementation Order
{Brief description of the recommended order and why}

### Next Step
Ready for implementation (cells-apply).
```

## Rules

- ALWAYS reference concrete file paths in tasks
- Tasks MUST be ordered by dependency  Phase 1 tasks shouldn't depend on Phase 2
- Testing tasks should reference specific scenarios from the specs
- Each task should be completable in ONE session (if a task feels too big, split it)
- Use hierarchical numbering: 1.1, 1.2, 2.1, 2.2, etc.
- NEVER include vague tasks like "implement feature" or "add tests"
- Every tasks artifact MUST include a `Source Decisions` section and keep canonical `cells/*` refs as the active artifact names
- Include task-level source trace expectations (source used, fallback reason, blocked/partial condition)
- If dependency evidence is incomplete, return `status: partial | blocked` and list remediation
- If task groups do not include routed source evidence per `cells-source-routing-contract.md`, return `status: partial`
- If filesystem config exists, apply any `rules.tasks` from `openspec/config.yaml`
- If the project uses TDD, integrate test-first tasks: RED task (write failing test)  GREEN task (make it pass)  REFACTOR task (clean up)
- Return the standard structured envelope with the markdown report above in `detailed_report`

## Browser Integration

When tasks involve rendered UI, routes, demos, or visual behavior, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Add explicit browser tasks when relevant, such as:
- resolve local serve/demo command
- open the target page and validate a user flow
- capture screenshot or diff evidence for visible changes
- verify runtime i18n, theming, or state transitions.

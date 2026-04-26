---
name: cells-tasks
description: "Use when breaking Cells design and specs into ordered, file-level implementation tasks, task groups, dependency sequencing, and verification-ready checklists."
license: MIT
metadata:
  author: D. J
  version: "2.1"
---

## Purpose

You are a sub-agent responsible for creating the TASK BREAKDOWN. You take the proposal, specs, and design, then produce a `tasks.md` with concrete, actionable implementation steps organized by phase.

## What You Receive

From the orchestrator:
- Change name
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
Read and follow `skills/_shared/cells-workflow-contract.md` for canonical workflow naming and compatibility-read order.
Read and follow `skills/_shared/cells-source-routing-contract.md` for deterministic source selection and minimum evidence.
For Cells-oriented changes, also read `skills/_shared/cells-governance-contract.md` and `skills/_shared/cells-policy-matrix.yaml`.

- If mode is `engram`: Read and follow `skills/_shared/engram-convention.md`. Artifact type: `tasks`. Retrieve `proposal`, `spec`, and `design` canonically.
- If mode is `openspec`: Read and follow `skills/_shared/openspec-convention.md`.
- If mode is `hybrid`: Follow BOTH conventions  persist to Engram AND write `tasks.md` to filesystem. Retrieve dependencies from Engram (primary) with filesystem fallback.
- If mode is `none`: Return result only. Never create or modify project files.

## What to Do

### Step 1: Dependency Gate (Mandatory)

Before producing any output, verify that all required canonical artifacts exist.

When mode is `engram` or `hybrid`, retrieve all three required artifacts:
1. `mem_search(query: "cells/{change-name}/proposal", project: "{project}")`
2. `mem_search(query: "cells/{change-name}/spec", project: "{project}")`
3. `mem_search(query: "cells/{change-name}/design", project: "{project}")`
4. `mem_get_observation(id: {proposal_id})` (REQUIRED)
5. `mem_get_observation(id: {spec_id})` (REQUIRED)
6. `mem_get_observation(id: {design_id})` (REQUIRED)

If any required canonical dependency is absent, return `status: blocked` with:
```
missing_artifact: cells/{change-name}/<missing-phase>
reason: "cells-tasks requires proposal, spec, and design artifacts before tasks can be generated"
required_action: "Run the missing phase(s) first or provide the required canonical artifact"
```

Do not use `mem_search` preview text as complete artifact content.

### Step 2: Load Skill Registry

Load the skill registry from the orchestrator's pre-resolved context. If the orchestrator did not pass a resolved skill registry path, read `skills/skill-registry/SKILL.md` to understand available skills and routing.

### Step 3: Analyze the Design

From the design document, identify:
- All files that need to be created/modified/deleted
- The dependency order (what must come first)
- Testing requirements per component

Before writing tasks, validate source coverage by intent:
- UI/component/package/API task groups -> run `skills/cells-components-catalog/scripts/search_docs.py` SQL lookup first and then confirm against project evidence (`custom-elements.json`, `src/`, `test/`).
- Cells docs/process/CLI/testing/theming/i18n task groups -> consult `skills/cells-official-docs-catalog/` first.
- Any testing task group must use this strict stack first: `skills/cells-cli-usage/` -> `skills/cells-coverage/` -> `skills/cells-test-creator/`.

Do not skip or reorder these sources. Do not use generic fallback runners (`npm test`, `npm run test`, `npx web-test-runner`) for Cells contexts unless explicitly requested by the user.

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

### Step 5: Artifact Persistence (Mandatory)

If mode is `engram`, persist the tasks artifact in Engram:

```
mem_save(
   title: "cells/{change-name}/tasks",
   topic_key: "cells/{change-name}/tasks",
   type: "architecture",
   project: "{project}",
   content: "{your full tasks markdown from Step 4}"
)
```

If mode is `openspec` or `hybrid`, `tasks.md` was already written in Step 4.

If mode is `hybrid`, also call `mem_save` as above (write to BOTH backends).

If mode is `none`, return inline only.

Do not skip this step in `engram` or `hybrid`, or downstream phases will not find the tasks artifact.

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

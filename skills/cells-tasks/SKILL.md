---
name: cells-tasks
description: >
  Break a planned change into ordered, concrete implementation tasks with file-level actions and testing work. Use when the orchestrator already has proposal, specs, and design context and needs an actionable task checklist for implementation.
license: MIT
metadata:
  author: D. J
  version: "2.0"
---

## Purpose

You are a sub-agent responsible for creating the TASK BREAKDOWN. You take the proposal, specs, and design, then produce a `tasks.md` with concrete, actionable implementation steps organized by phase.

## What You Receive

From the orchestrator:
- Change name
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.

- If mode is `engram`: Read and follow `skills/_shared/engram-convention.md`. Artifact type: `tasks`. Retrieve `proposal`, `spec`, and `design` as dependencies.
- If mode is `openspec`: Read and follow `skills/_shared/openspec-convention.md`.
- If mode is `hybrid`: Follow BOTH conventions  persist to Engram AND write `tasks.md` to filesystem. Retrieve dependencies from Engram (primary) with filesystem fallback.
- If mode is `none`: Return result only. Never create or modify project files.

## What to Do

### Step 1: Analyze the Design

From the design document, identify:
- All files that need to be created/modified/deleted
- The dependency order (what must come first)
- Testing requirements per component

### Step 2: Write The Task Content

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
```

### Task Writing Rules

Each task MUST be:

| Criteria | Example  | Anti-example  |
|----------|-----------|----------------|
| **Specific** | "Create `internal/auth/middleware.go` with JWT validation" | "Add auth" |
| **Actionable** | "Add `ValidateToken()` method to `AuthService`" | "Handle tokens" |
| **Verifiable** | "Test: `POST /login` returns 401 without token" | "Make sure it works" |
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

### Step 3: Return Summary

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
- If filesystem config exists, apply any `rules.tasks` from `openspec/config.yaml`
- If the project uses TDD, integrate test-first tasks: RED task (write failing test)  GREEN task (make it pass)  REFACTOR task (clean up)
- Return the standard structured envelope with the markdown report above in `detailed_report`

## Browser Integration

When tasks involve rendered UI, routes, demos, or visual behavior, also read:
- `skills/_shared/browser-testing-convention.md`
- `agent-browser/SKILL.md` when available

Add explicit browser tasks when relevant, such as:
- resolve local serve/demo command
- open the target page and validate a user flow
- capture screenshot or diff evidence for visible changes
- verify runtime i18n, theming, or state transitions.

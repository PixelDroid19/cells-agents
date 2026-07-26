---
name: cells-init
description: "Use when starting a Cells workflow, detecting stack and conventions, bootstrapping persistence, or establishing project context before other phases."
---

## Purpose

You are a sub-agent responsible for initializing CELLS workflow context in a project. You detect the project stack and conventions, then bootstrap the active persistence backend.

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
Read and follow `skills/_shared/cells-workflow-contract.md` for canonical workflow naming and compatibility-read order.
If the project is Cells-oriented, also read and follow `skills/_shared/cells-conventions.md`.
If the project is Cells-oriented, use `skills/_shared/cells-official-reference.md` to decide which official docs and specialist skills are relevant before loading them.

This phase writes `cells-init/{project-name}`. Handle persistence mode (engram/openspec/hybrid/none) per `skills/_shared/artifact-recovery.md`'s Persistence Mode Handling section. In `engram`, write `cells-init/{project-name}` canonically and do not create `openspec/`; in `openspec`/`hybrid`, run full filesystem bootstrap.

## What to Do

### Step 1: Resolve Context

Read `.cells-agent/context.json` when present, then inspect the workspace files
needed for this initialization. Load skills directly by their frontmatter
descriptions; do not require a generated registry or a host-specific memory tool.

### Step 2: Detect Project Context

Read the project to understand:
- Tech stack (check package.json, go.mod, pyproject.toml, etc.)
- Existing conventions (linters, test frameworks, CI)
- Architecture patterns in use

For Cells projects, explicitly inspect:
- `package.json` scripts such as `cells lit-component:test`, docs, lint, and demo commands
- `custom-elements.json`
- `src/` and `test/`
- `@bbva-spherica-components/*`, `@bbva-web-components/*`, `lit`, and `@open-wc/scoped-elements`
- whether the project is a base component, a feature composition, or a data manager package
- `skills/cells-cli-usage/`, `skills/cells-coverage/`, `skills/cells-test-creator/`, and `skills/cells-app-architecture/` when present — load only the testing skill(s) the intent needs (cells-cli-usage for commands, cells-coverage only for coverage work, cells-test-creator only for authoring tests; never generic npm/web-test-runner fallbacks in Cells contexts) — plus the architecture model
- whether the workspace exposes a local serve, demo, or route path suitable for browser validation via `skills/_shared/browser-testing-convention.md` and `skills/agent-browser/SKILL.md`
- whether there is evidence of an already running dev server, existing preview URL, or known browser/CDP reuse path that should be preferred later

### Step 3: Initialize Persistence Backend

If mode resolves to `openspec` or `hybrid`, create this directory structure:

```
openspec/
 config.yaml               Project-specific CELLS config
 specs/                    Source of truth (empty initially)
 changes/                  Active changes
     archive/              Completed changes
```

If mode resolves to `engram` or `none`, skip filesystem bootstrap.

### Step 4: Generate Config (openspec or hybrid mode)

Based on what you detected, create the config when mode includes OpenSpec filesystem persistence:

```yaml
# openspec/config.yaml
schema: spec-driven

context: |
  Tech stack: {detected stack}
  Architecture: {detected patterns}
  Testing: {detected test framework}
  Style: {detected linting/formatting}
  Cells: {component library / feature composition / non-Cells}

rules:
  proposal:
    - Include rollback plan for risky changes
    - Identify affected modules/packages
  specs:
    - Use Given/When/Then format for scenarios
    - Use RFC 2119 keywords (MUST, SHALL, SHOULD, MAY)
  design:
    - Include sequence diagrams for complex flows
    - Document architecture decisions with rationale
  tasks:
    - Group tasks by phase (infrastructure, implementation, testing)
    - Use hierarchical numbering (1.1, 1.2, etc.)
    - Keep tasks small enough to complete in one session
  apply:
    - Follow existing code patterns and conventions
    - Load relevant coding skills for the project stack
  verify:
    - Run tests if test infrastructure exists
    - Compare implementation against every spec scenario
  archive:
    - Warn before merging destructive deltas (large removals)
```

### Step 5: Artifact Persistence (Mandatory)

Persist initialization context as `cells-init/{project-name}` per `skills/_shared/artifact-recovery.md`'s Persistence Mode Handling section (`openspec/config.yaml` was already written in Step 4 for `openspec`/`hybrid`).

Do not skip this step in `engram` or `hybrid`, or later phases cannot recover initialization context.

### Step 6: Return Summary

Return a structured summary adapted to the resolved mode:

#### If mode is `engram`:

Persist project context following `skills/_shared/engram-convention.md` with title and topic_key `cells-init/{project-name}`.

Return:
```
## CELLS Initialized

**Project**: {project name}
**Stack**: {detected stack}
**Persistence**: engram

### Context Saved
Project context persisted to Engram.
- **Engram ID**: #{observation-id}
- **Topic key**: cells-init/{project-name}

No project files created.

### Next Steps
Ready for /cells-explore <topic> or /cells-new <change-name>.
```

#### If mode is `openspec`:
```
## CELLS Initialized

**Project**: {project name}
**Stack**: {detected stack}
**Persistence**: openspec

### Structure Created
- openspec/config.yaml  Project config with detected context
- openspec/specs/       Ready for specifications
- openspec/changes/     Ready for change proposals

### Next Steps
Ready for /cells-explore <topic> or /cells-new <change-name>.
```

#### If mode is `none`:
```
## CELLS Initialized

**Project**: {project name}
**Stack**: {detected stack}
**Persistence**: none (ephemeral)

### Context Detected
{summary of detected stack and conventions}

### Recommendation
Enable `engram` or `openspec` for artifact persistence across sessions. Without persistence, all CELLS artifacts will be lost when the conversation ends.

### Next Steps
Ready for /cells-explore <topic> or /cells-new <change-name>.
```

## Rules

- NEVER create placeholder spec files - specs are created via cells-spec during a change
- ALWAYS detect the real tech stack, don't guess
- For Cells projects, mention concrete evidence: package names, test command, and whether `custom-elements.json` exists
- For Cells projects, mention whether future confirmation should reuse an existing runtime/browser/port before starting a new one
- If the project already has an `openspec/` directory, report what exists and continue using the canonical layout
- Keep config.yaml context CONCISE - no more than 10 lines
- Return the standard structured envelope with the mode-specific markdown report in `detailed_report`

## Browser Integration

When the workspace contains demos, app routes, or rendered UI, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Initialization should record whether the repo exposes a practical local browser-validation path, such as a demo server, app route, or component preview command.
It should also record whether later browser confirmation should reuse an existing runtime or CDP port instead of launching a fresh browser.

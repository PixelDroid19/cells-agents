# OpenSpec File Convention (shared across all SDD skills)

This convention matches `agent-teams-lite` filesystem layout, but in this package it is secondary to Engram unless the active mode is strictly `openspec`.

## Directory Structure

```
openspec/
├── config.yaml              <- Project-specific SDD config
├── specs/                   <- Source of truth (main specs)
│   └── {domain}/
│       └── spec.md
└── changes/                 <- Active changes
    ├── archive/             <- Completed changes (YYYY-MM-DD-{change-name}/)
    └── {change-name}/       <- Active change folder
        ├── state.yaml       <- DAG state (orchestrator, survives compaction)
        ├── exploration.md   <- (optional) from cells-explore
        ├── proposal.md      <- from cells-propose
        ├── specs/           <- from cells-spec
        │   └── {domain}/
        │       └── spec.md  <- Delta spec
        ├── design.md        <- from cells-design
        ├── tasks.md         <- from cells-tasks (updated by cells-apply)
        └── verify-report.md <- from cells-verify
```

## Artifact File Paths

| Skill | Creates / Reads | Path |
|-------|----------------|------|
| orchestrator | Creates/Updates | `openspec/changes/{change-name}/state.yaml` (DAG state for compaction recovery) |
| cells-init | Creates | `openspec/config.yaml`, `openspec/specs/`, `openspec/changes/`, `openspec/changes/archive/` |
| cells-explore | Creates (optional) | `openspec/changes/{change-name}/exploration.md` |
| cells-propose | Creates | `openspec/changes/{change-name}/proposal.md` |
| cells-spec | Creates | `openspec/changes/{change-name}/specs/{domain}/spec.md` |
| cells-design | Creates | `openspec/changes/{change-name}/design.md` |
| cells-tasks | Creates | `openspec/changes/{change-name}/tasks.md` |
| cells-apply | Updates | `openspec/changes/{change-name}/tasks.md` (marks `[x]`) |
| cells-verify | Creates | `openspec/changes/{change-name}/verify-report.md` |
| cells-archive | Moves | `openspec/changes/{change-name}/` → `openspec/changes/archive/YYYY-MM-DD-{change-name}/` |
| cells-archive | Updates | `openspec/specs/{domain}/spec.md` (merges deltas into main specs) |

## Reading Artifacts

Each skill reads its dependencies from the filesystem using the canonical OpenSpec paths:

```
Proposal:  openspec/changes/{change-name}/proposal.md
Specs:     openspec/changes/{change-name}/specs/  (all domain subdirectories)
Design:    openspec/changes/{change-name}/design.md
Tasks:     openspec/changes/{change-name}/tasks.md
Verify:    openspec/changes/{change-name}/verify-report.md
Config:    openspec/config.yaml
Main specs: openspec/specs/{domain}/spec.md
```

## Writing Rules

- ALWAYS create the change directory (`openspec/changes/{change-name}/`) before writing artifacts
- If a file already exists, READ it first and UPDATE it (don't overwrite blindly)
- If the change directory already exists with artifacts, the change is being CONTINUED
- Use the `openspec/config.yaml` `rules` section to apply project-specific constraints per phase
- In `hybrid`, treat these files as a filesystem projection of the canonical Engram-backed workflow state

## Config File Reference

```yaml
# openspec/config.yaml
schema: spec-driven

context: |
  Tech stack: {detected}
  Architecture: {detected}
  Testing: {detected}
  Style: {detected}

rules:
  proposal:
    - Include rollback plan for risky changes
  specs:
    - Use Given/When/Then for scenarios
    - Use RFC 2119 keywords (MUST, SHALL, SHOULD, MAY)
  design:
    - Include sequence diagrams for complex flows
    - Document architecture decisions with rationale
  tasks:
    - Group by phase, use hierarchical numbering
    - Keep tasks completable in one session
  apply:
    - Follow existing code patterns
    tdd: false           # Set to true to enable RED-GREEN-REFACTOR
    test_command: ""     # e.g., "npm test", "pytest"
  verify:
    test_command: ""     # Override for verification
    build_command: ""    # Override for build check
    coverage_threshold: 0  # Set > 0 to enable coverage check
  archive:
    - Warn before merging destructive deltas
```

## State File Reference

When the orchestrator persists filesystem state, use this schema:

```yaml
# openspec/changes/{change-name}/state.yaml
change: {change-name}
phase: {last-phase}
artifact_store: openspec
artifacts:
  proposal: true
  spec: true
  design: false
  tasks: false
  verify_report: false
tasks_progress:
  completed: []
  pending: []
layout:
  profile: canonical
last_updated: 2026-03-09T00:00:00Z
```

## Archive Structure

When archiving, the change folder moves to:
```
openspec/changes/archive/YYYY-MM-DD-{change-name}/
```

Use today's date in ISO format. The archive is an AUDIT TRAIL — never delete or modify archived changes.

# Engram Artifact Convention (shared across all CELLS skills)

This is the canonical persistence architecture for this package.

> **NOTE**: Critical engram calls (`mem_search`, `mem_get_observation`, `mem_save`) are inlined directly in the numbered steps of each `cells-*` skill. This file remains supplementary reference and naming authority.

## Naming Rules

ALL CELLS artifacts persisted to Engram MUST follow this deterministic naming:

```
title:     cells/{change-name}/{artifact-type}
topic_key: cells/{change-name}/{artifact-type}
type:      architecture
project:   {detected or current project name}
scope:     project
```

### Artifact Types (exact strings)

| Artifact Type | Produced By | Description |
|---------------|-------------|-------------|
| `explore` | cells-explore | Exploration analysis |
| `proposal` | cells-propose | Change proposal |
| `spec` | cells-spec | Delta specifications (all domains concatenated) |
| `design` | cells-design | Technical design |
| `tasks` | cells-tasks | Task breakdown |
| `apply-progress` | cells-apply | Implementation progress (one per batch) |
| `verify-report` | cells-verify | Verification report |
| `archive-report` | cells-archive | Archive closure with lineage |
| `ui-evidence` | any UI-aware skill | Compact browser validation evidence, screenshot paths, or visual diff summary |
| `state` | orchestrator | DAG state for recovery after compaction |

**Exception**: `cells-init` uses `cells-init/{project-name}` as both title and topic_key (it's project-scoped, not change-scoped).

### State Artifact

The orchestrator persists DAG state after each phase transition to enable recovery after context compaction:
- artifacts and DAG state live in Engram when mode is `engram` or `hybrid`
- the orchestrator remains delegate-only and restores state from Engram before resuming work

```
mem_save(
  title: "cells/{change-name}/state",
  topic_key: "cells/{change-name}/state",
  type: "architecture",
  project: "{project}",
  content: "change: {change-name}\nphase: {last-phase}\nartifact_store: engram\nartifacts:\n  proposal: true\n  specs: true\n  design: false\n  tasks: false\ntasks_progress:\n  completed: []\n  pending: []\nlast_updated: {ISO date}"
)
```

Recovery: `mem_search("cells/{change-name}/state")` → `mem_get_observation(id)` → parse YAML → restore orchestrator state.

### Example

```
mem_save(
  title: "cells/add-dark-mode/proposal",
  topic_key: "cells/add-dark-mode/proposal",
  type: "architecture",
  project: "my-app",
  content: "# Proposal: Add Dark Mode\n\n..."
)
```

## Recovery Protocol (2 steps — MANDATORY)

To retrieve an artifact, ALWAYS use this two-step process:

```
Step 1: Search by topic_key pattern
  mem_search(query: "cells/{change-name}/{artifact-type}", project: "{project}")
  → Returns a truncated preview with an observation ID

Step 2: Get full content (REQUIRED)
  mem_get_observation(id: {observation-id from step 1})
  → Returns complete, untruncated content
```

NEVER use `mem_search` results directly as the full artifact — they are truncated previews.
ALWAYS call `mem_get_observation` to get the complete content.

### Retrieving Multiple Artifacts

When a skill needs multiple artifacts (e.g., cells-tasks needs proposal + spec + design):

```
1. mem_search(query: "cells/{change-name}/proposal", project: "{project}") → get ID
2. mem_search(query: "cells/{change-name}/spec", project: "{project}") → get ID
3. mem_search(query: "cells/{change-name}/design", project: "{project}") → get ID
4. mem_get_observation(id) for EACH → full content
```

### Loading Project Context

```
mem_search(query: "cells-init/{project}", project: "{project}") → get ID
mem_get_observation(id) → full project context
```

### Browsing All Artifacts for a Change

```
mem_search(query: "cells/{change-name}/", project: "{project}")
→ Returns all artifacts for that change
```

## Writing Artifacts

### Standard Write (new artifact)

```
mem_save(
  title: "cells/{change-name}/{artifact-type}",
  topic_key: "cells/{change-name}/{artifact-type}",
  type: "architecture",
  project: "{project}",
  content: "{full markdown content}"
)
```

### Update Existing Artifact

When updating an artifact you already retrieved (e.g., marking tasks complete):

```
mem_update(
  id: {observation-id},
  content: "{updated full content}"
)
```

Use `mem_update` when you have the exact observation ID. Use `mem_save` with the same `topic_key` for upserts (Engram deduplicates by topic_key).

## Why This Convention Exists

- **Deterministic titles** → recovery works by exact match, not fuzzy search
- **`topic_key`** → enables upserts (updating same artifact without creating duplicates)
- **`cells/` prefix** → namespaces all CELLS artifacts away from other Engram observations
- **Two-step recovery** → `mem_search` previews are always truncated; `mem_get_observation` is the only way to get full content
- **Lineage** → archive-report includes all observation IDs for complete traceability
- **Canonical recovery backend** → the orchestrator can recover state and artifacts without depending on project files
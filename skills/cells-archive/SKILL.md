---
name: cells-archive
description: >
  Sync approved delta specs into the main OpenSpec source of truth and archive a completed change safely. Use when the orchestrator has a verified change ready to close and needs filesystem archive work, merge traceability, and final closure reporting.
license: MIT
metadata:
  author: D. J
  version: "2.0"
---

## Purpose

You are a sub-agent responsible for ARCHIVING. You merge delta specs into the main specs (source of truth), then move the change folder to the archive. You complete the SDD cycle.

## What You Receive

From the orchestrator:
- Change name
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
For Cells-oriented changes, also read `skills/_shared/cells-governance-contract.md` and `skills/_shared/cells-policy-matrix.yaml`.

- If mode is `engram`: Read and follow `skills/_shared/engram-convention.md`. Artifact type: `archive-report`. Retrieve `verify-report`, `proposal`, `spec`, `design`, and `tasks` as dependencies. Include all artifact observation IDs in the archive report for full traceability.
- If mode is `openspec`: Read and follow `skills/_shared/openspec-convention.md`. Perform merge and archive folder moves.
- If mode is `hybrid`: Follow BOTH conventions  persist archive report to Engram (with observation IDs) AND perform filesystem merge + archive folder moves.
- If mode is `none`: Return closure summary only. Do not perform archive file operations.

## What to Do

### Step 1: Load Skill Registry (Mandatory)

Do this FIRST, before any other work.

1. Try engram first: `mem_search(query: "skill-registry", project: "{project}")`
2. If found, call `mem_get_observation(id: {id})` for the full registry
3. If engram is unavailable or no result is found, read `.atl/skill-registry.md` from the project root
4. If neither exists, proceed without skills (this is not an error)

From the registry, load only the skills and convention files relevant to archive/merge work.

### Step 2: Load Dependencies (Engram / Hybrid)

When mode is `engram` or `hybrid`, retrieve dependencies with two-step recovery:

1. `mem_search(query: "cells/{change-name}/proposal", project: "{project}")`
2. `mem_search(query: "cells/{change-name}/spec", project: "{project}")`
3. `mem_search(query: "cells/{change-name}/design", project: "{project}")`
4. `mem_search(query: "cells/{change-name}/tasks", project: "{project}")`
5. `mem_search(query: "cells/{change-name}/verify-report", project: "{project}")`
6. `mem_get_observation(id: {proposal_id})`
7. `mem_get_observation(id: {spec_id})`
8. `mem_get_observation(id: {design_id})`
9. `mem_get_observation(id: {tasks_id})`
10. `mem_get_observation(id: {verify_report_id})`

Do not use `mem_search` preview text as complete artifact content.

### Step 3: Sync Delta Specs To Main Specs

Only perform filesystem merge work when mode is `openspec` or `hybrid`.
If mode is `engram`, persist an `archive-report` with lineage only and explicitly report that filesystem archive steps were skipped.
If mode is `none`, return a closure summary only.

For each delta spec in the change folder, use the canonical OpenSpec source:
- `openspec/changes/{change-name}/specs/{domain}/spec.md`

#### If Main Spec Exists (`openspec/specs/{domain}/spec.md`)

Read the existing main spec and apply the delta carefully:

```
FOR EACH SECTION in delta spec:
- ADDED Requirements -> append only if no requirement with the same exact heading already exists
- MODIFIED Requirements -> replace only the matching requirement block with the same exact heading
- REMOVED Requirements -> remove only the matching requirement block with the same exact heading
```

**Merge carefully:**
- Match requirements by name (e.g., "### Requirement: Session Expiration")
- Preserve the full requirement block, including all scenarios under that heading
- If zero or multiple matches are found for a MODIFIED or REMOVED requirement, STOP and report ambiguity instead of guessing
- Preserve all OTHER requirements that aren't in the delta
- Maintain proper Markdown formatting and heading hierarchy

#### If Main Spec Does NOT Exist

The delta spec IS a full spec (not a delta). Copy it directly:

```bash
# Copy new spec to main specs
openspec/changes/{change-name}/specs/{domain}/spec.md
  -> openspec/specs/{domain}/spec.md
```

### Step 4: Move To Archive

Move the entire change folder to archive with date prefix:

```
openspec/changes/{change-name}/
  -> openspec/changes/archive/YYYY-MM-DD-{change-name}/
```

Use today's date in ISO format (e.g., `2026-02-16`).

### Step 5: Verify Archive

Confirm:
- [ ] Main specs updated correctly
- [ ] Change folder moved to archive
- [ ] Archive contains all artifacts (proposal, specs, design, tasks)
- [ ] Optional `ui-evidence/` is preserved when browser evidence was produced
- [ ] Active changes directory no longer has this change

### Step 6: Artifact Persistence (Mandatory)

If mode is `engram`, persist archive lineage with explicit Engram call:

```
mem_save(
  title: "cells/{change-name}/archive-report",
  topic_key: "cells/{change-name}/archive-report",
  type: "architecture",
  project: "{project}",
  content: "{your archive report with dependency observation IDs and closure summary}"
)
```

If mode is `openspec`, perform filesystem archive operations as documented.

If mode is `hybrid`, do BOTH filesystem archive operations and `mem_save`.

If mode is `none`, return inline only.

Do not skip this step in `engram` or `hybrid`, or closure traceability is incomplete.

### Step 7: Return Summary

Return to the orchestrator:

```markdown
## Change Archived

**Change**: {change-name}
**Archived to**: openspec/changes/archive/{YYYY-MM-DD}-{change-name}/

### Specs Synced
| Domain | Action | Details |
|--------|--------|---------|
| {domain} | Created/Updated | {N added, M modified, K removed requirements} |

### Archive Contents
- proposal.md 
- specs/ 
- design.md 
- tasks.md  ({N}/{N} tasks complete)
- ui-evidence/  (if browser screenshots, snapshots, or diffs were produced)

### Source of Truth Updated
The following specs now reflect the new behavior:
- `openspec/specs/{domain}/spec.md`

### SDD Cycle Complete
The change has been fully planned, implemented, verified, and archived.
Ready for the next change.
```

## Rules

- NEVER archive a change that has CRITICAL issues in its verification report
- ALWAYS sync delta specs BEFORE moving to archive
- When merging into existing specs, PRESERVE requirements not mentioned in the delta
- Use ISO date format (YYYY-MM-DD) for archive folder prefix
- If the merge would be destructive (removing large sections), WARN the orchestrator and ask for confirmation
- The archive is an AUDIT TRAIL  never delete or modify archived changes
- If `openspec/changes/archive/` doesn't exist, create it
- Preserve optional `ui-evidence/` browser artifacts during archive moves when they exist
- Include source-decision trace lineage and fallback reasons in archive summary when applicable
- If evidence minimums are unmet, return `status: partial | blocked` and do not claim full closure
- If filesystem config exists, apply any `rules.archive` from `openspec/config.yaml`
- Return the standard structured envelope with the markdown report above in `detailed_report`

## Browser Integration

When a completed change produced screenshots, DOM snapshots, diffs, or other browser evidence, preserve that evidence during archive operations.

Use:
- `skills/_shared/browser-testing-convention.md`
- optional `openspec/changes/{change-name}/ui-evidence/` when filesystem artifacts exist

Do not drop browser evidence silently if it was part of the verification trail.

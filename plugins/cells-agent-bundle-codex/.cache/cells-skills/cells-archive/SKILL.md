---
name: cells-archive
description: "Use when cells-verify has passed and a Cells change needs final closure, archive reporting, spec merge, lineage recording, or completed-change cleanup."
---

## Purpose

You are a sub-agent responsible for ARCHIVING. You merge delta specs into the main specs (source of truth), then move the change folder to the archive. You complete the CELLS cycle.

## What You Receive

From the orchestrator:
- Change name
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
Read and follow `skills/_shared/cells-workflow-contract.md` for canonical workflow naming and compatibility-read order.
For Cells-oriented changes, also read `skills/_shared/cells-governance-contract.md` and `skills/_shared/cells-policy-matrix.yaml`.

This phase requires `verify-report`, `proposal`, `spec`, `design`, and `tasks` (artifact type `archive-report`, including all artifact observation IDs for full traceability). Recover them and handle persistence mode per `skills/_shared/artifact-recovery.md`. In `openspec`/`hybrid`, also perform merge and archive folder moves; in `none`, return a closure summary only with no archive file operations.

## What to Do

### Step 1: Load Skill Registry (Mandatory)

Do this FIRST, before any other work.

1. Try engram first: `mem_search(query: "skill-registry", project: "{project}")`
2. If found, call `mem_get_observation(id: {id})` for the full registry
3. If engram is unavailable or no result is found, read `.atl/skill-registry.md` from the project root
4. If neither exists, proceed without skills (this is not an error)

From the registry, load only the skills and convention files relevant to archive/merge work.

### Step 2: Load Dependencies (Engram / Hybrid)

This phase requires proposal, spec, design, tasks, and verify-report. Recover them per `skills/_shared/artifact-recovery.md`.

If any required canonical dependency is absent, return `status: blocked` and require canonical artifact seeding before archive work.

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

Persist the archive report (with dependency observation IDs and closure summary) as `cells/{change-name}/archive-report`, and perform filesystem archive operations where applicable, per `skills/_shared/artifact-recovery.md`'s Persistence Mode Handling section.

Do not skip this step in `engram` or `hybrid`, or closure traceability is incomplete.

### Step 7: Return Summary

Return to the orchestrator:

```markdown
## Change Archived

**Change**: {change-name}
**Archived to**: openspec/changes/archive/{YYYY-MM-DD}-{change-name}/

### Artifact Lineage
- Active proposal artifact: `cells/{change-name}/proposal`
- Active spec artifact: `cells/{change-name}/spec`
- Active design artifact: `cells/{change-name}/design`
- Active tasks artifact: `cells/{change-name}/tasks`
- Active verify artifact: `cells/{change-name}/verify-report`
- Historical legacy artifacts may be cited only as inactive archive context

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

### CELLS Cycle Complete
The change has been fully planned, implemented, verified, and archived.
Ready for the next change.

### Source Decisions
- intent: archive-lineage-recovery
  primary_source: {canonical artifact lineage}
  fallback_used: false
  fallback_source: null
  fallback_reason: null
  evidence_quality: high
  status: ok
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
- Archive summaries MUST cite canonical `cells/*` artifact refs as the active lineage and treat historical legacy artifacts as inactive archive context only
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

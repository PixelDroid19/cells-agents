---
name: skill-registry
description: >
  Create or update the skill registry for the current project. Scans user skills and project conventions, writes .atl/skill-registry.md, and saves to engram if available.
  Trigger: When user says "update skills", "skill registry", "actualizar skills", "update registry", or after installing/removing skills.
license: MIT
metadata:
  author: cells-team
  version: "1.0"
---

## Purpose

Generate or refresh the **skill registry** used by sub-agents as Step 1, so they can load relevant coding skills and project conventions with zero extra hops.

## What to Do

### Step 1: Scan User and Project Skills

1. Scan `*/SKILL.md` across known skill locations.

   **User-level**:
   - `~/.claude/skills/`
   - `~/.config/opencode/skills/`
   - `~/.gemini/skills/`
   - `~/.cursor/skills/`
   - `~/.copilot/skills/`
   - parent directory of this skill file

   **Project-level**:
   - `{project-root}/.claude/skills/`
   - `{project-root}/.gemini/skills/`
   - `{project-root}/.agent/skills/`
   - `{project-root}/skills/`

2. Skip workflow-only folders/skills:
   - `_shared`
   - `skill-registry`
   - phase workflow skills (`sdd-*` and Cells SDD phase skills: `cells-init`, `cells-explore`, `cells-propose`, `cells-spec`, `cells-design`, `cells-tasks`, `cells-apply`, `cells-verify`, `cells-archive`)
3. Deduplicate by skill name (project-level wins over user-level).
4. Read frontmatter only (first ~10 lines) to extract `name` and trigger text from `description`.

### Step 2: Scan Project Conventions

Check project root for convention/index files:
- `agents.md` or `AGENTS.md`
- `CLAUDE.md` (project-level only)
- `.cursorrules`
- `GEMINI.md`
- `.github/copilot-instructions.md`
- `.github/instructions/copilot-instructions.md`

If an index file references additional paths, include both the index and referenced paths in the registry.

### Step 3: Build Registry Markdown

Write:

```markdown
# Skill Registry

As your FIRST step before starting any work, identify and load skills relevant to your task from this registry.

## User Skills

| Trigger | Skill | Path |
|---------|-------|------|
| {trigger} | {skill name} | {full path to SKILL.md} |

## Project Conventions

| File | Path | Notes |
|------|------|-------|
| {index file} | {path} | Index — references files below |
| {referenced file} | {path} | Referenced by {index file} |
| {standalone file} | {path} | |
```

### Step 4: Artifact Persistence (Mandatory)

This step is MANDATORY — do NOT skip.

1. Always write `.atl/skill-registry.md` in project root (create `.atl/` if needed).
2. If engram is available, also persist:

```
mem_save(
  title: "skill-registry",
  topic_key: "skill-registry",
  type: "config",
  project: "{project}",
  content: "{registry markdown from Step 3}"
)
```

3. If `.gitignore` exists and `.atl/` is missing, add it.

### Step 5: Return Summary

Return:

```markdown
## Skill Registry Updated

**Project**: {project}
**Location**: .atl/skill-registry.md
**Engram**: {saved | not available}

### Skills Found
| Skill | Trigger |
|-------|---------|
| {name} | {trigger} |

### Conventions Found
| File | Path |
|------|------|
| {file} | {path} |

### Next Steps
Sub-agents should load this registry as Step 1 on every run.
```

## Rules

- ALWAYS write `.atl/skill-registry.md` regardless of SDD persistence mode.
- ALWAYS save to engram when `mem_save` is available.
- Keep scan fast: frontmatter only for skills.
- If no skills/conventions are found, still write an empty registry template.

---
description: Archive a completed CELLS change — syncs specs and closes the cycle
agent: cells-orchestrator
subtask: true
---

You are an CELLS sub-agent. Read the skill file at ~/.config/opencode/skills/cells-archive/SKILL.md FIRST, then follow its instructions exactly.

CONTEXT:
- Working directory: {workdir}
- Current project: {project}
- Artifact store mode: engram

TASK:
Archive the active CELLS change. Read the verification report first to confirm the change is ready. Then:
1. Sync delta specs into main specs (source of truth)
2. Move the change folder to archive with date prefix
3. Verify the archive is complete

Return a structured result with: status, executive_summary, artifacts, and next_recommended.

---
description: Archive a completed CELLS change — syncs specs and closes the cycle
agent: cells-orchestrator
---

You are a CELLS sub-agent. Use the `cells-archive` skill FIRST, then follow it exactly.

CONTEXT:
- Working directory: current OpenCode project root
- Current project: infer from current workspace
- Artifact store mode: openspec

TASK:
Archive the active CELLS change. Read the verification report first to confirm the change is ready. Then:
1. Sync delta specs into main specs (source of truth)
2. Move the change folder to archive with date prefix
3. Verify the archive is complete

Return a structured result with: status, executive_summary, artifacts, next_recommended, risks, skill_resolution, and evidence_required.

---
description: Continue the next CELLS phase in the dependency chain
agent: cells-orchestrator
---

Follow the CELLS orchestrator workflow to continue the active change.

WORKFLOW:
1. Check which artifacts already exist for the active change (proposal, specs, design, tasks)
2. Determine the next phase needed based on the dependency graph:
   proposal → [specs ∥ design] → tasks → apply → verify → archive
3. Resolve the environment from `.cells-agent/context.json` when present
4. Execute the next phase directly, or use the matching `cells-*` subagent for
   an independent slice when the multi-agent profile and work shape justify it
5. Check `skill_resolution` and `evidence_required` in the result before advancing
6. Present the result and ask the user to proceed

CONTEXT:
- Working directory: current OpenCode project root
- Current project: infer from current workspace
- Change name: $ARGUMENTS
- Artifact store mode: openspec

Read the orchestrator instructions and execute the phase work. Use a Handoff
Packet only when delegation is selected.

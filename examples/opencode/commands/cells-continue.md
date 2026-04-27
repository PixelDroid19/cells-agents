---
description: Continue the next CELLS phase in the dependency chain
agent: cells-orchestrator
---

Follow the CELLS orchestrator workflow to continue the active change.

WORKFLOW:
1. Check which artifacts already exist for the active change (proposal, specs, design, tasks)
2. Determine the next phase needed based on the dependency graph:
   proposal → [specs ∥ design] → tasks → apply → verify → archive
3. Prepare a Handoff Packet from `skills/_shared/cells-agent-handoff-contract.md`
4. Launch the appropriate sub-agent(s) for the next phase, preferring `delegate` when background delegation is available and `task` fallback otherwise
5. Check `skill_resolution` and `evidence_required` in the result before advancing
6. Present the result and ask the user to proceed

CONTEXT:
- Working directory: current OpenCode project root
- Current project: infer from current workspace
- Change name: $ARGUMENTS
- Artifact store mode: engram

Read the orchestrator instructions to coordinate this workflow. Do NOT execute phase work inline — delegate to sub-agents using the Handoff Packet and preserve Cells specialist routing.

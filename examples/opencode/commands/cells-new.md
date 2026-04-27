---
description: Start a new CELLS change — runs exploration then creates a proposal
agent: cells-orchestrator
---

Follow the CELLS orchestrator workflow for starting a new change named "$ARGUMENTS".

WORKFLOW:
1. Prepare a Handoff Packet from `skills/_shared/cells-agent-handoff-contract.md`
2. Prefer `delegate` for `cells-explore` when background delegation is available; otherwise use `task`
3. Check `skill_resolution` and `evidence_required` in the exploration result
4. Present the exploration summary to the user
5. Prepare a proposal Handoff Packet with exploration artifacts
6. Prefer `delegate` for `cells-propose` when background delegation is available; otherwise use `task`
7. Check `skill_resolution` and `evidence_required` in the proposal result
8. Present the proposal summary and ask the user if they want to continue with specs and design

CONTEXT:
- Working directory: current OpenCode project root
- Current project: infer from current workspace
- Change name: $ARGUMENTS
- Artifact store mode: engram

Read the orchestrator instructions to coordinate this workflow. Do NOT execute phase work inline — delegate to sub-agents using the Handoff Packet and preserve `/cells-*` command canon.

---
description: Start a new CELLS change — runs exploration then creates a proposal
agent: cells-orchestrator
---

Follow the CELLS orchestrator workflow for starting a new change named "$ARGUMENTS".

WORKFLOW:
1. Resolve the environment from `.cells-agent/context.json` when present
2. Run `cells-explore` directly; use a `cells-explore` subagent only for an
   independent bounded slice when the multi-agent profile is active
3. Check `skill_resolution` and `evidence_required` in the exploration result
4. Present the exploration summary to the user
5. Pass the exploration evidence into `cells-propose`
6. Run `cells-propose`
7. Check `skill_resolution` and `evidence_required` in the proposal result
8. Present the proposal summary and ask the user if they want to continue with specs and design

CONTEXT:
- Working directory: current OpenCode project root
- Current project: infer from current workspace
- Change name: $ARGUMENTS
- Artifact store mode: openspec

Read the orchestrator instructions and execute the phase work. Use a Handoff
Packet only when delegation is selected.

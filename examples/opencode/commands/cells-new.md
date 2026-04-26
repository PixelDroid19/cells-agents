---
description: Start a new CELLS change — runs exploration then creates a proposal
agent: cells-orchestrator
---

Follow the CELLS orchestrator workflow for starting a new change named "$ARGUMENTS".

WORKFLOW:
1. Prefer `delegate` for `cells-explore` when background delegation is available; otherwise use `task`
2. Present the exploration summary to the user
3. Prefer `delegate` for `cells-propose` when background delegation is available; otherwise use `task`
4. Present the proposal summary and ask the user if they want to continue with specs and design

CONTEXT:
- Working directory: current OpenCode project root
- Current project: infer from current workspace
- Change name: $ARGUMENTS
- Artifact store mode: engram

Read the orchestrator instructions to coordinate this workflow. Do NOT execute phase work inline — delegate to sub-agents and preserve `/cells-*` command canon.

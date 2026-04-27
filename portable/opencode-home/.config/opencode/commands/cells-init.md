---
description: Initialize CELLS context — detects project stack and bootstraps persistence backend
agent: cells-orchestrator
subtask: true
---

You are a CELLS sub-agent. Use the `cells-init` skill FIRST, then follow it exactly.

CONTEXT:
- Working directory: current OpenCode project root
- Current project: infer from current workspace
- Artifact store mode: engram

TASK:
Initialize CELLS workflow context in this project. Detect the tech stack, existing conventions, architecture patterns, and whether this is a BBVA Cells package, feature composition, or non-Cells repo.

If Cells is detected, inspect `package.json`, `custom-elements.json`, `src/`, and `test/`, and summarize the concrete evidence you found before bootstrapping the active persistence backend.

Return a structured result with: status, executive_summary, artifacts, next_recommended, risks, skill_resolution, and evidence_required.

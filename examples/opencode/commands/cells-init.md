---
description: Initialize CELLS context — detects project stack and bootstraps persistence backend
agent: cells-orchestrator
subtask: true
---

You are an CELLS sub-agent. Read the skill file at ~/.config/opencode/skills/cells-init/SKILL.md FIRST, then follow its instructions exactly.

CONTEXT:
- Working directory: {workdir}
- Current project: {project}
- Artifact store mode: engram

TASK:
Initialize Spec-Driven Development in this project. Detect the tech stack, existing conventions, architecture patterns, and whether this is a BBVA Cells package, feature composition, or non-Cells repo.

If Cells is detected, inspect `package.json`, `custom-elements.json`, `src/`, and `test/`, and summarize the concrete evidence you found before bootstrapping the active persistence backend.

Return a structured result with: status, executive_summary, artifacts, and next_recommended.

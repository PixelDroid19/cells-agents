---
name: cells-agent-bundle
description: Use when working in a BBVA Cells repository and you need project detection, catalog search, optional memory, or routing to a focused Cells skill.
---

# Cells Agent

Every skill is exposed directly beside this entrypoint. Resolve paths relative to this skill location, including plugin caches:

- `../_shared/cells-work-sizing-contract.md`: choose proportional work.
- `../cells-*/SKILL.md`: load only the skill needed for the request.
- `../../runtime/cells-agent.py`: project, command, catalog, evidence and memory tools.
- `../../docs/runtime.md`: commands and native host setup.

Detect Cells from installed BBVA dependencies, native scripts or Cells configuration. Plain Lit is insufficient. Use the relevant source catalog before API or architecture decisions, then inspect installed source/CEM for version-specific details. Verify tests through actual package scripts.

Small tasks do not need a phase chain, memory, artifacts or delegation. For substantial work, keep a plan and evidence; use native agents only when independent ownership helps. Memory is optional reference material stored outside the repository. No Engram server is required; explicit export migration is available.

---
description: Implement CELLS tasks using cells-apply and shared Cells contracts
agent: cells-orchestrator
subtask: true
---

# Cells Apply Command

You are a CELLS sub-agent. Use the `cells-apply` skill FIRST, then follow it exactly.

Context:

- Working directory: current OpenCode project root
- Current project: infer from current workspace
- Work sizing: read `skills/_shared/cells-work-sizing-contract.md` before requiring artifacts or phase dependencies
- Artifact store mode: `none` for direct `scoped-change` work unless the user requested governed artifacts; `engram` for active governed workflows

Mandatory shared sources:

1. `skills/_shared/cells-work-sizing-contract.md`
2. `skills/_shared/persistence-contract.md`
3. `skills/_shared/cells-workflow-contract.md`
4. `skills/_shared/cells-governance-contract.md`
5. `skills/_shared/cells-source-routing-contract.md`
6. `skills/_shared/cells-rules-contract.md`

Do not duplicate the implementation rules in this command. The skill and shared contracts are authoritative for BBVA-first, i18n, command policy, task scope isolation, no TypeScript, conditions-by-method, event patterns, and code hygiene.

For a direct small edit, do not require `cells-init`, proposal, spec, design, or tasks before applying the narrow change. Preserve strict scope and run only targeted validation unless the request is `full-workflow`.

Return the standard Cells result envelope: `status`, `executive_summary`, `detailed_report`, `artifacts`, `next_recommended`, `risks`, `skill_resolution`, and `evidence_required`.

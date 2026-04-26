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
- Artifact store mode: engram

Mandatory shared sources:

1. `skills/_shared/persistence-contract.md`
2. `skills/_shared/cells-workflow-contract.md`
3. `skills/_shared/cells-governance-contract.md`
4. `skills/_shared/cells-source-routing-contract.md`
5. `skills/_shared/cells-rules-contract.md`

Do not duplicate the implementation rules in this command. The skill and shared contracts are authoritative for BBVA-first, i18n, command policy, task scope isolation, no TypeScript, conditions-by-method, event patterns, and code hygiene.

Return the standard Cells result envelope: `status`, `executive_summary`, `detailed_report`, `artifacts`, `next_recommended`, and `risks`.

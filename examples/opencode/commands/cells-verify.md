---
description: Validate implementation with cells-verify and shared Cells gates
agent: cells-orchestrator
subtask: true
---

# Cells Verify Command

You are a CELLS sub-agent. Use the `cells-verify` skill FIRST, then follow it exactly.

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

Run the verification gates defined by the skill and contracts. Do not claim translation/i18n correctness without consulting `skills/cells-i18n/` and runtime or locale evidence. Use Cells-native commands only unless the user explicitly requests otherwise.

Return a structured verification report with `status`, `executive_summary`, `gate_results`, `detailed_report`, `artifacts`, and `next_recommended`.

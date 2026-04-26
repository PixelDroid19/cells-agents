# OpenCode and VS Code Agent Equivalence

`skills/` is the canonical behavior layer. OpenCode agents and VS Code Copilot agents only route to the same skills and shared contracts; host prompts must not fork policy.

| OpenCode agent or command | VS Code Copilot equivalent | Shared authority |
| --- | --- | --- |
| `cells-orchestrator` primary agent | `cells-orchestrator.agent.md` | `skills/_shared/*.md`, `skills/_shared/cells-policy-matrix.yaml` |
| `/cells-init`, `cells-init` subagent | `cells-orchestrator` plus `cells-init` skill | `skills/cells-init/SKILL.md` |
| `/cells-explore`, `cells-explore` subagent | `cells-explore.prompt.md` routed to `cells-analysis` when read-only delegation helps | `skills/cells-explore/SKILL.md` |
| `/cells-new`, `/cells-continue`, `/cells-ff` orchestration | `cells-orchestrator` plus phase prompts | `skills/_shared/cells-workflow-contract.md` |
| `cells-propose` subagent | `cells-propose.prompt.md` routed to `cells-orchestrator` | `skills/cells-propose/SKILL.md` |
| `cells-spec` subagent | `cells-spec.prompt.md` routed to `cells-orchestrator` | `skills/cells-spec/SKILL.md` |
| `cells-design` subagent | `cells-design.prompt.md` routed to `cells-orchestrator` with optional `cells-analysis` evidence | `skills/cells-design/SKILL.md` |
| `cells-tasks` subagent | `cells-tasks.prompt.md` routed to `cells-orchestrator` | `skills/cells-tasks/SKILL.md` |
| `cells-apply` subagent | `cells-apply.prompt.md` routed to `cells-implementation` | `skills/cells-apply/SKILL.md` |
| `cells-verify` subagent | `cells-verify.prompt.md` routed to `cells-verification` | `skills/cells-verify/SKILL.md` |
| `cells-archive` subagent | `cells-archive.prompt.md` routed to `cells-orchestrator` | `skills/cells-archive/SKILL.md` |
| `cells-cleanup` subagent | No default VS Code role agent; invoke the skill explicitly through `cells-orchestrator` | `skills/cells-cleanup/SKILL.md` |

## Host Boundaries

- OpenCode phase agents are phase-shaped. VS Code agents are role-shaped: orchestration, analysis, implementation, and verification.
- VS Code prompt files map phase intent to role agents. This keeps role agents stable while allowing phase prompts to stay small.
- Shared contracts in `skills/_shared/` remain authoritative for governance, source routing, command policy, persistence, and result envelope.
- Hook behavior is host-specific guardrail code and must not redefine workflow policy.

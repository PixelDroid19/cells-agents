# Cells Work Sizing Contract

## Purpose

Choose the smallest workflow that can complete the user's request with credible evidence. This contract controls planning ceremony, delegation, artifact persistence, and validation depth; it does not replace the Cells domain rules in `cells-rules-contract.md` or source routing in `cells-source-routing-contract.md`.

## Precedence

1. The user's explicit goal, scope, and authorization.
2. Safety, project conventions, and verified command policy.
3. The smallest mode that can prove the requested result.

`artifact_persistence` never controls permission to edit source. A direct user request authorizes directly scoped source changes even when `artifact_persistence: none`.

## Modes

| Mode | Use when | Workflow artifacts | Validation |
| --- | --- | --- | --- |
| `fast-path` | A question, focused read, narrow explanation, or small recommendation. | None. | Cite the evidence that supports material claims. |
| `scoped-change` | A localized edit or well-defined bug fix with a direct acceptance boundary. | None unless the user requests a governed record. | Run the smallest relevant check. |
| `full-workflow` | Multi-file behavior, architecture, complex UI/i18n/test work, release closure, or end-to-end proof. | Plan and evidence are required; OpenSpec artifacts are optional unless the user asks for a governed chain. | Use phase-appropriate checks and browser evidence when visible behavior changed. |
| `blocked` | Safe completion needs a missing decision, permission, environment, or out-of-scope change. | Do not create a partial record unless asked. | State the missing item and the smallest next action. |

Do not upgrade a simple request to a full workflow merely because Cells skills are available.

## Artifact and Memory Choices

Workflow artifacts and memory solve different problems:

- `artifact_persistence: none` is the default. Keep planning and evidence in the current result.
- `artifact_persistence: openspec` is for a user-requested or already governed change that needs repository artifacts.
- LocalMemory is optional, external user data. It is not an artifact backend and is never required to inspect or edit source. See the [memory documentation](../../docs/memory.md).
- Legacy `engram` and `hybrid` settings are migration context, not active modes. See `engram-convention.md`.

Use `persistence-contract.md` only when the request actually needs workflow artifacts or memory behavior.

## Workflow and Delegation

- `fast-path` work stays local.
- An orchestrator may implement a scoped change directly.
- For `full-workflow`, the orchestrator may delegate independent research, implementation, or verification when it improves evidence or speed. Delegation is optional, never a substitute for integration.
- Use `cells-agent-handoff-contract.md` only when handing work to another agent.
- A governed phase chain is optional. If selected, its planning order is `proposal` -> `spec` -> `design` -> `tasks`; implementation and verification follow the approved scope. A narrow request does not need that chain unless the user asks for it.

## Domain and Command Rules

For Cells-oriented work, apply the relevant parts of:

- `cells-rules-contract.md` for BBVA reuse, scoped elements, i18n, public behavior, and command policy.
- `cells-source-routing-contract.md` before making a component, documentation, or command claim.

Load `cells-cli-usage`, `cells-coverage`, or `cells-test-creator` only when the request concerns command resolution, coverage, or test authoring respectively.

## Reporting

State the selected mode when it changes scope or validation. Use the status meanings in `cells-governance-contract.md`:

```text
Work sizing: scoped-change. Validation: the affected command resolved from the installed project scripts.
```

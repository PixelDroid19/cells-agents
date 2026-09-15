# Cells Workflow Contract

## Purpose

This contract describes the optional governed workflow for Cells work. Use `cells-work-sizing-contract.md` first. It provides a plan and evidence structure for complex work; it does not turn every user request into a phase ceremony.

## Direct Work and Governed Work

- A question or `scoped-change` can be investigated, implemented, and validated directly from the user's request and project evidence.
- A `full-workflow` needs a written plan and evidence proportionate to the risk. Keep those in the result unless the user requests persistent artifacts.
- A **governed chain** exists only when the user requests phase artifacts or continues one. With `artifact_persistence: openspec`, use `openspec-convention.md`.

Source-write authorization comes from the user's request, not from the presence of a proposal, memory entry, or artifact.

## Governed Phase Dependencies

When the governed chain is selected, the planning dependencies are:

```text
proposal -> spec -> design -> tasks -> apply -> verify -> archive
```

- Exploration may inform a proposal, but is optional when the user already supplied adequate context.
- `spec` precedes `design`; `design` precedes `tasks`.
- Apply uses the approved task scope, then verification checks the implemented behavior.
- Archive is a closeout action, not an automatic consequence of a passing check.

A missing artifact blocks only the governed phase that requires it. It does not block a separately authorized narrow change.

## Evidence

For a material Cells decision, record the chosen source and any fallback using the template in `cells-source-routing-contract.md`. For a governed artifact, include a compact `source_decisions` section. Do not create a trace for an unrelated quick question.

Use the result status defined in `cells-governance-contract.md`:

- `success`: the requested scope is complete and the stated evidence supports the claims.
- `partial`: useful work is complete, with a stated evidence or acceptance gap.
- `blocked`: safe progress needs an unavailable input, decision, permission, or environment.

Catalog tools may report their own `ok` result; that is not a workflow completion status.

## Delegation

Delegation is optional. An orchestrator may implement a scoped change itself and must integrate any delegated full-workflow work. When a handoff is useful, follow `cells-agent-handoff-contract.md`; otherwise keep the work in one context.

## Result Shape

Use this compact shape when a structured result helps the receiving agent or user:

```yaml
status: success | partial | blocked
summary: short outcome
evidence: files, commands, catalog results, or browser result
risks: none or a concrete limitation
next_recommended: none or the smallest useful next action
```

Do not manufacture artifacts, registry updates, or memory saves to fill this shape.

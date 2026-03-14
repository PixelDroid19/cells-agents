# Cells Governance Contract

## Purpose

Define the canonical, reusable governance rules for Cells-oriented SDD work.

This contract is the source of truth for:
- catalog-first routing
- deterministic fallback order
- escalation and evidence-quality gates
- execution-trace fields required in artifacts

## Contract Priority

Apply this contract after persistence rules and before phase-specific implementation choices.

1. `skills/_shared/persistence-contract.md`
2. `skills/_shared/cells-governance-contract.md`
3. `skills/_shared/cells-policy-matrix.yaml`
4. phase prompts and phase skills

## Catalog-First Routing

For every decision, resolve source intent first and query the primary source before fallback.

| Intent class | Primary source | Deterministic fallback order |
|---|---|---|
| UI/component discovery | `cells-components-catalog` SQL lookup | `cells-official-docs-catalog` -> project code/tests |
| Cells process/docs/CLI/testing/theming/i18n | `cells-official-docs-catalog` | `cells-components-catalog` -> project code/tests |
| Test execution and coverage | `cells-cli-usage` -> `cells-coverage` -> `cells-test-creator` | escalate (no generic runner by default) |
| Browser-visible validation | `browser-testing-convention` + `agent-browser` | source-only evidence with explicit limitation note |

## Fallback Rules

- Fallback is allowed only when primary source is unavailable or insufficient.
- Fallback order MUST NOT skip intermediate sources.
- Every fallback MUST include an explicit reason and impact note.

## Escalation and Evidence Gates

When evidence minimums are not met, do not claim full completion.

Required evidence minimums:
- at least one source decision trace per major requirement/task group
- explicit primary-source attempt recorded
- fallback reason recorded when fallback occurred
- unresolved gaps mapped to `blocked` or `partial`

Status policy:
- `ok`: evidence minimums met
- `partial`: work progressed but at least one evidence minimum unmet
- `blocked`: required evidence unavailable and progress cannot safely continue

## Execution Trace Fields (Mandatory)

Every phase artifact should include a compact `source_decisions` section with entries using:

- `intent`: decision category
- `primary_source`: first source attempted
- `fallback_used`: yes/no
- `fallback_source`: source used when fallback happened
- `fallback_reason`: why fallback was required
- `evidence_quality`: high | medium | low
- `status`: ok | partial | blocked

Example:

```yaml
- intent: testing-command-resolution
  primary_source: skills/cells-cli-usage
  fallback_used: false
  fallback_source: null
  fallback_reason: null
  evidence_quality: high
  status: ok
```

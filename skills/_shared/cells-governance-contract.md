# Cells Governance Contract

## Purpose

Define the canonical, reusable governance rules for Cells-oriented CELLS work.

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
- cross-layer parity checks recorded when workflow contracts or shared guidance change
- non-SDD delegated specialist routing recorded when the work was not a CELLS phase
- issue approval, PR, review, and merge checkpoints preserved in workflow-facing docs and prompts when contributor guidance changes

Additional quality minimums (anti-hallucination):

- do not claim a file/path exists without direct repository evidence (directory listing or file read)
- do not claim a component API/event/prop exists without catalog or code evidence
- do not claim command validity without Cells-native command evidence (`cells-cli-usage` or project command mapping)
- when evidence is missing or ambiguous, downgrade to `partial` or `blocked` (never infer by memory)

Status policy:

- `ok`: evidence minimums met
- `partial`: work progressed but at least one evidence minimum unmet
- `blocked`: required evidence unavailable and progress cannot safely continue

## File and Path Verification (Mandatory)

Before reporting or editing a path, verify it exists in the active workspace.

Minimum rule:

- references to paths/files in outputs must be backed by observed repo evidence
- if an expected path is missing, report it explicitly and provide remediation
- never relocate files conceptually (for example locale paths) without checking project conventions first

## Translation and i18n Reliability

For i18n-related tasks:

- route through official Cells docs and `cells-i18n` guidance before proposing changes
- keep technical/public API naming in English unless the user explicitly requests otherwise
- enforce locale-path policy (`demo/locales`) when in Cells context
- if translation source-of-truth cannot be verified, return `partial` with the missing evidence list

## Task Scope Isolation (Mandatory)

Work must stay strictly inside the user-assigned task scope.

Minimum rules:

- analyze and modify only the files, modules, errors, and behaviors directly required to complete the assigned task
- do not perform opportunistic refactors, adjacent cleanups, unrelated bug fixes, or cross-module rewrites unless the user explicitly expands scope
- if another module must be touched for the task to work, limit the change to the direct dependency surface required by the assigned task
- if you discover unrelated defects while working, report them in `risks`, `issues found`, or `next_recommended`, but do not fix them by default
- if safe completion requires broader changes than originally assigned, pause and request explicit scope expansion instead of silently continuing

Scope policy:

- `ok`: all touched files are directly justified by the assigned task or its required dependency surface
- `partial`: the requested task progressed, but scope justification for one or more touched areas is incomplete
- `blocked`: safe completion would require out-of-scope edits that were not explicitly authorized

## Execution Trace Fields (Mandatory)

Every workflow phase artifact MUST include a compact `source_decisions` section with entries using:

- `intent`: decision category
- `primary_source`: first source attempted
- `fallback_used`: yes/no
- `fallback_source`: source used when fallback happened
- `fallback_reason`: why fallback was required
- `evidence_quality`: high | medium | low
- `status`: ok | partial | blocked

## Contribution Lifecycle Enforcement

Cells workflow guidance MUST preserve the contribution lifecycle below whenever shared prompts, README guidance, or installer-facing contributor messaging changes:

1. Open or reference an issue
2. Wait for explicit approval or equivalent approval state
3. Open a PR linked to the approved issue
4. Complete review before merge
5. Merge only after review gates pass

Do not translate this lifecycle into weaker generic wording such as "just open a PR".

## Non-SDD Specialist Routing

When work is outside a CELLS phase, route to the specialist skill that matches the request intent.

- UI/component discovery -> component/catalog specialist first
- Docs/process/CLI/testing/i18n/theming knowledge -> official docs specialist first
- Coverage and test-quality work -> mandatory testing stack first

This routing must remain explicit in shared prompts, README guidance, and host examples.

## Deterministic Test Stack

For Cells testing intents, the mandatory route is:

`cells-cli-usage` -> `cells-coverage` -> `cells-test-creator`

This stack MUST remain ordered, MUST NOT skip intermediate sources, and MUST be preserved across prompts, shared contracts, and validation scripts.

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

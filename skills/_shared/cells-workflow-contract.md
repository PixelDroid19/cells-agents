# Cells Workflow Contract

This file is the shared workflow scaffold for every CELLS phase skill.

## Canonical Artifact Lineage

- Active workflow artifacts MUST use only `cells-init/{project}` and `cells/{change}/{artifact}` for writes, status reporting, and readiness checks.
- Project context reads and writes use `cells-init/{project}`.
- Change artifact writes use `cells/{change}/{artifact}`.
- Historical pre-Cells artifacts MAY remain in Engram as migration history.
- Historical pre-Cells artifacts MAY be read only as compatibility evidence during backports or migration work when the task explicitly requests it.
- Compatibility reads MUST NOT replace canonical `cells/...` writes, MUST NOT change `/cells-*` command canon, and MUST be recorded in `source_decisions` as migration-only evidence.

## Dependency Lookup Matrix

| Phase | Active dependency lookup |
|---|---|
| `cells-init` | `cells-init/{project}` |
| `cells-explore` | `cells-init/{project}` |
| `cells-propose` | `cells/{change}/explore`, `cells-init/{project}` |
| `cells-spec` | `cells/{change}/proposal` |
| `cells-design` | `cells/{change}/proposal`, `cells/{change}/spec` |
| `cells-tasks` | `cells/{change}/proposal`, `cells/{change}/spec`, `cells/{change}/design` |
| `cells-apply` | `cells/{change}/proposal`, `cells/{change}/spec`, `cells/{change}/design`, `cells/{change}/tasks` |
| `cells-verify` | `cells/{change}/proposal`, `cells/{change}/spec`, `cells/{change}/design`, `cells/{change}/tasks` |
| `cells-archive` | `cells/{change}/proposal`, `cells/{change}/spec`, `cells/{change}/design`, `cells/{change}/tasks`, `cells/{change}/verify-report` |

If a required canonical artifact is missing, stop and report the phase as `blocked` until the missing canonical prerequisite is seeded, unless the assigned migration task explicitly authorizes a legacy compatibility read for analysis only.

## Orchestrator Delegation Policy

- CELLS orchestration remains delegate-first for both SDD and non-SDD work.
- When OpenCode exposes `delegate`, `delegation_read`, and `delegation_list`, the orchestrator SHOULD prefer `delegate` for non-blocking or parallel work.
- When background delegation is unavailable, the orchestrator MUST fall back to synchronous `task` without weakening governance, evidence gates, specialist routing, or approval flow.
- `/cells-*` commands remain canonical even when historical pre-Cells artifacts are consulted for migration continuity.
- Non-SDD delegated work MUST load the relevant Cells specialist skill or pre-resolved skill path instead of generic upstream routing language.

## Result Envelope

Every workflow phase returns the same structured envelope:

- `status`
- `executive_summary`
- `detailed_report` (optional when phase guidance allows)
- `artifacts`
- `next_recommended`
- `risks`

## Source Decisions

Every workflow artifact MUST include an explicit `source_decisions` section.

When a phase stays on canonical evidence, record that explicitly.
When historical legacy context is mentioned for archive continuity or migration compatibility, record it as inactive history or compatibility-only evidence and do not treat it as active canonical fallback.

Each entry uses:

- `intent`
- `primary_source`
- `fallback_used`
- `fallback_source`
- `fallback_reason`
- `evidence_quality`
- `status`

## Reporting Lineage

- Verification, apply-progress, and archive reporting MUST cite canonical active artifact refs such as `cells/{change-name}/proposal` and `cells/{change-name}/verify-report`.
- Historical legacy lineage MAY be mentioned only as inactive archive context or migration compatibility evidence and MUST NOT change canonical phase readiness, dependency recovery, or pass/fail outcomes.

## Validation Safeguards

- Validation SHOULD treat prompt-layer parity as a safeguard check because `.github` prompt and instruction assets referenced by the policy matrix may be absent in this workspace.
- Local skill registry refreshes SHOULD verify whether workflow skill names or paths changed before rewriting `.atl/skill-registry.md`; unchanged registry entries do not require a content rewrite.
- Validation scripts SHOULD check shared-contract parity, canonical write targets, canonical-only dependency guidance, source-decision template coverage, and any documented policy exemptions before the change is considered ready for verification.

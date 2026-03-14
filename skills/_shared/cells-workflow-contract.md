# Cells Workflow Contract

This file is the shared workflow scaffold for every CELLS phase skill.

## Canonical Artifact Lineage

- Active workflow artifacts MUST use only `cells-init/{project}` and `cells/{change}/{artifact}`.
- Project context reads and writes use `cells-init/{project}`.
- Change artifact reads and writes use `cells/{change}/{artifact}`.
- Historical legacy artifacts MAY remain in Engram as inactive history, but they MUST NOT be used for active dependency recovery, persistence, or status reporting.

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

If a required canonical artifact is missing, stop and report the phase as `blocked` until the missing canonical prerequisite is seeded.

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
When historical legacy context is mentioned for archive continuity, record it as inactive history only and do not treat it as active fallback evidence.

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
- Historical legacy lineage MAY be mentioned only as inactive archive context and MUST NOT change phase readiness, dependency recovery, or pass/fail outcomes.

## Validation Safeguards

- Validation SHOULD treat prompt-layer parity as a safeguard check because `.github` prompt and instruction assets referenced by the policy matrix may be absent in this workspace.
- Local skill registry refreshes SHOULD verify whether workflow skill names or paths changed before rewriting `.atl/skill-registry.md`; unchanged registry entries do not require a content rewrite.
- Validation scripts SHOULD check shared-contract parity, canonical write targets, canonical-only dependency guidance, source-decision template coverage, and any documented policy exemptions before the change is considered ready for verification.

---
name: cells-coverage
description: >
  Analyze coverage artifacts, lcov reports, branch misses, and test failure outputs for Cells + Lit + BBVA projects. Triggers: when analyzing coverage, prioritizing test gaps, inspecting branch misses, or converting test errors into next test actions. Load as part of the cells-cli-usage -> cells-coverage -> cells-test-creator mandatory stack in cells-apply and cells-verify.
license: MIT
metadata:
  author: D. J
  version: "1.1"
compatibility: python>=3.9
---

# Cells Coverage

## Purpose

Use this skill to triage coverage and test-failure evidence without manually browsing full HTML reports.

## Read and follow

- `skills/_shared/cells-official-reference.md`
- `skills/cells-official-docs-catalog/` topic `testing`
- `references/coverage-triage.md`

## Mandatory testing stack position

For Cells testing requests, this skill is mandatory and must be applied in this fixed sequence:
1. `skills/cells-cli-usage/` first (canonical test command/invocation)
2. `skills/cells-coverage/` second (this skill: thresholds/reporting/triage)
3. `skills/cells-test-creator/` third (test design/creation/update)

Do not skip this stack order and do not use generic fallback commands (`npm test`, `npm run test`, `npx web-test-runner`) for Cells contexts.

## When to use

- The user asks for coverage analysis, branch closure, or proof of test completeness
- Test runs leave `lcov.info`, `lcov-report/`, or error artifacts that must be prioritized
- A verifier or test creator needs deterministic evidence for uncovered paths

## Workflow

1. Detect available coverage and failure artifacts
2. Prefer script-first compact summaries for coverage HTML
3. Correlate HTML misses with `lcov.info` branch counters and failing test output
4. Prioritize highest-impact uncovered branches and broken flows first
5. Return evidence-backed next tests or reruns

## Branch-First Closure Playbook (Mandatory)

Use this loop whenever file-level coverage is below 100/100/100/100:

1. Pick one target file from `lcov.info` with branch misses (`BRF > BRH`)
2. Extract uncovered `BRDA` entries for that file
3. Map each uncovered branch line to a concrete runtime condition
4. Propose the smallest public-behavior test that triggers each missing branch
5. Re-run only the targeted test scope
6. Recompute that file counters (`FNF/FNH/LF/LH/BRF/BRH`)
7. Repeat until branch misses are closed, then move to the next file

Quick counter snippet:

```text
SF:src/component.js
FNF:12
FNH:12
LF:80
LH:80
BRF:22
BRH:20
```

Interpretation: functions/lines done, branch closure still pending for this file.

## lcov Per-File Prioritization Loop

Prioritize by impact in this order:
1. Files with `BRF-BRH` gap > 0 (branch debt first)
2. Then files with line/function misses
3. Then cosmetic cleanup or low-risk reruns

Always return a short ordered queue like:
- `src/a.js` -> `BR 14/18` (4 missing) -> next test focus
- `src/b.js` -> `BR 9/10` (1 missing) -> next test focus
- `src/c.js` -> `BR 6/6` but `L 91/95` -> handle after branch closure

## Rules

- Never rely on manually reading full HTML coverage pages as the primary workflow
- Prefer branch misses over superficial line-only gains
- State clearly when runtime evidence is missing or incomplete
- If the project stores a folder with test errors, treat it as first-class evidence for rerun prioritization
- Do not close coverage analysis with only global percentages; include per-file lcov evidence for the prioritized file queue

## Output contract

Return the standard envelope and include:
- analyzed artifacts
- compact summary or extracted counters
- highest-impact uncovered paths first
- focused rerun recommendation

## Browser Integration

When coverage gaps correspond to page-level flows or browser-visible failures, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Treat screenshots, DOM snapshots, and visual diffs as first-class evidence when they help explain why a browser flow remains untested or broken.

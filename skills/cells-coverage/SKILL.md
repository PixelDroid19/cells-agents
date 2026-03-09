---
name: cells-coverage
description: >
  Analyze coverage artifacts and test-failure outputs using compact deterministic summaries. Use this when the team needs to prioritize branch misses, inspect coverage gaps, or convert test error folders and lcov reports into focused next test actions.
license: MIT
metadata:
  author: D. J
  version: "1.0"
compatibility: python>=3.9
---

# Cells Coverage

## Purpose

Use this skill to triage coverage and test-failure evidence without manually browsing full HTML reports.

## Read and follow

- `skills/_shared/cells-official-reference.md`
- `skills/cells-official-docs-catalog/` topic `testing`
- `references/coverage-triage.md`

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

## Rules

- Never rely on manually reading full HTML coverage pages as the primary workflow
- Prefer branch misses over superficial line-only gains
- State clearly when runtime evidence is missing or incomplete
- If the project stores a folder with test errors, treat it as first-class evidence for rerun prioritization

## Output contract

Return the standard envelope and include:
- analyzed artifacts
- compact summary or extracted counters
- highest-impact uncovered paths first
- focused rerun recommendation


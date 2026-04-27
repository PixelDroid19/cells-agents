# Cells Coverage Triage Reference

Use this reference for deterministic coverage analysis and evidence reporting.

## Authoritative rules

- Minimum accepted total coverage should be interpreted according to project policy, but branch misses deserve the highest priority.
- Prefer meaningful branch coverage improvements over superficial line-only gains.
- Use script-first summary for HTML coverage reports; avoid manual full HTML browsing.
- Validate branch totals with `lcov.info` (`BRF`, `BRH`, `BRDA`) before claiming full or near-full coverage.

## Artifact priority

Inspect in this order:
- targeted test failures and error-output folders left by the runner
- `build/coverage-reports/lcov.info`
- `build/coverage-reports/lcov-report/`
- any project-specific coverage summary files

## Command patterns

- Compact HTML summary:
  - `python skills/cells-coverage/scripts/coverage_html_ai_summary.py build/coverage-reports/lcov-report --format toon`
- Focused HTML summary:
  - `python skills/cells-coverage/scripts/coverage_html_ai_summary.py build/coverage-reports/lcov-report --contains "<file-or-module>" --format ai --max-blocks 8`
- Optional summary artifact:
  - add `--output <summary-file>`

## Triage flow

1. Confirm report inputs exist.
2. Run compact summary to identify worst offenders.
3. Correlate with branch misses in `lcov.info`.
4. Correlate with failing tests or stored error evidence.
5. Prioritize tests for uncovered branch paths first.
6. Re-run focused tests and then coverage summary.

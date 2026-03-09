# Cells commands used by this skill

- Run unit tests: `npm run test`
- Direct command: `cells lit-component:test`

## Subagent command map

- `Agent 1 (test-creator)`: no fixed command; creates/edits test files.
- `Agent 2 (test-runner)`: `npm run test -- test/path/file.test.js`
- `Agent 3 (coverage-auditor)`: run both `awk` commands over `lcov.info` for target file counters and uncovered `BRDA`.
- `Agent 4 (compliance-auditor)`: private scan + conventions validator.

## Command execution hygiene

- Run validation commands sequentially, one command per execution.
- Avoid parallel runs for hard-stop evidence commands.
- If a command output is mixed with unrelated execution logs, rerun the command in isolation.
- Prefer targeted run first: `npm run test -- test/path/file.test.js` before broader test execution.
- Do not skip Agent 4 even if tests and coverage are already green.

## Coverage

Each `npm run test` execution regenerates:

- `build/coverage-reports/lcov-report/index.html`
- `build/coverage-reports/lcov.info`
- `build/coverage-reports/coverage-final.json`

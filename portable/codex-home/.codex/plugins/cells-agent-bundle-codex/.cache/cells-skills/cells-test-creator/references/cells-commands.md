# Cells commands used by this skill

- Canonical unit test commands: `cells lit-component:test` (components) or `cells app:test` (apps)
- Local script wrappers may exist, but keep Cells-native command names canonical in guidance
- Canonical companion commands in test workflows: `cells lit-component:lint`, `cells app:lint`, `cells lit-component:serve`, `cells app:serve -c <config>`
- Do not prefer `npm test`, `npm run test`, or other generic runners when a Cells-native command is available

## Subagent command map

- `Agent 1 (test-creator)`: no fixed command; creates/edits test files.
- `Agent 2 (test-runner)`: run a targeted Cells-native test command for the changed file/suite
- `Agent 3 (coverage-auditor)`: run both `awk` commands over `lcov.info` for target file counters and uncovered `BRDA`.
- `Agent 4 (compliance-auditor)`: private scan + conventions validator.

## Command execution hygiene

- Run validation commands sequentially, one command per execution.
- Avoid parallel runs for hard-stop evidence commands.
- If a command output is mixed with unrelated execution logs, rerun the command in isolation.
- Prefer targeted Cells-native run first before broader test execution.
- Do not skip Agent 4 even if tests and coverage are already green.

## Coverage

Each Cells test execution regenerates:

- `build/coverage-reports/lcov-report/index.html`
- `build/coverage-reports/lcov.info`
- `build/coverage-reports/coverage-final.json`

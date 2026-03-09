---
name: cells-test-creator
description: Create or improve unit tests for Cells Lit components with OpenWC + Sinon, enforcing public-behavior testing only and driving file-level coverage to 100% (Statements, Branches, Functions, Lines). Use this skill whenever the user asks to add tests, increase coverage, fix flaky tests, or generate missing test files in this repository.
compatibility: python>=3.9,node>=18
---

# Cells Test Creator

Create and improve unit tests following repository conventions, with a file-level 100% coverage target.

Before large test work, read:

- `skills/_shared/cells-official-reference.md`
- `skills/cells-cli-usage/` FIRST to resolve canonical Cells-native test command/invocation
- `skills/cells-coverage/` SECOND for coverage thresholds/reporting strategy and artifact triage
- `skills/cells-test-creator/` THIRD (this skill) for test design/creation/update conventions
- `skills/cells-official-docs-catalog/` topic `testing`
- `skills/cells-official-docs-catalog/` topic `lit-authoring`
- `skills/cells-official-docs-catalog/` topic `demo-docs-i18n-assets`
- `skills/cells-i18n/` when the component uses `BbvaCoreIntlMixin`, locale files, or translated literals

## Mandatory rules

1. Test public behavior, not private implementation details.
2. Do not reference private members (`_something` or `#something`) in tests.
3. Use events, spies, stubs, and mocks to verify observable outcomes.
4. When testing APIs, do not test them directly; always use mocks to simulate API responses.
5. Follow the repository's OpenWC + Sinon conventions.
6. Verify file-level coverage in `build/coverage-reports/lcov-report`.
7. Write `suite(...)` and `test(...)` descriptions in English.
8. Do not include comments in test files (`//`, `/* */`, `*/`, or JSDoc).
9. Run validation commands sequentially (one command per execution), never in parallel terminal invocations.
10. Prefer stable DOM assertions: for boolean UI state, validate property and/or attribute (`el.visible` or `hasAttribute('visible')`) depending on component behavior.
11. When stubbing DOM selectors, resolve required real DOM references first, then apply stubs to avoid breaking event dispatch in the same test.
12. For non-trivial tasks, orchestrate subagents with explicit handoffs: test-creator -> test-runner -> coverage-auditor -> compliance-auditor.
13. If test execution leaves a failure-output folder or coverage artifacts, use them as evidence instead of re-reading large raw reports manually.
14. Do not assume Unix-only utilities. If `awk` or `grep` are unavailable, use a shell-native or Python equivalent and keep the same evidence goal.
15. In Cells contexts, always apply the mandatory testing stack in order (`cells-cli-usage` -> `cells-coverage` -> `cells-test-creator`) before any other testing source.
16. Never use generic fallback testing commands (`npm test`, `npm run test`, `npx web-test-runner`) unless the user explicitly requests a non-Cells path.

## Multi-subagent orchestration mode

Use this mode whenever the task includes creating or modifying tests.

### Agent 1: Test Creator

Goal:

- Create or update `test/.../*.test.js` using only public behavior.

Output contract:

- Updated test file(s).
- Short note listing the branches/behaviors intended to cover.

### Agent 2: Test Runner

Goal:

- Execute targeted tests and ensure they pass before coverage checks.

Required command:

- Use the repo-local targeted test command resolved through `skills/cells-cli-usage/`
- Keep Cells-native commands canonical (`cells lit-component:test` or `cells app:test`) for Cells workflows
- Do NOT default to generic external commands (`npm run *`, `npm test`, `npx web-test-runner`) for Cells app/theme orchestration
- If uncertain whether a command is Cells-native, ask before running a non-Cells command

Output contract:

- Pass/fail result.
- If failed, exact failing test names and messages.

### Agent 3: Coverage Auditor (principal)

Goal:

- Verify file-level 100/100/100/100 and drive branch closure.
- Use `skills/cells-coverage/` to summarize HTML coverage and prioritize branch misses when artifacts exist.

Required commands:

- Extract file-level `FNF/FNH/LF/LH/BRF/BRH` counters from `build/coverage-reports/lcov.info` using shell-native or Python tooling
- Extract uncovered `BRDA` entries for the target source file using shell-native or Python tooling

Output contract:

- File-level counters.
- Uncovered `BRDA` lines (or explicit empty result).

### Agent 4: Compliance Auditor

Goal:

- Verify no private references and validate conventions.

Required commands:

- Scan the target test file for private-member access using a shell-native or Python pattern search
- `python skills/cells-test-creator/scripts/validate_test_conventions.py --path test/path/file.test.js`

Output contract:

- Private scan result (must be empty).
- Conventions result with `valid: true`.

### Orchestrator loop

1. Run Agent 1.
2. Run Agent 2; if fail, return to Agent 1.
3. Run Agent 3; if branch gaps exist, return to Agent 1 with uncovered `BRDA` lines.
4. Run Agent 4; if violations exist, return to Agent 1.
5. Finish only when Agents 2, 3, and 4 all pass.

## Hard stop checks before finishing

Before delivering tests, run these checks and fix any violation:

When subagent mode is active, these checks are executed by Agent 4 (checks 1-2), Agent 2 (check 3), and Agent 3 (checks 4-5).

Execution reliability rules before hard-stop checks:

- Execute each check in a separate terminal command.
- If output is mixed, truncated, or includes unrelated command echoes, rerun the check in isolation.
- Do not validate coverage until the targeted test command exits with success.

1. Private member scan (must return no matches):

Use a shell-native or Python search that finds private-member access such as `._foo` in `test/path/file.test.js`

2. Conventions validator:

`python skills/cells-test-creator/scripts/validate_test_conventions.py --path test/path/file.test.js`

3. Targeted test execution for the changed file:

Use the repo-local targeted test command resolved through `skills/cells-cli-usage/`

4. File-level coverage verification from `lcov.info` (must be 100/100/100/100):

Extract file-level counters for the target source file from `build/coverage-reports/lcov.info` using shell-native or Python tooling

5. Uncovered branches check (must print nothing):

Extract uncovered `BRDA` entries for the target source file from `build/coverage-reports/lcov.info` using shell-native or Python tooling

If check (1) finds usage like `el._selectedButton(...)` or `el._loadCurrencies()`, rewrite the test to use public behavior only (DOM events, rendered output, public lifecycle methods, emitted events).

If check (5) prints uncovered branches, use a branch-closure loop:

1. Map `BRDA:<line>,...` entries to source lines in the target file.
2. Add the smallest public-behavior test that activates each missing branch.
3. Re-run only the targeted file tests.
4. Re-run checks (4) and (5) until branch report is empty.

If coverage HTML exists, prefer compact triage first:

`python skills/cells-coverage/scripts/coverage_html_ai_summary.py build/coverage-reports/lcov-report --contains "src/path/file.js" --format ai --max-blocks 8`

## Repository conventions

- Test command: resolve the local test path through `skills/cells-cli-usage/` and prefer existing repo scripts.
- Test command: resolve through `skills/cells-cli-usage/` and keep the equivalent Cells-native command as canonical.
- Structure: `src/...` -> `test/...` (mirrored path).
- Expected name: `<source-file>.test.js`.
- Suite patterns: `suite(...)`, `setup(...)`, `teardown(...)`, `test(...)`.
- Double cleanup: call `sinon.restore()` in `teardown`.

Read these references before major changes:

- `references/testing-conventions.md`
- `references/naming-and-structure.md`
- `references/coverage-workflow.md`
- `references/anti-patterns.md`
- `references/cells-commands.md`

## Recommended workflow

1. Identify the target file with low coverage in `lcov-report`.
2. Review uncovered branches/lines in the coverage HTML report.
3. Write tests through the public API to cover missing branches.
4. Run the hard stop checks in the exact order defined above.
5. Run the resolved repo-local test command.
6. Confirm 100/100/100/100 for the target file using `lcov.info` file-level record, not only runner summary.
7. If a new test fails due to DOM wiring side effects, prefer test-local stubs with explicit selector mappings instead of mutating shared DOM behavior.
8. Use the 4-agent orchestration loop and keep each agent output as evidence.
9. If the component or tests use i18n, consult `skills/cells-i18n/` and verify `IntlMsg` initialization plus locale parity before closing.

## Generate a base test when missing

Use this script:

`python skills/cells-test-creator/scripts/generate_test_base.py --source src/path/component.js`

Useful options:

- `--tag-name bbva-my-component`
- `--component-name MyComponent`
- `--dry-run`
- `--force`

The script:

- Creates the destination folder if it does not exist.
- Generates `test/.../<file>.test.js` with a base template.
- Avoids private-member references in the template.
- Generates English test descriptions with no comments.

## Validate test conventions

Use:

`python skills/cells-test-creator/scripts/validate_test_conventions.py --path test/path/file.test.js`

Checks:

- File location/name.
- Minimum OpenWC/Sinon structure.
- No private-member references.
- No comments.
- English `suite/test` descriptions with no placeholders.

## Acceptance criteria

- Tests pass locally with the resolved repo-local test command.
- The target file reaches 100% Statements/Branches/Functions/Lines.
- No private access and no assertions coupled to internal implementation details.
- Evidence of hard stop checks executed (private scan clean + validator clean).
- Evidence of file-level lcov validation for the exact target source file.
- Evidence exists for all four agents (creator, runner, coverage auditor, compliance auditor).

## Browser Integration

When unit tests alone cannot prove page-level, demo-level, or browser-visible behavior, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Use browser runs as complementary evidence for:
- route or demo flows
- interaction wiring across multiple components
- visual state regressions
- runtime i18n and theming behavior that is difficult to prove with unit tests alone.

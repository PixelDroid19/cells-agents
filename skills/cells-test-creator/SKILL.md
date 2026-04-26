---
name: cells-test-creator
description: "Use when creating, updating, validating, or improving Cells OpenWC/Sinon tests, public-behavior coverage, mocks, fixtures, or test convention compliance."
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

## Test Design Philosophy

Tests should verify what the component DOES, not HOW it does it. This matters because:
- Implementation changes during refactoring, but public behavior stays stable
- Tests coupled to implementation details (`_privateMethod`, `#privateField`) break on every refactor
- Public-behavior tests serve as living documentation of the component contract

### Core Principles

1. **Public behavior only** — test rendered output, emitted events, and public API. Never reference `_private` or `#private` members. Why? Private members are implementation details that should be free to change.

2. **Use events, spies, stubs, and mocks** — verify observable outcomes, not internal state. When testing APIs, use mocks to simulate responses rather than calling real APIs. Why? Tests must be deterministic and fast.

3. **Follow repository conventions** — use OpenWC + Sinon patterns already in the codebase. Write `suite(...)` and `test(...)` descriptions in English with no comments. Why? Consistent naming enables team review and automated tooling.

4. **Stable DOM assertions** — validate properties and/or attributes (`el.visible` or `hasAttribute('visible')`) depending on component behavior. When stubbing DOM selectors, resolve real DOM references first, then apply stubs. Why? Unstable selectors break when component internals change.

5. **Coverage target: 100/100/100/100** — Statements, Branches, Functions, Lines at file level. Verify in `build/coverage-reports/lcov-report`. Use failure-output folders as evidence instead of re-reading raw reports.

6. **Reuse mocks pattern** — extract shared setup to `test/mocks/*` when the same setup shape appears 2+ times. Why? Duplicated setup becomes maintenance burden and obscures what each test is actually verifying.

7. **Sequential execution** — run validation commands one at a time, never in parallel. Why? Mixed output makes it impossible to attribute failures to specific commands.

8. **Cells-native commands only** — resolve test commands through `cells-cli-usage` first. Never use `npm test`, `npm run test`, `npx web-test-runner` unless user explicitly requests. Why? Cells commands carry toolchain guarantees for coverage paths and test setup.

## Multi-subagent orchestration (recommended pattern)

For non-trivial test work, use this handoff pattern to keep each agent focused:

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

## Reusable mock and harness pattern

When setup logic repeats, move it to `test/mocks/*` and consume it from tests.

Minimum pattern:

```js
// test/mocks/component-harness.js
export function createComponentHarness({ api = {}, flags = {} } = {}) {
  const stubs = {
    fetchData: sinon.stub().resolves(api.response ?? { items: [] }),
  };
  return { stubs, flags };
}
```

```js
// test/src/my-component.test.js
import { createComponentHarness } from '../../mocks/component-harness.js';

setup(() => {
  const { stubs } = createComponentHarness();
  // attach stubs to element dependencies via public wiring
});
```

Extraction trigger (mandatory):
- If setup/stub scaffolding is duplicated 2+ times, extract it to a reusable helper in `test/mocks/*` before closing.

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

### Code Quality (applies to test files too)

- **No trailing commas** in arrays, objects, or function arguments.
- **Semicolons required** — every statement ends with `;`.
- **No unnecessary blank lines** — one between test blocks is enough.
- **Max 3 `if` statements per test helper** — extract to separate helpers for more.
- **Use `.map()` over repetitive test setup** — extract repeated setup to `test/mocks/*`.
- **No comments in test files** — test descriptions, assertions, and helper names should be self-documenting. Why? Comments in tests become stale after refactors and confuse test runners.
- **JSDoc in test helpers: no blank lines inside blocks** — if mock helpers in `test/mocks/*` use JSDoc, keep description on one line with no internal blank lines. Why? Same readability rationale as production code.

## Browser Integration

When unit tests alone cannot prove page-level, demo-level, or browser-visible behavior, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Use browser runs as complementary evidence for:
- route or demo flows
- interaction wiring across multiple components
- visual state regressions
- runtime i18n and theming behavior that is difficult to prove with unit tests alone.

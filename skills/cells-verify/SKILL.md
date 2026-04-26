---
name: cells-verify
description: "Use when validating Cells implementation against specs, design, tasks, command policy, tests, coverage evidence, i18n, browser-visible behavior, or archive readiness."
license: MIT
metadata:
  author: D. J
  version: "2.1"
---

## Purpose

You are a sub-agent responsible for VERIFICATION. You are the quality gate. Your job is to prove  with real execution evidence  that the implementation is complete, correct, and behaviorally compliant with the specs.

Static analysis alone is NOT enough. You must execute the code.

## What You Receive

From the orchestrator:
- Change name
- Artifact store mode (`engram | openspec | hybrid | none`)

## Execution and Persistence Contract

Read and follow `skills/_shared/persistence-contract.md` for mode resolution rules.
Read and follow `skills/_shared/cells-workflow-contract.md` for canonical workflow naming and compatibility-read order.
If the project is Cells-oriented, also read and follow `skills/_shared/cells-conventions.md`.
If the project is Cells-oriented, also read and follow `skills/_shared/cells-governance-contract.md` and `skills/_shared/cells-policy-matrix.yaml`.
If the project is Cells-oriented, use `skills/_shared/cells-official-reference.md` to route verification to the right official testing, lifecycle, i18n, and CLI guidance.
If the project leaves coverage reports or structured test-error artifacts, use `skills/cells-coverage/` for compact triage.
If the project touches translated literals, locales, or `BbvaCoreIntlMixin`, use `skills/cells-i18n/` to verify runtime and locale coherence.
If the change affects rendered UI, routes, demos, theming, or browser-visible interaction flows, also read `skills/_shared/browser-testing-convention.md` and `skills/agent-browser/SKILL.md` when available.

For Cells testing and test-execution decisions, apply this mandatory stack first and in order:
1. `skills/cells-cli-usage/` (canonical command resolution)
2. `skills/cells-coverage/` (coverage thresholds/reporting and artifact triage)
3. `skills/cells-test-creator/` (test quality/design/compliance criteria)

Do not skip or reorder this stack. Do not use generic fallback commands (`npm test`, `npm run test`, `npx web-test-runner`) in Cells contexts.

- If mode is `engram`: Read and follow `skills/_shared/engram-convention.md`. Artifact type: `verify-report`. Retrieve `proposal`, `spec`, `design`, and `tasks` canonically.
- If mode is `openspec`: Read and follow `skills/_shared/openspec-convention.md`. Save to `openspec/changes/{change-name}/verify-report.md`.
- If mode is `hybrid`: Follow BOTH conventions  persist to Engram AND write `verify-report.md` to filesystem.
- If mode is `none`: Return the verification report inline only. Never write files.

## What to Do

### Step 1: Load Skill Registry (Mandatory)

Do this FIRST, before any other work.

1. Try engram first: `mem_search(query: "skill-registry", project: "{project}")`
2. If found, call `mem_get_observation(id: {id})` for the full registry
3. If engram is unavailable or no result is found, read `.atl/skill-registry.md` from the project root
4. If neither exists, proceed without skills (this is not an error)

From the registry, load only the skills and convention files relevant to verification.

### Step 2: Load Dependencies (Engram / Hybrid)

When mode is `engram` or `hybrid`, retrieve dependencies with two-step recovery:

1. `mem_search(query: "cells/{change-name}/proposal", project: "{project}")`
2. `mem_search(query: "cells/{change-name}/spec", project: "{project}")`
3. `mem_search(query: "cells/{change-name}/design", project: "{project}")`
4. `mem_search(query: "cells/{change-name}/tasks", project: "{project}")`
5. `mem_get_observation(id: {proposal_id})`
6. `mem_get_observation(id: {spec_id})` (REQUIRED for compliance matrix)
7. `mem_get_observation(id: {design_id})`
8. `mem_get_observation(id: {tasks_id})`

If any required canonical dependency is absent, return `status: blocked` and require canonical artifact seeding before verification.

Do not use `mem_search` preview text as complete artifact content.

### Step 3: Check Completeness

Verify ALL tasks are done:

```
Read the tasks artifact from the active backend
 Count total tasks
 Count completed tasks [x]
 List incomplete tasks [ ]
 Flag: CRITICAL if core tasks incomplete, WARNING if cleanup tasks incomplete
```

### Step 4: Check Correctness (Static Specs Match)

For EACH spec requirement and scenario, search the codebase for structural evidence:

```
FOR EACH REQUIREMENT in specs/:
 Search codebase for implementation evidence
 For each SCENARIO:
    Is the GIVEN precondition handled in code?
    Is the WHEN action implemented?
    Is the THEN outcome produced?
    Are edge cases covered?
 Flag: CRITICAL if requirement missing, WARNING if scenario partially covered
```

Note: This is static analysis only. Behavioral validation with real execution happens later in this workflow.

### Step 5: Check Coherence (Design Match)

Verify design decisions were followed:

```
FOR EACH DECISION in design.md:
 Was the chosen approach actually used?
 Were rejected alternatives accidentally implemented?
 Do file changes match the "File Changes" table?
Flag: WARNING if deviation found (may be valid improvement)
```

### Step 5b: Check Task Scope Isolation

Verify the implementation did not fix unrelated modules, unrelated errors, or opportunistic cleanup outside the requested task unless explicit scope expansion was requested.

Flag: WARNING if touched files lack a direct task/dependency justification.
Flag: CRITICAL if broad out-of-scope edits changed behavior without approval.

### Step 6: Check Testing (Static)

Verify test files exist and cover the right scenarios:

```
Search for test files related to the change
 Do tests exist for each spec scenario?
 Do tests cover happy paths?
 Do tests cover edge cases?
 Do tests cover error states?
 Flag: WARNING if scenarios lack tests, SUGGESTION if coverage could improve
```

For Cells projects, also confirm tests cover:
- public properties and reflected attributes
- emitted custom events
- `scopedElements` render paths
- loading, empty, disabled, and error states when applicable
- i18n and locales setup when the component uses `BbvaCoreIntlMixin`

For real Cells UI/component verification, also verify when applicable:
- existing BBVA component reuse was preferred over reinvented local UI
- template dependencies are imported and registered in `scopedElements`
- `WidgetMixin` and `this.emitEvent(...)` are used consistently with feature/data-manager architecture
- component-owned literals use `this.t(...)`
- keys are present in `demo/locales/locales.json`
- SCSS-backed styling and runtime style artifacts are aligned
- browser validation exists for visible changes

### Step 6b: Run Tests (Real Execution)

Detect the project's test runner and execute the tests:

```
Detect test runner from:
 1. `skills/cells-cli-usage/` first for the correct Cells-native command path
 2. `skills/cells-coverage/` second for threshold/reporting constraints when configured
 3. `skills/cells-test-creator/` third for quality and convention checks
 4. `package.json` scripts.test (wrapper mapping only after Cells command resolution)
 Fallback: ask orchestrator

Prefer the smallest confirmation scope that proves the change:
 targeted file/suite first for small or isolated changes
 broader project test execution only when risk, coupling, or user request justifies it

Execute: {test_command}
Capture:
 Total tests run
 Passed
 Failed (list each with name and error)
 Skipped
 Exit code

Flag: CRITICAL if exit code != 0 (any test failed)
Flag: WARNING if skipped tests relate to changed areas
```

For Cells projects, read `skills/cells-test-creator/` before judging test quality, missing coverage, or convention violations.

### Step 6c: Build & Type Check (Real Execution)

Detect and run the build/type-check command:

```
Detect build command from:
 openspec/config.yaml  rules.verify.build_command (if filesystem config exists)
 package.json  scripts.build  also run tsc --noEmit if tsconfig.json exists
 pyproject.toml  python -m build or equivalent
 Makefile  make build
 Fallback: skip and report as WARNING (not CRITICAL)

For small, isolated changes, prefer the lightest relevant confirmation command before a full project build.
Execute: {build_command}
Capture:
 Exit code
 Errors (if any)
 Warnings (if significant)

Flag: CRITICAL if build fails (exit code != 0)
Flag: WARNING if there are type errors even with passing build
```

### Step 6d: Coverage Validation (Real Execution  if threshold configured)

Run with coverage only if `rules.verify.coverage_threshold` is set in filesystem config:

```
IF coverage_threshold is configured:
 Run: {test_command} --coverage (or equivalent for the test runner)
 Parse coverage report
 Compare total coverage % against threshold
 Flag: WARNING if below threshold (not CRITICAL  coverage alone doesn't block)
 Report per-file coverage for changed files only
 If HTML coverage or runner error folders exist, summarize them with `skills/cells-coverage/` before concluding

IF coverage_threshold is NOT configured:
 Run deterministic policy check instead of raw coverage execution:
  Verify repository evidence path exists (`scripts/validate_governance_behavior.py --scenario coverage-policy-exemption`)
  Require output proving governance scope and explicit exemption rationale
  record `Coverage policy exemption: N/A` with deterministic evidence
  Report coverage field as `N/A (policy exemption)` rather than generic "Not configured"
```

### Step 6e: Workflow Contract Validation (Deterministic)

When the change modifies workflow skills, shared contracts, or persistence/reporting guidance instead of executable runtime code:

```
Run deterministic contract checks in addition to any targeted tests:
 python scripts/validate_governance_behavior.py --scenario workflow-contract-parity
 python scripts/validate_governance_behavior.py --scenario canonical-write-contract
 python scripts/validate_governance_behavior.py --scenario canonical-lineage-only
 python scripts/validate_governance_behavior.py --scenario source-decision-template

Treat these passing checks as deterministic proof for canonical write behavior, canonical-only dependency guidance, and source_decisions template coverage when no runtime phase execution exists.
```

### Step 6f: Browser Functional And Visual Validation

When the implemented change affects rendered UI, demos, routes, i18n-visible output, styling, or interaction flows:

```
Resolve the local serve/demo command and target URL through `skills/cells-cli-usage/`
Reuse an already running dev server, route, browser session, or CDP port when available
Open or connect with `agent-browser` using that existing runtime first
Snapshot before interaction
Execute the minimum user flow needed to prove the changed behavior
Re-snapshot after route or DOM changes
Capture screenshot or screenshot diff evidence when the change is visual
Flag: CRITICAL if a required user flow is broken or blocked at runtime
Flag: WARNING if the flow works but visible output or screenshot evidence shows a mismatch
If no local runtime can be started, report browser validation as blocked evidence
```

Use browser validation as supporting runtime proof. It complements tests and code review, especially for feature flows, visible state transitions, i18n, and theming.

### Step 7: Spec Compliance Matrix (Behavioral Validation)

This is the most important step. Cross-reference EVERY spec scenario against the actual test run results from Step 6b to build behavioral evidence.

For each scenario from the specs, find which test(s) cover it and what the result was:

```
FOR EACH REQUIREMENT in specs/:
  FOR EACH SCENARIO:
   Find tests that cover this scenario (by name, description, or file path)
   Look up that test's result from Step 6b output
   Assign compliance status:
       COMPLIANT    test exists AND passed
       FAILING      test exists BUT failed (CRITICAL)
       UNTESTED     no test found for this scenario (CRITICAL)
       PARTIAL     test exists, passes, but covers only part of the scenario (WARNING)
   Record: requirement, scenario, test file, test name, result
```

A spec scenario is only considered COMPLIANT when there is a test that passed proving the behavior at runtime. Code existing in the codebase is NOT sufficient evidence.

### Step 7b: Fixed Compliance Checklist (Mandatory)

Before issuing a verdict, complete this exact checklist:

1. Restriction compliance confirmed
   - Scope restrictions respected for the verified batch; touched files stay inside the requested task/module boundary or are justified as direct dependencies (for example, tests-only batches did not edit `src/**` or `demo/locales/**`)
2. No private assertions
   - Test evidence shows no private member access/assertions (`._*` or `#*`) in changed tests
3. Native Cells command evidence
   - Execution evidence uses Cells-native commands (`cells app:*`, `cells lit-component:*`, `/cells-*`) unless user explicitly requested non-Cells path
4. lcov file-level evidence
   - Target files show 100/100/100/100 (Statements/Branches/Functions/Lines) with per-file lcov counters
5. Real Cells implementation rules
   - Reuse-first, `scopedElements`, event pattern, i18n parity, styling alignment, and browser validation requirements are satisfied for the verified scope
6. Code hygiene
   - Public API contracts use JSDoc where needed; no leftover TODO/comments/commented-out code/formatting noise remain in changed files

If any checklist item fails, verdict cannot be `PASS`.

### Step 8: Artifact Persistence (Mandatory)

Persist the report according to the resolved `artifact_store.mode`, following the conventions in `skills/_shared/`:

- **engram**: Use `engram-convention.md`  artifact type `verify-report`
- **openspec**: Write to `openspec/changes/{change-name}/verify-report.md`
- **none**: Return the full report inline, do NOT write any files

For Engram persistence use explicit call:

```
mem_save(
   title: "cells/{change-name}/verify-report",
   topic_key: "cells/{change-name}/verify-report",
   type: "architecture",
   project: "{project}",
   content: "{your full verification report markdown}"
)
```

If mode is `hybrid`, do BOTH filesystem write and `mem_save`.

Do not skip this step in `engram` or `hybrid`, or archive lineage becomes incomplete.

### Step 9: Return Summary

If mode is `openspec` or `hybrid`, return to the orchestrator the same markdown content you wrote to `verify-report.md`.
If mode is `engram` or `none`, return that same markdown content inline.

Use the following markdown as the `detailed_report` body and wrap the overall reply in the standard structured envelope:

```markdown
## Verification Report

**Change**: {change-name}
**Version**: {spec version or N/A}

---

### Artifact Lineage
- Active proposal artifact: `cells/{change-name}/proposal`
- Active spec artifact: `cells/{change-name}/spec`
- Active design artifact: `cells/{change-name}/design`
- Active tasks artifact: `cells/{change-name}/tasks`
- Active verify artifact: `cells/{change-name}/verify-report`
- Historical legacy artifacts may be cited only as inactive archive context

---

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | {N} |
| Tasks complete | {N} |
| Tasks incomplete | {N} |

{List incomplete tasks if any}

---

### Build & Tests Execution

**Build**:  Passed /  Failed
```
{build command output or error if failed}
```

**Tests**:  {N} passed /  {N} failed /  {N} skipped
```
{failed test names and errors if any}
```

**Coverage**: {N}% / threshold: {N}%   Above threshold /  Below threshold / - Not configured

**Browser Validation**: {Not required | Passed | Warning | Failed | Blocked}
```
{route, interactions, screenshot or diff evidence summary}
```

---

### Spec Compliance Matrix

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| {REQ-01: name} | {Scenario name} | `{test file} > {test name}` |  COMPLIANT |
| {REQ-01: name} | {Scenario name} | `{test file} > {test name}` |  FAILING |
| {REQ-02: name} | {Scenario name} | (none found) |  UNTESTED |
| {REQ-02: name} | {Scenario name} | `{test file} > {test name}` |  PARTIAL |

**Compliance summary**: {N}/{total} scenarios compliant

---

### Correctness (Static  Structural Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| {Req name} |  Implemented | {brief note} |
| {Req name} |  Partial | {what's missing} |
| {Req name} |  Missing | {not implemented} |

---

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| {Decision name} |  Yes | |
| {Decision name} |  Deviated | {how and why} |

---

### Source Decisions
| Intent | Primary Source | Fallback Used | Fallback Source | Fallback Reason | Evidence Quality | Status |
|--------|----------------|---------------|-----------------|-----------------|------------------|--------|
| {verification-path} | {canonical source} | {yes/no} | {source or null} | {reason or null} | {high/medium/low} | {ok/partial/blocked} |

---

### Issues Found

**CRITICAL** (must fix before archive):
{List or "None"}

**WARNING** (should fix):
{List or "None"}

**SUGGESTION** (nice to have):
{List or "None"}

---

### Verdict
{PASS / PASS WITH WARNINGS / FAIL}

{One-line summary of overall status}

---

### Fixed Compliance Checklist

| Check | Result | Evidence |
|------|--------|----------|
| Restriction compliance |  OK /  FAIL | {path diff / scope note} |
| No private assertions |  OK /  FAIL | {private scan result} |
| Native Cells command evidence |  OK /  FAIL | `{command(s)}` |
| lcov 100/100/100/100 evidence |  OK /  FAIL | {per-file counters} |
| Real Cells implementation rules |  OK /  FAIL | {reuse/scopedElements/events/i18n/styles/browser note} |
| Code hygiene |  OK /  FAIL | {JSDoc/comment/formatting note} |
```

## Rules

### Verification Principles

1. **Read actual source code** — don't trust summaries or assume implementation matches intent. Verification requires ground truth, which is the code itself.

2. **Execute tests — static analysis alone is not verification** — code existing doesn't prove it works. Only passing tests prove behavioral compliance. A spec scenario is COMPLIANT only when a covering test has PASSED.

3. **Specs first, design second** — compare against specs for behavioral correctness (does it do the right thing?), then design for structural correctness (does it do it the right way?).

### Cells-Specific Checks

4. **Report mismatches explicitly** — if source code, `custom-elements.json`, package docs, and tests disagree, flag it. Why? Mismatches indicate documentation drift or implementation bugs.

5. **Locale path violations are verification issues** — any locale file outside `demo/locales` must be reported. Why? Cells runtime only reads from `demo/locales`, so misplaced files cause silent translation failures.

6. **Browser evidence required for visible changes** — if the change affects what users see, verify in browser before claiming closure. Why? Unit tests can't prove visual correctness (colors, layout, icon rendering). Reuse existing runtime to save time.

7. **Cells-native commands only** — use `cells app:*`, `cells lit-component:*`. Why? Cells commands carry toolchain guarantees for coverage, lint, and test setup.

### Reporting Discipline

8. **Be objective** — report what IS, not what should be. CRITICAL = must fix before archive. WARNING = should fix. SUGGESTION = nice to have.

9. **Do NOT fix issues — only report them** — the orchestrator decides what to fix and in what order. Fixing issues during verification introduces unreviewed changes.

10. **Targeted confirmation first** — don't escalate every small change into full-project execution. Run the smallest relevant test suite, broaden only when risk or coupling justifies it.

11. **Cite canonical artifact refs** — verification reports must reference `cells/{change-name}/proposal`, `spec`, `design`, `tasks`. Historical legacy artifacts are inactive archive context only.

12. **Source-decision trace required** — include `{intent, primary_source, fallback_used, evidence_quality, status}` for each verification path. Why? Enables traceability and audit.

## Browser Integration

Browser validation is mandatory whenever the verified change affects rendered UI, routes, demos, visible state transitions, styling, theming, or runtime i18n.

Always use:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Treat browser results as runtime evidence that complements tests, build output, and the spec compliance matrix.

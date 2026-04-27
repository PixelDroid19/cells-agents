---
name: cells-verify
description: "Use when validating Cells implementation against specs, design, tasks, command policy, tests, coverage evidence, i18n, browser-visible behavior, or archive readiness."
---

# Cells Verify

## Purpose

Verify that the implementation is complete, correct, and proven by real execution evidence.

Use [verification-playbook.md](references/verification-playbook.md) for the detailed report template, compliance checklist, and execution examples.

## What You Receive

- change name
- artifact store mode: `engram | openspec | hybrid | none`

## Execution and Persistence Contract

Read and follow:

- `skills/_shared/persistence-contract.md`
- `skills/_shared/cells-workflow-contract.md`
- `skills/_shared/cells-source-routing-contract.md`
- `skills/_shared/cells-rules-contract.md`
- `skills/_shared/cells-conventions.md`
- `skills/_shared/cells-governance-contract.md`
- `skills/_shared/cells-policy-matrix.yaml`
- `skills/_shared/cells-official-reference.md`

Also use:

- `skills/cells-coverage/` when coverage reports or test-artifact triage exist
- `skills/cells-i18n/` when translated literals, locale files, or `BbvaCoreIntlMixin` are in scope
- `skills/_shared/browser-testing-convention.md` and `skills/agent-browser/SKILL.md` for browser-visible changes

For Cells testing and test-execution decisions, apply the mandatory testing stack from `skills/_shared/cells-rules-contract.md` and `skills/_shared/cells-source-routing-contract.md`.

Mode handling:

- `engram`: use `skills/_shared/engram-convention.md` and persist `verify-report`
- `openspec`: write `openspec/changes/{change-name}/verify-report.md`
- `hybrid`: do both
- `none`: return the full report inline

## Workflow

### Step 1: Load Skill Registry

Before any other work:

1. `mem_search(query: "skill-registry", project: "{project}")`
2. `mem_get_observation(id: {id})` when available
3. fallback: read `.atl/skill-registry.md`
4. if neither exists, proceed without it

### Step 2: Load Canonical Dependencies

When mode is `engram` or `hybrid`, retrieve:

1. `mem_search(query: "cells/{change-name}/proposal", project: "{project}")`
2. `mem_search(query: "cells/{change-name}/spec", project: "{project}")`
3. `mem_search(query: "cells/{change-name}/design", project: "{project}")`
4. `mem_search(query: "cells/{change-name}/tasks", project: "{project}")`
5. `mem_get_observation(...)` for each result

If any required canonical dependency is absent, return `status: blocked`.

### Step 3: Check Completeness

- count total tasks
- count completed tasks
- list incomplete tasks
- flag core gaps as CRITICAL

### Step 4: Check Correctness

For each requirement and scenario:

- locate structural implementation evidence
- verify preconditions, actions, outcomes, and edge cases
- mark missing or partial coverage explicitly

Static analysis is not enough; runtime proof comes later.

### Step 5: Check Coherence

- compare implementation against design decisions
- note deviations and whether they are justified
- check touched files against the intended scope

Verify the implementation did not fix unrelated modules, unrelated errors, or opportunistic cleanup outside the requested task unless explicit scope expansion was requested.

### Step 6: Check Testing and Runtime Evidence

Static test check:

- confirm test files exist for the changed area
- verify coverage of happy path, edge cases, error states, and public behavior

Runtime check:

1. resolve the test command through `skills/cells-cli-usage/`
2. review coverage/reporting constraints through `skills/cells-coverage/`
3. validate test quality through `skills/cells-test-creator/`
4. run the smallest confirmation scope that proves the change

When the change touches i18n, verify contextually:

- component/demo work: confirm `demo/locales/locales.json` or repo-equivalent demo locale evidence
- app/runtime work: confirm app-level locale configuration and/or generated test locale evidence
- tests that depend on translations: confirm `IntlMsg` setup, `localesHost`, and locale-load waiting when applicable

When the change modifies workflow skills or shared contracts instead of runtime code, run deterministic contract checks:

- `python scripts/validate_governance_behavior.py --scenario workflow-contract-parity`
- `python scripts/validate_governance_behavior.py --scenario canonical-write-contract`
- `python scripts/validate_governance_behavior.py --scenario canonical-lineage-only`
- `python scripts/validate_governance_behavior.py --scenario source-decision-template`

Coverage policy rule:

- if coverage threshold is configured, run coverage and compare against the threshold
- otherwise use `scripts/validate_governance_behavior.py --scenario coverage-policy-exemption`
- record `Coverage policy exemption: N/A`
- include `with deterministic evidence`
- report coverage as `N/A (policy exemption)`

When the change is browser-visible, use the browser validation checklist from [verification-playbook.md](references/verification-playbook.md).

### Step 7: Build the Compliance Matrix

For every spec scenario, map:

- requirement
- scenario
- covering test
- runtime result
- status: `COMPLIANT | FAILING | UNTESTED | PARTIAL`

### Step 8: Persist the Report

Persist according to mode.

For Engram:

```text
mem_save(
   title: "cells/{change-name}/verify-report",
   topic_key: "cells/{change-name}/verify-report",
   type: "architecture",
   project: "{project}",
   content: "{your full verification report markdown}"
)
```

If mode is `hybrid`, do both filesystem and Engram persistence.

### Step 9: Return Summary

Use the template from [verification-playbook.md](references/verification-playbook.md).

The report must include:

- artifact lineage
- completeness
- build and test execution
- coverage outcome
- browser validation outcome when relevant
- spec compliance matrix
- source decisions
- issues found
- verdict
- fixed compliance checklist

## Rules

### Verification rules

- Read actual source code, not summaries.
- Execute tests; static analysis alone is not verification.
- Specs first, design second.
- Prefer targeted confirmation before broader execution.
- Do not fix issues during verification; report them.

### Cells-specific rules

- report mismatches across source, docs, manifests, and tests
- existing BBVA component reuse, `scopedElements`, event pattern, i18n parity, style alignment, and browser validation must be checked when relevant
- locale path violations are verification issues when the implementation invents or uses an unsupported locale path for the touched surface
- use Cells-native commands unless the user explicitly requests a non-Cells path

### Reporting rules

- be objective
- separate CRITICAL, WARNING, and SUGGESTION findings
- cite canonical artifact refs: `cells/{change-name}/proposal`, `spec`, `design`, `tasks`, `verify-report`
- include explicit source decisions for each verification path

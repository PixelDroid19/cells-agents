---
name: cells-verify
description: "Use when verifying a Cells change against requested specs, tests, coverage, i18n, source evidence, and browser-visible behavior."
---

# Cells Verify

## Purpose

Verify the actual change, not a generic checklist. Use the strongest relevant evidence that is available within the requested scope.

Read [Cells rules](../_shared/cells-rules-contract.md) and [source routing](../_shared/cells-source-routing-contract.md) when their evidence classes apply to the change.

## Evidence Requirements

1. Re-read the changed files and compare them with the user request or active governed requirements.
2. Resolve any test, build, lint, documentation, or locale command through `cells-cli-usage` and installed project scripts before execution.
3. Run focused tests or checks that exercise the changed behavior. Add coverage analysis only when coverage is in scope.
4. For user-visible changes, inspect the relevant browser state when code and tests cannot prove the result.
5. Check that the change did not fix unrelated modules, unrelated errors, or opportunistic cleanup outside the requested task unless the user explicitly expanded scope. Also check that it did not hide errors or weaken tests.

For workflow-contract changes, validate links, referenced paths, YAML/Markdown structure, and the relevant semantic contract checks. Do not use a text-presence check as proof that behavior is correct.

## Stop Conditions

- `success`: required checks passed and evidence supports the requested result.
- `partial`: a useful check ran, but a stated evidence gap remains (for example, no runnable browser environment when browser proof is useful but not essential).
- `blocked`: a required command, environment, input, or permission is unavailable and prevents safe verification.

Continue safe, in-scope debugging when new evidence suggests a next step. Do not stop solely because an arbitrary retry count was reached.

## Output

Report changed scope, commands actually run, pass/fail results, browser evidence when applicable, limitations, and the final status. Persist `verify-report.md` only for an active OpenSpec workflow.

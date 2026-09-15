# Cells Governance Contract

## Purpose

Keep Cells work evidence-based, within the user's scope, and aligned with the actual project. This contract applies alongside `cells-rules-contract.md` and `cells-source-routing-contract.md`; it does not override explicit user authorization with an internal workflow preference.

## Scope and Evidence

- Verify a path before reporting or editing it.
- Do not claim a component API, event, command, locale location, or browser result without the relevant catalog, project, command, or runtime evidence.
- Use the primary source and ordered fallback in `cells-source-routing-contract.md` for material Cells decisions.
- Record a compact source decision for a governed artifact or an important implementation choice. A quick answer only needs the evidence it relies on.
- Keep changes inside the user-approved files and behavior. Report unrelated findings instead of fixing them by default.

## Task Scope Isolation

Keep edits within the assigned task and the user's explicit behavior request. Do not perform opportunistic refactors, adjacent cleanups, unrelated bug fixes, or cross-module rewrites unless the user explicitly expands the scope. If an unrelated defect affects safe completion, report the concrete dependency and its effect instead of silently widening the change.

## Status Policy

| Status | Meaning |
| --- | --- |
| `success` | The requested scope is complete and the collected evidence supports the stated result. |
| `partial` | Work progressed safely, but a stated acceptance condition or evidence item remains unresolved. |
| `blocked` | Safe continuation requires an unavailable decision, permission, environment, or out-of-scope change. |

Do not use `success` for a claim supported only by memory, an unchecked plan, or a catalog hit that has not been applied to the project. Catalog commands may report `ok` for their own query result.

## Cells-Specific Reliability

- For UI, component, form, navigation, feedback, or typography work, search the component catalog before creating a replacement.
- For framework, CLI, testing, i18n, theming, or architecture guidance, search the official catalog before fallback.
- Resolve an executable Cells command from the installed project scripts and command resolver before running it.
- Use `cells-cli-usage`, `cells-coverage`, and `cells-test-creator` only when command resolution, coverage, or test authoring is actually in scope.
- When user-visible behavior changes, use browser evidence if static or unit evidence cannot establish the result.

## Contribution Work

When the user asks to create an issue, PR, review, or merge, follow the repository's configured contribution policy and the user-authorized action. Do not make an issue-first preference block an explicitly authorized local implementation task. Do not create or publish external records unless the user requested that action.

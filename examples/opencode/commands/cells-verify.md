---
description: Validate implementation matches specs, design, and tasks — enforces No-TypeScript, conditions-by-method, and BBVA-first gates
agent: cells-orchestrator
subtask: true
---

# Cells Verify Command

You are a CELLS sub-agent. Read the skill file at ~/.config/opencode/skills/cells-verify/SKILL.md FIRST, then follow its instructions exactly.

CONTEXT:

- Working directory: {workdir}
- Current project: {project}
- Artifact store mode: engram

## MANDATORY VERIFICATION GATES (run before any other check)

These 6 gates must ALL pass for `status: ok`. Any failure → `status: partial` or `status: blocked`.

### Gate 1 — No TypeScript

- Confirm zero `.ts` or `.tsx` files exist in `src/` and `test/`
- Scan all `.js` files for TypeScript syntax: type annotations, `interface`, `enum`, `as Type`, `<Type>` generics, `readonly`, `public`/`private`/`protected` keywords
- If found → flag each occurrence as a violation with file path and line

### Gate 2 — Conditions-by-Method Rule

- Review every method in every modified `.js` file
- Count `if` statements and ternary expressions per method body
- Any method with 3+ conditions → violation
- Getter methods (`get _xxx()`) are also in scope — max 2 conditions each
- Report violations as: `{file, method, condition_count, line_range}`

### Gate 3 — BBVA-First

- For every custom element tag used in templates, verify either:
  a. It is a known BBVA component (catalog evidence or `@bbva-*` / `@bbva-spherica-components/*` package), OR
  b. It was created via `cells-component-authoring` after a failed catalog lookup
- If a raw HTML element (`<p>`, `<h3>`, `<span>`, `<button>`) exists where a BBVA component was available → violation

### Gate 4 — Scoped Elements

- Confirm every custom element tag used in `render()` / `_renderXxx()` is imported and registered in `static get scopedElements()`
- Missing registration → violation

### Gate 5 — i18n

- Confirm no raw string literals appear inside `html\`...\`` template literals
- Confirm the `this.t('key') || ''` pattern is absent everywhere
- Confirm all i18n keys used by modified components exist in `demo/locales/locales.json`

### Gate 6 — Event Pattern

- Confirm all business/bridge-facing events use `this.emitEvent(...)` — not raw `this.dispatchEvent(...)`
- Confirm all event handlers call `evt.stopPropagation()` or `evt.preventDefault()` as first statement
- Confirm no event handler has 3+ condition branches without extracting to a named helper

## STANDARD VERIFY TASK

After running all 6 gates, continue with the standard cells-verify workflow:

1. Check completeness — are all tasks done?
2. Check correctness — does code match specs?
3. Check coherence — were design decisions followed?
4. For Cells projects, compare source, `custom-elements.json`, package docs, and tests for API/event consistency
5. Run tests and build (real execution via Cells-native commands only)
6. Build the spec compliance matrix

Reliability contract (mandatory):

- Apply `skills/_shared/cells-source-routing-contract.md` and `skills/_shared/cells-governance-contract.md`
- Verify file paths and command validity before reporting evidence
- If evidence is incomplete, return `partial` or `blocked` — never infer success

Testing stack for Cells contexts (strict order):

- `skills/cells-cli-usage/` → canonical test command/invocation
- `skills/cells-coverage/` → threshold/reporting and artifact triage
- `skills/cells-test-creator/` → test quality and convention checks

Command guardrail: Cells-native commands only (`cells app:*`, `cells lit-component:*`). No `npm run *`, `npm test`, `npx web-test-runner` unless user explicitly requests.

Return a structured verification report with: status, executive_summary, gate_results (one per gate), detailed_report, artifacts, and next_recommended.

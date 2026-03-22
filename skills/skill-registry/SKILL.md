---
name: skill-registry
description: >
  Knowledge gateway and anti-patterns catalog for Cells projects. Load this FIRST before writing any code, proposing components, or making architectural decisions. Provides mandatory BBVA component lookup, Cells official guidance routing, and a never-do list of anti-patterns.
  Trigger: Always — before any code work, component proposal, or design decision.
license: MIT
metadata:
  author: Cells Agent Bundle
  version: "2.0"
---

## Purpose

You are the **knowledge gateway** for Cells projects. Your job is to make sure the agent **knows what exists** before it invents something new, proposes a component, or makes a Cells mistake.

Load this skill **before** any code, design, or component work. Not as step 1 of a phase — as **step 0 of everything**.

## Mandatory Pre-Flight Knowledge Gates

Complete these gates **in order** before writing ANY code or proposing ANY component:

---

### Gate 1: BBVA Components Lookup (ALWAYS FIRST for UI work)

**NEVER invent a BBVA component.** If the task involves UI, typography, forms, buttons, tables, navigation, or feedback — search the catalog FIRST.

```bash
python skills/cells-components-catalog/scripts/search_docs.py --query "<what you need>"
```

Examples of wrong behavior this prevents:
- Writing `<p>`, `<h3>`, or `<span>` when `bbva-type-text` exists
- Building a custom toast when `bbva-notification-toast` exists
- Creating a stepper from scratch when `bbva-progress-step` exists
- Implementing a button with `<div onclick>` instead of `bbva-button-default`

When the search returns a match: **use the component and stop**. When the search is ambiguous: inspect the package:

```bash
python skills/cells-components-catalog/scripts/search_docs.py --package <package-name>
```

---

### Gate 2: Cells Official Guidance (ALWAYS for architecture, testing, i18n, theming)

If the task involves how Cells works, how to test, how to structure a feature, how to handle i18n, or how to theme — consult the official docs catalog FIRST.

```bash
python skills/cells-official-docs-catalog/scripts/search_docs.py --query "<your question>"
python skills/cells-official-docs-catalog/scripts/search_docs.py --topic <topic>
```

Topics: `architecture`, `testing`, `cli`, `component-api`, `lit-authoring`, `composition`, `theming`, `demo-docs-i18n-assets`, `application-runtime`, `application-communication`

---

### Gate 3: Anti-Patterns Catalog (ALWAYS — non-negotiable)

**Never do any of the following in a Cells project:**

#### i18n Anti-Patterns

| Anti-Pattern | Why | Correct approach |
|---|---|---|
| `this.t('key') \|\| ''` | The i18n runtime renders the key itself as fallback — it is NOT falsy. This pattern hides real missing translations and makes them look intentional. | Always check the locale file directly. If the key is missing, add it to `demo/locales/locales.json`. Never use `\|\| ''` to silence the key. |
| Hardcoded user-facing literals | Cells requires all user-facing text to go through `this.t(...)`. | Route every visible string through `this.t('key')`. Add the key to locale files. |
| `IntlMsg.lang = 'en'` at instance level without waiting | Race condition: the component may render before the locale loads, showing the key as text. | Set `IntlMsg.lang` at app/shell level. Await `window.IntlMsg.loadUrlResourcesComplete` in tests and demos. |
| Locale files outside `demo/locales/` | Cells enforces this location. | Always use `demo/locales/locales.json`. |

#### Component Anti-Patterns

| Anti-Pattern | Why | Correct approach |
|---|---|---|
| Using `<p>`, `<h1-h6>`, or `<span>` for text | BBVA has `bbva-type-text` and family for all typography. | Use `bbva-type-text` with the appropriate `weight` and `size` props. |
| Implementing `<div onclick>` as a button | Cells buttons handle focus, keyboard, a11y, and loading states. | Use `bbva-button-default` or the appropriate button variant. |
| Creating custom loading spinners | BBVA has `bbva-skeleton-default` and notification components for loading states. | Use the appropriate BBVA feedback component. |
| Inventing `<custom-element>` without checking the catalog | Reuse existing BBVA components first. | Search `cells-components-catalog` before creating any new component. |
| Using `<img>` for BBVA icons | BBVA icon system is not `<img>`. | Use the BBVA icon system (referenced in `cells-official-docs-catalog` topic `demo-docs-i18n-assets`). |

#### Architecture Anti-Patterns

| Anti-Pattern | Why | Correct approach |
|---|---|---|
| Putting API logic in the component | Violates Cells separation of concerns. | Use data managers for API interaction. Components own presentation only. |
| Skipping `cells-cli-usage` → `cells-coverage` → `cells-test-creator` stack | This stack is mandatory for Cells testing. | Always apply the stack in order before any test work. |
| Using generic `npm test` in Cells contexts | Cells has its own test commands via `cells lit-component:test` or `cells app:test`. | Resolve via `cells-cli-usage` first. |

---

## Skill Routing: When to Load Each Specialist Skill

Load these skills **before** the phase that needs them:

| Phase | Skills to load BEFORE starting | Why |
|---|---|---|
| `cells-explore` | `cells-components-catalog` (search) + `cells-official-docs-catalog` | Know what exists before exploring solutions |
| `cells-design` | `cells-component-researcher` + `cells-composition-architect` + `cells-feature-analyzer` + `cells-app-architecture` | Mandatory research before designing |
| `cells-apply` | `cells-component-authoring` (if new component) + `cells-cli-usage` + `cells-coverage` + `cells-test-creator` | Correct commands + correct component authoring |
| `cells-verify` | `cells-cli-usage` + `cells-coverage` + `cells-test-creator` + `cells-i18n` (if text changes) | Correct verification + i18n check |
| Any phase with i18n | `cells-i18n` + `cells-official-docs-catalog` topic `demo-docs-i18n-assets` | Locale parity + runtime setup |
| Any phase with browser UI | `agent-browser` + `_shared/browser-testing-convention` | Real validation of rendered output |

---

## Cells Component Non-Negotiables

Before closing any task that touches UI or components:

1. **Searched** the BBVA components catalog for existing solutions
2. **Used** the correct BBVA component (not HTML elements)
3. **Applied** `scopedElements` registration for every template dependency
4. **Routed** all user-facing literals through `this.t(...)`
5. **Verified** the component works in browser (via `agent-browser`)
6. **Checked** locale parity in `demo/locales/locales.json`
7. **Ran** the correct Cells test command (via `cells-cli-usage`)

---

## When This Skill Is The Only One You Need

If the user asks:
- "What BBVA component should I use for X?"
- "How do I handle i18n in Cells?"
- "How do I structure a feature in Cells?"
- "What's the correct Cells test command?"
- "Is there a BBVA component for Y?"

→ This skill is the answer. Load it, run the search commands, return the result.

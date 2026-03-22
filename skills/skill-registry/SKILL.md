---
name: skill-registry
description: >
  Knowledge gateway for Cells projects. Load this FIRST before any code, design, or component work. Routes to cells-components-catalog and cells-official-docs-catalog, provides mandatory pre-flight gates, and delegates Cells implementation rules to cells-rules-contract.
  Triggers: Always — before any code work, component proposal, design decision, or architectural choice in a Cells + Lit + BBVA project.
license: MIT
metadata:
  author: Cells Agent Bundle
  version: "3.0"
---

## Purpose

You are the **knowledge gateway** for Cells projects. Your job is to make sure the agent **knows what exists** before it invents something new, proposes a component, or makes a Cells mistake.

Load this skill **before** any code, design, or component work — as **step 0 of everything**.

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

### Gate 3: Anti-Patterns + Implementation Rules Reference (MANDATORY)

**Before implementing any Cells component, read `skills/_shared/cells-rules-contract.md`.**

It contains the single source of truth for:
- BBVA-First Rule and component anti-patterns table
- i18n anti-patterns (`this.t('key') || ''` is wrong, not falsy)
- `scopedElements` registration requirements
- `WidgetMixin` + `this.emitEvent(...)` usage rules
- Mandatory testing stack (`cells-cli-usage` → `cells-coverage` → `cells-test-creator`)
- Cells component checklist (reuse, scopedElements, WidgetMixin, i18n, browser validation)

Do not replicate these rules in individual skills. Reference `cells-rules-contract.md` instead.

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

## Cells Component Non-Negotiables (Summary)

Before closing any task that touches UI or components, verify via `cells-rules-contract.md`:

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

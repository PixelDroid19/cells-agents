---
name: skill-registry
description: "Use when routing Cells work to specialist skills, finding available skills, discovering BBVA components, choosing official docs, or starting a workflow with resource lookup."
---

## Purpose

You are the **knowledge gateway** for Cells projects. Your job is to make sure the agent **knows what exists** before it invents something new, proposes a component, or makes a Cells mistake.

Load this skill **before** any code, design, or component work — as **step 0 of everything**.

## Read First

- `skills/_shared/cells-rules-contract.md`
- `skills/_shared/cells-source-routing-contract.md`

These shared contracts are authoritative for BBVA-first UI rules, i18n rules, command policy, testing-stack order, and deterministic source routing.

## Mandatory Pre-Flight Knowledge Gates

Complete these gates **in order** before writing ANY code or proposing ANY component:

---

### Gate 1: BBVA Components Lookup

For UI, typography, forms, buttons, tables, navigation, or feedback, follow the BBVA lookup rule in `skills/_shared/cells-rules-contract.md` and the routing order in `skills/_shared/cells-source-routing-contract.md`.

```bash
python skills/cells-components-catalog/scripts/search_docs.py --query "<what you need>"
```

When the search is ambiguous, inspect the package:

```bash
python skills/cells-components-catalog/scripts/search_docs.py --package <package-name>
```

---

### Gate 2: Cells Official Guidance

If the task involves how Cells works, how to test, how to structure a feature, how to handle i18n, or how to theme — consult the official docs catalog FIRST.

```bash
python skills/cells-official-docs-catalog/scripts/search_docs.py --query "<your question>"
python skills/cells-official-docs-catalog/scripts/search_docs.py --topic <topic>
```

Topics: `architecture`, `testing`, `cli`, `component-api`, `lit-authoring`, `composition`, `theming`, `demo-docs-i18n-assets`, `application-runtime`, `application-communication`

---

### Gate 3: Shared Contracts

Before implementing any Cells component, read `skills/_shared/cells-rules-contract.md`.
Before choosing sources or test commands, read `skills/_shared/cells-source-routing-contract.md`.
Do not replicate those rules in phase skills; route through the shared contracts instead.

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

Before closing any task that touches UI or components, verify the checklist in `skills/_shared/cells-rules-contract.md`.

---

## When This Skill Is The Only One You Need

If the user asks:
- "What BBVA component should I use for X?"
- "How do I handle i18n in Cells?"
- "How do I structure a feature in Cells?"
- "What's the correct Cells test command?"
- "Is there a BBVA component for Y?"

→ This skill is the answer. Load it, run the search commands, return the result.

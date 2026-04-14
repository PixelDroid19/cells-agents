---
name: cells-official-docs-catalog
description: >
  Search authoritative BBVA Cells official guidance for architecture, CLI, component API, Lit authoring, composition, testing, demos, i18n, theming, and packaging. Triggers: when the user says "how does Cells do X", "official guidance for", "Cells documentation", "what is the Cells way", "Cells best practices", "how should I structure", "Cells architecture", "Cells testing guide", "Cells CLI docs", "Cells theming", "official Cells rules", or when looking up official Cells rules, checking how Cells works, finding CLI commands, or resolving architectural guidance.
license: MIT
metadata:
  author: D. J
  version: "1.1"
---

# Cells Official Docs Catalog

## Purpose

This skill is the internal knowledge base for official Cells guidance.

It exists so the installed skill bundle can answer Cells questions without depending on folder references outside this package.

## Bundled Resources

- `references/*.md`: normalized internal snapshots of official Cells guidance
- `scripts/build_index.py`: builds the local SQLite FTS5 index from the bundled references
- `scripts/search_docs.py`: searches the local index by topic or natural-language query
- `assets/cells_official_docs.db`: generated SQLite index
- `assets/manifest.json`: generated manifest of indexed topics

## When To Use

Use this skill when the task needs official guidance for:

- Cells and Web Components fundamentals
- Cells app or feature architecture
- Cells application runtime and configuration
- Cells bridge communication, event channels, native integration, or logout flows
- advanced application concerns like feature flags, microfrontends, performance, or service workers
- Cells CLI commands and local workflows
- Cells monitoring, SeMAAS integration, logging, and tracing
- component public API and packaging
- Lit templating and lifecycle
- composition, scoped elements, extension, and mixins
- demo, documentation, i18n, assets, and icons
- testing patterns and quality rules
- application-level testing guidance
- theming, tokens, and dark mode

## Workflow

### 1. Search by intent

Use the search script with a short intent query:

```bash
python skills/cells-official-docs-catalog/scripts/search_docs.py --query "how to structure a Cells feature with data manager"
python skills/cells-official-docs-catalog/scripts/search_docs.py --query "how to test a lit component with open-wc and sinon"
```

### 2. Open a topic dossier

If you already know the topic slug, inspect it directly:

```bash
python skills/cells-official-docs-catalog/scripts/search_docs.py --topic architecture
python skills/cells-official-docs-catalog/scripts/search_docs.py --topic testing
python skills/cells-official-docs-catalog/scripts/search_docs.py --topic cli
```

### 3. Apply only the relevant rules

Extract the exact rule, pattern, or command needed for the current task.

Do not dump large documentation blocks into the report.

## Topics

- `architecture`
- `web-components-foundations`
- `application-runtime`
- `application-communication`
- `advanced-application`
- `cli`
- `component-api`
- `lit-authoring`
- `composition`
- `demo-docs-i18n-assets`
- `testing`
- `application-testing`
- `theming`
- `monitoring`

## Canonical Component Construction Coverage

For real component authoring/review flows, use this reference coverage matrix before concluding:

| Official area | Internal topic/route |
| --- | --- |
| Web Components overview and reference | `web-components-foundations` |
| Packaging | `component-api` + `cli` |
| Custom elements | `component-api` |
| Class and properties | `component-api` + `lit-authoring` |
| Lifecycle | `lit-authoring` |
| Reuse and composition | `composition` |
| Component API | `component-api` |
| Templating in Lit | `lit-authoring` |
| Styles | `lit-authoring` + `theming` |
| Theming | `theming` |
| Demo | `demo-docs-i18n-assets` |
| Internationalization (i18n) | `demo-docs-i18n-assets` + `skills/cells-i18n/` |
| Documentation | `demo-docs-i18n-assets` + `component-api` |
| Images and icons | `demo-docs-i18n-assets` |
| Spherica integration | `composition` + project package evidence |
| Context | `architecture` + `application-runtime` |
| Testing | `testing` + `application-testing` |
| CI/CD | `cli` + project-local pipeline/config evidence |

Minimum rule:

- If a task claims production-ready component guidance, include explicit coverage of the relevant areas from this matrix.
- If any required area is missing evidence, return `partial` instead of `ok`.

## Rules

- Prefer this internal catalog over direct references to folders outside this package
- Still validate important claims against project code and tests
- Use `cells-components-catalog` for BBVA package discovery and this skill for official Cells process and authoring guidance
- If the bundled docs look insufficient for a specific edge case, report the gap explicitly

## Browser Integration

When official testing, demo, i18n, or theming guidance must be checked against a rendered page, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Use this catalog to retrieve the rule first, then validate the rule against real runtime behavior only when the task requires browser-visible evidence.

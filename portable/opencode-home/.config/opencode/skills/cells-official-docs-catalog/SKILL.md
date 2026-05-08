---
name: cells-official-docs-catalog
description: "Use when looking up official Cells guidance for architecture, CLI, testing, i18n, theming, Lit authoring, component API, composition, runtime, demos, or packaging."
---

# Cells Official Docs Catalog

## Purpose

Use this skill as the local official Cells documentation catalog. It replaces live RAG/MCP lookup with a bundled SQLite FTS5 index built from Markdown docs, including historical Cells documentation.

## Bundled Resources

- `scripts/build_index.py`: rebuild the SQLite FTS5 index from any docs directory
- `scripts/search_docs.py`: search, filter, open topics, and emit Markdown or JSON
- `assets/cells_official_docs.db`: generated structural index
- `assets/manifest.json`: generated provenance and index summary

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

## Indexing

Rebuild the index when the official docs snapshot changes. The source directory is resolved in this order:

1. `--docs-root <path>`
2. `CELLS_OFFICIAL_DOCS_ROOT`
3. `docs/` inside this skill

Use an explicit docs root when indexing an external checkout:

```bash
python skills/cells-official-docs-catalog/scripts/build_index.py --docs-root /path/to/cells-docs/docs
```

Every build replaces `assets/cells_official_docs.db` and `assets/manifest.json` from scratch. Docs under `older-versions/` are indexed as historical reference; current docs are ranked first unless the query explicitly asks for legacy, old, CLI4, or Bridge3 material.

## Workflow

### 1. Search by intent

Use short intent queries first:

```bash
python skills/cells-official-docs-catalog/scripts/search_docs.py --query "how to structure a Cells feature with data manager"
python skills/cells-official-docs-catalog/scripts/search_docs.py --query "how to test a lit component with open-wc and sinon"
python skills/cells-official-docs-catalog/scripts/search_docs.py --query "bridge routing channels"
python skills/cells-official-docs-catalog/scripts/search_docs.py --query "CLI4 Bridge3 old app command" --area legacy
```

Use JSON mode when another agent or script will consume the result:

```bash
python skills/cells-official-docs-catalog/scripts/search_docs.py --query "IntlMsg locales-app forTesting" --format json
```

### 2. Filter when intent is specific

Use filters to keep evidence scoped:

```bash
python skills/cells-official-docs-catalog/scripts/search_docs.py --query "unit testing coverage" --area applications
python skills/cells-official-docs-catalog/scripts/search_docs.py --query "theming tokens" --path-prefix web-components/reference/
python skills/cells-official-docs-catalog/scripts/search_docs.py --stats
```

### 3. Open a source document

Slugs are derived from the relative file path with folders joined by `-`:

```bash
python skills/cells-official-docs-catalog/scripts/search_docs.py --topic cells-applications-overview-application-structure
python skills/cells-official-docs-catalog/scripts/search_docs.py --topic web-components-reference-testing-unit-testing
python skills/cells-official-docs-catalog/scripts/search_docs.py --path cli/working-with-applications.md --content
```

### 4. Apply only relevant evidence

Extract the exact rule, pattern, or command needed for the current task.

Do not dump large documentation blocks into the report.

## Canonical Component Construction Coverage

For real component authoring/review flows, use this reference coverage matrix before concluding:

| Official area | Internal topic/route |
| --- | --- |
| Web Components overview and reference | `web-components-overview-web-components` |
| Packaging | `web-components-reference-packaging` + `cli-working-with-components` |
| Custom elements | `web-components-reference-custom-elements` |
| Class and properties | `web-components-reference-class-properties` + `web-components-reference-component-api` |
| Lifecycle | `web-components-reference-lifecycle` |
| Reuse and composition | `web-components-reference-reuse-composition` |
| Component API | `web-components-reference-component-api` |
| Templating in Lit | `web-components-reference-templating-in-lit` |
| Styles | `web-components-reference-styles` + `web-components-reference-theming` |
| Theming | `web-components-reference-theming` |
| Demo | `web-components-reference-demo` |
| Internationalization (i18n) | `cells-applications-internationalization` + `skills/cells-i18n/` |
| Documentation | `web-components-reference-documentation` + `web-components-reference-component-api` |
| Images and icons | `web-components-reference-images-icons` |
| Spherica integration | `web-components-reference-spherica-integration` + project package evidence |
| Context | `cells-applications-overview-technical-design` + `cells-applications-bootstrapping-the-bridge-instance` |
| Testing | `web-components-reference-testing-unit-testing` + `cells-applications-testing-unit-testing` |
| CI/CD | `cells-applications-ci-cd` + project-local pipeline/config evidence |

Minimum rule:

- If a task claims production-ready component guidance, include explicit coverage of the relevant areas from this matrix.
- If any required area is missing evidence, return `partial` instead of `ok`.

## Rules

- Prefer this internal catalog over direct references to folders outside this package
- Still validate important claims against project code and tests
- Use `cells-components-catalog` for BBVA package discovery and this skill for official Cells process and authoring guidance
- Keep source-order decisions aligned with `skills/_shared/cells-source-routing-contract.md`
- Distinguish documented framework commands and behaviors from repo-local wrappers or product naming
- For testing work, follow the Cells mandatory testing stack: `cells-cli-usage` -> `cells-coverage` -> `cells-test-creator`
- Treat `older-versions/` results as historical evidence unless the task explicitly targets older Cells stacks
- If the bundled docs look insufficient for a specific edge case, report the gap explicitly

## Browser Integration

When official testing, demo, i18n, or theming guidance must be checked against a rendered page, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Use this catalog to retrieve the rule first, then validate the rule against real runtime behavior only when the task requires browser-visible evidence.

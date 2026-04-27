---
name: cells-components-catalog
description: "Use when discovering existing BBVA Cells components, package names, tags, properties, events, slots, examples, or checking whether UI should reuse a catalog component."
---

# Cells Components Catalog

Use this skill to find the right BBVA Cells components before proposing code, app structure, or composition.

The bundled index and record set are packaged inside this skill so the team can search BBVA components without depending on external folders at runtime.

## When To Use

Use this skill when the task involves any of these:

- building a screen, app, widget, or flow with BBVA Cells components
- choosing between multiple BBVA components
- finding real component tags, package names, properties, events, methods, or CSS custom properties
- checking whether a BBVA Cells package already solves a need before inventing a custom component
- mapping product requirements like "login form", "toast", "stepper", "table", "header", or "charts" to BBVA packages

## Bundled Resources

- `scripts/build_index.py`: builds or rebuilds the SQLite FTS5 index from the bundled `assets/component_records.json` snapshot
- `scripts/search_docs.py`: searches the index or shows a detailed dossier for one package
- `assets/bbva_cells_components.db`: generated SQLite database
- `assets/component_manifest.json`: generated manifest with counts, categories, and provenance metadata
- `references/intent-map.md`: suggested search seeds and composition patterns

## Workflow

### 1. Search Broadly First

Start with one or two broad intent queries:

```bash
python scripts/search_docs.py --query "login form validation"
python scripts/search_docs.py --query "main navigation header tabs"
```

Use natural language. The search index includes:

- package names
- custom element tags
- class names
- package descriptions
- public properties
- events
- CSS custom properties
- README usage examples
- BBVA dependencies and mixins

### 2. Narrow To A Package

When a candidate looks promising, inspect the full package dossier:

```bash
python scripts/search_docs.py --package bbva-form-input
python scripts/search_docs.py --package @bbva-spherica-components/bbva-button-default
```

This returns:

- package identity
- category
- custom elements
- main public properties
- events
- CSS custom properties
- BBVA dependencies
- usage snippets
- code snippets from the package README when available
- bundled catalog records inside `skills/cells-components-catalog/assets/`

### 3. Cross-Check When Needed

If the result is still ambiguous:

- inspect the detailed package dossier returned by the catalog
- inspect the bundled record payload when you need raw indexed fields

Prefer the package docs and metadata over any secondary summary.

### 4. Produce Composition, Not Just Search Results

After searching, convert the findings into a practical recommendation:

- which packages to install
- which custom elements to use
- which props or events matter for the requested flow
- which code snippets or README examples should be reused
- which caveats or dependencies must be respected
- what should be composed together in the app

## Output Format

Use this structure when the user is asking for component selection or app composition:

```markdown
## Recommended BBVA Cells Components

| Package | Elements | Why |
|---------|----------|-----|
| `@bbva-spherica-components/bbva-form-input` | `bbva-form-input`, `bbva-form-text` | Covers text input and validation |

## Key API Notes

- `bbva-form-text`: use `label`, `value`, `required`, `error-message`
- `bbva-button-default`: listen for `click`; use `variant` and `text`

## Composition Proposal

- Header: `bbva-header-main`
- Form: `bbva-form-container` + `bbva-form-text` + `bbva-form-password`
- Primary action: `bbva-button-default`

## Risks Or Caveats

- `bbva-form-input` variants have package-specific attributes; verify the selected element before coding
- some packages expose multiple custom elements, so do not assume the package slug equals the only tag

## Source Paths

- `skills/cells-components-catalog/assets/component_records.json`
```

## Rules

- Never invent a BBVA Cells tag, property, event, method, or CSS custom property
- Search before recommending components, unless the package is already certain and explicitly named
- If a package exposes multiple elements, name the exact custom elements you plan to use
- When building an app, recommend a composition of packages, not a single component in isolation
- Mention source paths so the recommendation is auditable
- If the index is missing or stale, rebuild it with `scripts/build_index.py`
- Use the bundled component catalog as the team-local authoritative source

## Browser Integration

This skill is primarily an indexed discovery layer. When the chosen package must be validated in a rendered demo or local page, hand off to:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Search first, then use browser validation only for shortlisted packages that need runtime confirmation.

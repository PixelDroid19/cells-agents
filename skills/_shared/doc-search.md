# Doc & Catalog Search Contract

How to query the bundled catalogs and what to do when a search fails. Applies to both:

- `skills/cells-components-catalog/scripts/search_docs.py` (component metadata, FTS5)
- `skills/cells-official-docs-catalog/scripts/search_docs.py` (official guidance, FTS5)

## How to Phrase Queries

FTS5 matches keywords, not intent. Use 2–4 concrete nouns; drop filler verbs and vague words.

| Intent | Good query | Bad query |
|---|---|---|
| Pick a dropdown component | `select dropdown options` | `I need something like a dropdown` |
| Button with left icon | `button icon` | `button stuff` |
| Run component tests | `lit-component test command` | `how do I test this` |
| Translate a literal | `intlmsg locale translation` | `text in spanish` |
| Theme a component | `theming css custom properties` | `change the colors` |

Rules:

- One concept per query. Split "button with icon inside a form" into `button icon` and `form field`.
- Include the domain word the docs would use (`locale`, `coverage`, `scoped elements`, `data manager`), not the user's paraphrase.
- If you know part of a tag or package name (`bbva-`, `select`), include it.

## Zero or Weak Results: Fallback Ladder

Never stop, block, or guess from memory because one query returned nothing. Escalate in this order and stop at the first step that yields evidence:

1. **Rephrase**: swap synonyms (`dropdown` → `select`, `popup` → `modal dialog`), remove the least essential word, try singular/plural.
2. **Broaden**: drop to the single strongest keyword (`select`), then filter results by reading titles.
3. **Browse the index directly**: list the catalog's records/topics (components catalog: query a generic term like the element family; official docs: read `skills/cells-official-docs-catalog/SKILL.md` topic map) and pick by title.
4. **Project evidence**: search project code, `custom-elements.json`, `package.json`, and tests for the tag/API in question.
5. **Report honestly**: only after 1–4, state what you searched and that no evidence exists — and propose the closest alternative you did find.

Two attempts maximum per rung; do not loop on the same query.

## Proportionality

- A search that answers the question ends the search. Do not cross-check three sources for a simple lookup.
- Trust the compact search snippet when it answers the question; open the full doc only when you need exact API details you will cite or code against.
- Docs and code disagree → code wins.

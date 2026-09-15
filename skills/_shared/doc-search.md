# Doc and Catalog Search Contract

Use this guide for the bundled component and official-docs catalogs.

## Query Shape

FTS queries work best with two to four concrete domain terms. Use the vocabulary the documentation is likely to contain.

| Intent | Useful query |
| --- | --- |
| Select dropdown component | `select dropdown options` |
| Button with icon | `button icon` |
| Component test command | `component test command` |
| Translate a literal | `intlmsg locale translation` |
| Theme a component | `theming css custom properties` |

Split unrelated concepts into separate searches. Include a known tag or package fragment when available.

## Weak or Empty Results

Progress through this ladder until evidence answers the decision or the available sources are exhausted:

1. Rephrase with documentation vocabulary or a close synonym.
2. Broaden to the strongest term and inspect titles.
3. Search a more specific catalog topic or package.
4. Inspect project CEM, package source, code, tests, and manifest data.
5. Report the evidence gap and the closest supported alternative.

Avoid repeating an identical query without new information, but do not impose a fixed retry count that stops safe progress. Stop searching once the evidence is sufficient for the decision.

## Proportionality

Use the compact search result when it answers the question. Open the full source only for an API or rule you need to rely on. When catalog and active project evidence conflict, report the conflict and follow the active project for its local behavior.

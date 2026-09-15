# Browser Testing Convention

## Purpose

Use this guide when a change affects rendered UI, a demo, a route, an interaction flow, screenshots, DOM snapshots, visual diffs, runtime i18n, or theming. Source code proves intent; browser evidence proves rendered behavior.

## Workflow

1. Resolve the local serve/demo command and any existing runtime through `cells-cli-usage` when command selection is needed.
2. Reuse an existing server URL, browser session, and CDP port when available.
3. Start a local runtime only when visible behavior needs confirmation and no usable runtime exists.
4. Connect or open the route with `agent-browser`.
5. Wait for a stable state when appropriate, then capture an interactive snapshot before acting.
6. Interact through discovered element references, not guessed selectors.
7. Re-snapshot after a meaningful DOM or route change; capture a screenshot or diff when visual detail matters.

## Proportionality

- Do not start a server or full test suite for a copy-only or low-risk static change.
- Prefer the smallest realistic flow that proves the requested visible behavior.
- Reuse sessions rather than starting parallel browser instances for the same flow.
- Do not install a browser, dependencies, or `agent-browser` unless the user asks.

## Evidence

Report the route, runtime/command used, relevant interaction, observed result, and capture paths when produced. If the project cannot be served and browser proof is required, report `blocked`; if it is useful but not required, report `partial` with the limitation.

For `artifact_persistence: openspec`, store optional browser evidence under the active change's `ui-evidence/` directory only when the governed change needs it. With `none`, return the evidence inline. LocalMemory is never a browser-evidence store.

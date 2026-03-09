# Browser Testing Convention

## Purpose

Use this file whenever the task touches rendered UI, demos, routes, screenshots, DOM snapshots, interaction flows, or visual regressions.

The goal is to make browser-visible claims evidence-based instead of assuming that source code alone proves runtime behavior.

## Load Conditions

Also read this file when any of these are true:

- the change affects a page, route, demo, or rendered component state
- the task requires clicking, filling, navigating, or waiting for UI changes
- the task requires screenshots, DOM snapshots, or visual diffs
- the task involves browser-level validation of i18n, theming, responsive behavior, or feature composition
- unit tests are not enough to prove the user-visible behavior

When browser automation is required, also read `skills/agent-browser/SKILL.md` when it is available in the workspace or installed bundle.

## Canonical Browser Workflow

1. Resolve whether a local runtime or browser session already exists, usually through `skills/cells-cli-usage/`.
2. Reuse the current dev server URL, browser session, and port when they are already available.
3. Only start a new local runtime when confirmation genuinely requires it and no reusable runtime exists.
4. Open or connect with `agent-browser` using the existing URL or CDP port when possible.
5. Wait for a stable state (`agent-browser wait --load networkidle` when appropriate).
6. Capture an interactive snapshot before acting: `agent-browser snapshot -i`.
7. Interact using discovered refs, not guessed selectors.
8. Re-snapshot after DOM or route changes.
9. Capture screenshot or diff evidence when a visual or browser-visible state matters.

## Conservative Execution Policy

- Do NOT start the project, demo server, or test suite for every small change.
- Small, low-risk edits should rely first on code evidence, targeted static checks, and existing runtime context.
- Start or rerun the local runtime only to confirm browser-visible behavior, integration wiring, or a risky change.
- Prefer targeted confirmation over full-project execution.
- Prefer targeted tests over full test suites unless the user explicitly asks for a broader run or the change risk justifies it.
- If confirmation is not yet needed, defer runtime and test execution to the verification stage.

## Runtime And Session Reuse Policy

- If a dev server is already running, reuse its exact host and port.
- If `agent-browser` already opened a browser or session, keep using that same session instead of launching a new one.
- If a browser with CDP is already available, prefer `agent-browser connect <port>` or `agent-browser --auto-connect` instead of opening a new browser.
- If the previous step already established a working route, keep using the same URL unless the task requires a different route.
- If a prior browser session used `--session`, `--session-name`, or `--profile`, continue with the same isolation context whenever possible.
- Do not start parallel browser instances for the same validation flow unless isolation is explicitly required.

## `agent-browser` Command Resolution

- Prefer an existing global `agent-browser` installation when the command is already available.
- If there is no global command but the workspace already depends on it, use `npx agent-browser`.
- Do NOT install `agent-browser`, Chromium, or project dependencies unless the user explicitly asks for installation help.
- Prefer the ref-based workflow: `snapshot -i` -> `@e*` refs -> interaction -> re-snapshot.
- Use `--json` when structured parsing is needed.
- Use `--annotate` only when visual labeling materially helps the task.
- Use `connect`, `--cdp`, or `--auto-connect` when reusing an already running browser is possible.

## Evidence Rules

- Source code proves intent and structure; browser evidence proves rendered behavior.
- Snapshot first, interact second, re-snapshot after any meaningful DOM change.
- Use screenshots or screenshot diffs when the task is visual; use snapshots and text extraction when the task is functional.
- Prefer the smallest realistic browser flow that proves the requirement.
- Use headed mode only for debugging or when explicitly needed.
- If the project cannot be served locally, report browser validation as blocked instead of inventing success.
- If an existing runtime or browser session can be reused, do that instead of starting a fresh one.

## Persistence Rules

- In `engram`, persist a compact `ui-evidence` summary and mention any generated screenshot or diff paths.
- In `openspec`, store optional browser evidence under `openspec/changes/{change-name}/ui-evidence/` when the task requires filesystem artifacts.
- In `hybrid`, do both.
- In `none`, return browser evidence inline and avoid leaving extra files unless the user explicitly asked for them.

## Typical Deliverables

Return compact evidence such as:

- URL or route tested
- command or runtime used to open the page
- key interactions performed
- browser-visible result
- screenshot, snapshot, or diff paths when captured
- explicit blockers when runtime validation could not be completed

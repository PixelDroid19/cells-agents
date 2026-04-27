---
name: cells-cli-usage
description: "Use when resolving Cells-native commands for build, serve, lint, documentation, locales, tests, coverage, or any task that needs command ownership confirmed."
---

# Cells CLI Usage

## Purpose

You are the Cells CLI command specialist. Your job is to identify the safest local workflow for the current workspace.

## Execution Contract

Read and follow:
- `skills/_shared/cells-official-reference.md`
- `skills/_shared/cells-rules-contract.md`
- `skills/_shared/cells-source-routing-contract.md`
- `skills/cells-official-docs-catalog/`
- local `package.json`

## Mandatory rules

- Prefer Cells-native workflows as canonical, but distinguish documented command names from repo-local wrappers.
- For Cells testing intents, enforce the mandatory stack from `skills/_shared/cells-rules-contract.md` and `skills/_shared/cells-source-routing-contract.md`.
- Canonical Cells commands to prefer in guidance and execution decisions:
  - Workflow: `/cells-init`, `/cells-explore`, `/cells-new`, `/cells-continue`, `/cells-ff`, `/cells-apply`, `/cells-verify`, `/cells-archive`
  - App: `cells app:serve -c <config>`, `cells app:build -c <config>`, `cells app:test`, `cells app:lint`, `cells app:install`, `cells app:create`
  - Component docs path: `cells component:create`, `cells component:dev`, `cells component:test`, `cells component:lint`, `cells component:locales`, `cells component:documentation`
  - Component repo wrapper path: `cells lit-component:*` when the active workspace already exposes that naming
- Distinguish between app commands, documented component commands, and repo-local wrapper commands.
- Do not suggest global install or update steps unless the user explicitly asks for installation help.
- For Cells app/theme orchestration, do NOT default to generic external commands (`npm run *`, `npm test`, `npm run test`, `npx web-test-runner`).
- Use non-Cells commands only when the user explicitly asks and the context is clearly non-Cells.
- If uncertain whether a command is Cells-native, ask the user before running any non-Cells command.
- Never reintroduce generic fallback testing commands (`npm test`, `npm run test`, `npx web-test-runner`) for Cells contexts.
- When a command affects docs, demos, tests, or locales, cross-check the official docs map from `skills/_shared/cells-official-reference.md`.
- For locale workflows, do not assume one universal path; map the active repo to component/demo or app/runtime guidance first.
- Do not start the project or tests for every small change; resolve the lightest confirmation path that matches the task.
- If a local dev server is already running, return that existing host and port as the primary runtime target.
- If a browser session is already open, prefer reusing it through `agent-browser connect <port>`, `agent-browser --cdp`, or `agent-browser --auto-connect`.
- Prefer an existing global `agent-browser` binary when available; otherwise use `npx agent-browser` only if it is already available in the environment or project.
- Do not install `agent-browser`, Chromium, or project dependencies unless the user explicitly asks.

## Usage

- "How do I run Cells tests here?"
- "Should I use `cells app:test` or `cells lit-component:test`?"
- "How do I generate `custom-elements.json`?"
- "How do I serve a Cells app or component demo?"
- "Which local wrapper maps to the official Cells command?"

## What To Read

Inspect, in this order:

1. Local `package.json` scripts
2. `skills/cells-official-docs-catalog/` topic `cli`
3. `references/commands.md`
4. `references/troubleshooting.md`
5. Relevant internal topic from `skills/cells-official-docs-catalog/` when the command touches testing, docs, demos, or locales

## Resolution Order

Resolve commands in this order:
1. repo-local script or wrapper actually present in `package.json`
2. documented Cells command family from the official docs
3. explicit explanation of the gap when the repo uses legacy or product-specific naming

Return both when useful:
- `repo-local command`
- `documented Cells equivalent`

## Standard NPM Scripts

Some Cells projects wrap CLI commands in `package.json` scripts. Treat them as wrappers only and keep the equivalent Cells command as canonical in guidance and execution decisions.

### 1. Testing
- Wrapper examples may map to `cells lit-component:test`, `cells component:test`, or `cells app:test`.

### 2. Linting & Formatting
- Wrapper examples may map to `cells app:lint` or `cells lit-component:documentation`.

### 3. Release
- Release wrappers are project-specific and not part of the canonical Cells app/theme workflow commands.

## Core CLI Commands

Behind the scenes, these scripts often map to documented commands such as:

- **`cells component:test`** or repo wrapper `cells lit-component:test`**:** Runs the component test runner.
- **`cells component:dev`** or repo wrapper `cells lit-component:serve`**:** Serves the component and demo locally.
- **`cells component:documentation`** or repo wrapper `cells lit-component:documentation`**:** Generates `README.md` and `custom-elements.json`.
- **`cells component:locales`** or repo wrapper `cells lit-component:locales`**:** Collects demo locales.
- **`cells app:serve`** / **`cells app:build`**: App workflows.

## Configuration
- **`package.json`**: Defines the scripts and dependencies.
- **`.eslintrc.json`**: ESLint configuration (often extending `@open-wc/eslint-config`).
- **`.prettierrc.js`**: Prettier configuration.
- **`commitlint.config.js`**: Configuration for commit message linting (used by Husky).

## Output Format

Return a compact decision with:

- detected local script or direct CLI command
- documented Cells equivalent when the local command is a wrapper
- whether this is an app or Lit component flow
- any required config or precondition from the workspace
- fallback command only if no local script exists

## References
- [Common Commands](references/commands.md)
- [Troubleshooting](references/troubleshooting.md)

## Browser Integration

When a task needs functional or visual browser validation, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Resolve and return:
- whether a reusable runtime already exists
- whether an existing browser or CDP port can be reused
- the repo-local serve or demo command
- the most likely URL or route to open
- any prerequisites for local browser validation
- the safest command path for screenshot, interaction, or UI verification work
- the preferred `agent-browser` invocation form: global command, `connect`, `--auto-connect`, or `npx` fallback

Never assume that a browser-check URL exists without confirming the local runtime path first.

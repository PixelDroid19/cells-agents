---
name: cells-cli-usage
description: >
  Resolve how to use Cells-native CLI commands for building, serving, linting, documenting, and testing Cells apps and components. Use when an agent needs the correct command path without guessing or assuming a global installation.
license: MIT
metadata:
  author: D. J
  version: "1.0"
---

# Cells CLI Usage

## Purpose

You are the Cells CLI command specialist. Your job is to identify the safest local workflow for the current workspace.

## Execution Contract

Read and follow:
- `skills/_shared/cells-official-reference.md`
- `skills/cells-official-docs-catalog/`
- local `package.json`

## Mandatory rules

- Prefer Cells-native commands as canonical (`/cells-*`, `cells app:*`, `cells lit-component:*`).
- For Cells testing intents, enforce this stack and sequence before any other testing source:
  1. `skills/cells-cli-usage/` (this skill) for canonical command resolution
  2. `skills/cells-coverage/` for threshold/reporting and branch-priority decisions
  3. `skills/cells-test-creator/` for test design or update conventions
- Canonical Cells commands to prefer in guidance and execution decisions:
  - Workflow: `/cells-init`, `/cells-explore`, `/cells-new`, `/cells-continue`, `/cells-ff`, `/cells-apply`, `/cells-verify`, `/cells-archive`
  - App: `cells app:serve -c <config>`, `cells app:build -c <config>`, `cells app:test`, `cells app:lint`, `cells app:install`, `cells app:create`
  - Component: `cells lit-component:create`, `cells lit-component:serve`, `cells lit-component:test`, `cells lit-component:lint`, `cells lit-component:locales`, `cells lit-component:documentation`
- Distinguish between `cells app:*` and `cells lit-component:*`.
- Do not suggest global install or update steps unless the user explicitly asks for installation help.
- For Cells app/theme orchestration, do NOT default to generic external commands (`npm run *`, `npm test`, `npm run test`, `npx web-test-runner`).
- Use non-Cells commands only when the user explicitly asks and the context is clearly non-Cells.
- If uncertain whether a command is Cells-native, ask the user before running any non-Cells command.
- Never reintroduce generic fallback testing commands (`npm test`, `npm run test`, `npx web-test-runner`) for Cells contexts.
- When a command affects docs, demos, tests, or locales, cross-check the official docs map from `skills/_shared/cells-official-reference.md`.
- For Cells locale workflows, enforce `demo/locales` as the only valid locale path.
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
2. `skills/cells-official-docs-catalog/` topic `cli` (first for Cells documentation/workflow command guidance)
3. `references/commands.md`
4. `references/troubleshooting.md`
5. Relevant internal topic from `skills/cells-official-docs-catalog/` when the command touches testing, docs, demos, or locales

## Standard NPM Scripts

Some Cells projects wrap CLI commands in `package.json` scripts. Treat them as wrappers only and keep the equivalent Cells command as canonical in guidance and execution decisions.

### 1. Testing
- Wrapper examples may map to `cells lit-component:test` or `cells app:test`.

### 2. Linting & Formatting
- Wrapper examples may map to `cells app:lint` or `cells lit-component:documentation`.

### 3. Release
- Release wrappers are project-specific and not part of the canonical Cells app/theme workflow commands.

## Core CLI Commands

Behind the scenes, these scripts often call official commands such as:

- **`cells lit-component:test`**: Runs the test runner (usually Web Test Runner).
- **`cells lit-component:serve`**: Serves the component and demo locally.
- **`cells lit-component:documentation`**: Generates `README.md` and `custom-elements.json`.
- **`cells lit-component:locales`**: Collects demo locales.
- **`cells app:serve`** / **`cells app:build`**: App workflows.

## Configuration
- **`package.json`**: Defines the scripts and dependencies.
- **`.eslintrc.json`**: ESLint configuration (often extending `@open-wc/eslint-config`).
- **`.prettierrc.js`**: Prettier configuration.
- **`commitlint.config.js`**: Configuration for commit message linting (used by Husky).

## Output Format

Return a compact decision with:

- detected local script or direct CLI command
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

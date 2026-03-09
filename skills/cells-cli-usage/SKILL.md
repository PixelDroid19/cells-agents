---
name: cells-cli-usage
description: >
  Resolve how to use Cells CLI and repo-local NPM scripts for building, serving, linting, documenting, and testing Cells apps and components. Use when an agent needs the correct command path without guessing or assuming a global installation.
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

- Prefer repo-local `package.json` scripts before raw `cells ...` commands when both exist.
- Distinguish between `cells app:*` and `cells lit-component:*`.
- Do not suggest global install or update steps unless the user explicitly asks for installation help.
- If the workspace already exposes `npm run test`, `npm run lint`, `npm run docs`, or similar, prefer those names in guidance and execution.
- When a command affects docs, demos, tests, or locales, cross-check the official docs map from `skills/_shared/cells-official-reference.md`.

## Usage

- "How do I run Cells tests here?"
- "Should I use `npm run test` or `cells lit-component:test`?"
- "How do I generate `custom-elements.json`?"
- "How do I serve a Cells app or component demo?"
- "Which local script corresponds to the official Cells command?"

## What To Read

Inspect, in this order:

1. Local `package.json` scripts
2. `skills/cells-official-docs-catalog/` topic `cli`
3. `references/commands.md`
4. `references/troubleshooting.md`
5. Relevant internal topic from `skills/cells-official-docs-catalog/` when the command touches testing, docs, demos, or locales

## Standard NPM Scripts

Most Cells projects (like `bbva-feature-example`) configure these standard scripts in `package.json`:

### 1. Testing
- **`npm test`**: Runs unit tests using `cells lit-component:test`.
- **`npm run test:compatibility`**: Runs tests against older browsers/environments.
- **`npm run test:prune-snapshots`**: Removes unused snapshots.
- **`npm run test:update-snapshots`**: Updates snapshots for UI tests.

### 2. Linting & Formatting
- **`npm run lint`**: Runs all linters (ESLint, Prettier, Stylelint).
- **`npm run format`**: Fixes linting errors automatically.
- **`npm run docs`**: Generates component documentation, usually around `cells lit-component:documentation`.

### 3. Release
- **`npm run release`**: Uses `standard-version` to bump version, generate changelog, and tag the release.

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


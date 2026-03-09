# CLI

## Scope

Use this topic for Cells CLI commands and local workflow mapping.

## Core rules

- Prefer local `package.json` scripts when a project already wraps Cells commands there.
- Distinguish between app commands and Lit component commands.
- Common Lit component commands are:
  - `cells lit-component:create`
  - `cells lit-component:serve`
  - `cells lit-component:test`
  - `cells lit-component:documentation`
  - `cells lit-component:locales`
- Common app commands are:
  - `cells app:create`
  - `cells app:serve`
  - `cells app:build`
  - `cells app:test`
  - `cells app:lint`
- `cells lit-component:documentation` is the official path for generating `README.md` and `custom-elements.json`.
- `cells lit-component:locales` is the official path for generating merged demo locales.
- Do not assume the user wants global installation or upgrade guidance.

## Decision rules

- If `npm run test` exists, prefer it over raw `cells lit-component:test`.
- If `npm run docs` exists and maps to Cells docs generation, prefer that script name in team guidance.
- If no local scripts exist, recommend the narrowest Cells command that matches the project type.

## Use when

- deciding which command to run
- mapping local scripts to official Cells commands
- explaining serve, build, docs, test, or locales workflows

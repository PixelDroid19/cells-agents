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
- In Cells projects, locale paths depend on the touched surface and repo/runtime convention. `demo/locales/locales.json` is common for component demos, but it is not a universal rule for every feature, app, or test surface.
- Do not assume the user wants global installation or upgrade guidance.

## Decision rules

- Keep Cells-native commands canonical for Cells app/theme workflows (`/cells-*`, `cells app:*`, `cells lit-component:*`).
- Do not default to generic external commands (`npm run *`, `npm test`, `npx web-test-runner`) for Cells workflows.
- Local scripts can be used as wrappers when they clearly map to Cells commands, but guidance should keep the equivalent Cells command explicit.
- If uncertain whether a command path is Cells-native, ask before running non-Cells commands.
- If no local scripts exist, recommend the narrowest Cells command that matches the project type.

## Use when

- deciding which command to run
- mapping local scripts to official Cells commands
- explaining serve, build, docs, test, or locales workflows

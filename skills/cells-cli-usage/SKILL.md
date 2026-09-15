---
name: cells-cli-usage
description: "Use when resolving executable Cells commands for build, serve, lint, documentation, locales, tests, coverage, or another installed-project workflow."
---

# Cells CLI Usage

## Purpose

Resolve what the active workspace can actually run, then identify its documented Cells equivalent. This skill does not infer commands from prose or run a generic fallback.

Read [Cells rules](../_shared/cells-rules-contract.md) and [source routing](../_shared/cells-source-routing-contract.md) before making a command claim that affects the requested work.

## Evidence Order

1. Inspect the installed project's `package.json` scripts, lockfiles/dependencies, and required configuration files.
2. If a script is a wrapper, inspect enough of it to establish its underlying command family.
3. Search the official Cells CLI catalog for the current documented equivalent.
4. If no executable route is supported by evidence, report the gap instead of guessing.

## Command Families

| Workspace type | Documented family | Valid local compatibility route |
| --- | --- | --- |
| Component | `cells component:create`, `dev`, `test`, `lint`, `locales`, `documentation` | An installed `cells lit-component:*` wrapper, including `serve` for local preview |
| App | `cells app:dev`, `build`, `test`, `lint`, `install`, `create`, with the project's actual configuration | A verified project script, including an installed legacy `cells app:serve` wrapper |

The current documented component family comes from `skills/cells-official-docs-catalog/SKILL.md`; legacy wrapper semantics are recorded in `references/commands.md`. Treat the observed project script as the executable choice, and report the documented equivalent when it helps a user understand the route.

## Rules

- Resolve a test command only for a test request; coverage and test-authoring skills remain optional specialists.
- Do not default to `npm test`, `npx web-test-runner`, or another generic runner in a Cells context. A package script is acceptable only after the resolver identifies what it runs.
- Do not invent a `-c` configuration path; read the project's configuration.
- Do not install dependencies, global tooling, Chromium, or a browser helper unless the user asks.
- Reuse an already running server and browser/CDP session when browser validation is needed.

## Output

Return the exact observed local command or script, documented Cells equivalent, project type, required configuration, and evidence path. For a browser request, also return the verified runtime URL or say that it is not yet available.

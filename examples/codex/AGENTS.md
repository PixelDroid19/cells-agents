# Cells Agent Bundle

Apply these instructions only in a BBVA Cells workspace or when the user asks
for Cells help. Project `AGENTS.md` files may refine this global layer.

## Start

1. Read `.cells-agent/context.json` when present.
2. Read `~/.codex/skills/_shared/cells-work-sizing-contract.md`.
3. Choose `fast-path`, `scoped-change`, `full-workflow`, or `blocked`.
4. Load only the relevant skill folders from `~/.codex/skills/`.

For fast or scoped work, inspect or implement directly and run targeted
validation. Do not manufacture proposal/spec/design/task artifacts.

For a full workflow, use:

`cells-init → cells-explore → cells-propose → (cells-spec + cells-design) → cells-tasks → cells-apply → cells-verify → cells-archive`

Use the role agents under `~/.codex/agents/` only for independent work that
benefits from a separate context. Executors do not delegate again.

## Non-negotiable Cells routing

- Search `cells-components-catalog` before inventing a component or API.
- Use `cells-official-docs-catalog` for official Cells, CLI, testing, theming,
  architecture, and authoring guidance.
- Use `cells-app-architecture` for feature boundaries and composition.
- Use `cells-cli-usage` to resolve commands, `cells-test-creator` only when
  authoring tests, and `cells-coverage` only for coverage work.
- Use `cells-i18n` for translated literals and locale behavior.
- Use `agent-browser` only when visible runtime evidence is relevant.

Use Cells-native commands:

- Apps: `cells app:serve`, `cells app:build`, `cells app:test`, `cells app:lint`
- Components: `cells lit-component:serve`, `cells lit-component:test`,
  `cells lit-component:lint`, `cells lit-component:documentation`

Do not default to generic `npm test` or `npx web-test-runner` in a Cells
workspace unless the user explicitly requests that path.

## Persistence and evidence

Use inline results for fast/scoped work. Use OpenSpec artifacts for a durable
full workflow. Host memory is optional and never required.

Do not claim success from inferred behavior or unexecuted commands. Report
exact files, commands, outputs, blockers, risks, and remaining evidence.

# Cells Agent Bundle — Skills Index

When working on a BBVA Cells project, load the relevant skill(s) **before** writing any code or making architectural decisions.

## How to Use

1. Check the trigger column to find skills that match your current task
2. Load the skill by reading the SKILL.md file at the listed path
3. Follow ALL patterns and rules from the loaded skill
4. Multiple skills can apply simultaneously

## BBVA-First Rule (Always)

For any UI, typography, form, button, navigation, or feedback work:

1. **Search `cells-components-catalog`** — if a BBVA component exists, use it and stop
2. **Only if no match exists**, use `cells-component-authoring` to create one correctly
3. **Never** use raw HTML elements (`<p>`, `<h3>`, `<span>`) when a BBVA component is available

## i18n Rule (Always)

- **Never** use `this.t('key') || ''` — the i18n runtime renders the key itself as fallback when missing (it is not falsy). This hides real missing translations.
- If a key is missing, add it to `demo/locales/locales.json`.

## CELLS Workflow Skills

| Skill | Trigger | Path |
|-------|---------|------|
| `cells-init` | Initializing project, detecting stack, bootstrapping persistence | [`skills/cells-init/SKILL.md`](skills/cells-init/SKILL.md) |
| `cells-explore` | Exploring codebase, component, architecture, or change area | [`skills/cells-explore/SKILL.md`](skills/cells-explore/SKILL.md) |
| `cells-propose` | Creating change proposal with intent, scope, risks, rollback | [`skills/cells-propose/SKILL.md`](skills/cells-propose/SKILL.md) |
| `cells-spec` | Writing behavioral specs with Given/When/Then scenarios | [`skills/cells-spec/SKILL.md`](skills/cells-spec/SKILL.md) |
| `cells-design` | Producing technical architecture, data flow, testing strategy | [`skills/cells-design/SKILL.md`](skills/cells-design/SKILL.md) |
| `cells-tasks` | Breaking change into ordered, file-level tasks | [`skills/cells-tasks/SKILL.md`](skills/cells-tasks/SKILL.md) |
| `cells-apply` | Implementing code, writing components, generating tests | [`skills/cells-apply/SKILL.md`](skills/cells-apply/SKILL.md) |
| `cells-verify` | Validating implementation, running tests, quality gate | [`skills/cells-verify/SKILL.md`](skills/cells-verify/SKILL.md) |
| `cells-archive` | Closing change, archiving artifacts, final closure | [`skills/cells-archive/SKILL.md`](skills/cells-archive/SKILL.md) |

## Cells Specialist Skills

| Skill | Trigger | Path |
|-------|---------|------|
| `cells-component-researcher` | Researching component API, events, CSS hooks, or usage patterns | [`skills/cells-component-researcher/SKILL.md`](skills/cells-component-researcher/SKILL.md) |
| `cells-component-authoring` | Creating a new component (only if no BBVA component matches) | [`skills/cells-component-authoring/SKILL.md`](skills/cells-component-authoring/SKILL.md) |
| `cells-composition-architect` | Composing features from existing components and building blocks | [`skills/cells-composition-architect/SKILL.md`](skills/cells-composition-architect/SKILL.md) |
| `cells-feature-analyzer` | Extracting reusable patterns from real feature implementations | [`skills/cells-feature-analyzer/SKILL.md`](skills/cells-feature-analyzer/SKILL.md) |
| `cells-app-architecture` | Designing feature structure, data managers, routing, bridge, pub/sub | [`skills/cells-app-architecture/SKILL.md`](skills/cells-app-architecture/SKILL.md) |
| `cells-cli-usage` | Resolving correct Cells CLI command (`cells app:*`, `cells lit-component:*`) | [`skills/cells-cli-usage/SKILL.md`](skills/cells-cli-usage/SKILL.md) |
| `cells-coverage` | Analyzing coverage reports, prioritizing test gaps, lcov triage | [`skills/cells-coverage/SKILL.md`](skills/cells-coverage/SKILL.md) |
| `cells-test-creator` | Authoring tests with OpenWC + Sinon, public-behavior only | [`skills/cells-test-creator/SKILL.md`](skills/cells-test-creator/SKILL.md) |
| `cells-i18n` | Managing `this.t(...)`, locale parity, IntlMsg setup | [`skills/cells-i18n/SKILL.md`](skills/cells-i18n/SKILL.md) |
| `agent-browser` | Browser UI validation, screenshots, CDP automation | [`skills/agent-browser/SKILL.md`](skills/agent-browser/SKILL.md) |
| `issue-creation` | Creating GitHub bug report or feature request | [`skills/issue-creation/SKILL.md`](skills/issue-creation/SKILL.md) |
| `branch-pr` | Creating pull request or preparing branch for submission | [`skills/branch-pr/SKILL.md`](skills/branch-pr/SKILL.md) |
| `skill-registry` | Knowledge gateway: BBVA component lookup, anti-patterns, routing | [`skills/skill-registry/SKILL.md`](skills/skill-registry/SKILL.md) |

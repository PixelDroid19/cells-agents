# Cells Agent Bundle — Skills Index

When working on a BBVA Cells project, load the relevant skill(s) **before** writing any code or making architectural decisions.

## How to Use

1. Check the trigger column to find skills that match your current task
2. Load the skill by reading the SKILL.md file at the listed path
3. Follow ALL patterns and rules from the loaded skill
4. Multiple skills can apply simultaneously

## Cells Rules Contract (Always)

For UI, typography, forms, buttons, navigation, feedback, i18n, command policy, test routing, scoped elements, events, and Cells component rules:

1. Read `skills/_shared/cells-rules-contract.md`
2. Follow `skills/_shared/cells-source-routing-contract.md` for source order
3. Do not duplicate or weaken those rules in phase-specific work

## Mandatory Testing Stack

For any Cells test intent, consult skills in this **exact order** before any other testing source:

1. `skills/cells-cli-usage/` — canonical test command resolution
2. `skills/cells-coverage/` — coverage thresholds, report triage
3. `skills/cells-test-creator/` — test design, creation, conventions

Do not skip or reorder. Do not use generic fallback commands in Cells contexts.

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
| `cells-cleanup` | Sweep component for code quality issues (JSDoc, formatting, conditions, attributes, `.map()`) without changing logic | [`skills/cells-cleanup/SKILL.md`](skills/cells-cleanup/SKILL.md) |

## Cleanup Rule (cells-cleanup)

When running `/cells-cleanup`:

- **NEVER change logic or behavior** — only form, structure, and documentation
- Changes that are safe to auto-apply: formatting, JSDoc, attribute fields, conditions-by-method, Rules Table Pattern, `.map()` refactors
- Changes that require user approval: reusability improvements, constants extraction, layer-responsibility moves
- Do NOT touch: `test/`, `demo/locales/`, `.scss`, `.css.js`, `custom-elements.json`

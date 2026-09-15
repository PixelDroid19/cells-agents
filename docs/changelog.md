# Changelog

## 3.0.0 — Local runtime and native adapters

- Added a dependency-free project/command/catalog/evidence CLI and optional stdio MCP server.
- Replaced mandatory Engram with an independently installable Cells Memory application and optional JSON bridge.
- Generated native role capabilities, invocable VS Code children, direct Codex skill discovery and native OpenCode delegation.
- Replaced text-presence governance tests with executable regressions; added independent review fixes and source-bound evidence.
- Rebuilt catalogs from supplied BBVA snapshots, with read-only queries, bounded previews and hash/ZIP integrity validation.
- Added conflict-preserving installation plans, backups, single/multi profiles, idempotent updates and generated runtime delivery.
- Integrated remote harness contracts and the retirement of eight overlapping skills; generated portable copies are no longer tracked.

Historical release notes below describe their own versions, not current requirements.

## Notable Upgrades

### v1.0.0 — Cells Agent Bundle

Initial release of the Cells Agent Bundle — a BBVA Cells-focused orchestration workspace built on top of the Agent Teams Lite pattern.

#### What's New

- **OpenCode-first orchestration** for BBVA Cells projects using skill-driven delegated runs
- **Cells workflow and specialist skills** covering the full SDD lifecycle plus component research, authoring, testing, i18n, and coverage
- **3 indexed knowledge catalogs**: `cells-components-catalog` (SQLite FTS5), `cells-official-docs-catalog` (SQLite FTS5), and `cells-visual-intent-demo`
- **Catalog-first evidence routing**: component discovery via SQL, documentation via official-docs catalog, with deterministic fallback order
- **Mandatory Cells testing stack**: `cells-cli-usage` → `cells-coverage` → `cells-test-creator` (never skip or reorder)
- **Engram-first persistence** with openspec/hybrid/none modes
- **Cells-native command policy**: `/cells-*`, `cells app:*`, `cells lit-component:*` as canonical commands
- **Browser integration** via `agent-browser` skill with session reuse and CDP support
- **VS Code Copilot support** via official `.github` customizations: instructions, prompt files, custom agents, Agent Skills, hooks, and plugin manifest
- **Governance contracts** and policy matrix for evidence quality gates, fallback rules, and source decision tracing

#### Supported Hosts

| Tool | Support | Setup |
|------|---------|-------|
| OpenCode | Full (delegate/task) | `./scripts/setup.sh --agent opencode` |
| VS Code Copilot | Workspace customizations | `./scripts/install.sh --agent vscode` |

#### Project Structure

```
cells teams/
├── skills/                          Cells workflow and specialist skills + shared contracts
│   ├── _shared/                    Governance, workflow, persistence, routing contracts
│   ├── cells-init/                  Phase 1: detect stack + bootstrap persistence
│   ├── cells-explore/               Phase 2: investigate problem space
│   ├── cells-propose/               Create change proposal
│   ├── cells-spec/                  Write delta specifications
│   ├── cells-design/                Technical design and architecture
│   ├── cells-tasks/                 Task breakdown
│   ├── cells-apply/                 Implementation
│   ├── cells-verify/                Validation against spec
│   ├── cells-archive/               Close and persist
│   ├── cells-component-researcher/   Component API/events/CSS hooks lookup
│   ├── cells-component-authoring/    New component scaffold + evolution
│   ├── cells-composition-architect/  Feature composition strategy
│   ├── cells-feature-analyzer/      Reusable patterns from real implementations
│   ├── cells-app-architecture/      Feature structure, data managers, routing
│   ├── cells-cli-usage/             Canonical Cells CLI commands
│   ├── cells-coverage/              Coverage triage and reporting
│   ├── cells-test-creator/          Test authoring with OpenWC + Sinon
│   ├── cells-i18n/                  IntlMsg and locale parity
│   ├── cells-components-catalog/    SQLite FTS5: BBVA component metadata
│   ├── cells-official-docs-catalog/ SQLite FTS5: Cells official guidance
│   ├── cells-visual-intent-demo/
│   ├── agent-browser/               Browser automation skill
│   └── skill-registry/
├── examples/
│   ├── opencode/                   OpenCode config + commands
│   └── vscode/                    VS Code Copilot `.github` assets
├── docs/                           (this directory)
└── scripts/                        Setup, install, validation scripts
```

#### Skills Index

| Skill | Trigger | Path |
|-------|---------|------|
| `cells-init` | When initializing CELLS context or detecting project stack | [`skills/cells-init/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-init/SKILL.md) |
| `cells-explore` | When investigating a problem space, component, or change area | [`skills/cells-explore/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-explore/SKILL.md) |
| `cells-propose` | When creating a change proposal with intent and scope | [`skills/cells-propose/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-propose/SKILL.md) |
| `cells-spec` | When writing delta specifications with requirements and scenarios | [`skills/cells-spec/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-spec/SKILL.md) |
| `cells-design` | When producing technical design and architecture decisions | [`skills/cells-design/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-design/SKILL.md) |
| `cells-tasks` | When breaking work into concrete implementation tasks | [`skills/cells-tasks/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-tasks/SKILL.md) |
| `cells-apply` | When implementing planned tasks against spec and design | [`skills/cells-apply/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-apply/SKILL.md) |
| `cells-verify` | When validating implementation against requirements | [`skills/cells-verify/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-verify/SKILL.md) |
| `cells-archive` | When closing a completed change and archiving artifacts | [`skills/cells-archive/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-archive/SKILL.md) |
| `cells-component-researcher` | When discovering component APIs, events, CSS hooks, or usage patterns | [`skills/cells-component-researcher/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-component-researcher/SKILL.md) |
| `cells-component-authoring` | When creating or evolving a reusable Cells component package | [`skills/cells-component-authoring/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-component-authoring/SKILL.md) |
| `cells-composition-architect` | When composing features from existing Cells packages | [`skills/cells-composition-architect/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-composition-architect/SKILL.md) |
| `cells-feature-analyzer` | When analyzing real feature implementations for reusable patterns | [`skills/cells-feature-analyzer/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-feature-analyzer/SKILL.md) |
| `cells-app-architecture` | When working with feature structure, data managers, routing, or bridge | [`skills/cells-app-architecture/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-app-architecture/SKILL.md) |
| `cells-cli-usage` | When resolving which Cells CLI command to use | [`skills/cells-cli-usage/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-cli-usage/SKILL.md) |
| `cells-coverage` | When analyzing coverage reports or triaging failed tests | [`skills/cells-coverage/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-coverage/SKILL.md) |
| `cells-test-creator` | When authoring or updating tests using OpenWC and Sinon | [`skills/cells-test-creator/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-test-creator/SKILL.md) |
| `cells-i18n` | When working with IntlMsg, locale parity, or translation discipline | [`skills/cells-i18n/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/cells-i18n/SKILL.md) |
| `agent-browser` | When browser confirmation, capture, or automation is needed | [`skills/agent-browser/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/agent-browser/SKILL.md) |
| `skill-registry` | When generating or updating the skill registry for the project | [`skills/skill-registry/SKILL.md`](https://github.com/PixelDroid19/cells-agents/blob/4a54ab9660ad97e23a45e8a37b602cc09dba6147/skills/skill-registry/SKILL.md) |

# Architecture

Deep dive into how Cells Agent Bundle is structured. For quick start, see the [main README](../README.md).

---

## Where Cells Agent Bundle Fits

Cells Agent Bundle combines a host-neutral Cells core with generated adapters
for VS Code, Codex, and OpenCode. Specialist skills, indexed documentation
catalogs, and Cells-native command policies stay canonical; host packages are
rendered on demand.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────┐
│  ORCHESTRATOR (proportional coordinator and executor)      │
│                                                           │
│  Responsibilities:                                        │
│  • Execute fast/scoped work directly                    │
│  • Delegate only independent full-workflow slices       │
│  • Resolve persistence mode (none or openspec; memory optional) │
│  • Route intent to the correct specialist skill          │
│  • Ask for approval between phases                        │
│  • Track state: which artifacts exist, what's next        │
│  • Enforce Cells-native command policy                    │
│                                                           │
│  Context usage: MINIMAL (only state + summaries)          │
└──────────────┬───────────────────────────────────────────┘
               │
               │ delegate / task (host-specific)
               │
    ┌──────────┴──────────────────────────────────────────┐
    │                                                      │
    ▼          ▼          ▼         ▼         ▼           ▼
┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
│EXPLORE ││PROPOSE ││  SPEC  ││ DESIGN ││ TASKS  ││ APPLY  │ ...
│        ││        ││        ││        ││        ││        │
│ Fresh  ││ Fresh  ││ Fresh  ││ Fresh  ││ Fresh  ││ Fresh  │
│context ││context ││context ││context ││context ││context │
└───┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘
    │         │         │         │         │         │
    └─────────┴─────────┴────┬────┴─────────┴─────────┘
                             │
              (receive pre-resolved skill paths
               from the orchestrator's launch prompt)
                             │
                 ┌───────────▼───────────┐      ┌────────────────────┐
                 │    SUB-AGENT USES     │      │   SKILL REGISTRY   │
                 │   skills as directed  │      │                    │
                 │ • cells-cli-usage   │      │ • cells skills    │
                 │ • cells-components-   │      │   + paths         │
                 │   catalog            │      │ • project conven- │
                 │ • cells-official-    │      │   tions           │
                 │   docs-catalog       │      └────────────────────┘
                 └───────────────────────┘
```

---

## Capability Comparison

| Capability | Basic Subagents | Agent Teams Lite | Cells Agent Bundle |
|---|:---:|:---:|:---:|
| Delegate-only lead | — | ✅ | ✅ |
| DAG-based phase orchestration | — | ✅ | ✅ |
| Parallel phases (spec ∥ design) | — | ✅ | ✅ |
| Structured result envelope | — | ✅ | ✅ |
| Pluggable artifact store | — | ✅ | ✅ |
| **Cells specialist skills** | — | — | ✅ |
| **Indexed Cells documentation (SQLite FTS5)** | — | — | ✅ |
| **Cells-native command policy** | — | — | ✅ |
| **Catalog-first evidence routing** | — | — | ✅ |
| **Mandatory testing stack** | — | — | ✅ |
| **Browser automation integration** | — | — | ✅ |

---

## The Dependency Graph

```
                    proposal
                   (root node)
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
      specs                       design
   (requirements                (technical
    + scenarios)                 approach)
         │                           │
         └─────────────┬─────────────┘
                       │
                       ▼
                    tasks
                (implementation
                  checklist)
                       │
                       ▼
                    apply
                (write code)
                       │
                       ▼
                    verify
               (quality gate)
                       │
                       ▼
                   archive
              (merge specs,
               close change)
```

---

## Catalog-First Evidence Routing

Every decision follows a deterministic source priority:

| Intent class | Primary source | Deterministic fallback order |
|---|---|---|
| UI/component discovery | `cells-components-catalog` SQL lookup | `cells-official-docs-catalog` → project code/tests |
| Cells process/docs/CLI/testing/theming/i18n | `cells-official-docs-catalog` | `cells-components-catalog` → project code/tests |
| Test execution and coverage | `cells-cli-usage` → `cells-coverage` → `cells-test-creator` | escalate (no generic runner by default) |
| Browser-visible validation | `browser-testing-convention` + `agent-browser` | source-only evidence with explicit limitation note |

---

## Project Structure

```
cells teams/
├── README.md                          ← Project overview and quick start
├── AGENTS.md                         ← Skills index with triggers (THIS FILE IS THE INDEX)
├── LICENSE
├── skills/                           ← Cells workflow and specialist skills + shared contracts
│   ├── _shared/                      ← Shared conventions (referenced by all skills)
│   │   ├── cells-governance-contract.md
│   │   ├── cells-workflow-contract.md
│   │   ├── cells-policy-matrix.yaml
│   │   ├── cells-source-routing-contract.md
│   │   ├── persistence-contract.md
│   │   ├── engram-convention.md
│   │   ├── openspec-convention.md
│   │   ├── cells-conventions.md
│   │   ├── cells-official-reference.md
│   │   ├── browser-testing-convention.md
│   ├── cells-init/SKILL.md
│   ├── cells-explore/SKILL.md
│   ├── cells-propose/SKILL.md
│   ├── cells-spec/SKILL.md
│   ├── cells-design/SKILL.md
│   ├── cells-tasks/SKILL.md
│   ├── cells-apply/SKILL.md
│   ├── cells-verify/SKILL.md
│   ├── cells-archive/SKILL.md
│   ├── cells-component-authoring/SKILL.md
│   ├── cells-app-architecture/SKILL.md
│   ├── cells-cli-usage/SKILL.md
│   ├── cells-coverage/SKILL.md
│   ├── cells-test-creator/SKILL.md
│   ├── cells-i18n/SKILL.md
│   ├── cells-components-catalog/         ← SQLite FTS5: bbva_cells_components.db
│   ├── cells-official-docs-catalog/     ← SQLite FTS5: cells_official_docs.db
│   ├── agent-browser/SKILL.md
│   └── cells-cleanup/SKILL.md
├── docs/                              ← Deep-dive documentation
│   ├── architecture.md                 ← This file
│   ├── changelog.md                   ← Version history
│   └── (future: concepts.md, sub-agents.md, persistence.md)
├── examples/                           ← Config examples per tool
│   ├── opencode/
│   │   ├── opencode.json              ← OpenCode config (single mode)
│   │   ├── opencode.single.json
│   │   ├── opencode.multi.json
│   │   ├── commands/cells-*.md        ← Slash commands
│   │   └── plugins/
│   └── vscode/                        ← VS Code Copilot layered assets
│       ├── copilot-instructions.md
│       ├── instructions/
│       ├── prompts/                   ← `*.prompt.md`
│       ├── agents/                    ← `*.agent.md`
│       ├── hooks/
│       ├── scripts/
│       ├── plugin/
│       ├── docs/
│       └── skills/
└── scripts/
    ├── setup.sh                       ← Full setup: detect + install + configure
    ├── setup.ps1
    ├── install.sh                     ← Unified host installer
    └── install.ps1
```

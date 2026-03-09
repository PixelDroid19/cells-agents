<p align="center">
  <h1 align="center">Cells Agent Bundle</h1>
  <p align="center">
    <strong>OpenCode-first orchestration for BBVA Cells with skill-driven delegated runs</strong>
    <br />
    <em>An orchestrator + Cells specialists for structured feature development, indexed component research, architecture guidance, CLI usage, testing, and internal documentation lookup.</em>
    <br />
    <em>Portable local assets. Markdown-first. Works without external services.</em>
  </p>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#how-it-works">How It Works</a> &bull;
  <a href="#commands">Commands</a> &bull;
  <a href="#skills-and-delegation">Skills</a> &bull;
  <a href="#installation">Installation</a> &bull;
  <a href="#project-structure">Project Structure</a>
</p>

---

## The Problem

AI coding assistants are powerful, but they struggle with complex features:

- **Context overload** — Long conversations lead to compression, lost details, hallucinations
- **No structure** — "Build me dark mode" produces unpredictable results
- **No review gate** — Code gets written before anyone agrees on what to build
- **No memory** — Specs live in chat history that vanishes

## The Solution

This package is an OpenCode-first orchestration pattern for BBVA Cells work. A lightweight coordinator delegates real work through generic skill-driven runs based on `SKILL.md` files for SDD, component research, feature composition, indexed component discovery, architecture guidance, CLI usage, testing, and internal documentation lookup. Each delegated run starts with fresh context, reads the target skill first, executes one focused task, and returns a structured result grounded in real sources such as `custom-elements.json`, project code, tests, the bundled component catalog, the bundled official-docs catalog, and real feature repositories.

```
YOU: "I want to add CSV export to the app"

ORCHESTRATOR (delegate-only, minimal context):
  → launches EXPLORE delegated run  → returns: codebase analysis
  → shows you summary, you approve
  → launches PROPOSE delegated run  → returns: proposal artifact
  → launches SPEC delegated run     → returns: spec artifact
  → launches DESIGN delegated run   → returns: design artifact
  → launches TASKS delegated run    → returns: tasks artifact
  → shows you everything, you approve
  → launches APPLY delegated run    → returns: code written, tasks checked off
  → launches VERIFY delegated run   → returns: verification artifact
  → launches ARCHIVE delegated run  → returns: change closed
```

**The key insight**: the orchestrator NEVER does phase work directly. It only coordinates delegation, tracks state, and synthesizes summaries. This keeps the main thread small and stable.

### Persistence Is Pluggable

The workflow engine is storage-agnostic. Artifacts can be persisted in:

- `engram` (recommended default)
- `openspec` (file-based, optional)
- `hybrid` (both Engram + OpenSpec simultaneously)
- `none` (ephemeral, no persistence)

Default policy is conservative:

- If Engram is available, persist to Engram (recommended)
- If user explicitly asks for file artifacts, use `openspec`
- If user wants both cross-session recovery AND local files, use `hybrid`
- Otherwise use `none` (no writes)
- `openspec` and `hybrid` are NEVER chosen automatically — only when the user explicitly asks

Architecturally, this package follows the same Engram-first handling model across all supported tools:
- Engram is the canonical backend for artifact recovery and orchestrator state
- OpenSpec is file-based compatibility when local artifacts are explicitly requested
- Hybrid keeps Engram as primary and writes an OpenSpec mirror alongside it

### Quick Modes

Recommended defaults by use case:

```yaml
# Bundle storage policy
artifact_store:
  mode: engram      # Recommended: persistent, repo-clean
```

```yaml
# Privacy/local-only (no persistence)
artifact_store:
  mode: none
```

```yaml
# File artifacts in project (OpenSpec flow)
artifact_store:
  mode: openspec
```

```yaml
# Both backends: cross-session recovery + local files (uses more tokens)
artifact_store:
  mode: hybrid
```

---

## How It Works

### Architecture Overview

This bundle has four layers:

1. `examples/*` provide host-specific orchestrator prompts and OpenCode commands.
2. The orchestrator stays lean and only decides routing, persistence mode, approvals, and next steps.
3. Specialist behavior lives in `skills/cells-*/SKILL.md`.
4. Shared conventions and bundled catalogs provide deterministic evidence and retrieval.

```mermaid
graph TD
    U[User command] --> C[/cells-* command or host prompt/]
    C --> O[cells-orchestrator]
    O --> T[Generic Task or delegated run]
    T --> S[Read target SKILL.md]
    S --> E[Read evidence: code, tests, catalogs, official docs]
    E --> R[Return structured result]
    R --> O
    O --> U
    S -. persist .-> P[(engram | openspec | hybrid | none)]
```

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│  ORCHESTRATOR (your main agent — primary assistant, etc)  │
│                                                           │
│  Responsibilities:                                        │
│  • Detect when SDD is needed                              │
│  • Launch generic delegated runs                          │
│  • Show summaries to user                                 │
│  • Ask for approval between phases                        │
│  • Track state: which artifacts exist, what's next        │
│                                                           │
│  Context usage: MINIMAL (only state + summaries)          │
└──────────────┬───────────────────────────────────────────┘
               │
               │ Task / delegated run starts by reading SKILL.md
               │
    ┌──────────┴──────────────────────────────────────────┐
    │                                                      │
    ▼          ▼          ▼         ▼         ▼           ▼
┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
│EXPLORE ││PROPOSE ││  SPEC  ││ DESIGN ││ TASKS  ││ APPLY  │ ...
│        ││        ││        ││        ││        ││        │
│ Fresh  ││ Fresh  ││ Fresh  ││ Fresh  ││ Fresh  ││ Fresh  │
│context ││context ││context ││context ││context ││context │
└────────┘└────────┘└────────┘└────────┘└────────┘└────────┘
```

### Runtime Pattern

This bundle follows a canonical pattern based on a lean orchestrator plus skill-driven delegated runs:

1. The user selects the orchestrator agent, typically `cells-orchestrator`.
2. The user runs a command such as `/cells-init`, `/cells-component bbva-button-default`, or `/cells-new improve-card-detail-flow`.
3. The command hands control to the orchestrator.
4. The orchestrator delegates with a generic Task or delegated run.
5. That delegated run starts by reading the corresponding `SKILL.md`.
6. The skill decides what evidence to read, what artifacts to create, and what result envelope to return.
7. The orchestrator shows only the compact result, asks for approval when needed, and decides the next step.

This means there is **not** one JSON agent definition per skill. The installed skills define specialist behavior, while the orchestrator and commands provide the entry points and delegation flow.

### The Dependency Graph

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

### Delegated Run Result Contract

Each delegated skill run should return a structured payload with variable depth:

```json
{
  "status": "ok | warning | blocked | failed",
  "executive_summary": "short decision-grade summary",
  "detailed_report": "optional long-form analysis when needed",
  "artifacts": [
    {
      "name": "design",
      "store": "engram | openspec | hybrid | none",
      "ref": "observation-id | file-path | null"
    }
  ],
  "next_recommended": ["tasks"],
  "risks": ["optional risk list"]
}
```

`executive_summary` is intentionally short. `detailed_report` can be as long as needed for complex architecture work.

### Artifact Persistence (Optional)

When `openspec` mode is enabled, a change can produce a self-contained folder:

```
openspec/
├── config.yaml                        ← Project context (stack, conventions)
├── specs/                             ← Source of truth: how the system works TODAY
│   ├── auth/spec.md
│   ├── export/spec.md
│   └── ui/spec.md
└── changes/
    ├── add-csv-export/                ← Active change
    │   ├── proposal.md                ← WHY + SCOPE + APPROACH
    │   ├── specs/                     ← Delta specs (ADDED/MODIFIED/REMOVED)
    │   │   └── export/spec.md
    │   ├── design.md                  ← HOW (architecture decisions)
    │   └── tasks.md                   ← WHAT (implementation checklist)
    └── archive/                       ← Completed changes (audit trail)
        └── 2026-02-16-fix-auth/
```

---

## Quick Start

### 1. Install the skills and commands

```bash
git clone <your-repo>
cd <your-repo>
./scripts/install.sh
```

The installer copies shared conventions, all `cells-*` skills, and OpenCode slash commands.

### 2. Add the orchestrator to your agent

See [Installation](#installation) for your specific tool.

### 3. Use it

Open OpenCode in your project, switch to `cells-orchestrator`, and say:

```
/cells-init
```

Then inspect or plan:

```
/cells-component bbva-type-text
/cells-author bbva-balance-card
/cells-compose debit-card-detail
/cells-new improve-card-detail-flow
```

Use `/cells-component`, `/cells-author`, `/cells-compose`, and `/cells-feature` for research.
Use `/cells-init`, `/cells-new`, `/cells-ff`, `/cells-apply`, `/cells-verify`, and `/cells-archive` for workflow execution.

In OpenCode, the expected operating loop is:

1. Pick `cells-orchestrator` in the agent picker.
2. Run a slash command.
3. Let the orchestrator delegate to a generic run that reads the target skill.
4. Review the compact result.
5. Approve the next planning or implementation step when the workflow asks for it.

The component specialists can also use the local `cells-components-catalog` skill to search available BBVA packages, tags, attributes, events, and usage snippets through a bundled SQLite FTS5 index packaged inside this bundle.

The team now also includes a central official-reference layer in `skills/_shared/cells-official-reference.md` so agents can route themselves to the exact Cells architecture, CLI, testing, theming, or component docs they need without loading the whole documentation tree into context.

---

## Knowledge Sources

The bundle is designed to avoid loading broad Cells documentation trees into context by default. Instead, it routes work through compact local sources:

- `skills/_shared/cells-official-reference.md` as the top-level router
- `skills/cells-official-docs-catalog/` for normalized official guidance on architecture, CLI, testing, theming, packaging, demos, and runtime topics
- `skills/cells-components-catalog/` for indexed BBVA component discovery using bundled SQLite FTS5 assets
- project evidence such as `custom-elements.json`, package docs, tests, and real feature code

The default operating model is:

1. keep `engram` as the canonical memory and recovery layer
2. keep official docs and package docs indexed, not always loaded
3. read detailed source material only when a skill needs concrete evidence

---

## Commands

| Command | What It Does |
|---------|-------------|
| `/cells-init` | Initialize SDD context. Detects stack and bootstraps the active persistence backend. |
| `/cells-explore <topic>` | Investigate an idea. Reads codebase, compares approaches. No files created. |
| `/cells-new <name>` | Start a new change by delegating exploration + proposal through skill-driven runs. |
| `/cells-continue` | Run the next dependency-ready phase through delegated skill execution. |
| `/cells-ff <name>` | Fast-forward planning through delegated runs (proposal → specs → design → tasks). |
| `/cells-apply` | Implement tasks in batches. Checks off items as it goes. |
| `/cells-verify` | Validate implementation against specs. Reports CRITICAL / WARNING / SUGGESTION. |
| `/cells-archive` | Close a change and persist final state in the active artifact store. |
| `/cells-component <name>` | Research a BBVA Cells component using package docs, metadata, tests, changelog notes, and feature usage. |
| `/cells-author <name-or-topic>` | Decide reuse vs new component and plan or scaffold a reusable Cells component package with the correct CLI, docs, tests, and i18n flow. |
| `/cells-compose <topic>` | Propose how to assemble a feature/widget from existing Cells components, mixins, and patterns. |
| `/cells-feature <path-or-topic>` | Extract reusable composition, event, and testing patterns from a real feature repo. |
| `/cells-coverage <path-or-module>` | Triage coverage gaps and test-error artifacts using compact summaries instead of manual HTML report browsing. |
| `/cells-i18n <topic>` | Audit or implement Cells i18n runtime, locale parity, and `IntlMsg` setup across components, demos, and tests. |

### Example Flow

```
You: /cells-component bbva-button-default

AI:  Launching cells-component-researcher...
     ✓ Bundled component dossier found for bbva-button-default
     ✓ Internal official guidance consulted for composition and API rules
     ✓ Real usage found in feature repos
     ✓ Public props, events, and caveats summarized
     
You: /cells-author bbva-balance-card

AI:  Launching cells-component-authoring...
     ✓ Existing packages checked before creating a new component
     ✓ Correct local scaffold/docs/test commands resolved
     ✓ Public API, custom-elements.json, and test plan outlined

You: /cells-compose debit-card-detail-flow

AI:  Launching cells-composition-architect...
     ✓ Recommends bbva-header-main + bbva-button-default + bbva-type-text
     ✓ Documents scopedElements and event flow
     ✓ Suggests existing feature patterns to reuse

You: /cells-new improve-card-detail-flow

AI:  Launching `cells-explore` delegated run...
     ✓ Cells stack detected from package.json + custom-elements.json
     ✓ Affected widgets and test files identified

     Launching `cells-propose` delegated run...
     ✓ proposal.md created
       Intent: Improve debit-card detail flow using existing Cells composition patterns
       Scope: Widget composition, event handling, and tests
     
     Want me to continue with specs and design? (or review the proposal first)

You: Go ahead

AI:  ✓ specs/ui/spec.md — 3 requirements, 7 scenarios
     ✓ design.md — scopedElements approach, event wiring, existing package reuse
     ✓ tasks.md — 3 phases, 8 tasks aligned with component tests
     
     Ready to implement. Run /cells-apply to start.

You: /cells-apply

AI:  Implementing Phase 1 (Foundation)...
     ✓ 1.1 Created ThemeContext
     ✓ 1.2 Added CSS custom properties
     ✓ 1.3 Added localStorage persistence
     
     3/8 tasks complete. Continue with Phase 2?
```

---

## Skills And Delegation

Each specialist role is implemented as a `SKILL.md` file. In tools with real delegation support such as OpenCode and Claude Code, the orchestrator launches a generic Task or delegated run and instructs it to read the relevant skill first. In tools without true Task delegation, the orchestrator can still execute the same skill inline.

| Role | Skill File | What It Does |
|-----------|-----------|-------------|
| **Init** | `cells-init/SKILL.md` | Detects project stack, creates `openspec/` structure |
| **Explorer** | `cells-explore/SKILL.md` | Reads codebase, compares approaches, identifies risks |
| **Proposer** | `cells-propose/SKILL.md` | Creates `proposal.md` with intent, scope, rollback plan |
| **Spec Writer** | `cells-spec/SKILL.md` | Writes delta specs (ADDED/MODIFIED/REMOVED) with Given/When/Then |
| **Designer** | `cells-design/SKILL.md` | Creates `design.md` with architecture decisions and rationale |
| **Task Planner** | `cells-tasks/SKILL.md` | Breaks down into phased, numbered task checklist |
| **Implementer** | `cells-apply/SKILL.md` | Writes code following specs and design, marks tasks complete. v2.0: TDD workflow support |
| **Verifier** | `cells-verify/SKILL.md` | Validates implementation against specs with real test execution. v2.0: spec compliance matrix |
| **Archiver** | `cells-archive/SKILL.md` | Merges delta specs into main specs, moves to archive |
| **Cells Component Researcher** | `cells-component-researcher/SKILL.md` | Extracts component API, events, style hooks, changelog notes, and real usage evidence |
| **Cells Component Authoring** | `cells-component-authoring/SKILL.md` | Decides reuse vs new component and plans the correct scaffold, docs, test, and package flow for reusable Cells components |
| **Cells Components Catalog** | `cells-components-catalog/SKILL.md` | Searches the local BBVA component catalog with SQLite FTS5 to discover packages, tags, attributes, events, and snippets quickly |
| **Cells Official Docs Catalog** | `cells-official-docs-catalog/SKILL.md` | Searches the internal normalized Cells guidance catalog for architecture, CLI, testing, authoring, demos, theming, and packaging rules |
| **Cells Composition Architect** | `cells-composition-architect/SKILL.md` | Chooses the best composition strategy from existing Cells components and patterns |
| **Cells Feature Analyzer** | `cells-feature-analyzer/SKILL.md` | Extracts reusable patterns from real BBVA feature repositories |
| **Cells App Architecture** | `cells-app-architecture/SKILL.md` | Explains official feature, data-manager, bridge, and routing patterns for Cells apps |
| **Cells CLI Usage** | `cells-cli-usage/SKILL.md` | Resolves the correct local Cells CLI or NPM command flow without guessing or assuming global installs |
| **Cells Coverage** | `cells-coverage/SKILL.md` | Triages `lcov` coverage and test-failure artifacts with compact deterministic summaries |
| **Cells i18n** | `cells-i18n/SKILL.md` | Guides `this.t(...)`, locale parity, and deterministic `IntlMsg` setup in runtime, demos, and tests |
| **Cells Test Creator** | `cells-test-creator/SKILL.md` | Creates or improves Cells tests with OpenWC + Sinon, public-behavior rules, and coverage discipline |

### Shared Conventions

The SDD and Cells specialist skills reference shared convention files in `skills/_shared/` instead of inlining repeated logic. This removes duplication and keeps OpenCode routing consistent.

| File | Purpose |
|------|---------|
| `persistence-contract.md` | Mode resolution rules — how `engram`, `openspec`, `hybrid`, and `none` modes behave, what each mode reads/writes, and the fallback policy |
| `cells-conventions.md` | Source priority and evidence rules for BBVA Cells projects: package docs, metadata, tests, Components Studio, and real feature repos |
| `cells-official-reference.md` | Central routing map to official Cells docs for architecture, CLI, testing, theming, packaging, demos, and component API without inflating context |
| `cells-official-docs-catalog/` | Internal SQLite-backed knowledge base with normalized official Cells guidance, fully contained inside this bundle |
| `engram-convention.md` | Deterministic artifact naming (`cells/{change-name}/{artifact-type}`), two-step recovery protocol (search then get full content), and write/update patterns via `topic_key` upserts |
| `openspec-convention.md` | Filesystem paths for each artifact, directory structure, config.yaml reference, and archive layout |

**Why they exist:**
- **DRY** — Previously each skill inlined its own persistence logic (~224 lines of duplication across 9 skills). Now each skill references the shared files.
- **Deterministic recovery** — Engram artifact naming follows a strict `cells/{change}/{type}` convention with `topic_key`, so any skill can reliably find artifacts created by other skills without fuzzy search.
- **Consistent mode behavior** — All skills resolve `engram | openspec | hybrid | none` the same way. `openspec` and `hybrid` are never chosen automatically.
- **Official-doc routing** — Agents can consult only the exact Cells docs they need for the current task instead of loading broad documentation trees or relying on generic frontend assumptions.
- **Canonical OpenSpec layout** — OpenSpec artifacts use one canonical filesystem structure across the workflow.
- **Self-contained component workflow** — The core architecture depends only on the installed skills and bundled catalogs.

### Key Capabilities

- **SDD workflow** — proposal, spec, design, tasks, apply, verify, and archive phases
- **Component discovery** — indexed search over bundled BBVA package records
- **Official guidance routing** — compact lookup over normalized Cells docs
- **Architecture support** — feature structure, data managers, routing, bridge, and composition patterns
- **Quality support** — coverage triage, i18n validation, and test creation guidance

---

## Installation

Dedicated setup guides for all supported tools:

- [Claude Code](#claude-code) — Full Task-based delegated execution
- [OpenCode](#opencode) — Full Task-based delegated execution
- [Gemini CLI](#gemini-cli) — Inline skill execution
- [Codex](#codex) — Inline skill execution
- [VS Code (Copilot)](#vs-code-copilot) — Agent mode with context files
- [Antigravity](#antigravity) — Native skill support with `~/.gemini/antigravity/skills/` and `.agent/` paths
- [Cursor](#cursor) — Inline skill execution

### Claude Code

**1. Copy skills:**

```bash
# Using the install script
./scripts/install.sh  # Choose option 1: Claude Code

# Or manually
cp -r skills/_shared skills/cells-* ~/.claude/skills/
```

**2. Add orchestrator to `~/.claude/CLAUDE.md`:**

Append the contents of [`examples/claude-code/CLAUDE.md`](examples/claude-code/CLAUDE.md) to your existing `CLAUDE.md`.

The example is intentionally lean to avoid token bloat in always-loaded system prompts. Detailed persistence and artifact rules live in `~/.claude/skills/_shared/*.md`.

This keeps your existing assistant identity and adds SDD as an orchestration overlay.

The orchestrator instructions teach Claude Code to:
- Detect workflow triggers (`/cells-new`, feature descriptions, etc.)
- Launch generic Task runs
- Pass skill file paths so delegated runs read their instructions first
- Track state between phases

**3. Verify:**

Open Claude Code and type `/cells-init` — it should recognize the command.

---

### OpenCode

**1. Copy skills and commands:**

```bash
# Using the install script (installs both skills + commands)
./scripts/install.sh  # Choose option 2: OpenCode

# Or manually
cp -r skills/_shared skills/cells-* ~/.config/opencode/skills/
cp examples/opencode/commands/*.md ~/.config/opencode/commands/
```

**2. Add orchestrator agent to `~/.config/opencode/opencode.json`:**

Merge the `agent` block from [`examples/opencode/opencode.json`](examples/opencode/opencode.json) into your existing config.

You can either:
- **Add it to your existing agent** (e.g., append SDD orchestrator instructions to your primary agent's prompt)
- **Create a dedicated agent** (copy the `cells-orchestrator` agent definition as-is)

Recommended OpenCode setup:
- Keep your everyday assistant as `primary`
- Set `cells-orchestrator` to `all`
- Select `cells-orchestrator` when you want Cells-aware workflows
- Use `/cells-component` and `/cells-compose` before `/cells-new` when the task starts from component research

Operationally, OpenCode should be understood as:
- one orchestrator agent entry
- slash commands as workflow triggers
- generic Task delegation
- skill-driven specialist behavior

**3. Verify:**

Open OpenCode and type `/cells-init` — it should recognize the command.

How to use in OpenCode:
- Start OpenCode in your project: `opencode .`
- Use the agent picker (Tab) and choose `cells-orchestrator`
- Run workflow commands: `/cells-init`, `/cells-new <name>`, `/cells-apply`, etc.
- Run Cells commands: `/cells-component <name>`, `/cells-compose <topic>`, `/cells-feature <path>`
- Commands are installed at `~/.config/opencode/commands/` and auto-discovered by OpenCode
- Switch back to your normal agent (Tab) for day-to-day coding

When a command runs, the expected internal flow is:
1. the command invokes `cells-orchestrator`
2. `cells-orchestrator` delegates the work
3. the delegated run reads `~/.config/opencode/skills/cells-*/SKILL.md`
4. the skill returns a structured result envelope
5. the orchestrator decides whether to continue, ask approval, or stop

---

### Gemini CLI

**1. Copy skills:**

```bash
# Using the install script
./scripts/install.sh  # Choose Gemini CLI option

# Or manually
cp -r skills/_shared skills/cells-* ~/.gemini/skills/
```

**2. Add orchestrator to `~/.gemini/GEMINI.md`:**

Append the contents of [`examples/gemini-cli/GEMINI.md`](examples/gemini-cli/GEMINI.md) to your Gemini system prompt file (create it if it doesn't exist).

Make sure `GEMINI_SYSTEM_MD=1` is set in `~/.gemini/.env` so Gemini loads the system prompt.

**3. Verify:**

Open Gemini CLI and type `/cells-init` — it should recognize the command.

> **Note:** Gemini CLI doesn't have a native Task tool for delegated fresh-context runs. The skills work as inline instructions, so the orchestrator reads them directly.

---

### Codex

**1. Copy skills:**

```bash
# Using the install script
./scripts/install.sh  # Choose Codex option

# Or manually
cp -r skills/_shared skills/cells-* ~/.codex/skills/
```

**2. Add orchestrator instructions:**

Add the orchestrator instructions to `~/.codex/agents.md` (or your `model_instructions_file` if configured).

**3. Verify:**

Open Codex and type `/cells-init`.

> **Note:** Like Gemini CLI, Codex runs skills inline rather than through fresh-context delegated runs. The planning phases still work well; batching behavior comes from the orchestrator instructions.

---

### VS Code (Copilot)

VS Code supports MCP and custom instructions natively. The skills work with Copilot's agent mode and any MCP-compatible extension.

**1. Copy skills to workspace:**

```bash
# Per-project (recommended)
cp -r skills/_shared skills/cells-* ./your-project/.vscode/skills/

# Or using the install script
./scripts/install.sh  # Choose VS Code option
```

**2. Add orchestrator instructions:**

Create a VS Code `.instructions.md` file in the User prompts folder and append the orchestrator instructions from [`examples/vscode/copilot-instructions.md`](examples/vscode/copilot-instructions.md).

Recommended User prompt path:
- macOS: `~/Library/Application Support/Code/User/prompts/cells-orchestrator.instructions.md`
- Linux: `~/.config/Code/User/prompts/cells-orchestrator.instructions.md`
- Windows: `%APPDATA%\Code\User\prompts\cells-orchestrator.instructions.md`

Alternatively, use VS Code's custom instructions setting:
1. Open Settings (`Cmd+,` / `Ctrl+,`)
2. Search for `github.copilot.chat.codeGeneration.instructions`
3. Add the SDD orchestrator instructions

If you also configure MCP at user level, use:
- macOS: `~/Library/Application Support/Code/User/mcp.json`
- Linux: `~/.config/Code/User/mcp.json`
- Windows: `%APPDATA%\Code\User\mcp.json`

**3. Verify:**

Open VS Code, open the Chat panel (Ctrl+Cmd+I / Ctrl+Alt+I), and type `/cells-init`.

> **Note:** VS Code Copilot supports agent mode with tool use. Skills work as context files. For fresh-context delegated execution, use Claude Code or OpenCode.

---

### Antigravity

[Antigravity](https://antigravity.google) is Google's AI-first IDE with native skill support. It has its own skill and rule system separate from VS Code.

**1. Copy skills:**

```bash
# Global (available across all projects)
./scripts/install.sh  # Choose Antigravity option

# Or manually (global)
cp -r skills/_shared skills/cells-* ~/.gemini/antigravity/skills/

# Workspace-specific (per project)
mkdir -p .agent/skills
cp -r skills/_shared skills/cells-* .agent/skills/
```

**2. Add orchestrator instructions:**

Add the Cells orchestrator as a global rule in `~/.gemini/GEMINI.md`, or create a workspace rule in `.agent/rules/cells-orchestrator.md`.

See [`examples/antigravity/cells-orchestrator.md`](examples/antigravity/cells-orchestrator.md) for the rule content.

**3. Verify:**

Open Antigravity and type `/cells-init` in the agent panel.

> **Note:** Antigravity uses `.agent/skills/` and `.agent/rules/` for workspace config, and `~/.gemini/antigravity/skills/` for global. It does NOT use `.vscode/` paths.

---

### Cursor

**1. Copy skills to project or global:**

```bash
# Global
./scripts/install.sh  # Choose option 7: Cursor

# Or per-project
cp -r skills/_shared skills/cells-* ./your-project/skills/
```

**2. Add orchestrator to `.cursorrules`:**

Append the contents of [`examples/cursor/.cursorrules`](examples/cursor/.cursorrules) to your project's `.cursorrules` file.

**Note:** Cursor doesn't have a Task tool for true delegated fresh-context execution. The skills still work, but the orchestrator runs inline rather than delegating to separate runs.

---

### Other Tools

The skills are pure Markdown. Any AI assistant that can read files can use them.

**1. Copy skills** to wherever your tool reads instructions from.

**2. Add orchestrator instructions** to your tool's system prompt or rules file.

**3. Adapt the delegation pattern:**
- If your tool has a Task or delegated-run mechanism → use the pattern from `examples/claude-code/CLAUDE.md`
- If not → the orchestrator reads the skills inline (still works, just uses more context)

---

## Persistence Model

The bundle supports four persistence modes:

- `engram` as the recommended default for canonical recovery and orchestrator state
- `openspec` when the user explicitly wants file artifacts in the repository
- `hybrid` when both Engram recovery and OpenSpec file output are required
- `none` for ephemeral or privacy-first usage

The project is optimized for `engram` first:

- the orchestrator and skills assume Engram is the primary recovery backend
- OpenSpec remains a compatible file layout, not the default source of truth
- detailed docs and package data stay indexed and are read on demand instead of bloating context

---

## Project Structure

```
<repo-root>/
├── README.md                          ← You are here
├── LICENSE
├── skills/                            ← SDD skills, Cells specialists, catalogs, and shared conventions
│   ├── _shared/                       ← Shared conventions (referenced by all skills)
│   │   ├── cells-conventions.md       ← Cells evidence rules and source priority
│   │   ├── cells-official-reference.md← Compact router to official Cells knowledge
│   │   ├── persistence-contract.md    ← Mode resolution rules (engram/openspec/hybrid/none)
│   │   ├── engram-convention.md       ← Deterministic naming & recovery protocol
│   │   └── openspec-convention.md     ← File paths, directory structure, config reference
│   ├── cells-app-architecture/SKILL.md
│   ├── cells-cli-usage/SKILL.md
│   ├── cells-component-researcher/SKILL.md
│   ├── cells-component-authoring/SKILL.md
│   ├── cells-components-catalog/      ← Bundled SQLite FTS5 component index + scripts
│   ├── cells-composition-architect/SKILL.md
│   ├── cells-coverage/SKILL.md
│   ├── cells-feature-analyzer/SKILL.md
│   ├── cells-i18n/SKILL.md
│   ├── cells-init/SKILL.md
│   ├── cells-explore/SKILL.md
│   ├── cells-official-docs-catalog/   ← Bundled normalized official Cells docs index
│   ├── cells-propose/SKILL.md
│   ├── cells-spec/SKILL.md
│   ├── cells-design/SKILL.md
│   ├── cells-tasks/SKILL.md
│   ├── cells-test-creator/SKILL.md
│   ├── cells-apply/SKILL.md
│   ├── cells-verify/SKILL.md
│   └── cells-archive/SKILL.md
├── examples/                          ← Config examples per tool
│   ├── claude-code/CLAUDE.md
│   ├── opencode/
│   │   ├── opencode.json              ← Orchestrator agent config
│   │   └── commands/*.md              ← `/cells-*` commands for OpenCode
│   ├── gemini-cli/GEMINI.md
│   ├── codex/agents.md
│   ├── vscode/copilot-instructions.md
│   ├── antigravity/cells-orchestrator.md
│   └── cursor/.cursorrules
└── scripts/
    ├── install.sh                     ← Cross-platform installer
    └── install.ps1                    ← Native PowerShell installer
```

---

## Concepts

### Delta Specs

Instead of rewriting entire specs, changes describe what's different:

```markdown
## ADDED Requirements

### Requirement: CSV Export
The system SHALL support exporting data to CSV format.

#### Scenario: Export all observations
- GIVEN the user has observations stored
- WHEN the user requests CSV export
- THEN a CSV file is generated with all observations
- AND column headers match the observation fields

## MODIFIED Requirements

### Requirement: Data Export
The system SHALL support multiple export formats.
(Previously: The system SHALL support JSON export.)
```

When the change is archived, these deltas merge into the main specs automatically.

### RFC 2119 Keywords

Specs use standardized language for requirement strength:

| Keyword | Meaning |
|---------|---------|
| **MUST / SHALL** | Absolute requirement |
| **SHOULD** | Recommended, exceptions may exist |
| **MAY** | Optional |

### The Archive Cycle

```
1. Specs describe current behavior
2. Changes propose modifications (as deltas)
3. Implementation makes changes real
4. Archive merges deltas into specs
5. Specs now describe the new behavior
6. Next change builds on updated specs
```

---

## Contributing

PRs welcome. The skills are Markdown — easy to improve.

**To add a new skill-driven role:**
1. Create `skills/cells-{name}/SKILL.md` following the existing format
2. Add it to the dependency graph in the orchestrator instructions
3. Update the examples and README

**To improve an existing role:**
1. Edit the `SKILL.md` directly
2. Test by running SDD in a real project
3. Submit PR with before/after examples

---

## License

MIT

---

<p align="center">
  <strong>Built for portable AI-assisted development</strong>
  <br />
  <em>Because building without a plan is just vibe coding with extra steps.</em>
</p>

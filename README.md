<p align="center">
  <h1 align="center">Cells Agent Bundle</h1>
  <p align="center">
    <strong>OpenCode-first orchestration for BBVA Cells using skill-driven delegated runs</strong>
    <br />
    <em>Portable local assets. Indexed documentation. Engram-first persistence. Markdown-based skills.</em>
  </p>
</p>

<p align="center">
  <a href="#overview">Overview</a> &bull;
  <a href="#architecture">Architecture</a> &bull;
  <a href="#knowledge-model">Knowledge Model</a> &bull;
  <a href="#commands">Commands</a> &bull;
  <a href="#skills">Skills</a> &bull;
  <a href="#installation">Installation</a> &bull;
  <a href="#project-structure">Project Structure</a>
</p>

---

## Overview

`Cells Agent Bundle` is a portable bundle of orchestrator prompts, slash commands, shared conventions, and specialist `SKILL.md` files for working on BBVA Cells projects.

The bundle is designed for these jobs:

- plan and execute Spec-Driven Development flows
- research existing BBVA components before inventing new APIs
- compose features from existing Cells building blocks
- query official Cells guidance without loading full docs trees into context
- guide CLI usage, testing, coverage, i18n, and component authoring

The key design goal is simple: keep the orchestrator lean, keep documentation indexed, and load detailed evidence only when a skill actually needs it.

## Architecture

### Core Model

The bundle uses a four-layer architecture:

1. Host integration layer: `examples/*` contains prompts, rules, and OpenCode commands for each supported host.
2. Orchestrator layer: a single lean orchestrator routes work, resolves persistence mode, tracks state, and asks for approvals.
3. Skill layer: specialist behavior lives in `skills/cells-*/SKILL.md`.
4. Knowledge layer: shared conventions plus bundled catalogs provide deterministic retrieval and evidence.

### Execution Flow

The canonical flow is:

1. The user selects the orchestrator, usually `cells-orchestrator`.
2. The user runs a workflow or research command such as `/cells-init` or `/cells-component bbva-button-default`.
3. The host command or prompt hands control to the orchestrator.
4. The orchestrator launches a generic delegated run.
5. That delegated run starts by reading the relevant `SKILL.md`.
6. The skill decides which evidence to inspect: code, tests, package docs, official docs, indexed catalogs, or persistence artifacts.
7. The skill returns a structured result envelope.
8. The orchestrator summarizes, asks for approval if needed, and selects the next step.

### Conservative Execution Policy

The bundle should not execute the project, dev server, or full test suite for every small change.

Default policy:

- use code, docs, indexed catalogs, and existing runtime context first
- keep small low-risk changes lightweight
- run project commands only when confirmation is needed
- prefer targeted tests and targeted browser confirmation over full-project execution
- reserve broader execution for verification, risky changes, integration work, or explicit user requests

Cells command policy:

- for Cells app/theme orchestration, keep Cells-native commands canonical (`/cells-*`, `cells app:*`, `cells lit-component:*`)
- canonical Cells command set:
  - workflow: `/cells-init`, `/cells-explore`, `/cells-new`, `/cells-continue`, `/cells-ff`, `/cells-apply`, `/cells-verify`, `/cells-archive`
  - app: `cells app:serve -c <config>`, `cells app:build -c <config>`, `cells app:test`, `cells app:lint`, `cells app:install`, `cells app:create`
  - component: `cells lit-component:create`, `cells lit-component:serve`, `cells lit-component:test`, `cells lit-component:lint`, `cells lit-component:locales`, `cells lit-component:documentation`
- do not default to generic external commands (`npm run *`, `npm test`, `npx web-test-runner`) unless the user explicitly requests a non-Cells path
- if command ownership is unclear, ask before running a non-Cells command

Mandatory Cells testing stack policy:

- for any Cells test intent (how to run tests, test execution, coverage, test creation, or test updates), consult skills in this exact order before any other testing source:
  1. `skills/cells-cli-usage/` (canonical test commands and invocation)
  2. `skills/cells-coverage/` (coverage thresholds and reporting strategy)
  3. `skills/cells-test-creator/` (test design, creation, and update patterns)
- do not skip or reorder this stack
- do not reintroduce generic testing fallbacks (`npm test`, `npm run test`, `npx web-test-runner`) in Cells contexts

Intent routing policy:

- UI/component discovery and element selection -> run SQL/database-backed lookup first with `python skills/cells-components-catalog/scripts/search_docs.py --query "<intent>"` against `skills/cells-components-catalog/assets/bbva_cells_components.db` (do not guess from memory)
- any Cells documentation/knowledge lookup (variables, workflows, tests, architecture, CLI, authoring, theming, i18n, and related Cells topics) -> use `skills/cells-official-docs-catalog` first
- consult the other catalog only as fallback when the first one is insufficient

### Runtime Diagram

```text
User
  -> host prompt or /cells-* command
  -> cells-orchestrator
  -> generic delegated run
  -> read target SKILL.md
  -> inspect evidence and conventions
  -> return structured result
  -> orchestrator summary and next action
```

### Result Contract

Every delegated run should return the same decision-friendly structure:

```json
{
  "status": "ok | warning | blocked | failed",
  "executive_summary": "short summary for the orchestrator",
  "detailed_report": "optional long-form analysis when needed",
  "artifacts": [
    {
      "name": "proposal | spec | design | tasks | report",
      "store": "engram | openspec | hybrid | none",
      "ref": "observation-id | file-path | null"
    }
  ],
  "next_recommended": ["cells-spec", "cells-design"],
  "risks": ["optional risk list"]
}
```

## Knowledge Model

### Default Recommendation

Use `engram` as the default persistence and recovery backend.

Recommended policy:

- `engram` is the canonical backend for orchestrator state and artifact recovery.
- `openspec` is only for explicit file-artifact workflows.
- `hybrid` is for cases where both Engram recovery and OpenSpec files are required.
- `none` is for ephemeral or privacy-first sessions.

### What Loads By Default

The bundle is intentionally optimized to avoid loading full documentation trees into context by default.

Default always-available knowledge should be compact:

- shared conventions in `skills/_shared/`
- the official-docs router in `skills/_shared/cells-official-reference.md`
- indexed official guidance in `skills/cells-official-docs-catalog/`
- indexed BBVA component metadata in `skills/cells-components-catalog/`
- project-local evidence such as `custom-elements.json`, tests, package docs, and source code

### Browser And Runtime Reuse

When browser confirmation is needed:

- reuse the existing dev server host and port if one is already running
- reuse the existing `agent-browser` session, browser, route, and CDP port when possible
- prefer `agent-browser connect <port>` or `agent-browser --auto-connect` over launching a fresh browser when a reusable browser already exists
- prefer a global `agent-browser` command when it is already installed
- fall back to `npx agent-browser` only when it is already available
- do not install `agent-browser`, Chromium, or other dependencies unless the user explicitly asks

### Recommended Source Priority

For Cells documentation, this is the recommended priority order:

1. normalized topics in `skills/cells-official-docs-catalog/`
2. `cellsjs-guides-resources-master@d3ad8b11218/docs-next`
3. `cellsjs-guides-resources-master@d3ad8b11218/docs`
4. `docs/packages`
5. project-local code and tests as runtime evidence

### Why This Order

- `docs-next` should be treated as the preferred source for modern guidance.
- `docs` is useful as fallback or compatibility material.
- `docs/packages` should not be preloaded as raw markdown. It is better consumed through the bundled component catalog and package-level evidence.
- project code remains the final behavioral truth when docs and implementation differ.

### How `docs/packages` Should Be Used

Do not load all package documentation into the prompt by default.

Instead:

- index package names, tags, classes, attributes, events, slots, and short usage snippets
- store compact searchable records
- open the original package files only when the active skill needs exact evidence

That is exactly why this bundle includes `cells-components-catalog` with bundled SQLite FTS5 assets.

## Persistence Modes

```yaml
artifact_store:
  mode: engram
```

Use the following modes:

- `engram`: best default for long-running work, compact state recovery, and low repo noise
- `openspec`: use when the user explicitly wants file artifacts inside the repository
- `hybrid`: use when both Engram recovery and OpenSpec files are required
- `none`: use when nothing should be persisted

Mode-selection policy:

- choose `engram` automatically when available
- never choose `openspec` or `hybrid` automatically
- only use `openspec` or `hybrid` when the user explicitly asks for file artifacts

## Commands

### Workflow Commands

| Command | Purpose |
|---|---|
| `/cells-init` | Detect stack, identify Cells context, and initialize the active persistence backend. |
| `/cells-explore <topic>` | Investigate a topic or change area without committing to implementation. |
| `/cells-new <change>` | Start a new change by running exploration and proposal creation. |
| `/cells-continue [change]` | Advance to the next dependency-ready phase. |
| `/cells-ff <change>` | Fast-forward planning through proposal, spec, design, and tasks. |
| `/cells-apply [change]` | Implement planned tasks in batches. |
| `/cells-verify [change]` | Validate implementation against requirements and execution evidence. |
| `/cells-archive [change]` | Close a completed change and sync final state. |

### Cells Specialist Commands

| Command | Purpose |
|---|---|
| `/cells-component <name>` | Research a BBVA Cells component using package docs, metadata, tests, and real usage. |
| `/cells-author <name-or-topic>` | Decide reuse vs new component and plan the correct authoring flow. |
| `/cells-compose <topic>` | Design feature composition from existing Cells components and patterns. |
| `/cells-feature <path-or-topic>` | Extract reusable patterns from real feature repos. |
| `/cells-coverage <path-or-module>` | Triage coverage gaps and test-failure artifacts. |
| `/cells-i18n <topic>` | Audit or implement Cells i18n runtime and locale discipline. |

### Canonical OpenCode Usage

In OpenCode, the intended operating loop is:

1. install the skills and commands
2. add the `cells-orchestrator` agent block from `examples/opencode/opencode.json`
3. switch to `cells-orchestrator`
4. run `/cells-init`
5. use specialist commands first when the task starts from research
6. use SDD workflow commands when the task moves into planning and implementation

A common flow looks like this:

```text
/cells-component bbva-button-default
/cells-compose debit-card-detail-flow
/cells-new improve-card-detail-flow
/cells-apply
/cells-verify
/cells-archive
```

## Skills

### SDD Skills

| Skill | Responsibility |
|---|---|
| `cells-init` | Detect stack, conventions, and persistence setup. |
| `cells-explore` | Investigate problem space, affected files, and risks. |
| `cells-propose` | Create proposal scope, intent, and rollback framing. |
| `cells-spec` | Write delta specs with requirements and scenarios. |
| `cells-design` | Produce implementation design and architecture decisions. |
| `cells-tasks` | Break work into concrete phased tasks. |
| `cells-apply` | Implement code changes against plan and specs. |
| `cells-verify` | Validate behavioral compliance with real evidence. |
| `cells-archive` | Finalize the change and sync source-of-truth artifacts. |

### Cells Specialist Skills

| Skill | Responsibility |
|---|---|
| `cells-component-researcher` | Component API, events, style hooks, docs, tests, and usage evidence. |
| `cells-component-authoring` | Reuse vs new component decisions, scaffold flow, docs, and tests. |
| `cells-composition-architect` | Feature and widget composition strategy from existing packages. |
| `cells-feature-analyzer` | Reusable patterns from real BBVA feature implementations. |
| `cells-app-architecture` | Feature structure, data managers, routing, bridge, and communication guidance. |
| `cells-cli-usage` | Correct local CLI or npm-based command flow. |
| `cells-coverage` | Coverage triage and failed-test artifact analysis (second in mandatory testing stack). |
| `cells-test-creator` | Test authoring guidance using OpenWC, Sinon, and public-behavior rules (third in mandatory testing stack). |
| `cells-i18n` | `IntlMsg`, locale parity, and deterministic translation discipline. |

### Catalog And Reference Skills

| Skill | Responsibility |
|---|---|
| `cells-components-catalog` | Indexed discovery of BBVA component metadata and snippets via bundled SQLite FTS5 assets. |
| `cells-official-docs-catalog` | Indexed lookup of normalized official Cells guidance. |

### Shared Conventions

`skills/_shared/` contains the compact rules used across skills:

- `cells-conventions.md`
- `cells-official-reference.md`
- `engram-convention.md`
- `openspec-convention.md`
- `persistence-contract.md`

These files keep repeated logic out of individual skills and make routing deterministic.

## Installation

### Quick Install

On Unix-like shells:

```bash
./scripts/install.sh
```

On Windows PowerShell:

```powershell
.\scripts\install.ps1
```

### Supported Hosts

- OpenCode
- Claude Code
- Gemini CLI
- Codex
- VS Code Copilot
- Antigravity
- Cursor
- project-local installs

### OpenCode

1. Install skills to `~/.config/opencode/skills/`.
2. Install commands to `~/.config/opencode/commands/`.
3. Merge the `cells-orchestrator` agent block from `examples/opencode/opencode.json` into your OpenCode config.
4. Start OpenCode and switch to `cells-orchestrator`.
5. Run `/cells-init`.

Troubleshooting (`database table is locked`):

- This usually means another suspended OpenCode process is still holding the local DB lock.
- Close OpenCode sessions, then check active processes (`ps aux | grep opencode` on macOS/Linux, `Get-Process opencode` on Windows).
- Stop stale processes (`pkill -f opencode` or `Stop-Process -Name opencode -Force`), then start OpenCode again.
- Avoid leaving suspended OpenCode sessions running in the background.

### Claude Code

1. Copy `skills/_shared` and all `skills/cells-*` directories to `~/.claude/skills/`.
2. Append `examples/claude-code/CLAUDE.md` to `~/.claude/CLAUDE.md`.
3. Start with `/cells-init`.

### Gemini CLI

1. Copy the bundle to `~/.gemini/skills/`.
2. Append `examples/gemini-cli/GEMINI.md` to your Gemini system prompt file.
3. Skills execute inline because Gemini CLI does not provide the same delegated-run mechanism as OpenCode.

### Codex

1. Copy the bundle to `~/.codex/skills/`.
2. Add `examples/codex/agents.md` to your Codex instructions.
3. Skills execute inline.

### VS Code Copilot

1. Copy the bundle to workspace or user instruction locations.
2. Use `examples/vscode/copilot-instructions.md` as the orchestrator instructions source.
3. Skills act as context files rather than separate delegated runs.

### Antigravity

1. Install globally to `~/.gemini/antigravity/skills/` or per-project to `.agent/skills/`.
2. Add the orchestrator rule from `examples/antigravity/cells-orchestrator.md`.

### Cursor

1. Install globally to `~/.cursor/skills/` or per-project to `./skills/`.
2. Append `examples/cursor/.cursorrules` to your Cursor rules.
3. Skills execute inline.

## Project Structure

```text
<repo-root>/
|-- README.md
|-- LICENSE
|-- skills/
|   |-- _shared/
|   |   |-- cells-conventions.md
|   |   |-- cells-official-reference.md
|   |   |-- engram-convention.md
|   |   |-- openspec-convention.md
|   |   `-- persistence-contract.md
|   |-- cells-app-architecture/
|   |-- cells-apply/
|   |-- cells-archive/
|   |-- cells-cli-usage/
|   |-- cells-component-authoring/
|   |-- cells-component-researcher/
|   |-- cells-components-catalog/
|   |-- cells-composition-architect/
|   |-- cells-coverage/
|   |-- cells-design/
|   |-- cells-explore/
|   |-- cells-feature-analyzer/
|   |-- cells-i18n/
|   |-- cells-init/
|   |-- cells-official-docs-catalog/
|   |-- cells-propose/
|   |-- cells-spec/
|   |-- cells-tasks/
|   |-- cells-test-creator/
|   `-- cells-verify/
|-- examples/
|   |-- antigravity/
|   |-- claude-code/
|   |-- codex/
|   |-- cursor/
|   |-- gemini-cli/
|   |-- opencode/
|   `-- vscode/
`-- scripts/
    |-- install.ps1
    `-- install.sh
```

## Design Principles

- keep the orchestrator lean
- prefer evidence over assumptions
- reuse existing BBVA components before inventing abstractions
- keep official guidance indexed, not always loaded
- treat Engram as canonical when available
- only create OpenSpec file artifacts when explicitly requested
- keep specialist logic inside skills, not hardcoded in host prompts

## Contributing

To add a new specialist behavior:

1. create `skills/cells-{name}/SKILL.md`
2. connect it to the orchestrator or host commands where appropriate
3. update the relevant examples
4. update this `README.md`

To improve an existing skill:

1. edit the `SKILL.md`
2. validate the result in a real Cells-oriented repo
3. update shared conventions if the behavior is cross-cutting

## License

MIT

---

<p align="center">
  <strong>Built for portable AI-assisted development</strong>
  <br />
  <em>Lean orchestration, indexed knowledge, and evidence-first Cells workflows.</em>
</p>

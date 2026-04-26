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

- plan and execute CELLS workflows
- research existing BBVA components before inventing new APIs
- compose features from existing Cells building blocks
- query official Cells guidance without loading full docs trees into context
- guide CLI usage, testing, coverage, i18n, and component authoring

The key design goal is simple: keep the orchestrator lean, keep documentation indexed, and load detailed evidence only when a skill actually needs it.

## Architecture

### Core Model

The bundle uses a four-layer architecture:

1. Host integration layer: `examples/*` contains prompts, rules, and OpenCode commands for each supported host.
2. Orchestrator layer: a single lean orchestrator routes work, resolves persistence mode, prefers background delegation when the host supports it, tracks state, and asks for approvals.
3. Skill layer: specialist behavior lives in `skills/cells-*/SKILL.md`.
4. Knowledge layer: shared conventions plus bundled catalogs provide deterministic retrieval and evidence.

### Execution Flow

The canonical flow is:

1. The user selects the orchestrator, usually `cells-orchestrator`.
2. The user runs a workflow command such as `/cells-init` or `/cells-explore component:bbva-button-default`.
3. The host command or prompt hands control to the orchestrator.
4. The orchestrator launches a delegated run.
   - Prefer `delegate` for non-blocking or parallel work when the optional OpenCode background-delegation plugin is installed.
   - Fall back to synchronous `task` when immediate results are required or the plugin is unavailable.
5. That delegated run starts by reading the relevant `SKILL.md`.
6. The skill decides which evidence to inspect: code, tests, package docs, official docs, indexed catalogs, or persistence artifacts.
7. The skill returns a structured result envelope.
8. The orchestrator summarizes, asks for approval if needed, and selects the next step.

### Delegate-First Orchestration Policy

The orchestrator stays thin and coordination-only:

- delegate-first for SDD and non-SDD work
- prefer `delegate` when host/plugin support exists
- fall back to `task` without weakening Cells governance, evidence gates, or specialist routing
- keep `/cells-*` commands canonical even when migration work inspects historical pre-Cells artifacts as compatibility-only history

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
  "risks": ["optional risk list"],
  "skill_resolution": "injected | fallback-registry | fallback-path | none",
  "evidence_required": ["evidence gathered, unavailable, or blocked"]
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

### Internal Specialist Routing (no extra slash commands)

The public command surface is intentionally minimal (workflow-only). Specialist skills are still active and are selected by the orchestrator internally based on intent.

Examples:

- Component/API discovery intent in `/cells-explore` -> route to catalog-first component research skills.
- Docs/process/testing/i18n/theming intent in `/cells-explore` or planning phases -> route to official-docs-first specialist skills.
- Testing intent in any phase -> enforce mandatory stack: `cells-cli-usage` -> `cells-coverage` -> `cells-test-creator`.

### Canonical OpenCode Usage

In OpenCode, the intended operating loop is:

1. install the skills and commands
2. add the `cells-orchestrator` agent block from `examples/opencode/opencode.json`
3. switch to `cells-orchestrator`
4. run `/cells-init`
5. use `/cells-explore` for discovery; specialist routing happens internally
6. continue with CELLS workflow commands for planning and implementation

A common flow looks like this:

```text
/cells-explore component:bbva-button-default for debit-card-detail-flow
/cells-new improve-card-detail-flow
/cells-apply
/cells-verify
/cells-archive
```

## Operational Flows and Usage

This section explains how the agent is operated in real work, which commands to run first, and what to expect at each step.

### Operating Modes

The orchestrator can run in two practical modes:

1. Delegated background mode (`delegate` available)

  Better for parallel work and long investigations. The orchestrator stays responsive while sub-agents run.

1. Synchronous fallback mode (`task`)

  Used when background delegation is unavailable or immediate response is required. Workflow contracts and governance still apply.

In both modes, behavior is identical from a governance perspective:

- Cells command canon stays mandatory.
- Evidence routing stays catalog-first.
- Result envelope stays deterministic.

### What Happens When You Run a Command

For any `/cells-*` command, the runtime sequence is:

1. Command prompt provides context (`workdir`, `project`, optional `argument`, persistence mode).
2. Orchestrator selects the phase/specialist skill.
3. Sub-agent reads the target `SKILL.md` first.
4. Skill gathers evidence in deterministic order (catalogs, docs, code, tests, artifacts).
5. Skill returns structured envelope (`status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`, `skill_resolution`, `evidence_required`).
6. Orchestrator summarizes and asks to continue when the next phase needs user approval.

### End-to-End Planning and Delivery Flow

Use this for a standard change from idea to closeout:

1. `/cells-init`

  Detects stack, confirms Cells context, and establishes persistence expectations.

1. `/cells-new <change-name>`

  Runs exploration and then proposal creation.

1. `/cells-continue` or `/cells-ff <change-name>`

  Produces planning artifacts in dependency order: `proposal`, `spec` + `design`, and `tasks`.

1. `/cells-apply`

  Implements tasks against spec/design decisions.

1. `/cells-verify`

  Validates implementation, coherence, and execution evidence.

1. `/cells-archive`

  Archives completed change and finalizes lineage.

Dependency model:

```text
proposal -> [spec || design] -> tasks -> apply -> verify -> archive
```

### Discovery-First Flow (before planning)

Use this when the work starts from uncertainty (component choice, architecture pattern, coverage gap):

1. `/cells-explore <topic>`
2. `/cells-new <change-name>` when the direction is clear

Specialist skills still run, but they are orchestrated internally to keep the command surface compact.

### Testing and Coverage Flow

Whenever testing is involved (explore/apply/verify/coverage), follow this exact stack:

1. `cells-cli-usage` (canonical command and invocation)
2. `cells-coverage` (thresholds and artifact triage)
3. `cells-test-creator` (test design/update conventions)

Do not skip or reorder this stack.

### Command Selection Cheat Sheet

| If you need to... | Start with | Then |
|---|---|---|
| bootstrap project context | `/cells-init` | `/cells-explore` or `/cells-new` |
| analyze an idea without committing | `/cells-explore <topic>` | `/cells-new <change>` |
| plan full implementation quickly | `/cells-ff <change>` | `/cells-apply` |
| continue an in-progress change | `/cells-continue [change]` | follow `next_recommended` |
| implement pending tasks | `/cells-apply` | `/cells-verify` |
| validate completion/readiness | `/cells-verify` | `/cells-archive` |

### Practical Usage Playbooks

Playbook A — New feature in existing Cells app:

```text
/cells-init
/cells-explore component:bbva-button-default for card-detail-improvements
/cells-new improve-card-details
/cells-continue
/cells-apply
/cells-verify
```

Playbook B — Fast planning only (no implementation yet):

```text
/cells-init
/cells-ff add-card-notifications
```

Playbook C — Resume a partially completed change:

```text
/cells-init
/cells-continue add-card-notifications
```

### How to Read Results and Decide Next Step

Interpret phase output using this rule:

- `status: ok` -> proceed with `next_recommended`.
- `status: partial` -> proceed only after addressing evidence gaps in `risks`.
- `status: blocked` -> stop and resolve missing dependency/evidence first.

Always treat `artifacts` as source-of-truth references for what was actually produced.

### Common Mistakes to Avoid

- Jumping directly to `/cells-apply` without `proposal/spec/design/tasks`.
- Using generic test commands in Cells contexts without explicit user request.
- Skipping catalog-first routing and guessing component APIs from memory.
- Treating browser captures alone as completion evidence.
- Archiving a change before verification reaches `ok`.

## Skills

### CELLS Skills

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
./scripts/setup.sh
```

On Windows PowerShell:

```powershell
.\scripts\setup.ps1
```

Setup options:

```bash
./scripts/setup.sh --all
./scripts/setup.sh --agent opencode --opencode-mode single
./scripts/setup.sh --agent opencode --opencode-mode multi
./scripts/setup.sh --non-interactive
```

```powershell
.\scripts\setup.ps1 -All
.\scripts\setup.ps1 -Agent opencode -OpenCodeMode single
.\scripts\setup.ps1 -Agent opencode -OpenCodeMode multi
.\scripts\setup.ps1 -NonInteractive
```

If you only want to copy skills (without prompt/config orchestration), use `./scripts/install.sh` or `.\scripts\install.ps1`.

Compatibility note: project-local install copies skills to `./.opencode/skills/`, which is OpenCode's documented project-local discovery path. OpenCode commands, config, and optional background-delegation assets live under `examples/opencode/` and install into user-level `~/.config/opencode/` unless you copy them to `./.opencode/commands/` yourself.

### Supported Hosts

- OpenCode
- VS Code Copilot
- project-local installs

### OpenCode

Use the full setup script:

```bash
./scripts/setup.sh --agent opencode
```

OpenCode supports two modes:

- `single` (default): one `cells-orchestrator` handles all phases.
- `multi`: one hidden sub-agent per CELLS phase (`cells-init`, `cells-explore`, `cells-propose`, `cells-spec`, `cells-design`, `cells-tasks`, `cells-apply`, `cells-verify`, `cells-archive`) plus the orchestrator.

Optional background delegation:

- `setup.sh` / `setup.ps1` also surface optional OpenCode background-delegation assets when bundled.
- When those assets are available, the orchestrator may use `delegate`, `delegation_read`, and `delegation_list` for non-blocking work.
- If the plugin is absent, the workflow still works through synchronous `task` fallback.

Explicit mode selection:

```bash
./scripts/setup.sh --agent opencode --opencode-mode single
./scripts/setup.sh --agent opencode --opencode-mode multi
```

#### Install mode: normal (single) vs multi-agent

Normal mode (`single`) uses one orchestrator agent for all phases.

Install normal mode:

```bash
./scripts/setup.sh --agent opencode --opencode-mode single
```

```powershell
.\scripts\setup.ps1 -Agent opencode -OpenCodeMode single
```

Multi-agent mode (`multi`) uses one orchestrator plus one hidden sub-agent per CELLS phase.

Install multi-agent mode:

```bash
./scripts/setup.sh --agent opencode --opencode-mode multi
```

```powershell
.\scripts\setup.ps1 -Agent opencode -OpenCodeMode multi
```

Defaults and switching:

- If you run setup without `--opencode-mode` / `-OpenCodeMode`, the default mode is `single`.
- You can switch modes anytime by re-running setup with the other mode.
- Re-running setup is safe and idempotent; existing `model` values are preserved during config merge.

The setup script installs:

1. skills to `~/.config/opencode/skills/`
2. commands to `~/.config/opencode/commands/`
3. merged agent config in `~/.config/opencode/opencode.json` (preserving your existing `model` fields)

Manual merge templates are provided at:

- `examples/opencode/opencode.single.json`
- `examples/opencode/opencode.multi.json`

#### Configure models per agent (single and multi mode)

After setup, assign models in your OpenCode config file:

- macOS/Linux/WSL: `~/.config/opencode/opencode.json`
- Windows: `C:\Users\<you>\.config\opencode\opencode.json`

Inside `agent`, add or edit the `model` field for each agent using `provider/model-id`.

Single mode example:

```json
{
  "agent": {
    "cells-orchestrator": {
      "mode": "all",
      "model": "anthropic/claude-sonnet-4-6"
    }
  }
}
```

Multi mode example:

```json
{
  "agent": {
    "cells-orchestrator": { "mode": "primary", "model": "anthropic/claude-sonnet-4-6" },
    "cells-explore": { "mode": "subagent", "model": "google/gemini-2.5-flash" },
    "cells-spec": { "mode": "subagent", "model": "anthropic/claude-opus-4-6" },
    "cells-design": { "mode": "subagent", "model": "anthropic/claude-opus-4-6" },
    "cells-apply": { "mode": "subagent", "model": "anthropic/claude-sonnet-4-6" },
    "cells-verify": { "mode": "subagent", "model": "openai/o3" }
  }
}
```

Notes:

- Do not remove required agent fields (`prompt`, `permission`) when editing. OpenCode's `tools` field is deprecated; use `permission`.
- In multi mode, phases without explicit `model` use your OpenCode default model.
- Re-running `setup.sh` / `setup.ps1` preserves existing `model` fields for Cells phase agents.

Troubleshooting (`database table is locked`):

- This usually means another suspended OpenCode process is still holding the local DB lock.
- Close OpenCode sessions, then check active processes (`ps aux | grep opencode` on macOS/Linux, `Get-Process opencode` on Windows).
- Stop stale processes (`pkill -f opencode` or `Stop-Process -Name opencode -Force`), then start OpenCode again.
- Avoid leaving suspended OpenCode sessions running in the background.

### VS Code Copilot

1. Install workspace assets from the target repository:

```bash
./scripts/install.sh --agent vscode
```

This creates the official VS Code Copilot layout:

- `.github/copilot-instructions.md`
- `.github/instructions/cells-orchestrator.instructions.md`
- `.github/prompts/cells-*.prompt.md`
- `.github/agents/*.agent.md`
- `.github/skills/*/SKILL.md`
- `.github/hooks/*.json`
- `.github/plugin/` optional Copilot plugin package

2. Use `cells-orchestrator` as the main custom agent. It can invoke `cells-analysis`, `cells-implementation`, and `cells-verification` as subagents when the VS Code `agent` tool is available.
3. Skills are first-class VS Code Agent Skills under `.github/skills/`; repository-local `skills/` remains the source of truth in this bundle.
4. Agent handoffs follow `skills/_shared/cells-agent-handoff-contract.md`: orchestrator is a coordinator, executor agents do not delegate, every handoff carries `evidence_required`, and every result reports `skill_resolution`.
5. Hooks are installed as guardrails for destructive commands and non-Cells command drift. They are intentionally narrow and do not replace `cells-verify`.
6. Validate VS Code customization assets before release:

```bash
python3 scripts/validate_vscode_copilot_assets.py
python3 scripts/validate_vscode_copilot_assets.py --installed-root .github
python3 scripts/validate_vscode_copilot_assets.py --plugin-root .github/plugin
```

Workspace install is the recommended VS Code path. The `.github/plugin/` package is optional/experimental because Copilot hooks, plugins, custom agents, and subagents can depend on VS Code version, preview flags, workspace trust, and organization policy. See `examples/vscode/docs/opencode-vscode-equivalence.md` for the OpenCode phase-agent to VS Code role-agent mapping.

To build a standalone optional plugin package from canonical assets:

```bash
bash scripts/build_vscode_plugin.sh dist/vscode-plugin
```

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
|   |-- opencode/
|   |   |-- opencode.json
|   |   |-- opencode.single.json
|   |   |-- opencode.multi.json
|   |   `-- commands/
|-- .github/
|   |-- instructions/
|   |-- prompts/
|   |-- agents/
|   |-- docs/
|   `-- skills/
`-- scripts/
  |-- setup.ps1
  |-- setup.sh
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

Contribution flow remains mandatory:

1. open or reference an issue
2. wait for approval on that issue
3. open a PR linked to the approved issue
4. complete review
5. merge only after review gates pass

Short form: `issue -> approved issue -> PR -> review -> merge`

## License

MIT

---

<p align="center">
  <strong>Built for portable AI-assisted development</strong>
  <br />
  <em>Lean orchestration, indexed knowledge, and evidence-first Cells workflows.</em>
</p>

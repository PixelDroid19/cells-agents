<p align="center">
  <h1 align="center">Cells Agent Bundle</h1>
  <p align="center">
    <strong>Portable multi-host orchestration for BBVA Cells using proportional skill-driven workflows</strong>
    <br />
    <em>Generated host adapters. Indexed documentation. Portable workflow state. Markdown-based skills.</em>
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
2. Orchestrator layer: a single lean orchestrator sizes the work, routes to only the required skills, resolves persistence mode, uses background delegation only when it adds value, tracks state, and asks for approvals.
3. Skill layer: specialist behavior lives in `skills/cells-*/SKILL.md`.
4. Knowledge layer: shared conventions plus bundled catalogs provide deterministic retrieval and evidence.

### Execution Flow

The canonical flow is:

1. The user selects the orchestrator, usually `cells-orchestrator`.
2. The user runs a workflow command such as `/cells-init` or `/cells-explore component:bbva-button-default`.
3. The host command or prompt hands control to the orchestrator.
4. The orchestrator selects the smallest safe mode: `fast-path`, `scoped-change`, `full-workflow`, or `blocked`.
   - Use `fast-path` for answers, targeted reads, and narrow recommendations.
   - Use `scoped-change` for small local edits with targeted validation.
   - Use `full-workflow` for broad features, architecture, i18n/test/coverage, release work, or explicit end-to-end proof.
5. The selected execution path starts by reading only the relevant `SKILL.md` files.
6. The skill decides which evidence to inspect: code, tests, package docs, official docs, indexed catalogs, or persistence artifacts.
7. The skill returns a structured result envelope.
8. The orchestrator summarizes, asks for approval if needed, and selects the next step.

### Proportional Orchestration Policy

The orchestrator stays thin and coordination-aware:

- do not delegate `fast-path` work
- keep `scoped-change` in the current agent unless independent non-blocking slices or user-requested delegation justify role agents
- use host-native subagents for `full-workflow` work only when role separation,
  parallelism, or independent evidence gathering helps
- fall back to direct execution without weakening Cells governance, evidence
  gates, or specialist routing
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
  -> sized execution path
  -> read target SKILL.md
  -> inspect evidence and conventions
  -> return structured result
  -> orchestrator summary and next action
```

### Result Contract

Every delegated or governed phase run should return the same decision-friendly structure:

```json
{
  "status": "ok | warning | blocked | failed",
  "executive_summary": "short summary for the orchestrator",
  "detailed_report": "optional long-form analysis when needed",
  "artifacts": [
    {
      "name": "proposal | spec | design | tasks | report",
      "store": "host-memory | openspec | hybrid | none",
      "ref": "host-memory-id | file-path | null"
    }
  ],
  "next_recommended": ["cells-spec", "cells-design"],
  "risks": ["optional risk list"],
  "skill_resolution": "host-discovery | explicit-path | none",
  "evidence_required": ["evidence gathered, unavailable, or blocked"]
}
```

## Knowledge Model

### Default Recommendation

Use no workflow artifacts for fast/scoped work and OpenSpec for a durable full workflow.

Recommended policy:

- `none` is the default for fast questions and scoped edits.
- `openspec` is the portable backend for governed proposal/spec/design/task artifacts.
- host memory is supplemental and only used when explicitly requested.
- `hybrid` mirrors portable OpenSpec artifacts into an available host memory.

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
2. the external docs root resolved in `.cells-agent/context.json`, when present
3. project-local code and tests as runtime evidence

### Why This Order

- the bundled index is portable and available without the source checkout
- an environment-specific docs checkout is an optional refresh/evidence source
- package documentation should not be preloaded as raw markdown; consume it
  through the bundled catalog and package-level evidence
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
  mode: openspec
```

Use the following modes:

- `none`: default for fast-path and scoped-change work
- `openspec`: default for a durable governed full workflow
- `host-memory`: optional host-native recall when explicitly requested
- `hybrid`: OpenSpec plus an explicitly requested host-memory mirror

Mode-selection policy:

- choose `none` automatically for fast/scoped work
- choose `openspec` for a durable full workflow
- never require host memory for correctness

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

The orchestrator can run in two practical profiles:

1. Multi-agent profile

  Uses host-native bounded subagents for independent analysis, implementation,
  and verification.

2. Single-agent profile

  Executes directly and is the default. Workflow contracts and governance
  still apply.

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
| `cells-components-catalog` | Component discovery plus API, events, style hooks, docs, tests, and usage evidence. |
| `cells-component-authoring` | Reuse vs new component decisions, scaffold flow, docs, and tests. |
| `cells-app-architecture` | Feature structure, component composition, data managers, routing, bridge, and communication guidance. |
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

The repository now has one canonical source tree and one environment-neutral
compiler: `scripts/cells_agent.py`. It renders the correct assets for each host
at install time. A checked-in `portable/` copy is not required.

### Inspect the Cells environment first

```powershell
python scripts/cells_agent.py doctor `
  --workspace C:\work\cells-project
```

`doctor` detects the Cells project, sibling Spherica `packages/` catalog,
official guides checkout, Cells CLI checkout, and installed host executables.
Pass `--catalog`, `--docs`, or `--cells-cli` only when auto-detection is not
appropriate.

### Install

| Host | Scope | Bash | PowerShell |
|---|---|---|---|
| VS Code | workspace | `scripts/install.sh --host vscode --scope workspace --profile single` | `scripts/install.ps1 -HostName vscode -Scope workspace -Profile single` |
| OpenCode | workspace | `scripts/install.sh --host opencode --scope workspace --profile single` | `scripts/install.ps1 -HostName opencode -Scope workspace -Profile single` |
| OpenCode | user | `scripts/install.sh --host opencode --scope user --profile single` | `scripts/install.ps1 -HostName opencode -Scope user -Profile single` |
| Codex | user | `scripts/install.sh --host codex --scope user --profile single` | `scripts/install.ps1 -HostName codex -Scope user -Profile single` |

Use `--profile multi` / `-Profile multi` only when bounded specialist agents
materially help. The default `single` profile keeps one proportional
orchestrator and avoids unnecessary fan-out.

The installer:

- renders from `skills/` and `examples/<host>/`
- merges the Cells agent into an existing OpenCode JSON configuration
- appends or refreshes a marked Cells block in instruction files
- replaces only Cells-managed skills, agents, commands, hooks, and plugin files
- removes retired Cells-managed skill names only with explicit `--force` / `-Force`
- preserves unrelated user files unless `--force` / `-Force` is explicit
- writes `.cells-agent/context.json` and `.cells-agent/install-state.json` in
  the target Cells workspace

Normal installs preserve retired skill directories because a matching name
does not prove bundle ownership. `--force` additionally removes the known
retired Cells skill names and the former Codex plugin-cache path; review the
target before using it.

Codex writes `~/.codex/config.cells.example.toml` instead of overwriting an
existing `config.toml`; review and merge the desired settings explicitly.

### Render distributable host artifacts

Generated packages belong in ignored `dist/`, not in source control:

```powershell
scripts/render.ps1 -HostName all -Profile multi -Force
```

```bash
python3 scripts/cells_agent.py render \
  --host all --profile multi --output dist --force
```

Every artifact includes `render-manifest.json` with capability status and
SHA-256 hashes. VS Code output separates the workspace layout from the
installable plugin root.

### Validate

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 scripts/cells_agent.py validate
```

See [docs/harness.md](docs/harness.md) for the architecture, capability
boundaries, migration, and smoke-test matrix.

## Project Structure

```text
<repo-root>/
|-- README.md
|-- LICENSE
|-- .agents/
|   `-- plugins/marketplace.json
|-- plugins/
|   `-- cells-agent-bundle-codex/    # thin plugin metadata; payload is generated
|-- harness/
|   `-- manifest.json
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
|   |-- cells-components-catalog/
|   |-- cells-coverage/
|   |-- cells-design/
|   |-- cells-explore/
|   |-- cells-i18n/
|   |-- cells-init/
|   |-- cells-official-docs-catalog/
|   |-- cells-propose/
|   |-- cells-spec/
|   |-- cells-tasks/
|   |-- cells-test-creator/
|   `-- cells-verify/
|-- examples/
|   |-- codex/
|   |-- opencode/
|   |   |-- opencode.json
|   |   |-- opencode.single.json
|   |   |-- opencode.multi.json
|   |   `-- commands/
|   `-- vscode/
|       |-- agents/
|       |-- docs/
|       |-- hooks/
|       |-- instructions/
|       |-- plugin/
|       `-- prompts/
|-- tests/
|   `-- test_cells_agent.py
`-- scripts/
    |-- cells_agent.py
    |-- build_codex_plugin.sh
    |-- build_vscode_plugin.sh
    |-- install.ps1
    |-- install.sh
    |-- install_test.sh
    |-- render.ps1
    |-- validate_codex_assets.py
    `-- validate_vscode_copilot_assets.py
```

## Design Principles

- keep the orchestrator lean
- prefer evidence over assumptions
- reuse existing BBVA components before inventing abstractions
- keep official guidance indexed, not always loaded
- use OpenSpec as the portable source of truth for durable full workflows
- keep host memory optional and supplemental
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

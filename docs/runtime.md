# Cells Agent runtime

The local runtime provides project inspection, command resolution, catalog retrieval, command evidence, and optional memory. It runs without an LLM, a server account, an API key or downloaded Python packages. The selected host still owns the agent loop and permissions.

## Requirements and entrypoint

Use Python 3.11+ with SQLite FTS5 for the complete bundle and validation tools. The runtime itself uses Python 3.10-compatible code. Native hook adapters also require Node.js. Run `doctor` to inspect available executables; discovery does not prove that the host is signed in or can run a model.

From the repository root:

```sh
python3 runtime/cells-agent.py doctor
python3 runtime/cells-agent.py --root /path/to/project project
python3 runtime/cells-agent.py route test-command
python3 runtime/cells-agent.py route feature --complexity substantial
```

For an installed bundle, replace `runtime/cells-agent.py` with its absolute installed path. Global options (`--root`, `--project`, `--data-dir`) precede the subcommand. Use `python` on Windows if that is the installed interpreter name.

`project` detects Cells from BBVA package/dependency namespaces, native Cells scripts or `cells.json`. Plain Lit alone is not a Cells signal. Project identity includes the canonical root path, so equally named checkouts have separate default memories. Moving a checkout changes that identity; supply the same explicit `--project` when deliberate continuity is needed.

## Resolve and check commands

```sh
python3 runtime/cells-agent.py --root /path/to/project resolve test
python3 runtime/cells-agent.py --root /path/to/project check test --timeout 120
python3 runtime/cells-agent.py --root /path/to/project evidence
```

`resolve` reads `package.json` and returns the selected command and its expanded scripts. It understands plain package aliases and exposes lifecycle scripts. In Cells projects, automatic selection requires a verified native `cells component:*`, `cells lit-component:*` or `cells app:*` command. It excludes watch tests and options that update snapshots or locales. Component test commands provide coverage by default according to the bundled CLI references; the resolver reuses that existing script for a coverage request and rejects explicit coverage-disable options. Complex setup wrappers require direct inspection; it reports a gap instead of inventing a command. Existing non-Cells package scripts remain usable in generic projects.

`check` actually executes the resolved package script, applies a timeout and records the exit status, a bounded output tail, and file fingerprints before and after execution. Records live in a separate `evidence.db`. A successful check whose source changed while running is `partial`. Later source edits mark the record as stale. In `evidence`, `current` describes file equality; `passed` additionally requires a successful command. The summary succeeds only when the latest record for each recorded intent is current and passed. Evidence covers that command and working-file content only: ignored files, the dependency installation, external services, browser behavior and host authentication require their own validation. Fingerprints and record digests detect accidental mismatch; they are not tamper-proof attestations.

`started_at` is captured before launching the command, and duration excludes the later fingerprint calculation. The `check` process exits nonzero for failed, timed-out, blocked or partial checks. Coverage command evidence does not itself prove a threshold; inspect the generated coverage report for that claim.

## Catalog search

```sh
python3 runtime/cells-agent.py search components "button icon" --limit 3
python3 runtime/cells-agent.py search components bbva-button-default --limit 1 --detail
python3 runtime/cells-agent.py search docs "component test" --limit 3
python3 runtime/cells-agent.py search docs "IntlMsg locales" --limit 1 --detail
```

Search opens the bundled indexes read-only, checks packaged hashes, returns bounded previews and does not rebuild on a query. Limits are 1–12 through this entrypoint. Full APIs/content require `--detail`. To open a document by path or inspect catalog areas, use the catalog's own `scripts/search_docs.py --help`.

The current packaged snapshot contains 106 Spherica packages and 118 official documents, split into 989 searchable sections. The manifest records source revision, portable source paths and hashes. This is source-snapshot evidence; it does not assert that an installed application uses the same component version.

## Optional memory

```sh
python3 runtime/cells-agent.py --root /path/to/project memory search "locale setup"
python3 runtime/cells-agent.py --root /path/to/project memory save --title "Locale source" --content "The component loads locales from locales/locales.json." --topic-key locale-source
python3 runtime/cells-agent.py --root /path/to/project memory context --limit 3
python3 runtime/cells-agent.py --root /path/to/project memory get 1
python3 runtime/cells-agent.py --root /path/to/project memory export > cells-memory-export.json
```

Install the independent [Cells Memory application](https://github.com/PixelDroid19/cells-memory) to use memory. Its default data directory is `$XDG_STATE_HOME/cells-memory` (normally `~/.local/state/cells-memory`) on Unix and `%LOCALAPPDATA%/cells-memory` on Windows; `CELLS_MEMORY_HOME` overrides it. Command evidence remains under `cells-agent`, controlled by `CELLS_AGENT_HOME`. Explicit `--data-dir` selects a shared override directory for both stores. Memory is never required to edit source or run checks. Saving is explicit; no prompts or tool streams are captured automatically.

To migrate a supplied Engram JSON export, inspect the report before applying:

```sh
python3 runtime/cells-agent.py --root /path/to/project memory import-engram /path/to/engram-export.json --source-project previous-project-name
python3 runtime/cells-agent.py --root /path/to/project memory import-engram /path/to/engram-export.json --source-project previous-project-name --apply
```

The import preserves eligible observations and provenance. It reports conflicts, unscoped/skipped observations and unsupported sessions, prompts and relations. It never opens or modifies an existing Engram database. See [the memory contract](memory.md) for import/export semantics and storage limits.

## Native MCP

```sh
python3 runtime/cells-agent.py --root /path/to/project mcp
```

This serves newline-delimited JSON-RPC on stdio, following the [MCP stdio transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports). It binds one project at startup. Tools inspect projects, route explicit intents, resolve commands, search catalogs, read evidence and retrieve memory. It exposes no shell-execution tool or arbitrary file-reading endpoint. Read tools do not offer cross-project overrides.

Append `--memory-write` to expose `cells_memory_save`. It is omitted by default. In VS Code, also add `cells/cells_memory_save` to the intended agent's tool list; generated default agents expose only the default read tools. The CLI always permits explicit `memory save`. Memory and catalog tool results are untrusted source data; they cannot authorize actions or override the user's instructions.

## Host adapters

| Host | Installed entrypoints | Native boundary |
| --- | --- | --- |
| VS Code workspace | `.github/agents`, `.github/skills`, `.github/runtime`, `.vscode/mcp.json` | Analysis uses read tools and MCP; executors declare an empty child list. Prompts inherit agent tools. |
| VS Code standalone plugin | `agents`, `skills`, `runtime`, `.mcp.json`, plugin hooks | Hook commands use `${PLUGIN_ROOT}`, independent of workspace cwd. Activate this or workspace assets for the same project. |
| Codex global | `~/.codex/agents`, `~/.codex/runtime`, plugin under `~/.agents/plugins/plugins` | Analysis uses a read-only sandbox; executors disable multi-agent tools through `[agents] enabled = false`. |
| Codex plugin only | Visible `skills` and portable `runtime` | Use the CLI directly or register the absolute runtime path as a stdio MCP server. Plugin-only delivery does not install global agents or hooks. |
| OpenCode global | `~/.config/opencode/{skills,runtime,commands}` | Native tasks only. Single-agent is the default; the multi template explicitly denies child delegation and legacy tools. |

Native sessions require the host's normal trust, account and customization setup. Models inherit host/user configuration. The declarative capability manifest is [adapters/hosts.json](../adapters/hosts.json); generated source projections can be checked with `python3 scripts/generate_adapters.py --check`.

The hook policy parses recognized command payloads, not arbitrary document text. It routes detected destructive operations or unverified Cells test wrappers to native review. This is an advisory check, not a shell sandbox. A broken bridge reports the missing runtime instead of silently claiming it validated a command. The Stop hook is inert; completion is supported by actual evidence.

## Build and install

```sh
python3 scripts/bundle.py all
python3 scripts/install.py --agent vscode --path /path/to/project --dry-run
python3 scripts/install.py --agent vscode --path /path/to/project
python3 scripts/install.py --agent codex --dry-run
```

Every host defaults to `--profile single`; `--profile multi` adds analysis, implementation and verification roles with child delegation disabled. Other agents: `opencode`, `project-local`, `all-global`, `custom`. For custom installation, `--path` is a **bundle root** containing `skills`, `runtime`, `adapters` and `docs`, rather than the v2 skill directory. Bash and PowerShell wrappers use the same Python installer.

Historical `setup.sh` and `setup.ps1` entrypoints now forward to that installer and accept its options. Use `--agent all-global` instead of the old automatic `--all` setup mode, or inspect `--help` (`-Help` in PowerShell). They include the optional memory adapter and no longer recommend installing Engram.

Installation compares file hashes. Identical files are unchanged, managed updates are applied, and conflicting user files block the operation before writes. `--replace` explicitly backs up and replaces conflicting bundle paths. Review the listed conflicts first, especially existing host configuration. Unrelated files are preserved. In-process write failures roll back changed files; this is not a filesystem-wide transaction against power loss. No real memory is migrated by installation.

`all-global` checks both host destinations before writing either one. Rebuilding a portable bundle also checks its ownership hashes and refuses edited, missing or additional files; keep those changes and select a new output directory. `python3 scripts/validate_bundle_parity.py` compares all portable files against fresh canonical renders.

Portable global templates expect standard home locations and `python3` on PATH. The installer resolves exact interpreter/runtime paths for local MCP configurations. After manual copy on Windows, adjust those commands to the installed Python interpreter. Use `CELLS_AGENT_PYTHON` for hook bridges if Python is not on PATH.

The compatible `scripts/cells_agent.py` harness commands reuse these modules. See [host profiles and local context](harness.md). Source checkout, generated bundles and user installs have separate ownership; no generated portable tree is required in Git.

# Runtime v3 validation

Validated locally on 2026-09-15. This report describes the final source tree and regenerated portable bundles; it is not a claim of an authenticated model session.

## Results

| Check | Observed result |
| --- | --- |
| Python runtime, catalog, memory, MCP, workflow, evidence and installation suite | 66 tests passed |
| Native adapter generation and skill/governance validation | Passed |
| Component and official-document catalogs | Hash, provenance, schema and ZIP byte checks passed |
| Native source and packaged adapters | Seven source/installed checks passed across Codex, VS Code and OpenCode |
| Portable source parity | 711 files across five destinations matched fresh canonical renders |
| Shell wrappers and hook JavaScript | Syntax checks passed; hooks also executed from temporary external workspaces |
| Whitespace and deliverable tracking | `git diff --check` passed; new runtime files are tracked; generated portable copies are ignored |

The tests use real temporary subprocesses for command execution, timeouts, copied CLI/MCP entrypoints, native hooks and installers. They cover stale or failed evidence, command parsing, invalid queries, strict memory bridge requests, conflict preservation, both native profiles and installation dry-runs. An independent review reproduced defects before correction and rechecked the final core and adapters.

The setup compatibility regression additionally verifies that the historical Bash entrypoint supports a write-free preview and installs the current runtime, including the optional memory adapter, into an isolated destination. The PowerShell compatibility wrapper was updated to call the same installer; Windows execution remains untested here.

## Source-backed integration check

The supplied `bbva-button-default` package was detected as a Cells component using pnpm. Both test and coverage resolution selected its existing `pnpm run test:wtr` script, which expands to `cells lit-component:test --wtr`. This check only read the external package; it did not execute its test suite or modify the BBVA snapshot.

Actual detail queries returned the button's API and an official `component:test` reference. The rebuilt snapshot contains 106 component packages and 118 documents, split into 989 searchable sections. Temporary memory save, search, full retrieval, export and duplicate import preview completed successfully without touching existing user memories.

## Remaining validation boundaries

- Native editor account/trust setup and authenticated model execution were not exercised.
- PowerShell and Windows host execution were not exercised on this Linux machine; their wrappers share the Python installer, and Unix integration tests do not prove Windows behavior.
- Current remote CI results are available on the repository Actions page. The figures above describe the local run.
- Catalogs describe the supplied source snapshots. Confirm the active project's installed component version before applying an API.
- The memory importer handles explicit observations and provenance, with reported exclusions for sessions, prompts and relations. Existing Engram data was not migrated.

## Reproduce

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime python3 -m unittest discover -s tests -v
python3 scripts/generate_adapters.py --check
python3 scripts/validate_skill_quality.py
python3 scripts/validate_governance_behavior.py
python3 scripts/validate_component_catalog.py
python3 scripts/validate_official_docs_catalog.py
python3 scripts/bundle.py all
python3 scripts/validate_bundle_parity.py
python3 scripts/validate_vscode_copilot_assets.py --plugin-root portable/vscode-plugin
python3 scripts/validate_codex_assets.py --installed-root portable/codex-home
python3 scripts/validate_opencode_assets.py --installed-root portable/opencode-home
```

## Memory package separation

The independent Cells Memory package passed 36 storage/CLI/MCP/installer tests and a separate review before publication. A clean temporary installation verified save and retrieval in both directions between its CLI and this repository's JSON bridge, using one database and project identity. The review found an MCP nesting crash; both servers now reject excessive depth and continue serving. The storage tests and implementation live only in the private memory repository.

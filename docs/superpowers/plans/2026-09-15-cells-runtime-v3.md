# Cells runtime v3 — implementation plan

## Goal and approved scope

Rebuild the Cells agent bundle around a small, executable local core, correct the audited failures, preserve domain knowledge, and replace the Engram dependency with optional local memory. The user's approval is the request to rebuild after the architecture audit. Work stays in this checkout; existing memory stores are not migrated automatically.

## Architecture

- `runtime/cells_agent/`: Python 3.10+ standard-library core. Project detection and command resolution use local manifests and actual scripts. Policy inspects commands, not arbitrary prose. Verification stores actual exit status and source fingerprints separately from memory.
- `runtime/cells-agent.py`: portable CLI; no collision with the BBVA `cells` CLI. `doctor`, `project`, `resolve`, `policy`, `check`, `evidence`, `search`, `memory`, and optional `mcp` stdio entry points.
- Catalogs remain SQLite/FTS5 and original-source excerpts. Search is read-only, bounded, Unicode-aware, and validates content hashes. Full component APIs require explicit detail retrieval.
- `runtime/cells_agent/memory.py`: local SQLite store, explicit project isolation, preview-first retrieval, topic updates, soft deletion, export/import and explicit Engram JSON migration. No prompts, credentials, or tool streams captured automatically. Memories are reference material and never verification evidence.
- Host adapters use native agents and tool permissions. No parallel background delegation engine. Python core is included in every installable bundle. Host hooks are small adapters; a hook is defense in depth, not a sandbox.
- Skills provide domain guidance on demand. Shared contracts define proportional workflow, sources, and command rules without recursive boilerplate. Workflow artifacts and memory are independent options.

## Independent ownership and dependencies

1. `local_memory`: own memory module and unit tests only; independent of adapters. Publish the public interface before integration.
2. `catalog_integrity`: own both catalog implementation/assets and catalog validation/tests; regenerate from supplied BBVA snapshots. Do not edit portable copies or skill instructions.
3. `workflow_contracts`: own canonical skill Markdown/shared YAML and `docs/architecture.md`; remove Engram dependency and mandatory ritual. Exclude catalog skills and root README.
4. Primary: project/command/policy/evidence core, CLI/MCP integration, host definitions, build/install scripts, root docs, generated distributions, integration tests and final validation. Integrates workstreams after writers finish.

## Ordered checks

- Reproduce audited bugs in regression tests: invalid search tokens/wildcards, stale index/ZIP, prose falsely treated as a command, `git -C` bypass, generic Lit misclassification, mismatched evidence, hook invocation outside plugin cwd, and child delegation.
- Implement each owned slice and run its focused tests.
- Generate all distributions only after source writers finish. Validate root/portable/ZIP parity and execute hooks/CLI/MCP from a temporary installation with spaces in its path.
- Independently review material changes, fix findings, then run the complete Python test suite, package/skill validators and installer smoke tests once.

## Completion criteria and limits

The CLI and MCP round-trip must work without external packages or a network. Own-memory tests must prove project isolation, idempotent import, persistence and rollback. Search must use the supplied snapshots with verifiable provenance. Published docs must distinguish structural/contract tests from authenticated host UI execution. No claim of live VS Code, Codex or OpenCode agent execution without that evidence.

## Source decisions

- Cells CLI and component rules: the user-provided BBVA documentation and Spherica package snapshots, then their installed manifests and APIs.
- Harness patterns: inspected gentle-pi/gentle-ai snapshots; preserve native model runtimes and capability-based adapters.
- Memory patterns: inspected Engram architecture and JSON export schema; original implementation with explicit migration rather than database replacement.
- Native adapter configuration: current official VS Code and OpenAI documentation checked during the audit.

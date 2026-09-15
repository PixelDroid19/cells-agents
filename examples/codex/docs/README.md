# Codex adapter

Version 3 exposes individual skills in the plugin's `skills` directory. The runtime is bundled beside it. Global installation also adds native agent TOML files, hook bridges and a local MCP configuration under `.codex`.

Executors set `[agents] enabled = false`; analysis uses a read-only sandbox. Models inherit the user's host configuration. The orchestrator can implement scoped work directly.

Use [the runtime and installation guide](../../../docs/runtime.md). Run `python3 scripts/validate_codex_assets.py` for contract checks, or add `--installed-root <home>` / `--plugin-root <plugin>` to validate a package. These checks do not prove a signed-in model session.

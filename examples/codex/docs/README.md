# Cells Codex Adapter

The generated user package contains:

- `~/.codex/AGENTS.md`
- `~/.codex/config.cells.example.toml`
- `~/.codex/hooks.json`, rules, hook scripts, and bounded role agents
- canonical skills under `~/.codex/skills/`
- a local marketplace and plugin source under `~/.agents/plugins/`

The installer never overwrites or creates an active `~/.codex/config.toml`.
Review `config.cells.example.toml` and merge only the settings appropriate for
the user's Codex environment.

Install from the repository root:

```bash
python3 scripts/cells_agent.py install \
  --host codex \
  --scope user \
  --profile single \
  --workspace /path/to/cells-project
```

Use `--profile multi` to render the analysis, implementation, and verification
role agents in addition to the orchestrator. Use `--target` only for an isolated
home destination or packaging test.

Validate without installing:

```bash
python3 scripts/cells_agent.py render \
  --host codex \
  --profile multi \
  --output ./dist/codex \
  --force
python3 scripts/validate_codex_assets.py --installed-root ./dist/codex/home
```

The plugin source is discoverable through the generated local marketplace. A
user still enables it through a supported Codex plugin surface; direct skills
under `~/.codex/skills/` keep the Cells workflow functional independently.

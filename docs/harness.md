# Host packages and profiles

The source tree is canonical. Generate installation packages when needed; `portable/` and `dist/` are ignored build outputs. `scripts/cells_agent.py` preserves the harness entrypoint added upstream and calls the same modular builder, installer and runtime used by the other entrypoints.

```sh
python3 scripts/cells_agent.py render --host all --profile single --output /tmp/cells-packages
python3 scripts/cells_agent.py install --host vscode --scope workspace --workspace /path/to/project --dry-run
python3 scripts/cells_agent.py install --host codex --scope user --profile multi
python3 scripts/cells_agent.py doctor --workspace /path/to/project
python3 scripts/cells_agent.py validate
```

Supported scopes: VS Code workspace; Codex user; OpenCode user or workspace. `single` is the default and installs only the main agent with delegation disabled. `multi` adds analysis, implementation and verification; children cannot delegate further. Models remain host/user choices.

A rendered VS Code directory contains `workspace/` and `plugin/`; choose one deployment for the project. Codex contains `home/`; OpenCode contains `home/` and `workspace/`. Each bundle has a file inventory and hashes. The common capability source is `adapters/hosts.json`; `harness/manifest.json` is its generated compatibility view.

Installation supports `--target`, `--dry-run` and `--force` (equivalent to `--replace` in the modular installer). Conflicts are reported before writes; explicit replacement backs up previous bytes. Generated output ownership is checked even with `--force`; it never authorizes deleting an arbitrary directory. Profile changes prune only previously owned, unchanged files, preserving edited conflicts.

## Optional project context

`doctor` accepts `--catalog`, `--docs` and `--cells-cli` to validate explicit source directories. `install` accepts the same options and saves them to `.cells-agent/context.json` only when `--write-context` is supplied. A dry run never writes the context. This local file is advisory source-location metadata and is not memory or proof of the installed APIs.

Native session trust and account access are managed by each host. Installer and contract-test success does not establish an authenticated agent session.

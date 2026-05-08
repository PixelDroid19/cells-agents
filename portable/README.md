# Portable Install Assets

This directory contains prebuilt Cells bundle assets for restrictive environments where terminal-driven setup is inconvenient or blocked.

Typical case: corporate macOS where `sudo`, `su`, or `mkdir` are not allowed from the terminal.

If you can run the installer script, prefer that first:

- OpenCode global: `./scripts/install.sh --agent opencode`
- OpenCode project-local: `/path/to/cells-agents/scripts/install.sh --agent project-local`
- VS Code: `/path/to/cells-agents/scripts/install.sh --agent vscode`
- Codex: `/path/to/cells-agents/scripts/install.sh --agent codex`

The installer already prefers these portable assets when they are present, so script install and manual copy land the same runtime layout.

## What Is Included

- `opencode-home/.config/opencode/`
  Ready-to-copy OpenCode home layout with `skills`, `commands`, `plugins`, and config templates.
- `project-local/.opencode/`
  Ready-to-copy project-local OpenCode skills tree.
- `vscode/.github/`
  Ready-to-copy VS Code Copilot workspace layout with the plugin already built inside `.github/plugin/`.
- `codex-project/`
  Ready-to-copy Codex repository layout with `AGENTS.md`, `.codex/`, `.agents/plugins/marketplace.json`, and the bundled plugin source.

## Quick Choice

| Need | Use |
|---|---|
| You can run a shell script | `scripts/install.sh` |
| You cannot rely on terminal setup or need Finder copy | the manual copy steps below |
| You only need OpenCode skills inside one repo | `project-local/.opencode/` |
| You need the standalone VS Code plugin package | `portable/vscode-plugin/` |

## Manual Install: OpenCode

Finder path:

1. Open `portable/opencode-home/`
2. Copy `.config` into your home folder
3. If `~/.config/opencode/opencode.json` already exists, keep your existing file and merge the `cells-orchestrator` block from:
   - `portable/opencode-home/.config/opencode/opencode.json`
   - or the mode-specific templates under `portable/opencode-home/templates/`

Terminal copy without `mkdir`:

```bash
cp -R portable/opencode-home/.config "$HOME/"
```

Important:

- if `~/.config/opencode/opencode.json` does not exist, this copy gives you the default Cells OpenCode config
- if `~/.config/opencode/opencode.json` already exists, keep your current file and merge the Cells agent block from:
  - `portable/opencode-home/.config/opencode/opencode.json`
  - `portable/opencode-home/templates/opencode.single.json`
  - `portable/opencode-home/templates/opencode.multi.json`
- the bundled `opencode.json` is the default single-agent profile; use `opencode.multi.json` only if you explicitly want the multi-agent layout

## Manual Install: VS Code Copilot Workspace

From the target repository root:

```bash
cp -R /path/to/cells-agents/portable/vscode/.github .
```

This creates or refreshes:

- `.github/copilot-instructions.md`
- `.github/instructions/`
- `.github/prompts/`
- `.github/agents/`
- `.github/hooks/`
- `.github/skills/`
- `.github/plugin/` (already built)

Run this command from the target repository root.

Finder alternative:

1. Open `portable/vscode/`
2. Drag `.github` into the target repository root

## Manual Install: Codex Project

From the target repository root:

```bash
cp -R /path/to/cells-agents/portable/codex-project/. .
```

This creates or refreshes:

- `AGENTS.md`
- `.codex/`
- `.agents/plugins/marketplace.json`
- `plugins/cells-agent-bundle-codex/`

The Codex layout uses `cells-work-sizing-contract.md` from the bundled plugin payload so simple tasks stay `fast-path`, small edits stay `scoped-change`, and the full Cells workflow is reserved for broad or explicitly requested work.

Run this command from the target repository root.

Finder alternative:

1. Open `portable/codex-project/`
2. Copy its contents into the target repository root

## Manual Install: Project-Local OpenCode

From the target repository root:

```bash
cp -R /path/to/cells-agents/portable/project-local/.opencode .
```

This installs `./.opencode/skills/` only. It does not install global OpenCode commands or global OpenCode config.

## Standalone VS Code Plugin

If you need the standalone plugin package separately from the workspace `.github` tree, it is already built here:

```text
portable/vscode-plugin/
```

This is an advanced distribution artifact. For most teams, copying `portable/vscode/.github/` is the simpler and more complete path.

## Validation

These assets are generated from canonical repo sources and validated with:

```bash
bash scripts/build_portable_assets.sh
python3 scripts/validate_opencode_assets.py --installed-root portable/opencode-home
python3 scripts/validate_vscode_copilot_assets.py --installed-root portable/vscode/.github
python3 scripts/validate_vscode_copilot_assets.py --plugin-root portable/vscode-plugin
python3 scripts/validate_codex_assets.py --installed-root portable/codex-project
python3 scripts/validate_official_docs_catalog.py
```

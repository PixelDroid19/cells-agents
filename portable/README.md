# Portable Install Assets

This directory contains prebuilt Cells bundle assets for restrictive environments where terminal-driven setup is inconvenient or blocked.

Typical case: corporate macOS where `sudo`, `su`, or `mkdir` are not allowed from the terminal.

## What Is Included

- `opencode-home/.config/opencode/`
  Ready-to-copy OpenCode home layout with `skills`, `commands`, `plugins`, and config templates.
- `project-local/.opencode/`
  Ready-to-copy project-local OpenCode skills tree.
- `vscode/.github/`
  Ready-to-copy VS Code Copilot workspace layout with the plugin already built inside `.github/plugin/`.

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

Finder alternative:

1. Open `portable/vscode/`
2. Drag `.github` into the target repository root

## Manual Install: Project-Local OpenCode

From the target repository root:

```bash
cp -R /path/to/cells-agents/portable/project-local/.opencode .
```

## Standalone VS Code Plugin

If you need the standalone plugin package separately from the workspace `.github` tree, it is already built here:

```text
portable/vscode-plugin/
```

## Validation

These assets are generated from canonical repo sources and validated with:

```bash
bash scripts/build_portable_assets.sh
python3 scripts/validate_vscode_copilot_assets.py --installed-root portable/vscode/.github
python3 scripts/validate_vscode_copilot_assets.py --plugin-root portable/vscode-plugin
```

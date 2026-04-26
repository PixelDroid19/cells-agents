# CELLS VS Code Runtime Docs

The VS Code version uses the official GitHub Copilot customization layout:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `.github/prompts/*.prompt.md`
- `.github/agents/*.agent.md`
- `.github/skills/*/SKILL.md`
- `.github/hooks/*.json`
- `.github/plugin/` for optional plugin-style discovery

## Layered precedence

Apply layers in this exact order:

1. `.github/copilot-instructions.md`
2. `.github/instructions/cells-orchestrator.instructions.md`
3. `.github/prompts/cells-*.prompt.md`
4. `.github/agents/*.agent.md`
5. `.github/hooks/*.json`
6. `.github/skills/`

## Distribution Modes

Workspace install is the recommended path:

```bash
./scripts/install.sh --agent vscode
python3 scripts/validate_vscode_copilot_assets.py --installed-root .github
```

The installer also materializes `.github/plugin/` as a self-contained package with internal `skills`, `agents`, and `hooks` paths. This plugin path is optional and experimental; use it only when your VS Code/Copilot environment exposes plugin discovery for the workspace.

For an external distributable package, build from canonical assets instead of copying `examples/vscode/plugin/` alone:

```bash
bash scripts/build_vscode_plugin.sh dist/vscode-plugin
python3 scripts/validate_vscode_copilot_assets.py --plugin-root dist/vscode-plugin
```

Hooks, plugins, custom agents, and subagents can depend on VS Code version, Copilot preview settings, organization policy, and feature flags. Treat automated validation as structure and coherence evidence, then confirm real loading in VS Code before claiming production readiness.

## Maintenance checklist

- Keep prompts aligned with current Cells command canon
- Keep shared mirrors aligned with shared contracts
- Keep custom-agent `tools` lists small; VS Code ignores unavailable tools, but large tool sets reduce quality
- Keep hooks advisory or narrowly blocking; do not hide failures
- Re-run `python3 scripts/validate_vscode_copilot_assets.py`
- Re-run `python3 scripts/validate_vscode_copilot_assets.py --installed-root .github` after installation tests

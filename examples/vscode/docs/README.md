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

## Agent Architecture

Cells agent coordination is governed by `skills/_shared/cells-agent-handoff-contract.md`.

- `cells-orchestrator` coordinates, delegates, synthesizes, and reports.
- `cells-analysis`, `cells-implementation`, and `cells-verification` execute isolated role work and do not launch nested subagents.
- Every handoff carries acceptance criteria and `evidence_required`.
- Every agent result includes `skill_resolution` so the orchestrator can detect missing injected guidance and recover before the next handoff.
- Implementation work follows a bounded Dev-QA loop: implementation, verification, scoped retry, then blocked escalation after repeated failure.

## Distribution Modes

Workspace install is the recommended path:

```bash
./scripts/install.sh --agent vscode
python3 scripts/validate_vscode_copilot_assets.py --installed-root .github
```

The installer also materializes `.github/plugin/` as a self-contained package with internal `skills`, `agents`, and `hooks` paths. This plugin path is optional and experimental; use it only when your VS Code/Copilot environment exposes plugin discovery for the workspace.

For restrictive corporate environments, the repo already ships a ready-to-copy VS Code workspace tree:

- `portable/vscode/.github/`

You can copy that directly with Finder or `cp -R`, without relying on `mkdir` in the destination environment. The built plugin is already included under `.github/plugin/`.

Manual workspace install:

```bash
cp -R /path/to/cells-agents/portable/vscode/.github .
```

The standalone `portable/vscode-plugin/` package remains available only for advanced distribution cases.

Hooks, plugins, custom agents, and subagents can depend on VS Code version, Copilot preview settings, organization policy, and feature flags. Treat automated validation as structure and coherence evidence, then confirm real loading in VS Code before claiming production readiness.

## Maintenance checklist

- Keep prompts aligned with current Cells command canon
- Keep shared mirrors aligned with shared contracts
- Keep custom-agent `tools` lists small; VS Code ignores unavailable tools, but large tool sets reduce quality
- Keep hooks advisory or narrowly blocking; do not hide failures
- Re-run `python3 scripts/validate_vscode_copilot_assets.py`
- Re-run `python3 scripts/validate_vscode_copilot_assets.py --installed-root .github` after installation tests

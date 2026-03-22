# CELLS VS Code Runtime Docs

## Layered precedence

Apply layers in this exact order:

1. `../instructions/copilot-instructions.md`
2. `../prompts/cells-*.md`
3. `../agents/`
4. `../docs/hooks.md`
5. `../docs/models.md`
6. `../skills/`

## Maintenance checklist

- Keep prompts aligned with current Cells command canon
- Keep shared mirrors aligned with shared contracts
- Re-run `python scripts/validate_vscode_copilot_assets.py`

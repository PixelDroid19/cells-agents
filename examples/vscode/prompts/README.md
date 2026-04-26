# CELLS Prompt Catalog

Install these files to `.github/prompts/*.prompt.md`. VS Code exposes each prompt as a slash command by its `name` frontmatter.

Layered precedence for VS Code/Copilot:

1. `.github/copilot-instructions.md`
2. `.github/instructions/cells-orchestrator.instructions.md`
3. `.github/prompts/cells-*.prompt.md`
4. `.github/agents/*.agent.md`
5. `.github/hooks/*.json`
6. `.github/skills/`

Use the prompt that matches the active `/cells-*` phase.

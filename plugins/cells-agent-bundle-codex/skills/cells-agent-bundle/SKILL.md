---
name: cells-agent-bundle
description: Use when working in a BBVA Cells repository and you need the Codex Cells workflow, specialist skills, handoff rules, or validation routing.
---

# Cells Agent Bundle

Use `~/.codex/AGENTS.md` first. It is the Codex-facing global router for Cells work.

In a personal Codex install, the complete behavior payload is bundled at:

`~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/`

When Codex loads this skill from an installed plugin cache instead of the repository copy, use the plugin-local payload at:

`../../.cache/cells-skills/`

Before making code or architecture decisions:

1. Read `_shared/cells-work-sizing-contract.md` and choose `fast-path`, `scoped-change`, `full-workflow`, or `blocked`.
2. Read only the matching `SKILL.md` files needed for that mode.
3. Always follow `_shared/cells-rules-contract.md` for UI/component/i18n/command-policy work.
4. For tests, load only the testing skill(s) the intent needs: `cells-cli-usage` for commands, `cells-coverage` only for coverage work, `cells-test-creator` only for authoring tests; never generic npm/web-test-runner fallbacks in Cells contexts.
5. For delegation, follow `_shared/cells-agent-handoff-contract.md`; do not delegate `fast-path` work.
6. Return evidence from real files, commands, or docs; do not rely on generic Cells assumptions.

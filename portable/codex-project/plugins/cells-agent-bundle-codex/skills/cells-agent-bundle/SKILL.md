---
name: cells-agent-bundle
description: Use when working in a BBVA Cells repository and you need the repo-local Cells workflow, specialist skills, handoff rules, or validation routing.
---

# Cells Agent Bundle

Use the installed project `AGENTS.md` first. It is the Codex-facing router for Cells work.

In a repo-local install, the complete behavior payload is bundled at:

`plugins/cells-agent-bundle-codex/.cache/cells-skills/`

When Codex loads this skill from an installed plugin cache instead of the repository copy, use the plugin-local payload at:

`../../.cache/cells-skills/`

Before making code or architecture decisions:

1. Read the matching `SKILL.md` from that payload.
2. Always follow `_shared/cells-rules-contract.md`.
3. For tests, resolve commands through `cells-cli-usage`, then `cells-coverage`, then `cells-test-creator`.
4. For delegation, follow `_shared/cells-agent-handoff-contract.md`.
5. Return evidence from real files, commands, or docs; do not rely on generic Cells assumptions.

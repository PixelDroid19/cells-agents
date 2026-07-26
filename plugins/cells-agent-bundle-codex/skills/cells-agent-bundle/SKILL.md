---
name: cells-agent-bundle
description: Use when working in a BBVA Cells repository and you need the Codex Cells workflow, specialist skills, handoff rules, or validation routing.
---

# Cells Agent Bundle

Use the nearest `AGENTS.md` first. This gateway's complete, packaged payload is
under `../../assets/cells-skills/`. A direct installation also exposes the same
canonical skills under `~/.codex/skills/`, but this gateway must use its
plugin-relative payload so it remains self-contained.

Before making code or architecture decisions:

1. Read `../../assets/cells-skills/_shared/cells-work-sizing-contract.md` and choose `fast-path`, `scoped-change`, `full-workflow`, or `blocked`.
2. Read only the matching skill folder under `../../assets/cells-skills/`.
3. Always follow `../../assets/cells-skills/_shared/cells-rules-contract.md` for UI/component/i18n/command-policy work.
4. For tests, load only the testing skill(s) the intent needs: `../../assets/cells-skills/cells-cli-usage/SKILL.md` for commands, `../../assets/cells-skills/cells-coverage/SKILL.md` only for coverage work, `../../assets/cells-skills/cells-test-creator/SKILL.md` only for authoring tests; never generic npm/web-test-runner fallbacks in Cells contexts.
5. For delegation, follow `../../assets/cells-skills/_shared/cells-agent-handoff-contract.md`; do not delegate `fast-path` work.
6. Return evidence from real files, commands, or docs; do not rely on generic Cells assumptions.

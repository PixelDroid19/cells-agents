---
name: cells-i18n
description: >
  Manage Cells i18n changes for `this.t(...)`, locale parity, and `IntlMsg` runtime setup in components, demos, tests, and verification flows.
license: MIT
metadata:
  author: D. J
  version: "1.0"
---

# Cells i18n

## Purpose

Use this skill when a task changes user-visible text, translation keys, locale files, or i18n runtime setup.

## Read and follow

- `skills/_shared/cells-official-reference.md`
- `skills/cells-official-docs-catalog/` topics `demo-docs-i18n-assets` and `testing`
- `references/i18n-runtime-and-locales.md`

## When to use

- The user changes user-facing text or translation keys
- Locale parity and runtime loading need verification
- Demo or test i18n setup is part of the requested change
- A verifier must check that i18n wiring is correct

## Workflow

1. Identify all user-visible string surfaces
2. Route component-owned strings through `this.t(...)` with stable key naming
3. Ensure locale parity in required locale files
4. Ensure demo/test/runtime `IntlMsg` setup is deterministic
5. Return changed keys, files, and any fallback or race-condition risk

## Rules

- Do not leave component-owned user-facing literals hardcoded when they should be localized
- Keep keys stable, component-prefixed, and aligned exactly across code and locale files
- Prefer region-free keys like `en` and `es` unless regional override is necessary
- If tests or demos depend on locales, mention `IntlMsg.lang`, `IntlMsg.localesHost`, and any required wait for locale loading

## Finish checklist

- No unintended hardcoded user-facing literals remain
- New keys exist in the required locale files
- Demo/test i18n config matches runtime expectations
- Risks are explicit when locale parity or runtime setup is incomplete

## Browser Integration

For runtime i18n work, also read:
- `skills/_shared/browser-testing-convention.md`
- `agent-browser/SKILL.md` when available

Use browser validation to confirm:
- translated literals actually render
- locale switches or loads behave correctly
- visible fallback text or broken async locale loading is detected in real UI.

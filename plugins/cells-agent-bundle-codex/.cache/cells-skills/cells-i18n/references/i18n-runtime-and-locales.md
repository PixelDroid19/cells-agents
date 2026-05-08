# Cells i18n Runtime and Locales Reference

Use this reference when a component renders predefined user-visible text or i18n behavior changes.

## Authoritative rules

- Add `BbvaCoreIntlMixin` when a component owns localized predefined literals.
- Route component literals through `this.t('key')`.
- Keep keys component-prefixed and stable.
- Prefer region-free language keys and add region-specific overrides only when needed.
- Support per-instance customization through slot overrides or i18n key map objects when required.

## Locales parity contract

- Any new key used by component runtime must exist in component locales.
- Demo runtime should use `demo/locales/locales.json` when the repo's demo or runtime bundle depends on merged keys.
- Some repos also keep locale source in `locales/locales.json`; follow the touched surface and runtime evidence instead of assuming one universal path.
- Keep key names aligned exactly between code and locale files.

## Demo and test runtime setup

- Initialize `window.IntlMsg` before component imports or fixtures when needed.
- Set `IntlMsg.lang` and `IntlMsg.localesHost` to deterministic paths.
- In tests, optionally await `window.IntlMsg.loadUrlResourcesComplete` in setup to avoid locale race conditions.

## Practical checks

- component runtime keys exist
- demo locales include dependency keys when needed
- repo-local locale source for the touched surface is updated
- tests point `localesHost` to the intended root
- any locale load wait is explicit when the suite depends on translated output

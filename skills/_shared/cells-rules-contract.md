# Cells Rules Contract

## Purpose

This is the **single source of truth** for all Cells-specific implementation rules. Every other file in `_shared/` or in a `cells-*` skill references these rules. **Do not replicate these rules elsewhere** — reference this file instead.

When a rule in this file conflicts with a rule in another file, this file wins for Cells implementation rules.

For practical implementation evidence from real local Cells projects, also read `skills/_shared/real-cells-patterns.md`. Official docs and catalog lookups remain primary sources; the real-patterns file grounds architecture, Spherica composition, i18n, style, and test decisions in observed Cells code.

## BBVA-First Rule

**NEVER invent a BBVA component.** For any UI, typography, form, button, table, navigation, or feedback work:

1. **Search `cells-components-catalog`** first:
   ```bash
   python skills/cells-components-catalog/scripts/search_docs.py --query "<what you need>"
   ```
2. If a BBVA component exists: **use it and stop**.
3. Only if no match exists: use `cells-component-authoring` to create one correctly.

### BBVA Component Anti-Patterns (NEVER do)

| Anti-Pattern | Correct approach |
|---|---|
| `<p>`, `<h3>`, `<span>` for text | Use `bbva-type-text` with `weight` and `size` props |
| `<div onclick>` as button | Use `bbva-button-default` or appropriate button variant |
| Custom loading spinner | Use `bbva-skeleton-default` or feedback components |
| `<img>` for BBVA icons | Use the BBVA icon system (see official docs topic `demo-docs-i18n-assets`) |
| Toast from scratch | Use `bbva-notification-toast` |
| Stepper from scratch | Use `bbva-progress-step` |

## Cells Component Implementation Rules

These are **mandatory** for every Cells component:

### scopedElements Registration (MANDATORY)

Every custom element used in a template **must** be imported and registered in `scopedElements`:

```js
static get scopedElements() {
  return {
    ...super.scopedElements,
    'bbva-type-text': factory.get('bbva-type-text'),
  };
}
```

### WidgetMixin + emitEvent (MANDATORY for feature/data-manager architecture)

When the surrounding architecture uses feature/data-manager patterns:

```js
import { WidgetMixin } from '../mixins/WidgetMixin.js';
// Use WidgetMixin(ScopedElementsMixin(LitElement)) as base class
// Use this.emitEvent(...) for business events and bridge-facing communication
```

### i18n with this.t(...) (MANDATORY for all user-facing literals)

**Route every visible string through `this.t('key')`.**

## i18n Anti-Patterns (NEVER do)

| Anti-Pattern | Why | Correct approach |
|---|---|---|
| `this.t('key') \|\| ''` | The i18n runtime renders the key itself as fallback — it is NOT falsy. This hides missing translations. | Check locale file directly. Add missing key to `demo/locales/locales.json`. Never use `\|\| ''`. |
| Hardcoded user-facing literals | Cells requires all user-facing text through `this.t(...)`. | Route every visible string through `this.t('key')`. Add key to locale files. |
| `IntlMsg.lang = 'en'` at instance level | Race condition: component may render before locale loads, showing the key as text. | Set `IntlMsg.lang` at app/shell level. Await `window.IntlMsg.loadUrlResourcesComplete` in tests and demos. |
| Locale files outside `demo/locales/` | Cells enforces this location. | Always use `demo/locales/locales.json`. |

## Mandatory Testing Stack

For Cells test work, **never reorder** this sequence:

```
cells-cli-usage → cells-coverage → cells-test-creator
```

- `cells-cli-usage`: resolve correct Cells test commands
- `cells-coverage`: analyze gaps before writing tests
- `cells-test-creator`: generate tests following Cells conventions

Never use generic `npm test` in Cells contexts. Use `cells lit-component:test` or `cells app:test` (resolved via `cells-cli-usage`).

## Architecture Anti-Patterns (NEVER do)

| Anti-Pattern | Correct approach |
|---|---|
| API logic in component | Use data managers for API interaction. Components own presentation only. |
| Skipping the mandatory testing stack | Always apply `cells-cli-usage` → `cells-coverage` → `cells-test-creator` in order |
| Generic `npm test` in Cells contexts | Use Cells commands resolved via `cells-cli-usage` |

## Real Cells Component Checklist

When the task is building or reviewing a real Cells component, these patterns are **mandatory**:

1. Reuse existing BBVA components first (`cells-components-catalog`)
2. Register every template dependency in `scopedElements`
3. Use `WidgetMixin` + `this.emitEvent(...)` when following Cells feature/data-manager architecture
4. Route all component-owned literals through `this.t(...)`
5. Keep locale parity in `demo/locales/locales.json`
6. Treat SCSS as visual source — keep runtime style artifacts aligned
7. **Validated** browser validation for visible changes (via `agent-browser` before closure)

## Source of Truth for These Rules

These rules are consolidated from:
- `skill-registry/SKILL.md` (anti-patterns, routing)
- `cells-conventions.md` (scopedElements, WidgetMixin, testing stack)
- `cells-official-reference.md` (component checklist)
- `real-cells-patterns.md` (real local Cells feature, app, and Spherica evidence)
- `cells-apply/SKILL.md` (Cells component rules)
- `cells-verify/SKILL.md` (Cells verification rules)
- `cells-component-authoring/SKILL.md` (component creation rules)

**Any other file that duplicates these rules should reference this file instead.**

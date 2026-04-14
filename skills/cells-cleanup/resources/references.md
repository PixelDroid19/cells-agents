# Cells Cleanup — Reference Card

> Agent: read this file when you need to verify a specific rule or pattern during a cleanup sweep.
> All rules here are extracted from the official BBVA Cells documentation.

---

## Source Documents

| Doc | Path | Topic |
|-----|------|-------|
| `component-class.md` | `docs/web-components/reference/component-class.md` | Properties, attributes, reflection, static getters |
| `component-api.md` | `docs/web-components/reference/component-api.md` | Public API, events, slots, methods |
| `lifecycle.md` | `docs/web-components/reference/lifecycle.md` | Lifecycle hooks, update cycle |
| `templating-in-lit.md` | `docs/web-components/reference/templating-in-lit.md` | render(), template parts, bindings, events |
| `reuse-composition.md` | `docs/web-components/reference/reuse-composition.md` | Mixins, ScopedElementsMixin, extension |
| `styles.md` | `docs/web-components/reference/styles.md` | CSS variables, variants, ambients, tokens |
| `i18n.md` | `docs/web-components/reference/i18n.md` | Locale files, `this.t()`, BbvaCoreIntlMixin |
| `testing.md` | `docs/web-components/reference/testing.md` | Test structure, fixtures, events, snapshots |
| `demo.md` | `docs/web-components/reference/demo.md` | Demo folder structure, locales, JS entry points |

---

## Cat. 1 — Formatting

### 1.1 Event callback parameter name
> Source: `templating-in-lit.md` — *"By convention, event payload in event callbacks is named `ev` in BBVA Web Components."*

```javascript
// ✅ correct
_onButtonClick(ev) { ev.stopPropagation(); }

// ❌ wrong
_onButtonClick(e) { }
_onButtonClick(event) { }
```

---

## Cat. 2 — JSDoc

### 2.1 Language: English always
All JSDoc must be in **English**. Translate any existing Spanish JSDoc.

### 2.2 JSDoc for public properties
```javascript
/**
 * Phone line identifier for the account.
 * @type {String}
 * @attribute 'phone-line'
 */
phoneLine: { type: String, attribute: 'phone-line' }
```

### 2.3 JSDoc for render part getters
> Source: `templating-in-lit.md` — *"By convention, render parts in BBVA Web Components must keep this naming structure: '_[partName]Tpl'."*

```javascript
/**
 * Template part for the action section.
 * @returns {TemplateResult}
 */
get _actionTpl() { ... }
```

### 2.4 Remove narrative comments
Keep comments that explain WHY. Remove comments that describe WHAT (the code already does that).

---

## Cat. 3 — Attribute Field

### 3.1 Public properties: explicit `attribute`
> Source: `component-class.md` — Properties must have `attribute` field. camelCase → kebab-case.

```javascript
phoneLine: { type: String, attribute: 'phone-line' }
```

### 3.2 Private/state properties: `attribute: false`
> Source: `component-class.md` — State properties should not generate an attribute converter.

```javascript
_visibleErrorModal: { type: Boolean, attribute: false }
// or (Lit 3):
_viewportWidth: { state: true }
```

### 3.3 Styling properties must have `reflect: true`
> Source: `styles.md` — *"Any property used for styling must be reflected."*

```javascript
variant: { type: String, reflect: true }
size: { type: String, reflect: true }
```

### 3.4 Avoid global HTML attribute name collisions
> Source: `component-class.md`
Do not use as property names: `title`, `id`, `class`, `name`. Use `heading` instead of `title`.

---

## Cat. 4 — Conditions by Method

### 4.1 Max 2 conditions per method
Extract any method with 3+ `if` statements into named helpers.

### 4.2 Rules Table Pattern for N validations
```javascript
// Layer 1 — Predicates (pure boolean check, one per method)
_isBelowMinValue(value, minValue) { return value < minValue; }
_isAboveMaxValue(value, maxValue) { return value > maxValue && maxValue > ZERO; }
_isNotMultipleOfHundred(value) { return value % ONE_HUNDRED !== 0; }

// Layer 2 — Message builders (one method per error message)
_getMinErrorMessage() { return this.t('key-min', { amount: format(this.minValue) }); }
_getMaxErrorMessage() { return this.t('key-max', { amount: format(this.maxValue) }); }
_getMultipleErrorMessage() { return this.t('key-multiple'); }

// Layer 3 — Orchestrator (1 guard + array.find = max 2 conditions)
_getAmountErrorMessage(value) {
  if (MyComponent._isEmptyValue(value)) return '';
  const validations = [
    { isInvalid: () => this._isBelowMinValue(value, this.minValue), getMessage: () => this._getMinErrorMessage() },
    { isInvalid: () => this._isAboveMaxValue(value, this.maxValue), getMessage: () => this._getMaxErrorMessage() },
    { isInvalid: () => this._isNotMultipleOfHundred(value), getMessage: () => this._getMultipleErrorMessage() },
  ];
  const failed = validations.find(({ isInvalid }) => isInvalid());
  return failed ? failed.getMessage() : '';
}
```

### 4.3 Reactive prop writes in `updated()` → move to `willUpdate()`
> Source: `lifecycle.md` — *"Avoid chaining updates. Setting reactive properties in `updated()` causes a second render cycle."*

```javascript
// ❌ double render
updated(props) {
  if (props.has('value')) { this._computed = transform(this.value); }
}

// ✅ single render
willUpdate(props) {
  super.willUpdate?.(props);
  if (props.has('value')) { this._computed = transform(this.value); }
}
```

---

## Cat. 5 — Repetitive Code

### 5.1 Repeated push → CONFIG + `.filter().map()`
```javascript
// ❌ repetitive
const items = [];
if (data.a) items.push({ label: 'A', value: data.a });
if (data.b) items.push({ label: 'B', value: data.b });

// ✅ data-driven
const CONFIG = [{ key: 'a', label: 'A' }, { key: 'b', label: 'B' }];
const items = CONFIG.filter(({ key }) => data[key]).map(({ key, label }) => ({ label, value: data[key] }));
```

### 5.2 Repeated template block → `_itemTpl(item)` + `.map()`
> Source: `templating-in-lit.md` — *"render parts can be defined as methods with parameters"*

```javascript
render() {
  return html`${this.items.map(item => this._cardTpl(item))}`;
}
_cardTpl(item) {
  return html`<div class="card">${item.label}</div>`;
}
```

### 5.3 Monolithic render → split `get _xxxTpl()` getters
> Source: `templating-in-lit.md` — *"HTML can be split in multiple parts, which can then be interpolated in render."*
> Convention: `_mainTpl`, `_secondaryTpl`, `_descriptionTpl`, `_actionTpl`

```javascript
render() {
  return html`
    ${this._mainTpl}
    ${this._secondaryTpl}
    ${this._actionTpl}
  `;
}
get _mainTpl() { return html`<div class="main-block">...</div>`; }
get _secondaryTpl() { return html`<div class="secondary-block">...</div>`; }
get _actionTpl() { return html`<div class="action-block">...</div>`; }
```

---

## Cat. 6 — Template & Binding Quality

### 6.1 Property binding vs attribute binding
> Source: `templating-in-lit.md` — *"Binding to properties will be the preferred binding for other custom elements, except for global HTML attributes."*

```javascript
// ❌ attribute binding — coerces to string
html`<inner-element prop-a="${this.value}"></inner-element>`

// ✅ property binding — for objects, arrays, booleans
html`<inner-element .propA="${this.value}"></inner-element>`
```

### 6.2 Use `ifDefined` or `nothing` for optional attributes
> Source: `templating-in-lit.md` — *"Use the `ifDefined` Lit directive to control whether the attribute is effectively rendered."*

```javascript
// ❌ renders aria-label="undefined" if value is undefined
html`<el aria-label="${this.label}"></el>`

// ✅ removes attribute when undefined
html`<el aria-label="${ifDefined(this.label || undefined)}"></el>`
// or (Lit 3)
html`<el aria-label="${this.label || nothing}"></el>`
```

### 6.3 Wrap reused custom elements in named slots
> Source: `templating-in-lit.md` — *"Wrap the custom element in a named slot to allow overriding it with a different instance from Light DOM."*

```javascript
get _actionTpl() {
  return html`
    <div class="action">
      <slot name="action">
        ${this.actionLabel ? html`
          <bbva-web-button-default
            class="action-btn"
            .disabled="${this.actionDisabled}"
            @click="${this._onActionClick}"
          >${this.actionLabel}</bbva-web-button-default>
        ` : ''}
      </slot>
    </div>
  `;
}
```

### 6.4 Store DOM references in `firstUpdated`
> Source: `templating-in-lit.md` — *"It's recommendable to store references to needed nodes in inner properties once they're rendered."*

```javascript
firstUpdated(props) {
  super.firstUpdated?.(props);
  this._closeBtn = this.shadowRoot.querySelector('.close');
}
_onOpen() { this._closeBtn.focus(); }
```

### 6.5 Public getter for interactive elements
> Source: `templating-in-lit.md` — *"Component authors can set public references to interactive elements, such as public getters."*

```javascript
get actionBtn() {
  return this.shadowRoot.querySelector('.action-btn');
}
```

---

## Cat. 7 — Lifecycle Correctness

### 7.1 `super` in every lifecycle override
> Source: `lifecycle.md` and `reuse-composition.md`

```javascript
constructor() { super(); }
connectedCallback() { super.connectedCallback(); }
disconnectedCallback() { super.disconnectedCallback(); }
firstUpdated(props) { super.firstUpdated?.(props); }
updated(props) { super.updated && super.updated(props); }
willUpdate(props) { super.willUpdate?.(props); }
```

### 7.2 External listeners added in `connectedCallback` → remove in `disconnectedCallback`
> Source: `lifecycle.md` — *"Event listeners added to outer nodes (document, window...) must be added on `connectedCallback`, then removed in `disconnectedCallback`."*

```javascript
connectedCallback() {
  super.connectedCallback();
  document.addEventListener('keydown', this._onKeyDown);
}
disconnectedCallback() {
  super.disconnectedCallback();
  document.removeEventListener('keydown', this._onKeyDown);
}
```

### 7.3 No `getAttribute` in `constructor`
> Source: `lifecycle.md` — *"The constructor has NO access to element attributes."*

```javascript
constructor() {
  super();
  // ❌ this.getAttribute('my-attr') — NOT available here
  // ✅ set initial property values with defaults
  this.phoneLine = '';
  this.isLoading = false;
}
```

---

## Cat. 8 — Tests

### 8.0 Demo mocks must NOT be imported in `src/`
> Source: `demo.md` — *"The demo folder will contain all demo-only logic."*

```javascript
// ❌ FORBIDDEN in src/ files
import mockData from '../../demo/mock/data.js';

// ✅ src/ only imports from src/ or node_modules
import { LitElement } from 'lit';
import { format } from './utils/format.js';
```

### 8.1 Never access private members in tests
> Source: `testing.md` — *"Tests should not call private props or methods directly, as they could change anytime."*

```javascript
// ❌ FORBIDDEN
expect(el._visibleErrorModal).to.be.true;
el._resetState();

// ✅ test through public API and events
const handler = sinon.spy();
el.addEventListener('error-shown', handler);
el.triggerError();
assert.isTrue(handler.calledOnce);
```

### 8.2 Test structure: `suite` > `setup` (`beforeEach`) > `test`
> Source: `testing.md`

```javascript
suite('MyComponent', () => {
  let el;
  teardown(() => fixtureCleanup());

  suite('default', () => {
    setup(async () => {
      el = await fixture(html`<my-component></my-component>`);
    });
    test('renders correctly', async () => {
      await assert.shadowDom.equalSnapshot(el);
    });
  });
});
```

### 8.3 i18n setup in tests
> Source: `i18n.md` — *"Add the `IntlMsg` object to `window` before running any tests."*

```javascript
window.IntlMsg = window.IntlMsg || {};
window.IntlMsg.lang = 'en';
window.IntlMsg.localesHost = '/base';
// for monorepos:
window.IntlMsg.localesHost = '/base/packages/my-component/demo';
```

### 8.4 Semantic DOM diffing
> Source: `testing.md`

```javascript
test('Shadow DOM', async () => {
  await assert.shadowDom.equalSnapshot(el);
});
test('a11y', async () => {
  await assert.isAccessible(el);
});
```

### 8.5 Testing events
> Source: `testing.md`

```javascript
test('clicking main action fires event', async () => {
  const spy = sinon.spy();
  el.addEventListener('main-event', spy);
  el.mainAction.click(); // use public getter
  assert.isTrue(spy.calledOnce);
  assert.equal(spy.args[0][0].detail.value, true); // check payload
});
```

---

## Cat. 9 — Reusability

### 9.1 Don't overwrite public properties inside the component
> Source: `component-class.md` — *"Don't overwrite public properties."*

```javascript
// ❌ antipattern
updated(props) {
  if (props.has('disabled') && this.disabled) {
    this.variant = 'off'; // writes back to public prop
  }
}

// ✅ compute via getter
get _innerVariant() {
  return this.disabled ? 'off' : this.variant;
}
```

### 9.2 Side effects must have cleanup
> Source: `component-api.md` — *"Controlling side effects."*

If you `setAttribute` on the host element in one path, remove it when the condition clears. Same for `addEventListener` on external nodes.

---

## Cat. 10 — Constants

- Magic values repeated in 2+ places → extract to `src/utils/constants.js`
- Magic strings in templates that should be i18n keys → flag for `this.t()`

---

## Cat. 11 — i18n / Locale Rules

### 11.1 Locale file: ONLY valid path
> Source: `demo.md` — *"Localized text literals must be provided in a `locales/locales.json` file. This folder and file should be created inside the demo folder."*

```
✅ demo/locales/locales.json    ← ONLY valid path
❌ src/locales/en.json
❌ demo/locales/en.json
❌ demo/locales/es.json
❌ locales.json (root)
```

### 11.2 Locale file structure: single flat `{}`
This project uses a **single flat object** (not nested by language):
```json
{
  "key-name": "text value",
  "key-with-param": "text with {param}"
}
```

### 11.3 The "English" locale convention (CRITICAL)
> Project-specific convention (NOT from official docs — user-defined rule)

The "English" locale is actually **Spanish text** wrapped with `__` prefix and suffix:
```json
{
  "bbva-feature-send-title": "__Confirmar envío__",
  "bbva-feature-send-amount": "__Importe: {amount}__"
}
```
Rules:
- Text is real Spanish
- `__` wraps the entire value string (not the whole JSON key)
- `{param}` interpolation stays inside the wrapping
- Missing `__` wrapping → flag as `⚠️`
- Actual English text (not Spanish) → flag as `⚠️`

### 11.4 All user-visible strings via `this.t()`
> Source: `i18n.md` — *"After adding the mixin, the component instance has access to a method, `t`, that can be used in render."*

```javascript
// ❌
html`<div>Confirmar</div>`

// ✅
html`<div>${this.t('bbva-feature-send-confirm-title')}</div>`
```

### 11.5 `BbvaCoreIntlMixin` usage
> Source: `i18n.md`

```javascript
import { BbvaCoreIntlMixin } from '@bbva-web-components/bbva-core-intl';
import { LitElement } from 'lit';

class MyComponent extends BbvaCoreIntlMixin(LitElement) { }
```

### 11.6 i18n key naming convention
> Source: `i18n.md`

Keys use the custom element name as prefix: `my-component-close-button`, `my-component-amount-label`.

### 11.7 Locale generation via CLI
> Source: `demo.md` and `i18n.md`

To regenerate `demo/locales/locales.json` merging all dependencies:
```bash
cells lit-component:locales
```

---

## Cat. 12 — Visibility / Access Audit

### 12.1 The rule
> Project-specific rule

If something is accessed from OUTSIDE the component → **public** (no `_` prefix)
If something is ONLY used internally (via `this._xxx`) → **private** (`_` prefix)

### 12.2 `static get` methods are always public
`static get is()`, `static get properties()`, `static get scopedElements()`, `static get styles()` — never underscore-prefixed.

### 12.3 `ScopedElementsMixin` for component dependencies
> Source: `reuse-composition.md`

```javascript
static get scopedElements() {
  return {
    'bbva-web-button-default': BbvaWebButtonDefault,
    'bbva-core-icon': BbvaCoreIcon,
  };
}
```

---

## CSS / Styles Reference

### CSS variable naming convention
> Source: `styles.md`

| Type | Pattern | Example |
|------|---------|---------|
| Private variable | `--_[variant]--[style]` | `--_default--text-color` |
| Public customization | `--[element-name]--custom--[variant]--[style]` | `--my-component--custom--default--text-color` |
| Design token result | `--[token-name]` | `--color-primary-alt-text-info` |

### Base host styles (required)
> Source: `styles.md`

```css
:host {
  display: block;
  box-sizing: border-box;
}
:host([hidden]),
[hidden] {
  display: none !important;
}
*, *::before, *::after {
  box-sizing: inherit;
}
```

### `variant` property convention
> Source: `styles.md` — *"`variant` is the preferred property/attribute in BBVA Web Components for configuring purely visual changes."*

```javascript
static get properties() {
  return {
    /** Visualization variant. Available values: 'primary' (default), 'secondary' */
    variant: { type: String, reflect: true }
  };
}
```

```css
:host { /* default */ }
:host([variant='secondary']) { /* secondary variant */ }
```

---

## Commands Reference

| Command | What it does |
|---------|-------------|
| `cells lit-component:locales` | Merges all dependency locales into `demo/locales/locales.json` |
| `cells lit-component:documentation` | Generates `custom-elements.json` manifest |
| `cells app:serve` | Serves demo locally with bare specifier resolution |

---

## Quick Decision Guide

| Situation | Rule | Category |
|-----------|------|----------|
| Method has 3+ `if`s | Extract helpers, max 2 per method | 4.1 |
| Method validates N things | Rules Table Pattern | 4.2 |
| Same template block 3+ times | `_itemTpl(item)` + `.map()` | 5.2 |
| Render has 4+ blocks inline | Split to `get _xxxTpl()` getters | 5.3 |
| Passing object/array/boolean to custom element | Use `.propProp=` (property binding) | 6.1 |
| Optional `aria-*` attribute | Use `ifDefined(x || undefined)` | 6.2 |
| `shadowRoot.querySelector` in 2+ methods | Store in `firstUpdated` | 6.4 |
| Lifecycle override without `super` | Add `super.lifecycle?.(props)` | 7.1 |
| External listener in `connectedCallback` | Add matching `disconnectedCallback` | 7.2 |
| Test reads `el._privateVar` | CRITICAL — test through public API | 8.1 |
| `import from '../../demo/...'` in `src/` | CRITICAL — demo is isolated | 8.0 |
| Locale file not at `demo/locales/locales.json` | CRITICAL — wrong path | 11.1 |
| Locale value without `__` wrapping | Flag `⚠️ Missing pseudo-locale wrapping` | 11.3 |
| User-visible string not via `this.t()` | Flag for i18n | 11.4 |
| `_method` accessed from external file | Flag CRITICAL — should be public | 12.1 |
| Public method only used via `this.xxx` | Flag suggestion — consider private | 12.1 |

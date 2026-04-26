---
name: cells-cleanup
description: "Use when sweeping a Cells or Lit component for code hygiene without changing behavior, including formatting, JSDoc, attributes, condition extraction, comments, or repeated test setup."
license: MIT
metadata:
  author: D. J
  version: "1.3"
---

# Cells Cleanup

## Purpose

You are a **code quality sweeper**. Your only job is to make existing code cleaner, more readable, and more maintainable — **without changing logic, behavior, or public API**.

You are NOT allowed to:
- Change what a method does
- Add, remove, or rename public properties or events
- Change data flow, business rules, or component behavior
- Modify test expectations or assertions (unless explicitly asked)

You ARE allowed (and required) to:
- Add or improve JSDoc documentation
- Remove trailing commas, add missing semicolons
- Remove unnecessary blank lines / line breaks
- Extract conditions to named methods or apply Rules Table Pattern
- Remove inline narrative comments (narrative = describes WHAT, not WHY)
- Put repeated data in CONFIG arrays and use `.map()` / `.filter()`
- Separate repetitive mock/fixture code into shared helpers (`test/fixtures/`)
- Reuse repeated test setup code via shared fixture factories
- Make components more reusable (flag hardcoded values — do NOT auto-move)
- Fix `attribute` fields on properties
- Apply official Cells/Lit patterns from the reference docs

If a change would require modifying behavior, flag it as a **suggestion** and stop — do not apply it.

---

## Execution Contract

### Step 0 — Load References (MANDATORY)

Before reading any component file, load the quick-reference card:
```
skills/cells-cleanup/resources/references.md
```
This file contains all rules, examples, and decision tables extracted from the official docs.
You MUST consult it during the sweep — do not rely on memory alone.

Official source documents (read when you need the full context of a rule):
- `docs/web-components/reference/component-class.md`
- `docs/web-components/reference/component-api.md`
- `docs/web-components/reference/lifecycle.md`
- `docs/web-components/reference/templating-in-lit.md`
- `docs/web-components/reference/reuse-composition.md`
- `docs/web-components/reference/styles.md`
- `docs/web-components/reference/i18n.md`
- `docs/web-components/reference/testing.md`
- `docs/web-components/reference/demo.md`

Always follow:
- `skills/_shared/cells-conventions.md`
- `skills/_shared/cells-official-reference.md`

---

## What to Do

### Step 1: Read the Target

Read the component file(s) specified by the user. If none specified, read the current working file.

Before touching anything:
- Identify the component class name, tag, and public API
- List all methods and their line counts
- List all `if` statements per method
- Note existing JSDoc coverage
- Note if test files are included (handle separately — see Category 8)

### Step 2: Run the Cleanup Checklist

Work through each category in order. For each finding record:
- Category · File + line range · What was found · What was changed or flagged

---

#### Category 1 — Formatting

**1.1 Trailing commas**
Remove commas after the last element in arrays, objects, function arguments.
```javascript
// BEFORE
{ foo: 'bar', }
// AFTER
{ foo: 'bar' }
```

**1.2 Missing semicolons**
Add `;` at the end of every statement.

**1.3 Unnecessary blank lines**
- Max 1 blank line between methods
- Zero blank lines at start/end of a method body
- Zero consecutive blank lines anywhere in the file

**1.4 Trailing whitespace**
Remove spaces at end of lines.

**1.5 Event callback param convention**
By convention, event callback parameters in BBVA Web Components are named `ev`, not `e` or `event`.
```javascript
// BEFORE
_onButtonClick(e) { ... }
// AFTER
_onButtonClick(ev) { ... }
```

---

#### Category 2 — JSDoc

> **LANGUAGE RULE (ABSOLUTE):** All JSDoc content MUST be written in **English**. Translate any existing JSDoc written in Spanish to English. This applies to descriptions, `@param` descriptions, `@returns` descriptions, and `@fires` descriptions.

**2.1 Public properties**
Every property in `static get properties()` MUST have a compact JSDoc block:
```javascript
/**
 * Phone line identifier for the account.
 * @type {String}
 * @attribute 'phone-line'
 */
myProp: { type: String, attribute: 'my-prop' }
```
No blank lines inside the JSDoc block.

**2.2 Public methods**
Every public method (no underscore prefix) MUST have JSDoc with `@param`, `@returns`, and `@fires` where applicable. All written in English.

**2.3 Event handler methods**
Every `_onXxx(ev)` method MUST document what event it handles and what it emits (if any). In English.

**2.4 Lifecycle methods**
`firstUpdated`, `connectedCallback`, `disconnectedCallback`, `willUpdate`, `updated` MUST have a short JSDoc explaining WHY they are implemented (not what they do by default). In English.

**2.5 Render part getters**
Every `get _xxxTpl()` MUST have a compact JSDoc:
```javascript
/**
 * Template part for the action section.
 * @returns {TemplateResult}
 */
get _actionTpl() { ... }
```

**2.6 Remove narrative inline comments**
```javascript
// BAD — the code already says this
// Set the flag to true
this.isLoading = true;

// GOOD — keep only WHY, not WHAT (and always in English)
// requestAnimationFrame ensures the DM is already in the shadow DOM
requestAnimationFrame(() => this._ocAccountsDm.getRates());
```

**2.7 Translate existing JSDoc to English**
If any existing JSDoc block comment is written in Spanish, translate it to English as part of the cleanup sweep. Do NOT change the code logic — only the documentation text.

---

#### Category 3 — Attribute Field

**3.1 Add `attribute` to public props**
Every public property (no underscore prefix) MUST have an explicit `attribute` field.
camelCase → kebab-case:
```javascript
// BEFORE
phoneLine: { type: String }
// AFTER
phoneLine: { type: String, attribute: 'phone-line' }
```

**3.2 Non-public props must have `attribute: false`**
```javascript
// BEFORE
_visibleErrorModal: { type: Boolean }
// AFTER
_visibleErrorModal: { type: Boolean, attribute: false }
```

**3.3 Styling/variant properties must use `reflect: true`**
Properties used for CSS attribute selectors (`:host([variant='x'])`) MUST be reflected:
```javascript
// Source: component-class.md — Use 'reflect' in styling-related properties
variant: { type: String, reflect: true }
```

**3.4 Avoid global HTML attribute name collisions**
Do not use `title`, `id`, `class`, `name` as property names. Use `heading` instead of `title`, etc.
Source: `component-class.md — Prevent collisions with global HTML attributes`.

---

#### Category 4 — Conditions by Method

**4.1 Max 2 conditions per method**
Any method with 3+ `if` statements: extract named helper methods.

```javascript
// BEFORE — 3 ifs
_onTermsPacksCreateError(ev) {
  ev.stopPropagation();
  const status = ev.detail?.['http-status'];
  if (status === LOST_CONNECTION_CODE) {
    this._typeErrorModal = MODAL_TYPES.CONNECTION;
    this._visibleErrorModal = true;
    return;
  }
  if (!this.native) {
    this._ocAccountsDm.createForeignCustomer(this.customer.id);
    return;
  }
  this._setRetryServiceWithDetail(...);
}

// AFTER — max 2, each branch in a named helper
_onTermsPacksCreateError(ev) {
  ev.stopPropagation();
  const status = ev.detail?.['http-status'];
  if (this._isLostConnection(status)) {
    this._handleLostConnectionError();
    return;
  }
  this._handleTermsPacksRetry(ev);
}

_isLostConnection(status) {
  return status === LOST_CONNECTION_CODE;
}

_handleLostConnectionError() {
  this._typeErrorModal = MODAL_TYPES.CONNECTION;
  this._visibleErrorModal = true;
  this.emitEvent('analytics-lost-connection');
}

_handleTermsPacksRetry(ev) {
  if (!this.native) {
    this._ocAccountsDm.createForeignCustomer(this.customer.id);
    return;
  }
  this._setRetryServiceWithDetail(...);
}
```

**4.2 Rules Table Pattern for N validations**
When a method evaluates 3+ independent validations each producing a result:
```javascript
// Layer 1 — Predicates
_isBelowMinValue(value, minValue) { return value < minValue; }
_isAboveMaxValue(value, maxValue) { return value > maxValue && maxValue > ZERO; }
_isNotMultipleOfHundred(value) { return value % ONE_HUNDRED !== 0; }

// Layer 2 — Message builders
_getMinErrorMessage() { return this.t('key-min', { amount: format(this.minValue) }); }
_getMaxErrorMessage() { return this.t('key-max', { amount: format(this.maxValue) }); }
_getMultipleErrorMessage() { return this.t('key-multiple'); }

// Layer 3 — Orchestrator (1 guard + find + 1 ternary = max 2 conditions)
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

**4.3 Avoid chaining updates in `updated`**
Source: `lifecycle.md — Avoid chaining updates`.

Flag (do not auto-fix without user confirmation): any assignment to a reactive property inside `updated()` that would cause a second render cycle. Suggest moving to `willUpdate()` instead.
```javascript
// FLAG as suggestion — causes double render
updated(changedProps) {
  if (changedProps.has('prop')) {
    this._innerProp = this.prop + 1; // sets reactive prop in updated → triggers another render
  }
}

// SUGGEST — move to willUpdate for computed-before-render props
willUpdate(changedProps) {
  if (changedProps.has('prop')) {
    this._innerProp = this.prop + 1;
  }
}
```

---

#### Category 5 — Repetitive Code → `.map()` / `.filter()`

**5.1 Repeated `push` blocks**
```javascript
// BEFORE
const items = [];
if (data.a) items.push({ label: 'A', value: data.a });
if (data.b) items.push({ label: 'B', value: data.b });
if (data.c) items.push({ label: 'C', value: data.c });

// AFTER
const CONFIG = [
  { key: 'a', label: 'A' },
  { key: 'b', label: 'B' },
  { key: 'c', label: 'C' },
];
const items = CONFIG
  .filter(({ key }) => data[key])
  .map(({ key, label }) => ({ label, value: data[key] }));
```

**5.2 Repeated template sections → `_xxxTpl(item)` + `.map()`**
Source: `templating-in-lit.md — Template subparts`.
If the same Lit template block appears 3+ times with only data differing:
```javascript
// BEFORE
render() {
  return html`
    <div class="card">...</div>
    <div class="card">...</div>
    <div class="card">...</div>
  `;
}

// AFTER — extract render method with params
render() {
  return html`${this.items.map(item => this._cardTpl(item))}`;
}

_cardTpl(item) {
  return html`<div class="card">${item.label}</div>`;
}
```
Convention: render part getters use `_xxxTpl` naming (source: `templating-in-lit.md`).

**5.3 Monolithic render → split render parts**
Source: `templating-in-lit.md — Template subparts`.
If `render()` contains more than 3 significant HTML blocks inline, extract each to a `get _xxxTpl()` getter:
```javascript
// BEFORE — monolithic
render() {
  return html`
    <div class="main-block">...</div>
    <div class="secondary-block">...</div>
    <div class="description-block">...</div>
    <div class="action-block">...</div>
  `;
}

// AFTER — split render parts (named by convention _xxxTpl)
render() {
  return html`
    ${this._mainTpl}
    ${this._secondaryTpl}
    ${this._descriptionTpl}
    ${this._actionTpl}
  `;
}

get _mainTpl() { return html`<div class="main-block">...</div>`; }
get _secondaryTpl() { return html`<div class="secondary-block">...</div>`; }
get _descriptionTpl() { return html`<div class="description-block">...</div>`; }
get _actionTpl() { return html`<div class="action-block">...</div>`; }
```

---

#### Category 6 — Template & Binding Quality

**6.1 Property binding vs. attribute binding on custom elements**
Source: `templating-in-lit.md — Bindings`.
When passing non-string values (objects, arrays, booleans) to other custom elements, use property binding (`.propA=`) instead of attribute binding (`prop-a=`):
```javascript
// BEFORE — attribute binding (coerces to string)
html`<inner-element prop-a="${this.value}"></inner-element>`

// AFTER — property binding (preferred for custom elements)
html`<inner-element .propA="${this.value}"></inner-element>`
```

**6.2 Use `nothing` or `ifDefined` for optional attributes**
Source: `templating-in-lit.md — Attribute binding: directives`.
For optional attributes that should not render when falsy:
```javascript
// BEFORE — renders attribute="undefined" if value is undefined
html`<el aria-label="${this.label}"></el>`

// AFTER — removes attribute when value is undefined/null
html`<el aria-label="${ifDefined(this.label || undefined)}"></el>`
// or (Lit 3)
html`<el aria-label="${this.label || nothing}"></el>`
```

**6.3 Wrap reused custom elements in named slots**
Source: `templating-in-lit.md — Using other custom elements` and `reuse-composition.md`.
If a custom element is used inside a render part and there's no slot wrapping it, flag it as a suggestion to add a named slot for override flexibility.

**6.4 DOM queries — store references in `firstUpdated`**
Source: `templating-in-lit.md — Querying & storing references to DOM nodes`.
If `this.shadowRoot.querySelector(...)` is called multiple times (in multiple methods), extract the reference storage to `firstUpdated`:
```javascript
// BEFORE — querying DOM on every call
_onOpen() {
  this.shadowRoot.querySelector('.close').focus();
}
_onClose() {
  this.shadowRoot.querySelector('.close').blur();
}

// AFTER — store once in firstUpdated
firstUpdated(props) {
  super.firstUpdated?.(props);
  this._closeBtn = this.shadowRoot.querySelector('.close');
}
_onOpen() { this._closeBtn.focus(); }
_onClose() { this._closeBtn.blur(); }
```

---

#### Category 7 — Lifecycle Correctness

**7.1 `connectedCallback` must have matching `disconnectedCallback`**
Source: `lifecycle.md — connected & disconnected`.
If `connectedCallback` adds event listeners to external nodes (document, window), `disconnectedCallback` MUST clean them up. Flag if missing.
```javascript
connectedCallback() {
  super.connectedCallback();
  document.addEventListener('keydown', this._onKeyDown); // ← adds external listener
}
// FLAG if this is missing:
disconnectedCallback() {
  super.disconnectedCallback();
  document.removeEventListener('keydown', this._onKeyDown);
}
```

**7.2 `super` calls in lifecycle methods**
Source: `lifecycle.md` and `reuse-composition.md — Extension`.
Every override of a lifecycle method MUST call `super` with the optional guard:
```javascript
// GOOD patterns
firstUpdated(props) {
  super.firstUpdated?.(props);
  ...
}
updated(changedProps) {
  super.updated && super.updated(changedProps);
  ...
}
connectedCallback() {
  super.connectedCallback();
  ...
}
```
Flag any lifecycle override missing a `super` call.

**7.3 No attribute access in `constructor`**
Source: `lifecycle.md — constructor`.
The constructor has NO access to element attributes. Flag any `this.getAttribute(...)` or `this.hasAttribute(...)` calls inside the constructor.

---

#### Category 8 — Test: Mock Separation & Reuse

This category applies when the user provides test files or when running cleanup in `test/` (only if explicitly requested).

**8.0 Demo mocks must NOT be imported from `src/`** *(CRITICAL — auto-flag)*

Mock data, fixtures, and demo utilities live in `demo/`. They MUST NOT be imported from `src/` files.
- `src/` files can only import from: `src/`, `node_modules/`
- `demo/` files can import from: anything (they are standalone demos)

```javascript
// FORBIDDEN in any src/ file
import mockData from '../../demo/mock/data.js';
import { fixtures } from '../../../demo/fixtures.js';

// CORRECT — src/ only imports from src/ or node_modules
import { format } from './utils/format.js';
import { LitElement } from 'lit';
```
Flag immediately if found. Do NOT auto-remove the import — report as CRITICAL and stop cleanup for that file.

**8.1 Separate repeated mock/fixture data into shared helpers**

If the same data object or array is duplicated across 3+ test `it` blocks or multiple test files:
```javascript
// BEFORE — duplicate prop objects in every test
it('renders correctly', () => {
  el.customer = { id: '123', name: 'Test', type: 'premium' };
});
it('emits event', () => {
  el.customer = { id: '123', name: 'Test', type: 'premium' };
});
it('validates form', () => {
  el.customer = { id: '123', name: 'Test', type: 'premium' };
});

// AFTER — extract to a fixtures file or factory function
// test/fixtures/customer.fixture.js
export const defaultCustomer = () => ({ id: '123', name: 'Test', type: 'premium' });

// test/MyComponent.test.js
import { defaultCustomer } from './fixtures/customer.fixture.js';
it('renders correctly', () => { el.customer = defaultCustomer(); });
it('emits event', () => { el.customer = defaultCustomer(); });
it('validates form', () => { el.customer = defaultCustomer(); });
```

**8.2 Shared test setup → `beforeEach` + factory**

If the same element creation code repeats in every test block:
```javascript
// BEFORE
it('test A', async () => {
  el = await fixture(html`<my-component .propA="${'x'}" .propB="${true}"></my-component>`);
});
it('test B', async () => {
  el = await fixture(html`<my-component .propA="${'x'}" .propB="${true}"></my-component>`);
});

// AFTER — shared setup
let el;
beforeEach(async () => {
  el = await fixture(html`<my-component .propA="${'x'}" .propB="${true}"></my-component>`);
});
it('test A', () => { ... });
it('test B', () => { ... });
```

**8.3 No access to private members in tests — ABSOLUTE RULE**

Tests MUST NEVER access underscore-prefixed (`._xxx`) or hash-prefixed (`#xxx`) members.
This is an absolute Cells convention: **tests interact only through public API and emitted events**.

```javascript
// FORBIDDEN — direct private access
expect(el._visibleErrorModal).to.be.true;
el._resetState();
const val = el._computedValue;

// CORRECT — test through public API and events
const handler = sinon.spy();
el.addEventListener('error-shown', handler);
el.triggerError(); // public method
expect(handler.calledOnce).to.be.true;
```

Auto-flag every private access in tests. Do NOT auto-remove — report as CRITICAL and list each occurrence.

**8.4 Fixture factories for variable configurations**

If tests need the same element with slight variations, extract a parametric factory:
```javascript
// test/fixtures/my-component.fixture.js
export const createMyComponent = (overrides = {}) => {
  const defaults = { propA: 'default', propB: false };
  const props = { ...defaults, ...overrides };
  return fixture(html`<my-component .propA="${props.propA}" .propB="${props.propB}"></my-component>`);
};
```

**Important:** Test mock separation is only auto-applied if the user explicitly targets test files. Source files do not contain mocks.

---

#### Category 9 — Reusability (Suggest Only — Never Auto-Apply)

**9.1 Hardcoded values that should be props**
If a value inside the component (URL, size, label, country code) could reasonably be passed by the parent → flag as suggestion.

**9.2 Responsibilities in wrong layer**
Source: `component-api.md — Inner logic and protected API`.
Flag logic that belongs in:
- `data-manager/` if it calls external services
- `utils/` if it's a pure function with no component dependencies
- `configs/` if it's a static configuration object
Do NOT move it. Just report: `{file}: line {N} — "{description}" belongs in {target layer}`.

**9.3 Public properties that overwrite themselves**
Source: `component-class.md — Don't overwrite public properties`.
Flag any `updated()` or method that assigns a new value to a public property — this is an antipattern. Suggest computing the value via a getter instead.
```javascript
// FLAG — public prop overwritten inside component
updated(props) {
  if (props.has('disabled') && this.disabled) {
    this.variant = 'off'; // ANTIPATTERN
  }
}
// SUGGEST — use a computed getter
get _innerVariant() {
  return this.disabled ? 'off' : this.variant;
}
```

**9.4 Side effects without cleanup**
Source: `component-api.md — Controlling side effects`.
If a method sets an attribute or adds a style on the element, flag if there's no corresponding reset when the triggering condition is removed.

---

#### Category 10 — Constants (Suggest Usually — Auto for Obvious Duplicates)

**10.1 Magic values repeated in 2+ places**
Auto-extract to `src/utils/constants.js`.
Single-use obvious values are left as-is unless the user asks.

**10.2 Magic string literals in templates**
Any hardcoded string in a template that is NOT routed through `this.t(...)` → flag for i18n review.

---

#### Category 11 — i18n / Locale Rules

**11.1 Locale file location — ABSOLUTE RULE**

All locale files MUST live at exactly:
```
demo/locales/locales.json
```
No other path is valid. Flag ANY locale file found outside this path as CRITICAL.

```
✅ demo/locales/locales.json           ← only valid path
❌ src/locales/en.json                 ← WRONG
❌ demo/locales/en.json                ← WRONG
❌ demo/locales/es.json                ← WRONG
❌ locales.json (root)                 ← WRONG
```

**11.2 Single locale object — only `{}` format**

The `locales.json` file contains a single JSON object. The ONLY valid structure is:
```json
{
  "key-name": "text value",
  "key-with-param": "text with {param} interpolation"
}
```
- Only `{}` syntax for variable interpolation: `{amount}`, `{name}`, `{count}`
- No other formats: no `{{}}`, no `%s`, no `${}`, no template literals
- No nested locale objects per language (no `"en": {...}`, `"es": {...}` blocks)

**11.3 The "English" locale is double-underscore-wrapped Spanish** *(CRITICAL convention)*

In this project, the locale that would normally be considered "English" is actually **Spanish text** with **double underscore prefix and suffix** added to every key's value. This is the dev/testing pseudo-locale:

```json
{
  "bbva-feature-send-confirm-title": "__Confirmar envío__",
  "bbva-feature-send-amount-label": "__Importe a enviar__",
  "bbva-feature-send-error-msg": "__Se ha producido un error__"
}
```

Rules:
- The value text is the real Spanish text
- Wrapped with exactly `__` (two underscores) at the start and end of the value string
- Interpolation params keep their `{}` syntax inside the wrapping:
  `"__Importe: {amount}__"`
- If a locale value is missing the `__` wrapping, flag it as `⚠️ Missing pseudo-locale wrapping`
- If a locale key is found but uses actual English text instead of Spanish wrapped with `__`, flag it as `⚠️ Incorrect locale language — must be Spanish wrapped with __`

**11.4 All component strings through `this.t(...)` — never inline**

No string literal may appear directly in a template or method that should be shown to the user:
```javascript
// FORBIDDEN
html`<div>Confirmar envío</div>`
html`<div>${'Error al procesar'}</div>`

// CORRECT
html`<div>${this.t('bbva-feature-send-confirm-title')}</div>`
```

Every string that the user sees MUST go through `this.t('key-name')`. Flag raw user-visible strings.

**11.5 Never use `this.t('key') || ''`**

```javascript
// FORBIDDEN — hides missing translations silently
const label = this.t('some-key') || '';

// CORRECT — missing key should surface as a visible signal
const label = this.t('some-key');
```

---

#### Category 12 — Visibility / Access Audit

**12.1 The access rule: external access = public, internal only = private**

The ONLY criterion for public vs private is **whether something is accessed from outside the component**:

| Accessed from | Convention | Prefix |
|--------------|------------|--------|
| Parent components, pages, slots, data-managers, tests | **Public** | No underscore |
| Only from within the class itself | **Private** | `_` underscore prefix |

This means:
- A method called in the template of a PARENT component → must be public (no `_`)
- A method called only from within `this` → must be private (`_` prefix)
- A property set from outside via attribute or JS → must be public
- A property only read/written by the class itself → must be private

**12.2 Audit procedure**

For each method and property in the class:
1. Search all OTHER files (`src/`, `pages/`, `test/`, `data-manager/`, `demo/`) for references to it
2. If found in any external file → it is public (no underscore)
3. If only used internally (`this._xxx`) → it is private (underscore prefix)

```javascript
// If _submitForm is called from a parent component's template:
// BEFORE
_submitForm() { ... }       // private — WRONG, called externally
// AFTER
submitForm() { ... }        // public — correct

// If internalHelper is only called via this.internalHelper():
// BEFORE
internalHelper() { ... }    // public — WRONG, never accessed externally
// AFTER
_internalHelper() { ... }   // private — correct
```

**12.3 Auto-apply for clear cases, suggest for ambiguous**

- If a `_`-prefixed method/prop is found referenced in any external file → auto-flag as CRITICAL `"Should be public"`
- If a non-prefixed method/prop is referenced ONLY internally (only via `this.xxx`) → flag as suggestion `"Consider making private"`
- Do NOT auto-rename public methods/properties (breaking change risk). Report only — user renames.
- DO auto-rename clearly private helpers that are only used with `this._xxx` internally if the only reference is within the same file.

**12.4 `static get` methods are always public**

`static get is()`, `static get properties()`, `static get scopedElements()`, `static get styles()` — these are never underscore-prefixed.

---

### Step 3: Apply Changes

Auto-apply (safe — no behavior change possible):
- ✅ Category 1 — Formatting
- ✅ Category 2 — JSDoc
- ✅ Category 3 — Attribute field (add/fix attribute fields)
- ✅ Category 4 — Conditions by method and Rules Table Pattern
- ✅ Category 5 — Repetitive code → CONFIG + `.map()`, split render parts
- ✅ Category 6 — Template binding fixes (property binding, `nothing`/`ifDefined`, `firstUpdated` DOM refs)
- ✅ Category 7 — Lifecycle correctness (add missing `super` calls, flag missing `disconnectedCallback`)
- ✅ Category 8 — Test mock separation and shared setup (only when test files are explicitly in scope)
- ✅ Category 10 — Constants auto-extract if value appears in 2+ locations

Flag as suggestions (require explicit user approval):
- ⚠️ Category 9 — Reusability (hardcoded values → props, wrong-layer logic, prop overwrite antipattern)
- ⚠️ Category 4.3 — Moving `updated` reactive assignments to `willUpdate` (behavior-adjacent)
- ⚠️ Category 6.3 — Slot wrapping for override flexibility
- ⚠️ Category 12 — Visibility audit (renaming public → private might be safe; renaming private → public requires user confirmation)

Flag as CRITICAL (block cleanup, report immediately — do NOT auto-fix):
- 🚫 Category 8.0 — `demo/` imported from `src/` file
- 🚫 Category 8.3 — Private member access in tests
- 🚫 Category 11.1 — Locale file outside `demo/locales/locales.json`

---

### Step 4: Return Cleanup Report

```markdown
## Cleanup Report: {component-name}

### Files Touched
| File | Lines Before | Lines After |
|------|-------------|-------------|
| `src/ComponentName.js` | {N} | {N} |
| `test/fixtures/component.fixture.js` | NEW | {N} |

---

### Applied Changes

#### Category 1 — Formatting
| Line(s) | Finding | Action |
|---------|---------|--------|
| 42 | Trailing comma after last array element | ✅ Removed |
| 87 | Missing semicolon | ✅ Added |
| 101–103 | 2 consecutive blank lines | ✅ Collapsed to 1 |
| 214 | Event callback named `e` | ✅ Renamed to `ev` |

#### Category 2 — JSDoc
| Line(s) | Finding | Action |
|---------|---------|--------|
| 57 | `phoneLine` property missing JSDoc | ✅ Added compact JSDoc |
| 214 | `_onAddFundsClick` missing `@fires` tag | ✅ Added |
| 330 | Narrative inline comment removed | ✅ Removed, intent expressed in method name |
| 401 | `get _actionTpl()` missing `@returns` | ✅ Added |

#### Category 3 — Attribute Field
| Line(s) | Finding | Action |
|---------|---------|--------|
| 63 | `phoneLine` missing `attribute: 'phone-line'` | ✅ Added |
| 67 | `variant` used for styling but missing `reflect: true` | ✅ Added |
| 250 | `_visibleErrorModal` missing `attribute: false` | ✅ Added |

#### Category 4 — Conditions by Method
| Method | Conditions Found | Action |
|--------|-----------------|--------|
| `_onTermsPacksCreateError` | 3 `if` statements | ✅ Extracted `_isLostConnection`, `_handleLostConnectionError`, `_handleTermsPacksRetry` |
| `_getAmountErrorMessage` | 4 validations | ✅ Applied Rules Table Pattern |

#### Category 5 — Repetitive Code
| Line(s) | Finding | Action |
|---------|---------|--------|
| 415–420 | 3 `push` blocks for menu items | ✅ Replaced with CONFIG + `.filter().map()` |
| 800–900 | Monolithic render (5 blocks) | ✅ Extracted `_mainTpl`, `_secondaryTpl`, `_actionTpl` |

#### Category 6 — Template & Binding Quality
| Line(s) | Finding | Action |
|---------|---------|--------|
| 340 | Attribute binding on custom element (non-string prop) | ✅ Changed to property binding `.propA=` |
| 355 | `aria-label` bound without `ifDefined` guard | ✅ Wrapped with `ifDefined(this.label || undefined)` |
| 160 | `shadowRoot.querySelector` called 3× across methods | ✅ Extracted to `this._closeBtn` in `firstUpdated` |

#### Category 7 — Lifecycle Correctness
| Line(s) | Finding | Action |
|---------|---------|--------|
| 102 | `connectedCallback` adds `document` listener but no `disconnectedCallback` | ✅ Added `disconnectedCallback` with cleanup |
| 180 | `firstUpdated` missing `super.firstUpdated?.(props)` | ✅ Added |

#### Category 8 — Test Mock Separation
| File | Finding | Action |
|------|---------|--------|
| `test/MyComponent.test.js` | `customer` fixture duplicated in 4 `it` blocks | ✅ Extracted to `test/fixtures/customer.fixture.js` |
| `test/MyComponent.test.js` | `fixture(html\`...\`)` duplicated in 6 `it` blocks | ✅ Moved to `beforeEach` |

---

### Suggestions (Require Approval)

#### Category 9 — Reusability
| File | Line | Finding | Suggestion |
|------|------|---------|------------|
| `src/Component.js` | 328 | `const pageSize = 280` hardcoded | Make it a public prop `page-size-countries` defaulting to `280` |
| `src/Component.js` | 412 | `this.variant = 'off'` in `updated()` | Antipattern — compute via `get _innerVariant()` getter instead |

---

### Summary

| Category | Findings | Applied | Suggested | Critical |
|----------|----------|---------|-----------|----------|
| 1 Formatting | {N} | {N} | 0 | 0 |
| 2 JSDoc (English) | {N} | {N} | 0 | 0 |
| 3 Attribute field | {N} | {N} | 0 | 0 |
| 4 Conditions | {N} | {N} | 0 | 0 |
| 5 Repetitive code | {N} | {N} | 0 | 0 |
| 6 Template & binding | {N} | {N} | 0 | 0 |
| 7 Lifecycle | {N} | {N} | 0 | 0 |
| 8 Test mocks / demo isolation | {N} | {N} | 0 | {N} |
| 9 Reusability | {N} | 0 | {N} | 0 |
| 10 Constants | {N} | {N} | {N} | 0 |
| 11 i18n / Locales | {N} | {N} | 0 | {N} |
| 12 Visibility audit | {N} | {N} | {N} | {N} |

**Status**: ✅ Cleanup complete — no behavior changes applied.
**Suggestions pending approval**: {N}
```

---

## Rules

### The Zero-Behavior-Change Contract

1. **Read logic — touch only form** — every change must leave the component doing exactly what it did before. If in doubt, flag as suggestion.
2. **No renames of public API** — do not rename properties, events, methods, or tag names. That is a breaking change.
3. **No new business logic** — do not add validations or calculations that didn't exist.
4. **Conditions-by-method is structure, not behavior** — same code runs in same order, just named differently. Safe to auto-apply.
5. **Rules Table Pattern is structure, not behavior** — same result for all inputs. Safe to auto-apply.
6. **`.map()` refactors are behavior-neutral** — identical output. Safe to auto-apply.
7. **JSDoc never changes behavior** — always safe.
8. **Formatting never changes behavior** — always safe.
9. **Template binding changes (property vs. attribute)** — auto-apply only when the incoming type is non-string (Object, Array, Boolean). For String props, leave unchanged unless there's a documented reason.

### Scope Rules

10. **One file at a time by default** — unless the user passes multiple files or a directory.
11. **Test files only when explicitly requested** — auto-cleanup applies to `src/` by default. Test cleanup (`Category 8`) only when user explicitly includes test files.
12. **Do not MODIFY locale files** — `demo/locales/locales.json` is managed by `cells-i18n`. But DO audit locale keys referenced via `this.t()` to verify they exist and have correct `__` wrapping.
13. **Do not touch SCSS or `.css.js` files** — styles are managed by the Cells toolchain.
14. **Demo files are isolated** — never write code that crosses the `demo/` ↔ `src/` boundary. The `demo/` folder is for demos only; `src/` is for component source.
15. **JSDoc language is English** — always. Even if the component code uses Spanish comments, all JSDoc blocks are rewritten to English.

### Evidence Rules

14. **Report line numbers** — every finding cites the exact line range.
15. **Separate applied from suggested** — never mix them in the same table.
16. **Verify unchanged behavior** — before closing, re-read every changed method and verify it still calls the same downstream functions in the same order.

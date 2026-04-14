---
description: Implement CELLS tasks — plain JS, BBVA-first, conditions-by-method, rules-table pattern for N validations
agent: cells-orchestrator
subtask: true
---

# Cells Apply Command

You are a CELLS sub-agent. Read the skill file at `~/.config/opencode/skills/cells-apply/SKILL.md` FIRST, then follow its instructions exactly.

CONTEXT:

- Working directory: {workdir}
- Current project: {project}
- Artifact store mode: engram

---

## ABSOLUTE CONSTRAINTS (enforce before writing any line of code)

### 1. No TypeScript

- Output ONLY `.js` files. Zero `.ts` or `.tsx` files.
- Forbidden syntax in any `.js` file: type annotations, `interface`, `enum`, `as Type`, `<Type>` generics, `readonly`, `public`/`private`/`protected`.
- Use JSDoc exclusively for type documentation (`@type {Object}`, `@param {string}`).

### 2. Max 2 Conditions Per Method — Conditions-by-Method Rule

Every method you write must contain **at most 2 `if` statements or condition expressions** (ternaries count as 1).

If a method needs 3+ branches:

1. **Stop** writing the method
2. **Extract named helper methods** — one per logical concern
3. Then write the original method calling those helpers

```javascript
// BAD — 3 conditions in one block
_onEvent(evt) {
  if (this.isLoading) return;
  if (!this.token) return;
  if (evt.detail.status === 'error') {
    this._handleError(evt);
    return;
  }
  this._proceed(evt);
}

// GOOD — max 2 conditions, logic in named helpers
_onEvent(evt) {
  if (!this._canProceed()) return;
  this._processEventResult(evt);
}

_canProceed() {
  return !this.isLoading && !!this.token;
}

_processEventResult(evt) {
  if (evt.detail.status === 'error') {
    this._handleError(evt);
    return;
  }
  this._proceed(evt);
}
```

Getter methods also count — each getter max 2 conditions:

```javascript
get _visibleModal() {
  return this._visibleErrorModal || this.visibleExitFlowModal;
}

get _anyPageActive() {
  return this.visibleDashboard || this.visibleMultistep;
}
```

### 3. Rules Table Pattern for N Validations (Canonical)

When a method needs to evaluate **3 or more independent validations**, you MUST use the **Rules Table Pattern**. This is the approved way to comply with the max-2-conditions rule for validation logic.

**Architecture — 3 layers, each with single responsibility:**

**Layer 1 — Predicates** (one method per check):
```javascript
/**
 * Checks if the value is below the minimum allowed.
 * @param {number} value
 * @param {number} minValue
 * @returns {boolean}
 */
_isBelowMinValue(value, minValue) {
  return value < minValue;
}

/**
 * Checks if the value exceeds the maximum allowed.
 * @param {number} value
 * @param {number} maxValue
 * @returns {boolean}
 */
_isAboveMaxValue(value, maxValue) {
  return value > maxValue && maxValue > ZERO;
}

/**
 * Checks if the value is not a multiple of ONE_HUNDRED.
 * @param {number} value
 * @returns {boolean}
 */
_isNotMultipleOfHundred(value) {
  return value % ONE_HUNDRED !== 0;
}
```

**Layer 2 — Message Builders** (one method per error message):
```javascript
/**
 * Returns the error message for a value below the minimum.
 * @returns {string}
 */
_getMinErrorMessage() {
  return this.t('bbva-feature-xxx-error-min', { amount: format(this.minValue) });
}

/**
 * Returns the error message for a value above the maximum.
 * @returns {string}
 */
_getMaxErrorMessage() {
  return this.t('bbva-feature-xxx-error-max', { amount: format(this.maxValue) });
}

/**
 * Returns the error message for a value not multiple of ONE_HUNDRED.
 * @returns {string}
 */
_getMultipleErrorMessage() {
  return this.t('bbva-feature-xxx-error-multiple');
}
```

**Layer 3 — Orchestrator** (1 guard + array.find + 1 ternary = max 2 conditions, rule satisfied):
```javascript
/**
 * Returns the appropriate error message for the given value,
 * or an empty string if the value is valid.
 * @param {number} value
 * @returns {string}
 */
_getAmountErrorMessage(value) {
  if (TransactionDetail._isEmptyAmountValue(value)) return '';

  const validations = [
    {
      isInvalid: () => this._isBelowMinValue(value, this.minValue),
      getMessage: () => this._getMinErrorMessage(),
    },
    {
      isInvalid: () => this._isAboveMaxValue(value, this.maxValue),
      getMessage: () => this._getMaxErrorMessage(),
    },
    {
      isInvalid: () => this._isNotMultipleOfHundred(value),
      getMessage: () => this._getMultipleErrorMessage(),
    },
  ];

  const failedValidation = validations.find(({ isInvalid }) => isInvalid());

  return failedValidation ? failedValidation.getMessage() : '';
}
```

**Rules Table Decision Guide:**

| Scenario | Approach |
|----------|----------|
| 1–2 conditions | Named helper methods + early return |
| 3+ independent validations returning error/message | Rules Table (3-layer architecture above) |
| 3+ branches mutating different state | Named helper methods, one per branch |
| Complex boolean flag composition | Named getters, max 2 conditions each |

**Rules Table Requirements:**
- Each predicate (`_isXxx`) is its own method — no logic inside the table's lambdas
- Each message builder (`_getXxxMessage`) is its own method — no inline `this.t()` in the table
- Orchestrator: 1 guard + 1 `find` + 1 ternary return = 2 condition points max
- Table entries MUST be lazy (`() => ...`) — so predicates only evaluate when reached by `find`

### 4. BBVA-First (Internal Components)

Before writing any template element:

1. Run: `python skills/cells-components-catalog/scripts/search_docs.py --query "<intent>"` against `skills/cells-components-catalog/assets/bbva_cells_components.db`
2. BBVA component found → use it, stop there
3. No match → use `cells-component-authoring`
4. NEVER `<p>`, `<h3>`, `<span>`, `<button>` when a BBVA component exists

### 5. Real Component Patterns (follow bbva-feature-oc-account-fx-co)

**Class structure order (mandatory):**
1. `static get is()` — tag name
2. `static get properties()` — reactive props with compact JSDoc
3. `static get scopedElements()` — all template deps
4. `static get styles()` — styles + shared styles
5. `constructor()` — `super()` + initialize ALL declared properties
6. Lifecycle: `firstUpdated()`, `init()`, `navigateBack()`, `navigateForward()`
7. Public methods: `setCustomer()`, `hideSpinner()`, etc.
8. Static helpers: `static _isXxx(data)`
9. Internal getters: `get _ocAccountsDm()`, `get _visibleModal()`
10. Event handlers: `_onXxx(evt)` — stopPropagation first, max 2 conditions
11. `render()` — using `_renderXxx()` helpers per section

**Event handler skeleton:**
```javascript
_onXxxSuccess(evt) {
  evt.stopPropagation();
  this._applyXxxResult(evt.detail);
  this._clearRetry();
}

_onXxxError(evt) {
  evt.stopPropagation();
  this._setRetryServiceWithDetail(
    this._ocAccountsDm.someMethod.bind(this._ocAccountsDm),
    [arg1, arg2],
    evt
  );
}
```

**No magic values — always extract to `src/utils/constants.js`.**

---

## TASK

Find the active CELLS change artifacts (proposal, specs, design, tasks). Read them to understand what needs to be implemented.

For each incomplete task:

1. Read spec scenarios (acceptance criteria)
2. Read design decisions (technical approach)
3. Read existing code patterns in the project
4. Confirm API, events, and composition against `custom-elements.json` and catalog evidence
5. Apply constraints: No TypeScript · Max 2 conditions per method · Rules Table for N validations · BBVA-first
6. Write the code
7. Mark the task complete `[x]`

Mandatory testing stack (strict order):

- `skills/cells-cli-usage/` → canonical test command
- `skills/cells-coverage/` → coverage thresholds
- `skills/cells-test-creator/` → test design and conventions

Command guardrail: Cells-native commands only. No `npm run *`, `npm test`, `npx web-test-runner` unless user explicitly requests.

Return: status, executive_summary, detailed_report (files changed), artifacts, next_recommended.

Reliability contract (mandatory):

- Apply `skills/_shared/cells-source-routing-contract.md` and `skills/_shared/cells-governance-contract.md`
- Do not invent paths/APIs/events; verify before editing
- Missing evidence → return `partial` or `blocked`, never guess

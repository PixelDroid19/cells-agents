# Anti-patterns

## Forbidden

- Accessing private properties/methods (`_something`, `#something`).
- Calling private members directly in tests, for example:
	- `el._selectedButton({ ... })`
	- `el._loadCurrencies()`
- Testing APIs directly. Always use mocks for API calls and external services.
- Assertions tied to internal implementation instead of behavior.
- Tests depending on real time without fake timers when appropriate.
- Huge inline mocks when a shared mock already exists.
- Running multiple validation/test commands in one terminal execution when evidence is required per check.
- Stubbing `renderRoot.querySelector` before retrieving required real elements for event dispatch in the same test.
- Relying only on `hasAttribute('visible')` for third-party components that may expose visibility through property updates.
- Skipping the coverage auditor and inferring branch completeness from the test runner summary only.
- Finishing the task without a final compliance-auditor pass (private scan + conventions validator).

## Preferred

- Public events emitted/listened.
- Spies on public methods or collaborator functions.
- Stubs on data-manager/API calls.
- Assertions on rendered DOM and visible side effects.
- Run checks one by one and keep each output clean and attributable to a single command.
- Obtain real DOM nodes first, then stub selector calls with explicit `withArgs(...)` mappings only for the branches under test.
- For modal visibility assertions, use resilient checks aligned with component behavior (`property` and/or `attribute`).
- Use the full 4-agent loop and require green outputs from runner, coverage auditor, and compliance auditor before closing.
- Public interaction replacements for the examples above:
	- Dispatch `bbva-form-radio-button-input-change` on the rendered radio element.
	- Verify currency request through public lifecycle or emitted event behavior, without direct `_...` calls.

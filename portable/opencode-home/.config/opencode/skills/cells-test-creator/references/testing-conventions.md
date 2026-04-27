# Testing conventions (repo)

## Stack

- `@open-wc/testing`
- `sinon`
- `cells lit-component:test`

## Typical structure

```js
suite('MyComponent', () => {
  let el;

  setup(async () => {
    el = await fixture(html`<my-component></my-component>`);
  });

  teardown(() => {
    sinon.restore();
  });

  test('renders the component host', async () => {
    assert.exists(el);
  });
});
```

## Expected patterns

- Verify events with `oneEvent(...)` or listeners + spies.
- Verify methods without return values with `sinon.spy(...)`.
- Stub services/data-manager calls with `sinon.stub(...)`.
- Never test APIs directly. Always use mocks to simulate API responses and behaviors.
- Use reusable mocks from `test/mocks/mocks.js` when applicable.

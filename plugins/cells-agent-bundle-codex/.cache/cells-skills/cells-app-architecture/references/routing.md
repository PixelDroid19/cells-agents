# Navigation & Routing

Navigation in Cells features involves two levels: internal (within the feature) and external (navigating to other features or apps).

## Internal Navigation

Internal navigation is managed by the feature component itself, typically by switching visible child components based on state.

```javascript
// In your feature component
render() {
  switch (this.currentPage) {
    case 'dashboard':
      return html`<feature-dashboard></feature-dashboard>`;
    case 'details':
      return html`<feature-details></feature-details>`;
    default:
      return html`<feature-dashboard></feature-dashboard>`;
  }
}
```

## External Navigation (The Bridge)

To navigate outside the feature (e.g., to another page in the app or to close the feature), use the `WidgetMixin` helper methods which emit standard events caught by the Bridge.

### Methods

-   **`navigateForward(pageNameId, data)`**: Emits an event to navigate to a new page.
    ```javascript
    this.navigateForward('transfer-success', { transferId: '123' });
    // Emits: bbva-feature-xyz-transfer-success-navigation-external
    ```

-   **`navigateBack()`**: Emits an event to go back in history.
    ```javascript
    this.navigateBack();
    // Emits: navigation-go-back
    ```

### Event Pattern

The `navigateForward` method constructs an event name based on the feature name and target page.

-   Format: `${feature-name}-${target-page}-navigation-external`
-   Example: `bbva-feature-example-dashboard-navigation-external`

# Data Managers (DM)

Data Managers (DMs) in modern Cells features are non-visual LitElement components responsible for business logic, data aggregation, and communication with global API DMs.

## Responsibilities

-   **Orchestration**: Manage multiple global API DMs (e.g., `@bbva-global-apis-dm/bbva-global-customers-api-dm`).
-   **Data Aggregation**: Combine data from different sources into a coherent format for the UI.
-   **State Management**: Hold temporary state for the feature.
-   **Event Dispatching**: Notify the UI when data is ready or an error occurs.

## Structure

A Data Manager typically extends `WidgetMixin(ScopedElementsMixin(LitElement))` and uses `scopedElements` to define the global DMs it uses.

```javascript
import { LitElement, html } from 'lit';
import { ScopedElementsMixin } from '@open-wc/scoped-elements/lit-element.js';
import { WidgetMixin } from '../mixins/WidgetMixin.js';
import { BbvaGlobalCustomersApiDm } from '@bbva-global-apis-dm/bbva-global-customers-api-dm';

export class FeatureDataManager extends WidgetMixin(ScopedElementsMixin(LitElement)) {
  static get scopedElements() {
    return {
      'bbva-global-customers-api-dm': BbvaGlobalCustomersApiDm,
    };
  }

  static get properties() {
    return {
      host: { type: String },
      customers: { type: Array },
    };
  }

  render() {
    return html`
      <bbva-global-customers-api-dm
        id="customersDm"
        host="${this.host}"
        @request-success="${this._handleCustomersSuccess}"
        @request-error="${this._handleCustomersError}"
      ></bbva-global-customers-api-dm>
    `;
  }

  _handleCustomersSuccess(event) {
    this.customers = event.detail;
    this.emitEvent('customers-loaded', this.customers);
  }

  _handleCustomersError(event) {
    this.emitEvent('error', event.detail);
  }
}
```

## Pattern: Global vs Local DMs

-   **Global DMs**: Provided by the platform (`@bbva-global-apis-dm/...`). They handle specific API endpoints (e.g., Customers, Accounts).
-   **Feature DM**: The "Local" DM for your feature (e.g., `ExampleDataManager`). It instantiates Global DMs and exposes a simplified API to your feature's UI components.

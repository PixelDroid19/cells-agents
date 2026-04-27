# Architecture

## Scope

Use this topic for Cells app and feature architecture, bridge, pub/sub, routing, and data managers.

## Core rules

- Cells is a component-based architecture built on web standards and Web Components.
- The bridge is the core application piece for state, routing, and publish/subscribe communication.
- A Cells feature should separate visual structure from integration logic.
- Feature packages commonly organize code into `pages`, `data-manager`, `shared-components`, `mixins`, `configs`, `utils`, and `styles`.
- The main feature host usually orchestrates pages and data managers and coordinates navigation.
- Data managers own API and aggregation logic and should not become visual widgets.
- Communication should prefer explicit events for child-to-parent flow and properties for parent-to-child flow.
- Reuse existing feature patterns before inventing a new architecture.

## Bridge and Application Shell

The bridge coordinates application-level communication and integration:

- Creates and owns the application runtime
- Manages page navigation and routing
- Provides pub/sub channels for inter-component communication
- Coordinates data managers and feature initialization

## Data Managers

Data managers own API interaction and data aggregation logic. They should NOT become visual widgets.

Key responsibilities:
- Fetch data from external APIs
- Aggregate and transform data for pages/components
- Expose data via properties or events to the UI layer
- Handle loading, error, and caching states

## CellsPage and Pages

Pages are top-level application screens. `CellsPage` is the base class:

```js
class MyPage extends CellsPage {
  static get is() { return 'my-page'; }

  static get properties() {
    return {
      loading: Boolean,
      data: Array
    };
  }

  onPageEnter() {
    // Called each time user navigates to this page
    this.loadData();
  }
}
```

## Pub/Sub Communication (Event Channels)

Cells uses event channels for decoupled communication between components:

```js
// Publishing on a channel
this.publish('channel-name', { key: 'value' });

// Subscribing to a channel
this.subscribe('channel-name', this._onChannelMessage.bind(this));

// Unsubscribe on cleanup
this.unsubscribe('channel-name', this._onChannelMessage);
```

Event channels must have stable names and clear ownership.

## Routing

Cells Bridge handles routing through the application:

- Routes are defined in JSON page definition files or as static page configurations
- Navigation is handled via bridge methods
- Delegated routes allow components to declare their own sub-routes

## Feature Structure

Typical Cells feature package:

```
my-feature/
  pages/
    my-page.js
    my-page.scss
  data-managers/
    my-dm.js
  shared-components/
    my-widget.js
  mixins/
    my-mixin.js
  configs/
    config.json
  utils/
    helpers.js
  styles/
    tokens.scss
  my-feature.js   ← feature host entry point
```

## Signals to extract

- feature host responsibilities
- page structure
- data-manager boundaries
- routing and navigation flow
- bridge or pub/sub communication
- event naming and propagation

## Use when

- planning a new feature
- deciding where API logic belongs
- explaining widget, page, and data-manager boundaries
- reviewing event and routing architecture

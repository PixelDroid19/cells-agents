# Architecture

## Scope

Use this topic for Cells app and feature architecture.

## Core rules

- Cells is a component-based architecture built on web standards and Web Components.
- The bridge is the core application piece for state, routing, and publish/subscribe communication.
- A Cells feature should separate visual structure from integration logic.
- Feature packages commonly organize code into `pages`, `data-manager`, `shared-components`, `mixins`, `configs`, `utils`, and `styles`.
- The main feature host usually orchestrates pages and data managers and coordinates navigation.
- Data managers own API and aggregation logic and should not become visual widgets.
- Communication should prefer explicit events for child-to-parent flow and properties for parent-to-child flow.
- Reuse existing feature patterns before inventing a new architecture.

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

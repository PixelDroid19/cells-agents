# Application Communication

## Scope

Use this topic for bridge channels, event channels, native bridge, and logout or session-related app flows.

## Core rules

- Application communication should use explicit, documented channels and event contracts.
- Event channels must have stable names and clear ownership to avoid hidden coupling.
- Native bridge integration is an app-level concern and should be isolated from pure presentational components.
- Session-ending flows such as logout should be routed through the correct app services and cleanup points.
- Cross-layer communication should favor auditable contracts over implicit shared mutable state.

## Signals to extract

- channel naming
- event payload ownership
- bridge-to-feature boundaries
- native integration points
- logout or session teardown flow

## Use when

- reviewing bridge communication
- modeling event channels
- integrating web code with native capabilities
- deciding how logout propagates through the app

# Application Testing

## Scope

Use this topic for Cells application-level testing guidance beyond isolated component tests.

## Core rules

- Application tests should validate behavior at the correct layer: runtime wiring, channels, bridge interaction, and feature integration.
- Test setup should mirror the runtime contracts needed by the app or feature under test.
- Integration-level assertions should focus on observable behavior and communication, not hidden implementation details.
- Unit tests should remain deterministic and isolate external services, native integrations, and network dependencies with controlled doubles.
- App-level testing should complement, not replace, component-level public-behavior tests.

## Signals to extract

- app vs component test boundary
- bridge or channel test setup
- integration doubles and stubs
- runtime initialization needed for tests
- observable behaviors to assert

## Use when

- testing Cells applications or features
- deciding what belongs in unit vs integration coverage
- validating bridge or event-channel behavior

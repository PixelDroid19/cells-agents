# Advanced Application

## Scope

Use this topic for advanced Cells application concerns such as feature flags, microfrontends, performance, and service workers.

## Core rules

- Advanced application capabilities should be introduced deliberately and owned at the app architecture level.
- Feature flags should be explicit, traceable, and kept out of low-level component internals when possible.
- Microfrontend boundaries should preserve clear contracts, dependency control, and communication discipline.
- Performance work should focus on measurable bottlenecks, loading strategy, and unnecessary runtime overhead.
- Service workers should be treated as app infrastructure and coordinated with runtime, caching, and deployment behavior.

## Signals to extract

- whether the concern belongs to app infrastructure
- feature flag ownership and scope
- microfrontend integration boundaries
- performance-sensitive loading or rendering paths
- caching and offline strategy

## Use when

- evaluating advanced Cells architecture decisions
- reviewing feature-flag design
- planning microfrontend or performance-sensitive work
- reasoning about service-worker responsibilities

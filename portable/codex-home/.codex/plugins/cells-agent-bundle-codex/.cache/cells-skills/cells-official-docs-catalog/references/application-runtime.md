# Application Runtime

## Scope

Use this topic for Cells application structure, runtime bootstrap, and app-level configuration.

## Core rules

- The application layer owns bootstrap, global configuration, routing setup, bridge creation, and shared runtime services.
- App configuration should centralize environment-sensitive behavior instead of scattering it across widgets or pages.
- Components and features should consume app services through stable integration points, not by duplicating bootstrap logic.
- The bridge instance is an application concern and coordinates application-level communication and integration.
- Feature packages should remain focused on feature behavior while the app shell governs runtime composition.

## Signals to extract

- app bootstrap responsibility
- config ownership
- bridge instance lifecycle
- app shell vs feature boundaries
- runtime integration points

## Use when

- planning a Cells app shell
- deciding where runtime configuration belongs
- reasoning about bridge initialization or application wiring

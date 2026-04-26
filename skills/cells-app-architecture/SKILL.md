---
name: cells-app-architecture
description: "Use when designing Cells app or feature structure, data managers, routing, bridge communication, pub/sub, composition boundaries, or separation of responsibilities."
license: MIT
metadata:
  author: D. J
  version: "1.1"
---

# Cells App & Feature Architecture

## Purpose

This skill explains how Cells applications and feature packages should be structured, where runtime responsibilities belong, and how features communicate with the wider application.

## Execution Contract

Read and follow:
- `skills/_shared/cells-official-reference.md`
- `skills/_shared/real-cells-patterns.md`
- `skills/cells-official-docs-catalog/` topics `architecture`, `application-runtime`, `application-communication`, and `advanced-application`
- `references/feature-structure.md`
- `references/data-managers.md`
- `references/routing.md`
- `references/pub-sub.md`
- `references/bridge.md`

## Usage

Use this skill for prompts like:
- "How should I structure a new feature?"
- "Where do I put API logic?"
- "What belongs to the app shell vs the feature?"
- "How do pages within a feature communicate?"
- "Where should bridge, native, or channel logic live?"

## What To Extract

Always answer these boundaries explicitly:
- app shell responsibilities vs feature responsibilities
- feature host responsibilities vs data-manager responsibilities
- page/view concerns vs non-visual integration logic
- bridge or event-channel ownership
- routing and navigation flow
- where native integration should be isolated

## Core Guidance

### 1. Feature Package Structure

A standard Cells feature commonly organizes code into:
- `pages/`
- `data-manager/`
- `shared-components/`
- `mixins/`
- `configs/`
- `utils/`
- `styles/`

Use this as a baseline, then adapt only when the existing app architecture already establishes a different proven pattern.
Use `skills/_shared/real-cells-patterns.md` to distinguish modern Lit 3 feature evidence from legacy app evidence such as older GloMo runtimes.

### 2. Main Feature Host

The main feature component usually:
- orchestrates pages and data managers
- coordinates feature navigation
- wires feature-level events
- composes internal widgets and shared components

It should not become a dumping ground for low-level API or native integration details.

### 3. Data Managers

Data managers are non-visual integration pieces responsible for:
- interacting with APIs or shared runtime services
- aggregating and normalizing data for the feature
- exposing observable outputs or dispatching feature-relevant events

They should not become presentation widgets.

### 4. Communication

Prefer:
- events for child-to-parent communication
- properties for parent-to-child data flow
- explicit bridge or event-channel contracts for app-level integration

Keep native or app-runtime communication out of low-level presentational components whenever possible.

### 5. Advanced App Concerns

When the task involves feature flags, performance, service workers, microfrontends, or other advanced runtime concerns:
- treat them as application architecture topics first
- avoid hiding them inside ordinary feature components
- document ownership and boundaries clearly

## References

- `references/feature-structure.md`
- `references/data-managers.md`
- `references/routing.md`
- `references/pub-sub.md`
- `references/bridge.md`

## Browser Integration

When the architecture work affects routes, pages, feature shells, or browser-visible state transitions, also read:
- `skills/_shared/browser-testing-convention.md`
- `skills/agent-browser/SKILL.md` when available

Define browser checkpoints explicitly for:
- route entry points
- page-to-page transitions
- loading, empty, and error states
- visual theming or i18n-visible states

If a design decision changes what the user can see or do, call out how that state should be validated in a local browser run.

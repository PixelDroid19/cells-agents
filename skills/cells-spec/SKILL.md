---
name: cells-spec
description: "Use when a Cells change needs behavioral requirements, acceptance scenarios, and explicit boundaries."
---

# Cells Spec

## Purpose

Write the behavior that implementation and verification must preserve or deliver. Use this skill when the user asks for a specification or a governed workflow requires one; it is not required for a narrow direct edit.

## Dependencies

In a governed chain, read the proposal first. A spec precedes design and tasks. Outside that chain, use the user-approved requirements and direct project evidence that define the behavior.

## Contents

Use only the sections needed for the change:

```markdown
## Scope

## Requirements
- The system MUST ...

## Scenarios
### Scenario: descriptive name
Given ...
When ...
Then ...

## Non-goals

## Evidence and Validation
```

For visible Cells behavior, include the relevant component, i18n, event, or browser acceptance condition. For existing behavior, distinguish what project evidence proves today from what the change must add.

## Persistence and Status

With `artifact_persistence: openspec`, write the scoped specification under `openspec/changes/{change}/specs/`. Otherwise return it inline. Do not create a spec merely because implementation is authorized.

Use `partial` for a safe draft with stated unanswered requirements. Use `blocked` only when missing requirements make an unambiguous specification impossible.

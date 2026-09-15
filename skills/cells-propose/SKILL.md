---
name: cells-propose
description: "Use when the user asks for a Cells change proposal covering intent, scope, risks, alternatives, and rollback."
---

# Cells Propose

## Purpose

Turn user input and relevant exploration into a reviewable change proposal. A proposal is optional for directly authorized scoped implementation.

## Inputs

Use direct user requirements, project evidence, and exploration findings that are available. In a governed OpenSpec chain, read the active change context before updating the proposal. Do not block a proposal because a separate exploration artifact was never created.

## Proposal Contents

```markdown
## Goal

## Scope
- In scope
- Out of scope

## Current Evidence

## Proposed Change

## Affected Areas

## Risks and Rollback

## Validation
```

For Cells UI, command, i18n, or architecture claims, use the relevant source route and record a compact source decision. Include rollback only when the change can plausibly need it; do not add ceremony to a harmless copy or documentation update.

## Persistence

Write `openspec/changes/{change}/proposal.md` only when the user selected `artifact_persistence: openspec` or is continuing that governed change. Otherwise return the proposal inline.

## Status

Use `success` when the proposal gives a scoped, evidence-backed direction; `partial` when a concrete decision remains open; `blocked` only when a required decision prevents even a safe proposal.

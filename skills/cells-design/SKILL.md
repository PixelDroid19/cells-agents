---
name: cells-design
description: "Use when a Cells change needs a technical design, data flow, architecture decision, implementation boundary, or validation strategy."
---

# Cells Design

## Purpose

Produce the smallest technical design that makes the approved change implementable and reviewable.

## Dependencies

For a governed chain, read the specification before designing and preserve its acceptance conditions. Outside that chain, design from directly approved requirements and project evidence. Do not require a proposal artifact for a narrow architecture question unless the user asks for one.

## What to Decide

- affected modules and ownership boundaries;
- data flow, events, and public contracts;
- reuse versus composition versus new component evidence;
- i18n, style, and scoped-element requirements when relevant;
- test and browser strategy proportionate to the change;
- risks, compatibility, and rollback for material changes.

For component or framework claims, follow `cells-source-routing-contract.md`. Preserve existing data-manager and `WidgetMixin` patterns when the project uses them; do not introduce a new abstraction without evidence.

## Output

Use clear sections such as **Architecture Decisions**, **File Changes**, **Data and Events**, **Validation**, and **Risks**. Include a diagram only when it clarifies a multi-step flow.

Persist `design.md` only in a user-selected OpenSpec workflow. Report `partial` for a design with an explicit evidence gap and `blocked` only if a required design decision cannot be made safely.

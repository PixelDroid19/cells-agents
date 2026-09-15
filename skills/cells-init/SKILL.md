---
name: cells-init
description: "Use when the user asks to identify a Cells project's actual stack, conventions, command surface, or optional governed-workflow setup."
---

# Cells Init

## Purpose

Establish project context from the workspace. This phase is useful before broad or governed work; it is not required before every scoped edit.

## Read First

- `skills/_shared/cells-work-sizing-contract.md`
- `skills/_shared/cells-conventions.md` when Cells signals are present
- `skills/_shared/cells-source-routing-contract.md` when a component, framework, or command decision is needed

## Process

1. Inspect actual markers: `package.json`, installed scripts, `custom-elements.json` or other CEM, source layout, test configuration, locale setup, and CI configuration when relevant.
2. Identify whether the workspace is an app, component package, feature composition, or a non-Cells project with Lit signals.
3. Resolve command ownership only when the request needs it, using `cells-cli-usage` and installed scripts.
4. Record existing conventions that affect the requested work: BBVA/Spherica packages, `scopedElements`, `WidgetMixin`, `this.t(...)`, SCSS generation, and browser/runtime entry points.
5. Create OpenSpec configuration only when the user chose `artifact_persistence: openspec` for a governed change. Do not create a skill registry, LocalMemory entry, or placeholder artifact as a side effect.

## Output

Return the detected project type, direct evidence paths, relevant command route if resolved, and constraints for the requested task. Use `partial` if a needed project fact is missing; use `blocked` only when it prevents safe next work.

## Rules

- Detect from files and installed metadata, never from a generic assumption.
- Do not make LocalMemory or OpenSpec a prerequisite for source work.
- Keep initialization proportionate; a focused command question needs only the relevant manifest and resolver evidence.

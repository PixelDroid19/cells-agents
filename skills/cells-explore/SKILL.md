---
name: cells-explore
description: "Use when investigating a Cells codebase or architecture before proposing changes, including feature boundaries, bugs, and component usage."
---

# Cells Explore

## Purpose

Investigate the requested behavior and return evidence-backed options. This skill is read-only unless the user separately authorizes an implementation phase.

## Quick Start

1. Select the work size with [work sizing](../_shared/cells-work-sizing-contract.md).
2. Read the relevant source, tests, manifest, CEM, and local scripts.
3. Route a material Cells decision with [source routing](../_shared/cells-source-routing-contract.md).
4. Apply [Cells rules](../_shared/cells-rules-contract.md) only for relevant UI, i18n, public-behavior, or command questions.
5. Stop once the evidence defines a safe recommendation or state the exact gap.

## Cells Evidence

- Search `cells-components-catalog` first for component selection or APIs.
- Search `cells-official-docs-catalog` first for framework, CLI, test, architecture, i18n, or theming guidance.
- Fall back to active code, CEM, package source, and tests in the documented order.
- Load `cells-cli-usage`, `cells-coverage`, or `cells-test-creator` only when commands, coverage, or tests are part of the exploration.

## Output

Report:

- current behavior and direct evidence;
- affected files or boundaries;
- viable approaches and their tradeoffs when more than one exists;
- a recommendation, risks, and the smallest next action.

For a governed OpenSpec change, persist an exploration note only if it helps the requested chain. Otherwise return the result inline.

## Guardrails

- Do not invent file paths, component APIs, or runtime behavior.
- Do not require `cells-init`, proposal artifacts, a skill registry, or LocalMemory for a focused investigation.
- Use `partial` for a useful investigation with an evidence gap and `blocked` only when no safe recommendation can proceed.

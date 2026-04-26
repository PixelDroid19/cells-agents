---
name: cells-new
description: "Use when starting a new Cells change from an idea, feature, bug, or explored topic and needing structured exploration plus proposal creation."
license: MIT
metadata:
  author: D. J
  version: "1.0"
---

# Cells New — Start a Change

## Purpose

Bridge between exploration and proposal phases. Takes an explored topic and turns it into a structured change proposal.

## What You Receive

From the orchestrator:
- Change name
- Artifact store mode (`engram | openspec | hybrid | none`)
- Any prior exploration results

## Workflow

1. **Check exploration exists**: If the topic hasn't been explored yet, run `/cells-explore <topic>` first
2. **Load cells-propose skill**: Read `skills/cells-propose/SKILL.md` completely
3. **Create proposal**: Using exploration findings, produce proposal with:
   - Intent (what we're doing and why)
   - Scope (what's in/out)
   - Affected areas (files, components, tests)
   - Risks (what could go wrong)
   - Rollback plan (how to undo if needed)
4. **Persist proposal**: Follow active persistence mode (engram/openspec/hybrid/none)
5. **Return result**: Structured summary with proposal artifact reference

## Dependencies

- Requires: `cells-init` (project context must exist)
- Creates: `cells/{change-name}/proposal`
- Next: `/cells-continue` for spec + design, or `/cells-ff` for fast-forward planning

## Rules

- Do not create a proposal without exploration evidence first — the proposal needs real findings
- Keep scope concrete — reference specific files, components, or behaviors
- Identify risks explicitly — don't say "none" unless truly zero risk
- For Cells work, search `cells-components-catalog` before assuming a component doesn't exist

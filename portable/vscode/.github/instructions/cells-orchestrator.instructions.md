---
name: CELLS Orchestrator
description: Project-wide CELLS workflow routing, governance, source selection, and command policy.
applyTo: "**"
---

# CELLS Copilot Instructions

## Goal

You are the CELLS orchestrator for this workspace.

### Layered Precedence (Deterministic)

Apply layers in this exact order:

1. `.github/copilot-instructions.md`
2. This orchestrator instruction layer
3. Shared persistence and governance contracts under `.github/skills/_shared/`
4. Phase prompts under `.github/prompts/*.prompt.md`
5. Custom agents under `.github/agents/*.agent.md`
6. Workspace hooks under `.github/hooks/*.json`

## VS Code Copilot Operating Rules

- Use Agent mode for implementation and verification.
- Use the `cells-orchestrator` custom agent for multi-phase Cells work.
- Use subagents only through the `agent` tool and only when the selected custom agent exposes them.
- Use `/plan` or the built-in Plan agent for high-risk changes before implementation.
- Keep persistent project facts in repository memory when memory is available; keep task plans in session memory.
- Keep `/cells-*` commands canonical
- Do not suggest or default to generic external commands for Cells workflows

Response format for delegated phases MUST return `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`, `skill_resolution`, `evidence_required`.

## Intent Routing

Apply intent routing before choosing Cells skills:

- UI/component discovery and element selection
- Cells documentation or knowledge lookup
- testing, coverage, and test creation through the mandatory testing stack
- fallback to the other catalog only when the first one is insufficient

When fallback is used, record source decision trace with:

- intent
- primary_source
- fallback_source
- fallback_reason
- evidence_quality
- status

## Governance

- Preserve catalog-first evidence and deterministic fallback order
- Keep contribution flow explicit: issue -> approved issue -> PR -> review -> merge
- Preserve Cells specialist routing for non-SDD work
- Do not claim translation/i18n correctness without consulting `skills/cells-i18n/`
- Do not claim hook, memory, prompt, custom-agent, or skill correctness unless the relevant `.github/` asset path was checked

## Output Envelope

Delegated and mirrored CELLS phases must keep the same decision-friendly envelope:

- `status`
- `executive_summary`
- `artifacts`
- `next_recommended`
- `risks`
- `skill_resolution`
- `evidence_required`

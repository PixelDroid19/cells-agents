---
name: cells-fallback
description: Fallback Cells prompt when a dedicated phase prompt is missing.
argument-hint: "<cells phase and request>"
agent: cells-orchestrator
tools: ["search/codebase", "search/usages", "read/problems"]
---

# CELLS fallback prompt

WARNING: Dedicated prompt for this CELLS phase is missing.

Fallback behavior:

- use `cells-orchestrator` and the closest matching Cells skill first
- preserve Cells governance and `/cells-*` command canon
- return `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`

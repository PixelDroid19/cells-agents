---
name: cells-design
description: Produce a Cells technical design with architecture, data flow, risks, and verification strategy.
argument-hint: "<approved spec or change>"
agent: cells-orchestrator
tools: ["search/codebase", "search/usages", "read/problems", "web/fetch"]
---

# cells-design prompt

## Goal

Use the `cells-design` skill first. Describe the technical approach while preserving canonical Cells lineage and VS Code planning handoffs.

Use `cells-analysis` for additional read-only evidence before choosing architecture.

## Output envelope

Return `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`.

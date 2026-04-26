---
name: cells-apply
description: Implement an approved Cells task batch with scope gates and Cells-native commands.
argument-hint: "<approved task scope>"
agent: cells-implementation
tools: ["search/codebase", "search/usages", "read/problems", "editFiles", "runTerminalCommand"]
---

# cells-apply prompt

## Goal

Use the `cells-apply` skill first. Implement the assigned Cells task batch while preserving canonical lineage, scope gates, and Cells-native commands.

If tests are added or changed, consult `cells-cli-usage`, then `cells-coverage`, then `cells-test-creator` before edits and commands.

## Output envelope

Return `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`.

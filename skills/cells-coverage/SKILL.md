---
name: cells-coverage
description: "Use when analyzing Cells coverage reports, lcov data, branch misses, thresholds, test-failure artifacts, or prioritizing missing test cases."
---

# Cells Coverage

## Purpose

Turn coverage data into a focused test recommendation. This skill is only for coverage work; it is not a prerequisite for every test or Cells change.

## Inputs

Inspect the available coverage and failure artifacts, project coverage configuration, and relevant source/test files. Use `cells-cli-usage` only if a rerun command must be selected. Use `cells-test-creator` only if new or changed tests are needed.

## Analysis

1. Prefer compact summaries and `lcov.info` counters over manually scanning full HTML reports.
2. Identify the most consequential uncovered branch, line, or function for the requested scope.
3. Map it to a concrete observable condition.
4. Recommend the smallest public-behavior test or focused rerun that addresses it.
5. Recompute the affected file's counters when the user asks for closure or the project enforces a threshold.

Prioritize broken flows and branch gaps before cosmetic percentage gains. Do not claim coverage completion from a global percentage alone when a file-level requirement exists.

## Output

Return the inspected artifacts, per-file counters when available, prioritized missing behavior, focused next command, limitations, and status. Use browser evidence when a coverage gap corresponds to a user-visible flow that unit coverage cannot explain.

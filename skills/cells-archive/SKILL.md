---
name: cells-archive
description: "Use when the user asks to close a governed Cells change and preserve its verified artifact record."
---

# Cells Archive

## Purpose

Close a user-requested governed change after its verification evidence is available. Archiving is not required after every implementation and must not move files automatically.

## Closeout Criteria

- the requested implementation scope is complete or its open items are explicitly marked;
- verification evidence and limitations are recorded;
- active OpenSpec artifacts have been read before any update or archival move;
- any merge, archival, PR, or publication action is explicitly within the user's request.

## Process

1. Read the active proposal, spec, design, tasks, and verification report that actually exist for the governed change.
2. Summarize delivered behavior, validation evidence, risks, and remaining work.
3. Update or archive OpenSpec files only when the governed workflow and user request authorize it.
4. Keep LocalMemory separate; do not save a closure summary automatically.

## Status

Return `success` when closeout evidence supports completion, `partial` when open work is intentionally carried forward, and `blocked` when required closeout evidence is unavailable. Report exact paths moved or updated when an archive action occurred.

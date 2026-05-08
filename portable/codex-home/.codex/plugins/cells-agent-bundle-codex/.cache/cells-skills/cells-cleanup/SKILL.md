---
name: cells-cleanup
description: "Use when sweeping a Cells or Lit component for code hygiene without changing behavior, including formatting, JSDoc, attributes, condition extraction, comments, or repeated test setup."
---

# Cells Cleanup

## Purpose

Clean up Cells or Lit code without changing logic, behavior, or public API.

The detailed rulebook lives in [resources/references.md](resources/references.md). Use it as the source for category-specific decisions instead of duplicating those rules inline.

## Zero-Behavior-Change Contract

You are NOT allowed to:

- change what a method does
- add, remove, or rename public properties or events
- change data flow, business rules, or component behavior
- modify test expectations or assertions unless explicitly asked

You ARE allowed to:

- add or improve JSDoc
- remove trailing commas and add semicolons
- remove unnecessary blank lines and narrative comments
- extract conditions to named helpers or apply the Rules Table Pattern
- convert repetitive code to config arrays plus `.map()` / `.filter()`
- separate repeated test setup into reusable helpers when tests are explicitly in scope
- fix `attribute` fields and safe binding mistakes
- flag broader improvements as suggestions instead of applying them

## Execution Contract

Before reading the target file, load:

- `skills/cells-cleanup/resources/references.md`
- `skills/_shared/cells-conventions.md`
- `skills/_shared/cells-official-reference.md`

Use `resources/references.md` as the detailed rule source for every cleanup category.

## Workflow

### Step 1: Read the target

Before changing anything:

- identify the component class, tag, and public API
- list methods and rough hotspots
- note JSDoc coverage
- note whether test files are explicitly in scope

### Step 2: Run the cleanup categories

Apply the categories from [resources/references.md](resources/references.md) in order:

1. formatting
2. JSDoc
3. attribute field
4. conditions by method
5. repetitive code
6. template and binding quality
7. lifecycle correctness
8. tests and demo boundary
9. reusability review
10. constants
11. i18n and locale rules
12. visibility and access audit

For each finding, record:

- category
- file and line range
- what was found
- whether it was applied or only suggested

### Step 3: Apply only safe edits

Safe to auto-apply:

- formatting
- JSDoc
- explicit `attribute` fields
- conditions extracted without behavior change
- Rules Table refactors that preserve behavior
- `.map()` or fixture-helper refactors that preserve behavior

Suggestion only:

- reusability improvements
- constants extraction that broadens module ownership
- moving logic across layers
- visibility or API changes

Critical and do not auto-fix:

- demo imported from `src`
- private member access in tests
- invented or unsupported locale path for the touched surface

### Step 4: Return the cleanup report

Return:

- files touched
- applied changes by category
- suggestions requiring approval
- summary of behavior-neutrality

Use the category numbering from [resources/references.md](resources/references.md) so findings stay traceable.

## Scope Rules

- one file at a time unless the user passed multiple files or a directory
- test cleanup only when test files are explicitly in scope
- do not modify locale files directly; audit them through the repo's actual locale source for the touched surface
- do not touch SCSS or `.css.js` unless the user explicitly expands scope
- do not cross the `demo/` ↔ `src/` boundary

## Evidence Rules

- report exact line ranges
- separate applied changes from suggestions
- re-read every changed method before closing to confirm behavior did not move
- if an intended cleanup would change behavior, stop and report it as a suggestion

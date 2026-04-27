# Implementation Playbook

Use this reference when `cells-apply` needs the detailed flow instead of the shorter SKILL instructions.

## TDD flow

For each task:

1. read the task, relevant spec scenarios, and design decisions
2. write a failing test first
3. run the targeted test and confirm the failure is meaningful
4. implement the minimum code to pass
5. re-run tests
6. refactor without changing behavior
7. re-run tests again

Test runner resolution order:

1. `skills/cells-cli-usage/`
2. `skills/cells-coverage/`
3. `skills/cells-test-creator/`
4. repo-local wrapper after Cells command resolution

## Standard flow

For small or low-risk work:

1. read the task, specs, design, and surrounding code
2. make the smallest working change
3. run the lightest confirmation command that proves the change
4. document deviations, risks, and remaining work

## Browser validation checklist

When the change is browser-visible:

1. resolve the serve or demo command through `skills/cells-cli-usage/`
2. reuse an existing runtime or browser session when possible
3. snapshot before interaction
4. perform only the interaction needed to prove the changed behavior
5. snapshot or screenshot after DOM changes
6. report blocked runtime evidence explicitly if local validation cannot be executed

## Response template

```markdown
## Implementation Progress

**Change**: {change-name}
**Mode**: {TDD | Standard}

### Completed Tasks
- [x] ...

### Files Changed
| File | Action | Notes |
| --- | --- | --- |

### Source Decisions
- intent: ...
  primary_source: ...
  fallback_used: false
  fallback_source: null
  fallback_reason: null
  evidence_quality: high
  status: ok

### Tests
{only when relevant}

### Deviations from Design
{or "None  implementation matches design."}

### Issues Found
{or "None."}

### Remaining Tasks
- [ ] ...

### Status
{N}/{total} complete. {Ready for next batch | Ready for verify | Blocked by X}
```

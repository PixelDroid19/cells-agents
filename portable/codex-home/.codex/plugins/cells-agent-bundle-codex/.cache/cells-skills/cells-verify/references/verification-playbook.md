# Verification Playbook

Use this reference when `cells-verify` needs the full report structure or detailed runtime checklist.

## Runtime validation checklist

1. resolve commands through `skills/cells-cli-usage/`
2. prefer the smallest scope that proves the change
3. run tests and capture passed, failed, skipped, and exit code
4. run build or type-check when relevant
5. run coverage only when configured, otherwise use the governance exemption path
6. run browser validation when UI, demos, routes, styling, or runtime i18n changed

## Browser validation checklist

1. resolve the local serve or demo command
2. reuse existing runtime or browser session when possible
3. snapshot before interaction
4. perform the minimum flow needed to prove the change
5. snapshot or screenshot after DOM changes
6. report blocked runtime evidence explicitly if local validation cannot run

## Verification report template

```markdown
## Verification Report

**Change**: {change-name}
**Version**: {spec version or N/A}

### Artifact Lineage
- Active proposal artifact: `cells/{change-name}/proposal`
- Active spec artifact: `cells/{change-name}/spec`
- Active design artifact: `cells/{change-name}/design`
- Active tasks artifact: `cells/{change-name}/tasks`
- Active verify artifact: `cells/{change-name}/verify-report`

### Completeness
| Metric | Value |
| --- | --- |

### Build & Tests Execution
{commands, outputs, failures, or skips}

### Spec Compliance Matrix
| Requirement | Scenario | Test | Result |
| --- | --- | --- | --- |

### Correctness
| Requirement | Status | Notes |
| --- | --- | --- |

### Coherence
| Decision | Followed? | Notes |
| --- | --- | --- |

### Source Decisions
| Intent | Primary Source | Fallback Used | Fallback Source | Fallback Reason | Evidence Quality | Status |
| --- | --- | --- | --- | --- | --- | --- |

### Issues Found
**CRITICAL**: ...
**WARNING**: ...
**SUGGESTION**: ...

### Verdict
{PASS | PASS WITH WARNINGS | FAIL}

### Fixed Compliance Checklist
| Check | Result | Evidence |
| --- | --- | --- |
```

## Fixed compliance checklist

Before returning a PASS verdict, confirm:

1. restriction compliance
2. no private assertions in changed tests
3. native Cells command evidence
4. lcov file-level evidence when applicable
5. real Cells implementation rules satisfied for the verified scope
6. code hygiene of changed files

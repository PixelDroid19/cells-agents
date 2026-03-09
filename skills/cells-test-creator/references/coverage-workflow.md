# Coverage workflow

## Goal

Reach 100% for the target file in:

- Statements
- Branches
- Functions
- Lines

Principal owner in subagent mode: `Agent 3 (coverage-auditor)`.

## Workflow

1. Run `npm run test`.
2. Open `build/coverage-reports/lcov-report/index.html`.
3. Navigate to the target file and inspect uncovered blocks.
4. Write public-behavior tests to cover those blocks.
5. Repeat until the target file reaches 100%.

In subagent mode, Agent 3 must return uncovered `BRDA` lines to Agent 1 so test creation is driven by concrete missing branches.

## Branch closure protocol

Use this protocol when Branches is below 100%:

1. Extract file-level counters from `lcov.info`.
2. List uncovered `BRDA` entries for the target file.
3. Map each uncovered `BRDA:<line>,...` to the source line.
4. Add focused tests for each missing branch via public behavior.
5. Re-run only the target test file.
6. Re-check `BRDA` until no uncovered entries remain.

Recommended commands:

- `awk 'BEGIN{inrec=0} /^SF:src\/path\/file.js/{inrec=1;print;next} inrec && /^end_of_record/{exit} inrec && /^(FNF|FNH|LF|LH|BRF|BRH):/{print}' build/coverage-reports/lcov.info`
- `awk 'BEGIN{inrec=0} /^SF:src\/path\/file.js/{inrec=1;next} inrec && /^end_of_record/{exit} inrec && /^BRDA:/{if($0 ~ /,0$/) print}' build/coverage-reports/lcov.info`

## Evidence

The valid result is the file-level counters in `lcov.info` and an empty uncovered-branch report.

Mandatory closure signal in subagent mode:

- `BRDA` uncovered command prints nothing for the target file.

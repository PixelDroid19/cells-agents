# Naming and structure

## Mirror rule

- Source: `src/pages/dashboard/dashboard-oc-account.js`
- Test: `test/pages/dashboard/dashboard-oc-account.test.js`

## Naming rule

- Expected test filename: `<source-file>.test.js`

## Location

- All unit tests must live under `test/`.
- Avoid creating tests outside the mirrored hierarchy unless explicitly justified.

## Minimum expected template

- OpenWC + Sinon imports
- `suite`, `setup`, `teardown`, `test`
- Observable-behavior assertions

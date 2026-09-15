# Cells Source Routing Contract

## Purpose

Choose evidence by intent before making a material Cells claim. Catalogs are primary for bundled knowledge; project code and Custom Elements Manifest (CEM) data are the fallback for the active workspace.

## Intent Matrix

| Intent | Primary evidence | Ordered fallback |
| --- | --- | --- |
| Choose a UI/component package, tag, prop, event, or CSS hook | `cells-components-catalog` search | Project `custom-elements.json`/CEM, installed package source, project code and tests, then official docs |
| Cells framework, architecture, CLI guidance, testing, i18n, theming, demos, or packaging | `cells-official-docs-catalog` search | Project code/CEM/tests, then component catalog when package detail matters |
| Resolve a command to execute | Installed project scripts and manifest through `cells-cli-usage` | Official catalog's documented equivalent, then report a concrete gap |
| Create or update tests | Relevant official testing guidance and `cells-test-creator` | Existing project tests and test configuration |
| Analyze coverage | `cells-coverage` and actual report artifacts | Targeted test output and project configuration |
| Locate a file or local convention | Project tree and direct file reads | `partial` or `blocked`; do not invent a path |

The test command resolver is needed only when a test command must be selected or run. Coverage and test-authoring skills are not prerequisites for unrelated Cells work.

## Routing Rules

1. Classify the decision.
2. Consult its primary source unless the decision is purely local-path or runtime evidence.
3. Use the next fallback only when the primary source is unavailable or insufficient; record why for material work.
4. Stop once the evidence answers the decision. Do not cross-check sources for ceremony.

For UI discovery, a catalog result identifies candidates; verify the selected API against the active project's CEM, package source, or code before relying on it. For command execution, observed installed scripts determine what can run; official documentation identifies the current equivalent.

## Source Decision Template

Use this for governed artifacts or material decisions:

```yaml
- intent: component-selection
  primary_source: cells-components-catalog
  fallback_used: false
  fallback_source: null
  fallback_reason: null
  evidence_quality: high
  status: success
```

`status` uses the workflow meanings from `cells-governance-contract.md`. A catalog tool may retain its own `ok` query status.

## Evidence by Work Size

- `fast-path`: inspect the narrow source that answers the question.
- `scoped-change`: inspect the direct code and any source needed for an affected Cells rule or command.
- `full-workflow`: retain source decisions for each material requirement and validation claim.

Do not force a test-stack lookup, a catalog search, or a source-decision artifact when it has no connection to the user request.

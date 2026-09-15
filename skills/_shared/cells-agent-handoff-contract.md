# Cells Agent Handoff Contract

Use this contract only when work is actually delegated. It does not require delegation for a Cells task.

## Roles

- **Orchestrator:** selects work size, keeps the user scope intact, may implement a scoped change directly, and integrates final evidence for full-workflow work.
- **Executor:** completes the assigned research, implementation, or verification directly. It does not create further delegation unless the handoff explicitly permits it.

Delegate only when independent work, specialized evidence, or parallel validation materially improves the result. Native host agents and their normal permissions remain the execution mechanism; this contract does not invent a background runtime.

## Handoff Packet

Pass the smallest complete packet. Include known fields that affect execution; omit irrelevant or unknown fields rather than padding them with placeholders.

```markdown
## Handoff

- task: concise objective
- scope: allowed files, behaviors, and explicit exclusions
- current evidence: relevant findings and artifact paths, if any
- applicable rules: compact injected rules or exact skill paths
- acceptance criteria: observable completion conditions
- validation: command, browser, source, or blocked-evidence expectations
- dependencies: only prerequisites that actually apply
```

Injected compact rules are sufficient when they cover the task. An executor need not reload a registry or repeat source discovery merely because a generic handoff template mentions it.

## Evidence Loop

1. Give the executor a bounded task and measurable completion condition.
2. Inspect the returned evidence, not only the summary.
3. When a fix is safe and in scope, continue with the next concrete hypothesis or correction.
4. Do not impose an arbitrary retry count. Stop only when the same missing input, permission, or required evidence prevents safe progress.

For visible UI changes, request realistic browser evidence when source checks cannot prove the result. For testing work, load only the relevant testing specialist skill.

## Statuses

- `success`: the assigned scope and its required evidence are complete.
- `partial`: the assignment made safe progress, but an identified criterion or evidence item remains open.
- `blocked`: the executor cannot safely continue because a required input, permission, environment, or decision is unavailable.

Return the concrete reason, evidence collected, risks, and smallest next action. Catalog search results may use their own `ok` status and should not be converted into a workflow status without assessing the task.

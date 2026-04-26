# Cells Agent Handoff Contract

This contract defines how Cells agents coordinate work across hosts. It is the authority for agent roles, handoffs, evidence gates, skill resolution, and Dev-QA loops. Host files route to this contract; they must not fork policy.

## Role Boundaries

### Orchestrator

The Cells orchestrator is a coordinator, not executor.

- Keep the main thread thin: decide, delegate, synthesize, and report.
- Do small inline reads only when they are needed to route or verify a decision.
- Delegate broad exploration, multi-file implementation, test execution, browser validation, and verification work.
- Never use `/cells-new`, `/cells-continue`, or `/cells-ff` as executor skills; those are workflow intents handled by orchestration.
- Before delegation, resolve relevant Cells skills and shared contracts, then pass the smallest useful rules and artifact references to the subagent.
- After delegation, inspect `skill_resolution`. If it is not `injected`, reload the skill registry or referenced contracts before the next handoff.

### Executor Agents

Executor agents are analysis, implementation, verification, and archive workers.

- Do not delegate.
- Do not launch subagents.
- Do the assigned role directly and return the result envelope.
- Use only the artifact references, source routes, and scope boundaries in the handoff.
- Stop with `blocked` when required inputs, permissions, commands, or evidence are unavailable.

## Delegation Heuristics

Delegate when the work would inflate the orchestrator context or requires specialized evidence:

| Work type | Recommended owner |
| --- | --- |
| Read 1-3 files to decide routing | Orchestrator |
| Explore architecture, component choice, or source routing across several files | `cells-analysis` |
| Implement approved scope across files | `cells-implementation` |
| Run Cells-native test, coverage, browser, or release evidence | `cells-verification` |
| Synthesize final status, risk, and next action | Orchestrator |

Do not split a task so far that the receiving agent lacks enough context to finish. A handoff must include acceptance criteria and evidence expectations.

## Handoff Packet

Every agent-to-agent handoff must include this packet, either explicitly or as an equivalent host-specific prompt:

```markdown
## Handoff Packet

- from_agent: {sender}
- to_agent: {receiver}
- phase: {cells phase or role}
- task_reference: {change name, task id, or user request}
- priority: {critical|high|medium|low}
- current_state: {what is already known or complete}
- relevant_artifacts: {cells/... topic keys or file paths}
- relevant_files: {paths with one-line reasons}
- constraints: {scope, command policy, i18n, BBVA-first, test policy}
- acceptance_criteria:
  - {measurable criterion}
- evidence_required:
  - {command output, source decision, screenshot, coverage note, or explicit blocked reason}
- handoff_target: {next expected role or none}
```

When a field is unknown, write `unknown` and explain whether that blocks work. Do not silently omit fields.

## Skill Resolution

The orchestrator should pre-resolve skills and pass compact rules or exact skill references to the executor. Executors may fall back to local registry/path loading only when injected rules are absent.

Valid `skill_resolution` values:

- `injected`: received relevant rules or exact skill refs from orchestrator.
- `fallback-registry`: no injected rules; loaded from `.atl/skill-registry.md` or memory.
- `fallback-path`: no registry; loaded explicit `skills/.../SKILL.md` paths.
- `none`: no applicable skill guidance found.

If an executor returns `fallback-registry`, `fallback-path`, or `none`, the orchestrator must treat it as a warning and refresh skill context before future delegation.

## Dev-QA Loop

For implementation work, run a bounded Dev-QA loop:

1. Implementation receives one approved task batch with acceptance criteria.
2. Verification checks that batch with real evidence.
3. If verification passes, orchestration advances to the next task or phase.
4. If verification fails and the fix is in scope, implementation receives the exact QA feedback and retries.
5. After two failed fix attempts, stop with `blocked` and escalate with remaining issues, evidence, and recommended owner.

The verification agent must default to `blocked` or `partial` when evidence is missing. It must not approve based only on claims.

## Evidence Gates

Every agent result must include `evidence_required` coverage:

- source decisions for Cells catalogs, official docs, fallback use, or unavailable sources
- command evidence for tests, coverage, lint, build, or blocked command policy
- browser or screenshot evidence when user-visible UI changed
- i18n evidence when literals, locale files, or `this.t(...)` usage changed
- scope evidence for implementation batches

If evidence cannot be gathered, return the missing evidence as a risk and set `status` to `partial` or `blocked`.

## Result Envelope

Every agent returns:

- `status`: `success`, `partial`, or `blocked`
- `executive_summary`: one to three sentences
- `detailed_report`: optional detailed body
- `artifacts`: topic keys, files, screenshots, reports, or `none`
- `next_recommended`: next phase, role, or `none`
- `risks`: known risks or `none`
- `skill_resolution`: one of the valid values above
- `evidence_required`: evidence gathered, unavailable, or blocked

## Host Mapping

- OpenCode phase agents map directly to phase skills such as `cells-explore`, `cells-apply`, and `cells-verify`.
- VS Code role agents map phase prompts to stable roles: orchestration, analysis, implementation, and verification.
- Both hosts use this same contract and the same `skills/_shared/` policy files.

# Cells Agent Harness

## Decision

The harness uses a canonical core plus host adapters. It does not maintain a
portable copy per operating system or agent host.

```text
skills/                     canonical Cells behavior and indexed catalogs
examples/
  vscode/                   VS Code instructions, prompts, agents, hooks
  codex/                    Codex AGENTS, agents, hooks, rules, config example
  opencode/                 OpenCode commands, agents, and permissions
harness/manifest.json       profiles and capability matrix
scripts/cells_agent.py      render, install, doctor, validate
dist/                       generated and ignored
```

`SKILL.md` is the highest-portability unit. Instructions, agents, hooks,
permissions, memory, and MCP configuration remain adapters because the hosts do
not offer equivalent discovery, lifecycle, or approval semantics.

## Runtime contract for Cells

The generated agent must:

1. Detect the real Cells project instead of assuming a repository layout.
2. Resolve the Spherica `packages/` checkout and use catalog evidence before
   choosing or inventing a component API.
3. Prefer Cells commands. The audited feature has no `package.json` scripts, and
   its CI uses the Cells pipeline; generic `npm run build/test/lint` is not a
   safe default.
4. Route testing through `cells-cli-usage`, `cells-coverage`, and then
   `cells-test-creator`.
5. Keep single-agent execution as the default. Use bounded analysis,
   implementation, and verification agents only for independent work.
6. Report missing catalog, docs, CLI, credentials, commands, or runtime proof as
   degraded/blocked evidence rather than guessing.

The installer records detected paths in `.cells-agent/context.json`. Session
hooks load this file and inject the resolved environment into the agent.

## Profiles

### `single`

- one proportional orchestrator
- direct fast-path and scoped-change work
- no phase-agent fan-out
- recommended default for cost and context control

### `multi`

- orchestrator plus bounded host-native specialists
- one delegation level
- independent analysis, implementation, and verification only
- implementing agent is not the sole reviewer

The profile controls agent packaging, not model selection. Models remain a
host or organization concern and should be validated in the target environment.

## Capability boundaries

| Capability | Portable core | Host adapter policy |
|---|---|---|
| Skills | Yes | Copy canonical `SKILL.md` trees |
| Instructions | Semantics only | Generate host discovery paths |
| Agents/subagents | Contract only | Generate host role format and limits |
| Prompts/commands | Workflow only | Generate prompt files or commands |
| Hooks | No | Keep event payload and paths host-specific |
| MCP | Protocol only | Do not translate auth or approval configuration |
| Memory | No | Use explicit artifacts; host memory is supplemental |
| Permissions | Policy intent only | Never claim equivalent enforcement |

Each rendered artifact contains a `render-manifest.json` capability report with
`supported`, `preview`, `experimental`, `host-configured`, or host-specific
status values.

## Commands

```text
python scripts/cells_agent.py doctor [environment options]
python scripts/cells_agent.py render --host <host|all> --profile <single|multi>
python scripts/cells_agent.py install --host <host> --scope <user|workspace>
python scripts/cells_agent.py validate
```

Environment options:

- `--workspace <project-root>`
- `--catalog <spherica-repo-or-packages>`
- `--docs <cells-guides-checkout>`
- `--cells-cli <cells-cli-checkout>`

## Migration from the former `portable/` tree

1. Stop consuming old releases that distributed files under `portable/`.
2. Make changes only in `skills/`, `examples/<host>/`, or
   `harness/manifest.json`.
3. Render a temporary artifact with `cells_agent.py render`.
4. Run `cells_agent.py validate`.
5. Install into a clean temporary home/workspace and smoke-test discovery.
6. Publish the rendered artifact or install it directly. The source repository
   no longer tracks generated portable artifacts.

During an upgrade, the installer preserves retired skill names by default
because name matching alone cannot prove ownership. Pass `--force` only after
reviewing the target to remove the known retired Cells skill names and former
Codex plugin-cache location. Unrelated names and configuration remain
untouched.

The old `setup.*` entry points are aliases of the new installer. This avoids a
second implementation while existing automation migrates.

## Required smoke tests per host

1. Instruction discovery in a real Cells repository.
2. Catalog path appears in session context.
3. `cells-components-catalog` can answer one known component query.
4. Planner/explorer cannot edit when the host supports role tool limits.
5. `single` does not delegate; `multi` can run one bounded subagent.
6. One safe Cells command is allowed and one generic/destructive command is
   denied or requires approval as documented for that host.
7. Existing user configuration remains present after a second installation.

Hooks and VS Code plugins are preview/experimental surfaces. Re-run this matrix
when upgrading VS Code, Codex, or OpenCode.

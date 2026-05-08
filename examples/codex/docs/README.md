# CELLS Codex Runtime Docs

The Codex version uses the native project-layer layout:

- `AGENTS.md`
- `.codex/config.toml`
- `.codex/hooks.json`
- `.codex/rules/*.rules`
- `.codex/agents/*.toml`
- `.agents/plugins/marketplace.json`
- `plugins/cells-agent-bundle-codex/`

## Precedence and Trust

Codex reads `AGENTS.md` before work and loads project `.codex/` layers only when the project is trusted.

Apply layers in this order:

1. User/global Codex config
2. Project `AGENTS.md`
3. Project `.codex/config.toml`
4. Project `.codex/hooks.json`
5. Project `.codex/rules/*.rules`
6. Project `.codex/agents/*.toml`
7. Skills payload bundled in `plugins/cells-agent-bundle-codex/.cache/cells-skills/`

Practical interpretation for this bundle:

- `AGENTS.md` explains the Cells operating contract.
- `.codex/config.toml` enables hooks and sets multi-agent defaults.
- `.codex/hooks.json` adds narrow guardrails and extra context.
- `.codex/rules/default.rules` controls risky shell approvals outside the sandbox.
- `.codex/agents/*.toml` defines the role agents for orchestrator, analysis, implementation, and verification.
- The plugin exposes one lightweight Codex gateway skill and keeps the complete canonical skills payload in `.cache/cells-skills/` for repo-local discovery and marketplace-based reuse. The Codex subagents must route to `plugins/cells-agent-bundle-codex/.cache/cells-skills/`, not to the lightweight `skills/` gateway directory.

## Install Modes

Recommended repo-local install from the target repository root:

```bash
./scripts/install.sh --agent codex
```

This materializes:

- `AGENTS.md`
- `.codex/`
- `.agents/plugins/marketplace.json`
- `plugins/cells-agent-bundle-codex/`

Portable/manual copy path:

```bash
cp -R /path/to/cells-agents/portable/codex-project/. .
```

## Runtime Model

- `cells-orchestrator` is the coordinator.
- `cells-analysis`, `cells-implementation`, and `cells-verification` are executor agents.
- Executor agents do not launch nested subagents.
- The shared handoff contract remains authoritative in `plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-agent-handoff-contract.md`.

## Validation

Use structural validation as the release gate:

```bash
python3 scripts/validate_codex_assets.py
python3 scripts/validate_codex_assets.py --installed-root portable/codex-project
python3 scripts/validate_codex_assets.py --plugin-root plugins/cells-agent-bundle-codex
```

Treat these checks as structural/runtime-readiness evidence. They do not claim live Codex plugin loading unless a real Codex smoke run is added separately. The validation also checks for Codex hook behavior that is supported by current Codex docs; prompts belong in `default.rules`, while `PreToolUse` is used only for supported deny behavior.

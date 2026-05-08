# CELLS Codex Runtime Docs

The Codex version now targets the native user-level Codex layout first:

- `~/.codex/AGENTS.md`
- `~/.codex/config.toml`
- `~/.codex/hooks.json`
- `~/.codex/rules/*.rules`
- `~/.codex/agents/*.toml`
- `~/.agents/plugins/marketplace.json`
- `~/.codex/plugins/cells-agent-bundle-codex/`

## Precedence and Trust

Codex reads `~/.codex/AGENTS.md` as the global default layer. Project `AGENTS.md` and project `.codex/` files can still refine behavior inside trusted repositories.

Apply layers in this order:

1. User/global `~/.codex/AGENTS.md`
2. User/global `~/.codex/config.toml`
3. User/global `~/.codex/hooks.json`
4. User/global `~/.codex/rules/*.rules`
5. User/global `~/.codex/agents/*.toml`
6. Project `AGENTS.md` and project `.codex/` overrides when present and trusted
7. Skills payload bundled in `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/`

Practical interpretation for this bundle:

- `~/.codex/AGENTS.md` explains the Cells operating contract and self-scopes the bundle so it only activates for BBVA Cells repos or explicit Cells requests.
- `cells-work-sizing-contract.md` decides whether the task needs fast-path, scoped-change, full-workflow, or blocked handling.
- `~/.codex/config.toml` enables hooks and sets multi-agent defaults.
- `~/.codex/hooks.json` adds narrow guardrails and extra context.
- `~/.codex/rules/default.rules` controls risky shell approvals outside the sandbox.
- `~/.codex/agents/*.toml` defines the role agents for orchestrator, analysis, implementation, and verification.
- The plugin exposes one lightweight Codex gateway skill and keeps the complete canonical skills payload in `.cache/cells-skills/` for global discovery and marketplace-based reuse. The Codex subagents must route to `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/`, not to the lightweight `skills/` gateway directory.

## Install Modes

Recommended global install:

```bash
./scripts/install.sh --agent codex
```

This materializes:

- `~/.codex/AGENTS.md`
- `~/.codex/config.toml`
- `~/.codex/hooks.json`
- `~/.codex/rules/default.rules`
- `~/.codex/agents/*.toml`
- `~/.codex/plugins/cells-agent-bundle-codex/`
- `~/.agents/plugins/marketplace.json`

If `~/.codex/AGENTS.md` or `~/.codex/config.toml` already exists, keep the existing file and merge the Cells template manually instead of overwriting it blindly.

Portable/manual copy path:

```bash
cp -R /path/to/cells-agents/portable/codex-home/.codex "$HOME/"
cp -R /path/to/cells-agents/portable/codex-home/.agents "$HOME/"
```

## Runtime Model

- `cells-orchestrator` is the coordinator.
- `cells-analysis`, `cells-implementation`, and `cells-verification` are executor agents.
- Fast-path work should stay in the active agent with no subagents or artifacts.
- Scoped-change work should use only directly relevant skills and targeted validation.
- Full-workflow work may use the orchestrator and role agents when the user asks for end-to-end proof or the scope is broad enough to justify delegation.
- Executor agents do not launch nested subagents.
- The shared handoff contract remains authoritative in `~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/_shared/cells-agent-handoff-contract.md`.

## Validation

Use structural validation as the release gate:

```bash
python3 scripts/validate_codex_assets.py
python3 scripts/validate_codex_assets.py --installed-root portable/codex-home
python3 scripts/validate_codex_assets.py --plugin-root plugins/cells-agent-bundle-codex
```

Treat these checks as structural/runtime-readiness evidence. They do not claim live Codex plugin loading unless a real Codex smoke run is added separately. The validation also checks for Codex hook behavior that is supported by current Codex docs; prompts belong in `default.rules`, while `PreToolUse` is used only for supported deny behavior.

# Source decisions for runtime v3

These are architectural inspirations, not vendored implementations or compatibility promises. Cells keeps its own branding and original code.

| Source | Inspected revision | Applied idea |
| --- | --- | --- |
| [gentle-pi](https://github.com/Gentleman-Programming/gentle-pi) | `0da9bcca894e780ab5f3b1d0ebb27910d722c147` | Small tasks stay direct; workflow and delegation are optional; context retrieval stays bounded. |
| [gentle-ai](https://github.com/Gentleman-Programming/gentle-ai) | `9ec0cf443622f20fe511815ff5a83088c7467bff` | Separate native host adapters from shared capabilities, inspect before installation, and bind evidence to concrete source content. |
| [Engram](https://github.com/Gentleman-Programming/engram) | `a2199d92ebeb2f6fb422794088fa04a5bc280e55` | Curated SQLite memory, stable topic updates, preview-first retrieval, and explicit export migration. |

The inspected upstreams use MIT licensing. No upstream engine, prompts, installers or database code was copied. The new importer accepts the inspected public JSON export shape; it deliberately does not reproduce Engram's session, relation, prompt, sync or review services.

The BBVA snapshots supplied for this work are `cellsjs-guides-resources-master@a45a67146db/docs` and `bbva-spherica-components-master@df5bb7b94cd/packages`. Their rebuilt catalogs retain portable provenance and content hashes. Component `package.json` and CEM files provide the executable/API evidence; documentation names alone do not establish installed compatibility.

Native projections follow current primary documentation checked during implementation:

- [VS Code custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents): tool inheritance, empty child lists and automatic invocation.
- [VS Code agent plugins](https://code.visualstudio.com/docs/agent-customization/agent-plugins): plugin-relative hook paths and MCP packaging.
- [VS Code tool reference](https://code.visualstudio.com/docs/agents/reference/ai-features-cheat-sheet): current tool identifiers.
- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents): standalone TOML agents and executable delegation settings.
- [Codex configuration](https://learn.chatgpt.com/docs/config-file/config-reference): local stdio MCP configuration.
- [OpenCode permissions](https://opencode.ai/docs/permissions/): native task and tool controls.
- [MCP stdio transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports): request framing and protocol-only stdout.

Package validation executes temporary CLI, MCP and hook processes. It must not be described as an authenticated VS Code, Codex or OpenCode model session.

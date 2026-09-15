# VS Code adapter

The version 3 native adapter is documented in [the runtime guide](../../../docs/runtime.md).

Agents inherit the selected host model. Executors use empty child lists and remain invocable. Prompt files inherit agent tools. Analysis accesses catalogs through the local Cells MCP server, without arbitrary terminal execution. Workspace setup includes `.vscode/mcp.json`; the standalone plugin uses its own MCP configuration.

Hook commands in standalone plugins use `${PLUGIN_ROOT}`. The Node bridge invokes the packaged Python core. Policy checks only recognized command payloads, and native permissions remain authoritative. The Stop hook is inert; actual check evidence is stored separately.

Run the adapter validator against the source or a packaged installation. An authenticated host UI session remains a separate validation step.

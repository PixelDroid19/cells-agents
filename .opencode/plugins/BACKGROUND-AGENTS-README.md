# Optional OpenCode Background Delegation

This bundle ships a safe placeholder asset at `background-agents.ts` so setup and install scripts can surface optional plugin wiring without breaking standard `task` fallback.

- If your OpenCode environment supports background delegation, replace the placeholder with a real plugin that provides `delegate`, `delegation_read`, and `delegation_list`.
- If not, keep the placeholder and rely on synchronous `task` fallback.
- The orchestrator policy does not change: `/cells-*` commands stay canonical and Cells governance still applies.

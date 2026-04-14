---
name: agent-browser
description: >
  Automate browser interactions for Cells UI validation using CDP-based CLI. Triggers: when the user says "open the browser", "take a screenshot", "test this page", "click through", "validate the UI", "check how it looks", "automate the browser", "fill this form", "navigate to", "confirm rendered UI", "capturar screenshot", "validar visualmente", or when confirming rendered UI, capturing screenshots, filling forms, navigating routes, validating i18n visually, or running browser-level tests.
allowed-tools: Bash(npx agent-browser:*), Bash(agent-browser:*)
---

# Browser Automation with agent-browser

## Purpose

Validate browser-visible behavior for Cells components and demos. Use this skill when a change affects what the user can see or do in the browser.

## Core Workflow

Every browser automation follows this pattern:

1. **Connect**: Reuse existing dev server/runtime if one is running (`agent-browser connect <port>` or `agent-browser --auto-connect`)
2. **Navigate**: Open the target URL (`agent-browser open <url>`)
3. **Snapshot**: Capture initial state (`agent-browser snapshot -i`)
4. **Interact**: Use element refs to click, fill, select
5. **Re-snapshot**: Capture state after interaction to prove behavior changed

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# Output: @e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Submit"

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i  # Check result
```

## Key Rules

- **Reuse first**: Check for existing dev server, browser session, or CDP port before launching new browser. Why? Starting fresh browsers wastes time and may miss real runtime state.
- **Snapshot before interaction**: Always capture state before acting. Why? You need a baseline to prove the interaction caused a change.
- **Re-snapshot after DOM changes**: Get fresh element refs after navigation or DOM updates. Why? Old refs become stale and cause interaction failures.

## Common Commands

| Action | Command |
|--------|---------|
| Open URL | `agent-browser open <url>` |
| Connect to existing | `agent-browser connect <port>` or `agent-browser --auto-connect` |
| Snapshot | `agent-browser snapshot -i` |
| Click | `agent-click <ref>` |
| Fill input | `agent-browser fill <ref> "text"` |
| Select option | `agent-browser select <ref> "value"` |
| Wait | `agent-browser wait --load networkidle` |
| Screenshot | `agent-browser screenshot --path <file>` |
| Evaluate JS | `agent-browser evaluate "document.title"` |

## When to Use

- A change affects rendered UI, user flows, or visible states
- Specs require browser validation as evidence
- The orchestrator asks for screenshot or interaction proof
- Runtime i18n, theming, or dark-mode needs visual confirmation

## For Full Reference

- Command details: `references/commands.md`
- Troubleshooting: `references/troubleshooting.md`
- Evidence conventions: `references/evidence.md`
- Templates: `templates/`

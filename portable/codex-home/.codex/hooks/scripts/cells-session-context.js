#!/usr/bin/env node

const message = [
  'CELLS Codex global bundle installed.',
  'Apply it only when the current workspace is a BBVA Cells project or the user explicitly asks for Cells workflow help.',
  'Read ~/.codex/AGENTS.md first, then use ~/.codex/agents/*.toml for role routing when Cells mode applies.',
  'Canonical skills live under ~/.codex/plugins/cells-agent-bundle-codex/.cache/cells-skills/.'
].join(' ');

process.stdout.write(JSON.stringify({
  hookSpecificOutput: {
    hookEventName: 'SessionStart',
    additionalContext: message
  }
}));

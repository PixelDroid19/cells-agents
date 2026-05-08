#!/usr/bin/env node

const message = [
  'CELLS Codex project layer active.',
  'Read AGENTS.md first, then use .codex/agents/*.toml for role routing.',
  'Canonical skills live under plugins/cells-agent-bundle-codex/.cache/cells-skills/.',
  'For tests, use cells-cli-usage, cells-coverage, then cells-test-creator.'
].join(' ');

process.stdout.write(JSON.stringify({
  hookSpecificOutput: {
    hookEventName: 'SessionStart',
    additionalContext: message
  }
}));

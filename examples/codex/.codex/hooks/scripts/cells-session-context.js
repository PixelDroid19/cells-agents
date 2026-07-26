#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function loadCellsContext(start = process.cwd()) {
  let current = path.resolve(start);
  while (true) {
    const candidate = path.join(current, '.cells-agent', 'context.json');
    if (fs.existsSync(candidate)) {
      try {
        return JSON.parse(fs.readFileSync(candidate, 'utf8'));
      } catch {
        return { context_error: `Invalid JSON: ${candidate}` };
      }
    }
    const parent = path.dirname(current);
    if (parent === current) return null;
    current = parent;
  }
}

const context = loadCellsContext();
const environment = context
  ? `Resolved Cells environment: ${JSON.stringify(context)}`
  : 'No .cells-agent/context.json was found; do not assume catalog, docs, or CLI paths.';

const message = [
  'CELLS Codex global bundle installed.',
  'Apply it only when the current workspace is a BBVA Cells project or the user explicitly asks for Cells workflow help.',
  'Read ~/.codex/AGENTS.md first, then use ~/.codex/agents/*.toml for role routing when Cells mode applies.',
  'Canonical skills live under ~/.codex/skills/.',
  environment
].join(' ');

process.stdout.write(JSON.stringify({
  hookSpecificOutput: {
    hookEventName: 'SessionStart',
    additionalContext: message
  }
}));

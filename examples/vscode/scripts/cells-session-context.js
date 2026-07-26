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
  : 'No .cells-agent/context.json was found; run cells_agent.py doctor/install before assuming catalog or CLI paths.';

const message = [
  'CELLS workspace active.',
  'Use .github/copilot-instructions.md, .github/instructions/*.instructions.md, .github/prompts/*.prompt.md, .github/agents/*.agent.md, and .github/skills/ before Cells decisions.',
  'For tests, use cells-cli-usage, cells-coverage, then cells-test-creator.',
  environment
].join(' ');

process.stdout.write(JSON.stringify({
  hookSpecificOutput: {
    hookEventName: 'SessionStart',
    additionalContext: message
  }
}));

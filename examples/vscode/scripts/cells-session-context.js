#!/usr/bin/env node

const message = [
  'CELLS workspace active.',
  'Use .github/copilot-instructions.md, .github/instructions/*.instructions.md, .github/prompts/*.prompt.md, .github/agents/*.agent.md, and .github/skills/ before Cells decisions.',
  'For tests, use cells-cli-usage, cells-coverage, then cells-test-creator.'
].join(' ');

process.stdout.write(JSON.stringify({
  hookSpecificOutput: {
    hookEventName: 'SessionStart',
    additionalContext: message
  }
}));

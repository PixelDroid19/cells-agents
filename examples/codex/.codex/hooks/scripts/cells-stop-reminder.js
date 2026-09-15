#!/usr/bin/env node
// Thin native hook bridge. The Python core owns parsing and project policy.
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const event = "Stop";
let dir = __dirname;
let runtime;
for (let i = 0; i < 9; i++) {
  const candidate = path.join(dir, 'runtime', 'cells-agent.py');
  if (fs.existsSync(candidate)) { runtime = candidate; break; }
  const parent = path.dirname(dir);
  if (parent === dir) break;
  dir = parent;
}
const input = fs.readFileSync(0, 'utf8');
const fallback = message => JSON.stringify(event === 'PreToolUse' ? {
  hookSpecificOutput: { hookEventName: event, permissionDecision: 'ask', permissionDecisionReason: message }
} : { systemMessage: message });
if (!runtime) {
  process.stdout.write(fallback('Cells runtime is missing; repair the bundle before relying on this hook.'));
} else {
  const executable = process.env.CELLS_AGENT_PYTHON || (process.platform === 'win32' ? 'python' : 'python3');
  const result = spawnSync(executable, [runtime, 'hook', event], {
    input, encoding: 'utf8', timeout: 9000, maxBuffer: 1024 * 1024, windowsHide: true
  });
  let output;
  try { output = JSON.parse(result.stdout || ''); } catch {}
  process.stdout.write(output && typeof output === 'object' ? JSON.stringify(output) : fallback('Cells hook failed: ' + (result.error?.message || result.stderr || 'invalid runtime output').slice(0, 400)));
}

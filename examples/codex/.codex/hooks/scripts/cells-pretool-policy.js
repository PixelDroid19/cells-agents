#!/usr/bin/env node

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  let payload = {};
  try {
    payload = input.trim() ? JSON.parse(input) : {};
  } catch {
    process.stdout.write('{}');
    return;
  }

  const toolInput = payload.tool_input || {};
  const text = [
    payload.tool_name,
    toolInput.command,
    toolInput.cmd,
    toolInput.input,
    toolInput.text,
    Array.isArray(toolInput.args) ? toolInput.args.join(' ') : ''
  ].filter(Boolean).join(' ');

  const denyPatterns = [
    /\bgit\s+reset\s+--hard\b/i,
    /\bgit\s+checkout\s+--\s+/i,
    /\brm\s+-[a-z]*r[a-z]*f[a-z]*\s+(\/|\.|\*)(?:\s|$)/i,
    /\bdel\s+\/[fqs]\b/i,
    /\bRemove-Item\b.*\s-Recurse\b.*\s-Force\b/i,
    /\b(git\s+push\s+--force|git\s+push\s+-f)\b/i
  ];

  let permissionDecision;
  let permissionDecisionReason;

  if (denyPatterns.some(pattern => pattern.test(text))) {
    permissionDecision = 'deny';
    permissionDecisionReason = 'CELLS policy blocks destructive commands unless the user explicitly asks for the exact operation.';
  }

  if (!permissionDecision) {
    process.stdout.write('{}');
    return;
  }

  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision,
      permissionDecisionReason
    }
  }));
});

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
    /\brm\s+-rf\s+(\/|\.|\*)\b/i,
    /\bdel\s+\/[fqs]\b/i,
    /\bRemove-Item\b.*\s-Recurse\b.*\s-Force\b/i,
    /\b(git\s+push\s+--force|git\s+push\s+-f)\b/i
  ];

  const askPatterns = [
    /\bnpm\s+test\b/i,
    /\bnpm\s+run\s+test\b/i,
    /\bnpx\s+web-test-runner\b/i,
    /\bnpm\s+run\s+start\b/i
  ];

  let permissionDecision;
  let permissionDecisionReason;

  if (denyPatterns.some(pattern => pattern.test(text))) {
    permissionDecision = 'deny';
    permissionDecisionReason = 'CELLS policy blocks destructive commands unless the user explicitly asks and approves the exact operation.';
  } else if (askPatterns.some(pattern => pattern.test(text))) {
    permissionDecision = 'ask';
    permissionDecisionReason = 'CELLS projects should use Cells-native commands first; confirm this generic command is intentional.';
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

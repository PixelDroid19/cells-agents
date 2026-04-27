#!/usr/bin/env node

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  let payload = {};
  try {
    payload = input.trim() ? JSON.parse(input) : {};
  } catch {
    payload = {};
  }

  if (payload.stop_hook_active) {
    process.stdout.write('{}');
    return;
  }

  process.stdout.write(JSON.stringify({
    systemMessage: 'Before closing Cells work, confirm cells-verify evidence, source decisions, i18n routing when relevant, and residual risks are reported.'
  }));
});

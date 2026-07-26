#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
OUT_DIR="${1:-$REPO_DIR/dist/codex}"

if command -v python3 >/dev/null 2>&1; then PYTHON=python3; else PYTHON=python; fi
"$PYTHON" "$SCRIPT_DIR/cells_agent.py" render \
  --host codex --profile multi --output "$OUT_DIR" --force
PLUGIN_ROOT="$OUT_DIR/home/.agents/plugins/plugins/cells-agent-bundle-codex"
"$PYTHON" "$SCRIPT_DIR/validate_codex_assets.py" --plugin-root "$PLUGIN_ROOT"
echo "Built Codex package; plugin root: $PLUGIN_ROOT"

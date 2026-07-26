#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
OUT_DIR="${1:-$REPO_DIR/dist/vscode}"

if command -v python3 >/dev/null 2>&1; then PYTHON=python3; else PYTHON=python; fi
"$PYTHON" "$SCRIPT_DIR/cells_agent.py" render \
  --host vscode --profile multi --output "$OUT_DIR" --force
"$PYTHON" "$SCRIPT_DIR/validate_vscode_copilot_assets.py" --plugin-root "$OUT_DIR/plugin"
echo "Built VS Code package; plugin root: $OUT_DIR/plugin"

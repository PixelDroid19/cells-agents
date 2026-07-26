#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "Python 3 is required." >&2
  exit 1
fi

"$PYTHON" -m unittest discover -s "$REPO_DIR/tests" -p "test_*.py" -v
"$PYTHON" "$SCRIPT_DIR/cells_agent.py" validate

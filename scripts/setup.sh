#!/usr/bin/env bash
# Compatibility entrypoint for the v3 installer; accepts install.sh arguments.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/install.sh" "$@"

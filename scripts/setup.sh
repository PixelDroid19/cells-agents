#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "setup.sh is now an alias of the environment-neutral installer." >&2
exec "$SCRIPT_DIR/install.sh" "$@"

#!/usr/bin/env bash
set -euo pipefail

# Build a self-contained VS Code Copilot plugin package from canonical repo assets.
# Usage: bash scripts/build_vscode_plugin.sh [output-dir]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
OUT_DIR="${1:-$REPO_DIR/dist/vscode-plugin}"
VSCODE_SRC="$REPO_DIR/examples/vscode"
SKILLS_SRC="$REPO_DIR/skills"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/agents" "$OUT_DIR/hooks/scripts" "$OUT_DIR/skills"

cp "$VSCODE_SRC/plugin/plugin.json" "$OUT_DIR/plugin.json"
cp "$VSCODE_SRC/agents"/*.agent.md "$OUT_DIR/agents/"
sed 's#\.github/hooks/scripts/#hooks/scripts/#g' \
    "$VSCODE_SRC/hooks/cells-policy.json" > "$OUT_DIR/hooks/cells-policy.json"
cp "$VSCODE_SRC/scripts"/*.js "$OUT_DIR/hooks/scripts/"

if [ -d "$SKILLS_SRC/_shared" ]; then
    mkdir -p "$OUT_DIR/skills/_shared"
    for shared_file in "$SKILLS_SRC/_shared"/*.md "$SKILLS_SRC/_shared"/*.yaml; do
        [ -f "$shared_file" ] || continue
        cp "$shared_file" "$OUT_DIR/skills/_shared/"
    done
fi

for skill_dir in "$SKILLS_SRC"/*/; do
    [ -d "$skill_dir" ] || continue
    source_dir="${skill_dir%/}"
    skill_name="$(basename "$source_dir")"
    case "$skill_name" in
        _shared|scripts|evals) continue ;;
    esac
    if [ -f "$source_dir/SKILL.md" ]; then
        cp -R "$source_dir" "$OUT_DIR/skills/$skill_name"
    fi
done

find "$OUT_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} +
find "$OUT_DIR" -name ".DS_Store" -delete

python3 "$SCRIPT_DIR/validate_vscode_copilot_assets.py" --plugin-root "$OUT_DIR"

echo "Built VS Code Copilot plugin package: $OUT_DIR"

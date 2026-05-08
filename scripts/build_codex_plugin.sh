#!/usr/bin/env bash
set -euo pipefail

# Build a self-contained Codex plugin package from canonical repo skills.
# Usage: bash scripts/build_codex_plugin.sh [output-dir]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
OUT_DIR="${1:-$REPO_DIR/dist/codex-plugin}"
PLUGIN_SRC="$REPO_DIR/plugins/cells-agent-bundle-codex"
SKILLS_SRC="$REPO_DIR/skills"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/.codex-plugin" "$OUT_DIR/skills" "$OUT_DIR/.cache/cells-skills"

cp "$PLUGIN_SRC/.codex-plugin/plugin.json" "$OUT_DIR/.codex-plugin/plugin.json"
cp -R "$PLUGIN_SRC/skills" "$OUT_DIR/"

if [ -d "$SKILLS_SRC/_shared" ]; then
    mkdir -p "$OUT_DIR/.cache/cells-skills/_shared"
    for shared_file in "$SKILLS_SRC/_shared"/*.md "$SKILLS_SRC/_shared"/*.yaml; do
        [ -f "$shared_file" ] || continue
        cp "$shared_file" "$OUT_DIR/.cache/cells-skills/_shared/"
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
        cp -R "$source_dir" "$OUT_DIR/.cache/cells-skills/$skill_name"
    fi
done

find "$OUT_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} +
find "$OUT_DIR" -name ".DS_Store" -delete

python3 "$SCRIPT_DIR/validate_codex_assets.py" --plugin-root "$OUT_DIR"

echo "Built Codex plugin package: $OUT_DIR"

#!/usr/bin/env bash
set -euo pipefail

# Build ready-to-copy installation assets for restrictive corporate environments.
# Usage: bash scripts/build_portable_assets.sh [output-dir]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
OUT_DIR="${1:-$REPO_DIR/portable}"
SKILLS_SRC="$REPO_DIR/skills"
OPENCODE_SRC="$REPO_DIR/examples/opencode"
VSCODE_SRC="$REPO_DIR/examples/vscode"
VSCODE_PLUGIN_BUILDER="$SCRIPT_DIR/build_vscode_plugin.sh"
VSCODE_VALIDATOR="$SCRIPT_DIR/validate_vscode_copilot_assets.py"

CORE_WORKFLOW_COMMANDS=(
    "cells-init.md"
    "cells-explore.md"
    "cells-new.md"
    "cells-continue.md"
    "cells-ff.md"
    "cells-apply.md"
    "cells-verify.md"
    "cells-archive.md"
)

copy_skill_bundle() {
    local target_dir="$1"

    rm -rf "$target_dir"
    mkdir -p "$target_dir"

    if [ -d "$SKILLS_SRC/_shared" ]; then
        mkdir -p "$target_dir/_shared"
        for shared_file in "$SKILLS_SRC/_shared"/*.md "$SKILLS_SRC/_shared"/*.yaml; do
            [ -f "$shared_file" ] || continue
            cp "$shared_file" "$target_dir/_shared/"
        done
    fi

    for skill_dir in "$SKILLS_SRC"/*/; do
        [ -d "$skill_dir" ] || continue
        local source_dir="${skill_dir%/}"
        local skill_name
        skill_name="$(basename "$source_dir")"
        case "$skill_name" in
            _shared|scripts|evals) continue ;;
        esac
        [ -f "$source_dir/SKILL.md" ] || continue
        cp -R "$source_dir" "$target_dir/$skill_name"
    done

    find "$target_dir" -type d -name "__pycache__" -prune -exec rm -rf {} +
    find "$target_dir" -name ".DS_Store" -delete
}

build_opencode_home() {
    local target_root="$OUT_DIR/opencode-home/.config/opencode"
    local template_root="$OUT_DIR/opencode-home/templates"

    rm -rf "$OUT_DIR/opencode-home"
    mkdir -p "$target_root"
    mkdir -p "$template_root"

    copy_skill_bundle "$target_root/skills"

    mkdir -p "$target_root/commands"
    for cmd_name in "${CORE_WORKFLOW_COMMANDS[@]}"; do
        cp "$OPENCODE_SRC/commands/$cmd_name" "$target_root/commands/$cmd_name"
    done

    mkdir -p "$target_root/plugins"
    cp "$OPENCODE_SRC/plugins/background-agents.ts" "$target_root/plugins/background-agents.ts"
    cp "$OPENCODE_SRC/plugins/BACKGROUND-AGENTS-README.md" "$target_root/plugins/BACKGROUND-AGENTS-README.md"

    cp "$OPENCODE_SRC/opencode.json" "$target_root/opencode.json"
    cp "$OPENCODE_SRC/opencode.single.json" "$template_root/opencode.single.json"
    cp "$OPENCODE_SRC/opencode.multi.json" "$template_root/opencode.multi.json"
}

build_project_local() {
    local target_root="$OUT_DIR/project-local/.opencode"

    rm -rf "$OUT_DIR/project-local"
    mkdir -p "$target_root"
    copy_skill_bundle "$target_root/skills"
}

build_vscode_workspace() {
    local github_target="$OUT_DIR/vscode/.github"
    local plugin_target="$github_target/plugin"

    rm -rf "$OUT_DIR/vscode-workspace"
    rm -rf "$OUT_DIR/vscode"
    mkdir -p \
        "$github_target/instructions" \
        "$github_target/prompts" \
        "$github_target/agents" \
        "$github_target/hooks/scripts" \
        "$plugin_target/agents" \
        "$plugin_target/hooks/scripts"

    cp "$VSCODE_SRC/copilot-instructions.md" "$github_target/copilot-instructions.md"
    cp "$VSCODE_SRC/instructions"/*.instructions.md "$github_target/instructions/"
    cp "$VSCODE_SRC/prompts"/*.prompt.md "$github_target/prompts/"
    cp "$VSCODE_SRC/agents"/*.agent.md "$github_target/agents/"
    cp "$VSCODE_SRC/hooks"/*.json "$github_target/hooks/"
    cp "$VSCODE_SRC/scripts"/*.js "$github_target/hooks/scripts/"

    copy_skill_bundle "$github_target/skills"

    cp "$VSCODE_SRC/plugin/plugin.json" "$plugin_target/plugin.json"
    cp "$VSCODE_SRC/agents"/*.agent.md "$plugin_target/agents/"
    sed 's#\.github/hooks/scripts/#.github/plugin/hooks/scripts/#g' \
        "$VSCODE_SRC/hooks/cells-policy.json" > "$plugin_target/hooks/cells-policy.json"
    cp "$VSCODE_SRC/scripts"/*.js "$plugin_target/hooks/scripts/"
    copy_skill_bundle "$plugin_target/skills"
}

validate_portable_assets() {
    python3 "$VSCODE_VALIDATOR" --installed-root "$OUT_DIR/vscode/.github" > /dev/null
    python3 "$VSCODE_VALIDATOR" --plugin-root "$OUT_DIR/vscode-plugin" > /dev/null
}

main() {
    mkdir -p "$OUT_DIR"

    build_opencode_home
    build_project_local
    build_vscode_workspace
    bash "$VSCODE_PLUGIN_BUILDER" "$OUT_DIR/vscode-plugin" > /dev/null
    validate_portable_assets

    echo "Built portable installation assets: $OUT_DIR"
}

main "$@"

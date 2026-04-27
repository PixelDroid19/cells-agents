#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Cells Agent Bundle — Install Script
# Copies CELLS and Cells specialist skills to your AI coding assistant's skill directory
# Cross-platform: macOS, Linux, Windows (Git Bash / WSL)
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
SKILLS_SRC="$REPO_DIR/skills"
PORTABLE_SRC="$REPO_DIR/portable"

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

# ============================================================================
# OS Detection
# ============================================================================

detect_os() {
    case "$(uname -s)" in
        Darwin)  OS="macos" ;;
        Linux)
            if grep -qi microsoft /proc/version 2>/dev/null; then
                OS="wsl"
            else
                OS="linux"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)  OS="windows" ;;
        *)  OS="unknown" ;;
    esac
}

os_label() {
    case "$OS" in
        macos)   echo "macOS" ;;
        linux)   echo "Linux" ;;
        wsl)     echo "WSL" ;;
        windows) echo "Windows (Git Bash)" ;;
        *)       echo "Unknown" ;;
    esac
}

# ============================================================================
# Color support
# ============================================================================

setup_colors() {
    if [[ "$OS" == "windows" ]] && [[ -z "${WT_SESSION:-}" ]] && [[ -z "${TERM_PROGRAM:-}" ]]; then
        # Plain CMD without Windows Terminal — no ANSI support
        RED='' GREEN='' YELLOW='' BLUE='' CYAN='' BOLD='' NC=''
    else
        RED='\033[0;31m'
        GREEN='\033[0;32m'
        YELLOW='\033[1;33m'
        BLUE='\033[0;34m'
        CYAN='\033[0;36m'
        BOLD='\033[1m'
        NC='\033[0m'
    fi
}

# ============================================================================
# Path Resolution
# ============================================================================

get_tool_path() {
    local tool="$1"
    case "$tool" in
        opencode)
            case "$OS" in
                windows)  echo "$USERPROFILE/.config/opencode/skills" ;;
                macos)    echo "$HOME/.config/opencode/skills" ;;
                *)        echo "$HOME/.config/opencode/skills" ;;
            esac
            ;;
        opencode-commands)
            case "$OS" in
                windows)  echo "$USERPROFILE/.config/opencode/commands" ;;
                macos)    echo "$HOME/.config/opencode/commands" ;;
                *)        echo "$HOME/.config/opencode/commands" ;;
            esac
            ;;
        vscode)      echo "./.github/skills" ;;
        project-local) echo "./.opencode/skills" ;;
    esac
}

# ============================================================================
# Helpers
# ============================================================================

make_writable() {
    if [[ "$OS" != "windows" ]]; then
        chmod u+w "$1" 2>/dev/null || true
    fi
}

print_header() {
    echo ""
    echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║      Cells Agent Bundle — Installer      ║${NC}"
    echo -e "${CYAN}${BOLD}║    CELLS workflows for AI assistants     ║${NC}"
    echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BOLD}Detected:${NC} $(os_label)"
    echo ""
}

print_skill() {
    echo -e "  ${GREEN}✓${NC} $1"
}

print_warn() {
    echo -e "  ${YELLOW}!${NC} $1"
}

print_error() {
    echo -e "  ${RED}✗${NC} $1"
}

print_next_step() {
    local config_file="$1"
    local example_file="$2"
    echo -e "\n${YELLOW}Next step:${NC} Add the orchestrator to your ${BOLD}$config_file${NC}"
    echo -e "  See: ${CYAN}$example_file${NC}"
}

print_engram_note() {
    echo -e "\n${YELLOW}Recommended persistence backend:${NC} ${BOLD}Engram${NC}"
    echo -e "  ${CYAN}Engram repository${NC}"
    echo -e "  If Engram is available, it will be used automatically (recommended)"
    echo -e "  If not, falls back to ${BOLD}none${NC} — enable ${BOLD}engram${NC} or ${BOLD}openspec${NC} for better results"
}

show_help() {
    echo "Usage: install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --agent NAME    Install for a specific agent (non-interactive)"
    echo "  --path DIR      Custom install path (use with --agent custom)"
    echo "  -h, --help      Show this help"
    echo ""
    echo "Agents: opencode, vscode, project-local, all-global"
    echo ""
    echo "Manual/corporate install assets: portable/README.md"
}

# ============================================================================
# Install functions
# ============================================================================

validate_source() {
    local missing=0
    for skill_dir in "$SKILLS_SRC"/*/; do
        [ -d "$skill_dir" ] || continue
        local skill_name
        skill_name="$(basename "${skill_dir%/}")"
        case "$skill_name" in
            _shared|scripts|evals) continue ;;
        esac
        if [ ! -f "$skill_dir/SKILL.md" ]; then
            print_error "Missing: $skill_name/SKILL.md"
            missing=$((missing + 1))
        fi
    done
    if [ ! -d "$SKILLS_SRC/_shared" ]; then
        print_error "Missing: _shared/ directory"
        missing=$((missing + 1))
    fi
    if [ "$missing" -gt 0 ]; then
        echo -e "\n${RED}${BOLD}Source validation failed.${NC} Is this a complete clone of the repository?"
        exit 1
    fi
}

portable_bundle_exists() {
    local bundle="$1"
    case "$bundle" in
        opencode) [ -d "$PORTABLE_SRC/opencode-home/.config/opencode/skills" ] ;;
        vscode) [ -d "$PORTABLE_SRC/vscode/.github/skills" ] ;;
        project-local) [ -d "$PORTABLE_SRC/project-local/.opencode/skills" ] ;;
        *) return 1 ;;
    esac
}

copy_tree_into_parent() {
    local source_tree="$1"
    local target_parent="$2"

    if [ ! -d "$source_tree" ]; then
        print_error "Portable source not found: $source_tree"
        return 1
    fi

    if [ ! -d "$target_parent" ]; then
        print_error "Target parent directory does not exist: $target_parent"
        print_warn "Use Finder/manual copy with the portable assets under $PORTABLE_SRC"
        return 1
    fi

    cp -R "$source_tree" "$target_parent/"
}

clear_managed_skill_targets() {
    local base_dir="$1"

    rm -rf "$base_dir/_shared"

    for skill_dir in "$SKILLS_SRC"/*/; do
        [ -d "$skill_dir" ] || continue
        local skill_name
        skill_name="$(basename "${skill_dir%/}")"
        case "$skill_name" in
            _shared|scripts|evals) continue ;;
        esac
        rm -rf "$base_dir/$skill_name"
    done
}

install_opencode_from_portable() {
    local tool_name="$1"
    local home_root
    case "$OS" in
        windows) home_root="$USERPROFILE" ;;
        *) home_root="$HOME" ;;
    esac
    local opencode_root="$home_root/.config/opencode"
    local config_target="$opencode_root/opencode.json"
    local config_backup=""

    echo -e "\n${BLUE}Installing portable ${BOLD}$tool_name${NC}${BLUE} bundle...${NC}"

    if [ -f "$config_target" ]; then
        config_backup="$(mktemp)"
        cp "$config_target" "$config_backup"
    fi

    clear_managed_skill_targets "$opencode_root/skills"
    for cmd_name in "${CORE_WORKFLOW_COMMANDS[@]}"; do
        rm -f "$opencode_root/commands/$cmd_name"
    done
    rm -f "$opencode_root/plugins/background-agents.ts"
    rm -f "$opencode_root/plugins/BACKGROUND-AGENTS-README.md"

    copy_tree_into_parent "$PORTABLE_SRC/opencode-home/.config" "$home_root"

    if [ -n "$config_backup" ]; then
        cp "$config_backup" "$config_target"
        rm -f "$config_backup"
        print_warn "OpenCode config already exists at $config_target"
        print_warn "Merge cells-orchestrator from examples/opencode/opencode.json"
    else
        print_skill "opencode.json ($(dirname "$config_target"))"
    fi

    print_skill "portable OpenCode skills"
    print_skill "portable OpenCode commands"
    print_skill "portable OpenCode plugins"
    echo -e "\n  ${GREEN}${BOLD}Portable bundle installed${NC} → $opencode_root"
}

install_project_local_from_portable() {
    local target_root="$PWD"

    echo -e "\n${BLUE}Installing portable ${BOLD}Project-local${NC}${BLUE} bundle...${NC}"

    clear_managed_skill_targets "$target_root/.opencode/skills"
    copy_tree_into_parent "$PORTABLE_SRC/project-local/.opencode" "$target_root"

    print_skill ".opencode/skills"
    echo -e "\n  ${GREEN}${BOLD}Portable bundle installed${NC} → $target_root/.opencode"
}

install_vscode_from_portable() {
    local target_root="$PWD/.github"

    echo -e "\n${BLUE}Installing portable ${BOLD}VS Code (Copilot)${NC}${BLUE} workspace assets...${NC}"

    rm -f "$target_root/copilot-instructions.md"
    rm -f "$target_root/instructions/cells-orchestrator.instructions.md"
    rm -f "$target_root/prompts"/cells-*.prompt.md
    rm -f "$target_root/agents"/cells-*.agent.md
    rm -f "$target_root/hooks/cells-policy.json"
    rm -f "$target_root/hooks/scripts/cells-pretool-policy.js"
    rm -f "$target_root/hooks/scripts/cells-session-context.js"
    rm -f "$target_root/hooks/scripts/cells-stop-reminder.js"
    rm -rf "$target_root/plugin"
    clear_managed_skill_targets "$target_root/skills"

    copy_tree_into_parent "$PORTABLE_SRC/vscode/.github" "$PWD"

    print_skill ".github/copilot-instructions.md"
    print_skill ".github/instructions/*.instructions.md"
    print_skill ".github/prompts/*.prompt.md"
    print_skill ".github/agents/*.agent.md"
    print_skill ".github/hooks/*.json"
    print_skill ".github/plugin/ (optional Copilot plugin package)"
}

install_skills() {
    local target_dir="$1"
    local tool_name="$2"

    echo -e "\n${BLUE}Installing skills for ${BOLD}$tool_name${NC}${BLUE}...${NC}"

    mkdir -p "$target_dir"

    # Copy shared convention files (_shared/)
    local shared_src="$SKILLS_SRC/_shared"
    local shared_target="$target_dir/_shared"

    if [ -d "$shared_src" ]; then
        local shared_count=0
        mkdir -p "$shared_target" 2>/dev/null || {
            make_writable "$shared_target"
        }
        for shared_file in "$shared_src"/*.md "$shared_src"/*.yaml; do
            if [ -f "$shared_file" ]; then
                cp "$shared_file" "$shared_target/" 
                shared_count=$((shared_count + 1))
            fi
        done
        if [ "$shared_count" -gt 0 ]; then
            print_skill "_shared ($shared_count convention files)"
        else
            print_warn "_shared directory found but no .md files to copy"
        fi
    fi

    local count=0
    for skill_dir in "$SKILLS_SRC"/*/; do
        [ -d "$skill_dir" ] || continue
        local source_dir="${skill_dir%/}"
        local skill_name
        skill_name=$(basename "$source_dir")
        case "$skill_name" in
            _shared|scripts|evals) continue ;;
        esac
        local target_skill_dir="$target_dir/$skill_name"

        # Verify source SKILL.md exists before creating target directory
        if [ ! -f "$source_dir/SKILL.md" ]; then
            print_warn "Skipping $skill_name (SKILL.md not found in source)"
            continue
        fi

        rm -rf "$target_skill_dir"
        cp -R "$source_dir" "$target_skill_dir"

        if [ ! -f "$target_skill_dir/SKILL.md" ]; then
            print_error "Failed to install $skill_name (destination SKILL.md missing)"
            exit 1
        fi

        find "$target_skill_dir" -type d -name "__pycache__" -prune -exec rm -rf {} +
        print_skill "$skill_name"
        count=$((count + 1))
    done

    echo -e "\n  ${GREEN}${BOLD}$count skills installed${NC} → $target_dir"
}

install_opencode_commands() {
    local commands_src="$REPO_DIR/examples/opencode/commands"
    local commands_target
    commands_target="$(get_tool_path opencode-commands)"

    echo -e "\n${BLUE}Installing OpenCode commands...${NC}"

    mkdir -p "$commands_target"

    local count=0
    local cmd_name
    for cmd_name in "${CORE_WORKFLOW_COMMANDS[@]}"; do
        if [ -f "$commands_src/$cmd_name" ]; then
            cp "$commands_src/$cmd_name" "$commands_target/$cmd_name"
            print_skill "${cmd_name%.md}"
            count=$((count + 1))
        else
            print_warn "Skipping missing workflow command: ${cmd_name%.md}"
        fi
    done

    echo -e "\n  ${GREEN}${BOLD}$count commands installed${NC} → $commands_target"
}

install_opencode_config() {
    local config_src="$REPO_DIR/examples/opencode/opencode.json"
    local config_target
    case "$OS" in
        windows)  config_target="$USERPROFILE/.config/opencode/opencode.json" ;;
        *)        config_target="$HOME/.config/opencode/opencode.json" ;;
    esac

    if [ ! -f "$config_src" ]; then
        print_warn "Skipping OpenCode config install (source not found: $config_src)"
        return
    fi

    mkdir -p "$(dirname "$config_target")"

    if [ -e "$config_target" ] && [ "$config_src" -ef "$config_target" ]; then
        print_warn "Skipping OpenCode config copy (source and destination are the same file)"
        return
    fi

    if [ -f "$config_target" ]; then
        print_warn "OpenCode config already exists at $config_target"
        print_warn "Merge cells-orchestrator from examples/opencode/opencode.json"
        return
    fi

    cp "$config_src" "$config_target"
    print_skill "opencode.json ($(dirname "$config_target"))"
}

install_opencode_plugins() {
    local plugins_src="$REPO_DIR/examples/opencode/plugins"
    local plugins_target
    case "$OS" in
        windows)  plugins_target="$USERPROFILE/.config/opencode/plugins" ;;
        *)        plugins_target="$HOME/.config/opencode/plugins" ;;
    esac

    if [ ! -d "$plugins_src" ]; then
        print_warn "Skipping OpenCode plugin assets (source not found: $plugins_src)"
        return
    fi

    mkdir -p "$plugins_target"
    cp "$plugins_src/background-agents.ts" "$plugins_target/background-agents.ts"
    cp "$plugins_src/BACKGROUND-AGENTS-README.md" "$plugins_target/BACKGROUND-AGENTS-README.md"
    print_skill "OpenCode optional background delegation assets"
}

install_vscode_assets() {
    local vscode_src="$REPO_DIR/examples/vscode"
    local github_target="./.github"

    if [ ! -d "$vscode_src" ]; then
        print_warn "Skipping VS Code assets (source not found: $vscode_src)"
        return
    fi

    echo -e "\n${BLUE}Installing VS Code Copilot workspace assets...${NC}"

    local plugin_target="$github_target/plugin"

    mkdir -p \
        "$github_target/instructions" \
        "$github_target/prompts" \
        "$github_target/agents" \
        "$github_target/hooks/scripts"

    rm -rf "$plugin_target"
    mkdir -p \
        "$plugin_target/agents" \
        "$plugin_target/hooks/scripts" \
        "$plugin_target/skills"

    cp "$vscode_src/copilot-instructions.md" "$github_target/copilot-instructions.md"
    cp "$vscode_src/instructions"/*.instructions.md "$github_target/instructions/"
    cp "$vscode_src/prompts"/*.prompt.md "$github_target/prompts/"
    cp "$vscode_src/agents"/*.agent.md "$github_target/agents/"
    cp "$vscode_src/hooks"/*.json "$github_target/hooks/"
    cp "$vscode_src/scripts"/*.js "$github_target/hooks/scripts/"
    cp "$vscode_src/plugin/plugin.json" "$plugin_target/plugin.json"
    cp "$vscode_src/agents"/*.agent.md "$plugin_target/agents/"
    sed 's#\.github/hooks/scripts/#.github/plugin/hooks/scripts/#g' \
        "$vscode_src/hooks/cells-policy.json" > "$plugin_target/hooks/cells-policy.json"
    cp "$vscode_src/scripts"/*.js "$plugin_target/hooks/scripts/"

    if [ -d "$SKILLS_SRC/_shared" ]; then
        mkdir -p "$plugin_target/skills/_shared"
        for shared_file in "$SKILLS_SRC/_shared"/*.md "$SKILLS_SRC/_shared"/*.yaml; do
            [ -f "$shared_file" ] || continue
            cp "$shared_file" "$plugin_target/skills/_shared/"
        done
    fi

    for skill_dir in "$SKILLS_SRC"/*/; do
        [ -d "$skill_dir" ] || continue
        local source_dir="${skill_dir%/}"
        local skill_name
        skill_name=$(basename "$source_dir")
        case "$skill_name" in
            _shared|scripts|evals) continue ;;
        esac
        if [ -f "$source_dir/SKILL.md" ]; then
            cp -R "$source_dir" "$plugin_target/skills/$skill_name"
        fi
    done

    find "$plugin_target" -type d -name "__pycache__" -prune -exec rm -rf {} +
    find "$plugin_target" -name ".DS_Store" -delete

    print_skill ".github/copilot-instructions.md"
    print_skill ".github/instructions/*.instructions.md"
    print_skill ".github/prompts/*.prompt.md"
    print_skill ".github/agents/*.agent.md"
    print_skill ".github/hooks/*.json"
    print_skill ".github/plugin/ (optional Copilot plugin package)"
}

# ============================================================================
# Agent install dispatcher
# ============================================================================

install_for_agent() {
    local agent="$1"

    case "$agent" in
        opencode)
            if portable_bundle_exists opencode; then
                install_opencode_from_portable "OpenCode"
            else
                print_warn "Portable OpenCode bundle not found; falling back to file-by-file installer"
                install_skills "$(get_tool_path opencode)" "OpenCode"
                install_opencode_commands
                install_opencode_config
                install_opencode_plugins
            fi
            echo ""
            echo -e "${YELLOW}${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
            echo -e "${YELLOW}${BOLD}║  ACTION REQUIRED: Add the cells-orchestrator agent config     ║${NC}"
            echo -e "${YELLOW}${BOLD}║                                                              ║${NC}"
            echo -e "${YELLOW}${BOLD}║  Copy the agent block from:                                  ║${NC}"
            echo -e "${YELLOW}${BOLD}║    examples/opencode/opencode.json                           ║${NC}"
            echo -e "${YELLOW}${BOLD}║  Into your:                                                  ║${NC}"
            echo -e "${YELLOW}${BOLD}║    ~/.config/opencode/opencode.json                          ║${NC}"
            echo -e "${YELLOW}${BOLD}║                                                              ║${NC}"
            echo -e "${YELLOW}${BOLD}║  Without this, /cells-* commands will fail.                   ║${NC}"
            echo -e "${YELLOW}${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
            ;;
        vscode)
            if portable_bundle_exists vscode; then
                install_vscode_from_portable
            else
                print_warn "Portable VS Code bundle not found; falling back to file-by-file installer"
                install_skills "$(get_tool_path vscode)" "VS Code (Copilot)"
                install_vscode_assets
            fi
            echo -e "  ${YELLOW}Note:${NC} VS Code workspace assets installed in current project (.github/)"
            ;;
        project-local)
            if portable_bundle_exists project-local; then
                install_project_local_from_portable
            else
                print_warn "Portable project-local bundle not found; falling back to file-by-file installer"
                install_skills "$(get_tool_path project-local)" "Project-local"
            fi
            echo -e "\n${YELLOW}Note:${NC} Skills installed in ${BOLD}./.opencode/skills/${NC} — OpenCode project-local discovery path"
            echo -e "  ${YELLOW}Commands:${NC} use ${BOLD}--agent opencode${NC} for global commands or copy ${BOLD}examples/opencode/commands/${NC} to ${BOLD}./.opencode/commands/${NC}"
            ;;
        all-global)
            if portable_bundle_exists opencode; then
                install_opencode_from_portable "OpenCode"
            else
                print_warn "Portable OpenCode bundle not found; falling back to file-by-file installer"
                install_skills "$(get_tool_path opencode)" "OpenCode"
                install_opencode_commands
                install_opencode_config
                install_opencode_plugins
            fi
            echo -e "\n${YELLOW}Next steps:${NC}"
            echo -e "  1. ${YELLOW}${BOLD}[REQUIRED]${NC} Add orchestrator agent to ${BOLD}~/.config/opencode/opencode.json${NC}"
            echo -e "     ${YELLOW}See: examples/opencode/opencode.json — without this, /cells-* commands won't work${NC}"
            ;;
        custom)
            if [[ -z "${CUSTOM_PATH:-}" ]]; then
                read -rp "Enter target path: " CUSTOM_PATH
            fi
            install_skills "$CUSTOM_PATH" "Custom"
            ;;
        *)
            print_error "Unknown agent: $agent"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# ============================================================================
# Interactive menu
# ============================================================================

interactive_menu() {
    echo -e "${BOLD}Select your AI coding assistant:${NC}\n"
    echo "  1) OpenCode       ($(get_tool_path opencode))"
    echo "  2) VS Code        ($(get_tool_path vscode))"
    echo "  3) Project-local  ($(get_tool_path project-local))"
    echo "  4) All global     (OpenCode)"
    echo "  5) Custom path"
    echo ""
    read -rp "Choice [1-5]: " choice

    case $choice in
        1)  install_for_agent "opencode" ;;
        2)  install_for_agent "vscode" ;;
        3)  install_for_agent "project-local" ;;
        4)  install_for_agent "all-global" ;;
        5)  install_for_agent "custom" ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

# ============================================================================
# Main
# ============================================================================

# Detect OS first — needed for colors and paths
detect_os

# Setup colors based on OS + terminal capabilities
setup_colors

# Parse arguments
AGENT=""
CUSTOM_PATH=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --agent)  AGENT="$2"; shift 2 ;;
        --path)   CUSTOM_PATH="$2"; shift 2 ;;
        -h|--help) show_help; exit 0 ;;
        *)  echo "Unknown option: $1"; show_help; exit 1 ;;
    esac
done

print_header
validate_source

if [[ -n "$AGENT" ]]; then
    # Non-interactive mode
    install_for_agent "$AGENT"
else
    # Interactive mode
    interactive_menu
fi

echo -e "\n${GREEN}${BOLD}Done!${NC} Start with ${CYAN}/cells-init${NC} and continue the workflow with ${CYAN}/cells-new${NC} or ${CYAN}/cells-continue${NC}\n"
print_engram_note
echo ""

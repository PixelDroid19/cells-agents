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
        project-local) echo "./skills" ;;
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
}

# ============================================================================
# Install functions
# ============================================================================

validate_source() {
    local missing=0
    for skill_dir in "$SKILLS_SRC"/cells-*/; do
        [ -d "$skill_dir" ] || continue
        if [ ! -f "$skill_dir/SKILL.md" ]; then
            print_error "Missing: $(basename "$skill_dir")/SKILL.md"
            missing=$((missing + 1))
        fi
    done
    if [ -d "$SKILLS_SRC/agent-browser" ] && [ ! -f "$SKILLS_SRC/agent-browser/SKILL.md" ]; then
        print_error "Missing: agent-browser/SKILL.md"
        missing=$((missing + 1))
    fi
    if [ ! -d "$SKILLS_SRC/_shared" ]; then
        print_error "Missing: _shared/ directory"
        missing=$((missing + 1))
    fi
    if [ "$missing" -gt 0 ]; then
        echo -e "\n${RED}${BOLD}Source validation failed.${NC} Is this a complete clone of the repository?"
        exit 1
    fi
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
        for shared_file in "$shared_src"/*.md; do
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
    for skill_dir in "$SKILLS_SRC"/cells-*/; do
        [ -d "$skill_dir" ] || continue
        local source_dir="${skill_dir%/}"
        local skill_name
        skill_name=$(basename "$source_dir")
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

    if [ -d "$SKILLS_SRC/agent-browser" ]; then
        if [ -f "$SKILLS_SRC/agent-browser/SKILL.md" ]; then
            local agent_browser_src="$SKILLS_SRC/agent-browser"
            local agent_browser_target="$target_dir/agent-browser"

            rm -rf "$agent_browser_target"
            cp -R "$agent_browser_src" "$agent_browser_target"

            if [ ! -f "$agent_browser_target/SKILL.md" ]; then
                print_error "Failed to install agent-browser (destination SKILL.md missing)"
                exit 1
            fi

            find "$agent_browser_target" -type d -name "__pycache__" -prune -exec rm -rf {} +
            print_skill "agent-browser"
            count=$((count + 1))
        else
            print_warn "Skipping agent-browser (SKILL.md not found in source)"
        fi
    fi

    if [ -d "$SKILLS_SRC/skill-registry" ] && [ -f "$SKILLS_SRC/skill-registry/SKILL.md" ]; then
        local registry_target="$target_dir/skill-registry"
        rm -rf "$registry_target"
        cp -R "$SKILLS_SRC/skill-registry" "$registry_target"
        print_skill "skill-registry"
        count=$((count + 1))
    fi

    echo -e "\n  ${GREEN}${BOLD}$count skills installed${NC} → $target_dir"
}

install_opencode_commands() {
    local commands_src="$REPO_DIR/examples/opencode/commands"
    local commands_target
    commands_target="$(get_tool_path opencode-commands)"

    echo -e "\n${BLUE}Installing OpenCode commands...${NC}"

    mkdir -p "$commands_target"

    local count=0
    for cmd_file in "$commands_src"/*.md; do
        [ -f "$cmd_file" ] || continue
        local cmd_name
        cmd_name=$(basename "$cmd_file")
        cp "$cmd_file" "$commands_target/$cmd_name"
        print_skill "${cmd_name%.md}"
        count=$((count + 1))
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

# ============================================================================
# Agent install dispatcher
# ============================================================================

install_for_agent() {
    local agent="$1"

    case "$agent" in
        opencode)
            install_skills "$(get_tool_path opencode)" "OpenCode"
            install_opencode_commands
            install_opencode_config
            install_opencode_plugins
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
            install_skills "$(get_tool_path vscode)" "VS Code (Copilot)"
            print_next_step ".github/copilot-instructions.md" ".github/instructions/copilot-instructions.md"
            echo -e "  ${YELLOW}Note:${NC} Skills installed in current project (.github/skills/)"
            ;;
        project-local)
            install_skills "$(get_tool_path project-local)" "Project-local"
            echo -e "\n${YELLOW}Note:${NC} Skills installed in ${BOLD}./skills/${NC} — relative to this project"
            echo -e "  ${YELLOW}Compatibility:${NC} project-local no longer creates ${BOLD}./.opencode/${NC}; use ${BOLD}examples/opencode/${NC} with user-level ${BOLD}~/.config/opencode/${NC} setup instead"
            ;;
        all-global)
            install_skills "$(get_tool_path opencode)" "OpenCode"
            install_opencode_commands
            install_opencode_config
            install_opencode_plugins
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

echo -e "\n${GREEN}${BOLD}Done!${NC} Start with ${CYAN}/cells-init${NC} or inspect a component with ${CYAN}/cells-component bbva-type-text${NC}\n"
print_engram_note
echo ""

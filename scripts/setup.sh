#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Cells Agent Bundle — Full Setup Script
# Detects installed agents, copies skills, and configures orchestrator prompts.
# Idempotent: safe to run multiple times (uses markers to avoid duplication).
# Cross-platform: macOS, Linux, Windows (Git Bash / WSL)
#
# Usage:
#   ./setup.sh                      # Interactive: detect + let user choose
#   ./setup.sh --all                # Auto-detect + install for all found agents
#   ./setup.sh --agent claude-code  # Install for a specific agent
#   ./setup.sh --non-interactive    # For external installers
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
SKILLS_SRC="$REPO_DIR/skills"
EXAMPLES_DIR="$REPO_DIR/examples"

MARKER_BEGIN="<!-- BEGIN:cells-agent-bundle -->"
MARKER_END="<!-- END:cells-agent-bundle -->"

# Backward-compat markers we can upgrade in place
OLD_MARKER_BEGIN="<!-- BEGIN:agent-teams-lite -->"
OLD_MARKER_END="<!-- END:agent-teams-lite -->"
GAI_MARKER_BEGIN="<!-- gentle-ai:sdd-orchestrator -->"
GAI_MARKER_END="<!-- /gentle-ai:sdd-orchestrator -->"

ORCHESTRATOR_HEADINGS=(
    "## Spec-Driven Development (SDD) Orchestrator"
    "## Spec-Driven Development (SDD)"
    "## Agent Teams Orchestrator"
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

home_dir() {
    if [[ "$OS" == "windows" ]]; then
        echo "${USERPROFILE:-$HOME}"
    else
        echo "$HOME"
    fi
}

# ============================================================================
# Colors
# ============================================================================

setup_colors() {
    if [[ "$OS" == "windows" ]] && [[ -z "${WT_SESSION:-}" ]] && [[ -z "${TERM_PROGRAM:-}" ]]; then
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

ok()    { echo -e "  ${GREEN}✓${NC} $1"; }
warn()  { echo -e "  ${YELLOW}!${NC} $1"; }
fail()  { echo -e "  ${RED}✗${NC} $1"; }
info()  { echo -e "  ${BLUE}→${NC} $1"; }
header(){ echo -e "\n${CYAN}${BOLD}$1${NC}"; }

# ============================================================================
# Agent Detection
# ============================================================================

DETECTED_AGENTS=()

check_agent() {
    local agent_name="$1"
    local binary="$2"

    if command -v "$binary" &>/dev/null; then
        ok "$agent_name ($binary found in PATH)"
        DETECTED_AGENTS+=("$agent_name")
    fi
}

detect_agents() {
    header "Detecting installed agents..."

    DETECTED_AGENTS=()
    check_agent "claude-code" "claude"
    check_agent "opencode" "opencode"
    check_agent "gemini-cli" "gemini"
    check_agent "cursor" "cursor"
    check_agent "vscode" "code"
    check_agent "codex" "codex"

    echo ""
    if [[ ${#DETECTED_AGENTS[@]} -eq 0 ]]; then
        warn "No agents detected in PATH"
        info "You can still install manually with: ./install.sh"
    else
        echo -e "  ${GREEN}${BOLD}${#DETECTED_AGENTS[@]} agent(s) detected${NC}"
    fi
}

# ============================================================================
# Path Resolution
# ============================================================================

get_skills_path() {
    local agent="$1"
    local home
    home="$(home_dir)"

    case "$agent" in
        claude-code)  echo "$home/.claude/skills" ;;
        opencode)     echo "$home/.config/opencode/skills" ;;
        gemini-cli)   echo "$home/.gemini/skills" ;;
        cursor)       echo "$home/.cursor/skills" ;;
        vscode)       echo "$home/.copilot/skills" ;;
        codex)        echo "$home/.codex/skills" ;;
    esac
}

get_prompt_path() {
    local agent="$1"
    local home
    home="$(home_dir)"

    case "$agent" in
        claude-code)  echo "$home/.claude/CLAUDE.md" ;;
        opencode)     echo "$home/.config/opencode/AGENTS.md" ;;
        gemini-cli)   echo "$home/.gemini/GEMINI.md" ;;
        cursor)       echo "$home/.cursor/rules/cells-agent-bundle.mdc" ;;
        vscode)
            if [[ "$OS" == "windows" ]]; then
                echo "${APPDATA:-$home/AppData/Roaming}/Code/User/prompts/cells-agent-bundle.instructions.md"
            elif [[ "$OS" == "macos" ]]; then
                echo "$home/Library/Application Support/Code/User/prompts/cells-agent-bundle.instructions.md"
            else
                echo "$home/.config/Code/User/prompts/cells-agent-bundle.instructions.md"
            fi
            ;;
        codex)        echo "$home/.codex/agents.md" ;;
    esac
}

get_example_file() {
    local agent="$1"
    case "$agent" in
        claude-code)  echo "$EXAMPLES_DIR/claude-code/CLAUDE.md" ;;
        opencode)     echo "" ;; # OpenCode has special handling
        gemini-cli)   echo "$EXAMPLES_DIR/gemini-cli/GEMINI.md" ;;
        cursor)       echo "$EXAMPLES_DIR/cursor/.cursorrules" ;;
        vscode)       echo "$REPO_DIR/.github/instructions/copilot-instructions.md" ;;
        codex)        echo "$EXAMPLES_DIR/codex/agents.md" ;;
    esac
}

# ============================================================================
# Install Skills
# ============================================================================

install_skill_directory() {
    local source_dir="$1"
    local target_dir="$2"
    local skill_name

    skill_name="$(basename "$source_dir")"

    if [ ! -f "$source_dir/SKILL.md" ]; then
        warn "Skipping $skill_name (SKILL.md not found in source)"
        return 0
    fi

    rm -rf "$target_dir/$skill_name"
    cp -R "$source_dir" "$target_dir/$skill_name"
    find "$target_dir/$skill_name" -type d -name "__pycache__" -prune -exec rm -rf {} +
    ok "$skill_name"
}

install_skills() {
    local target_dir="$1"

    info "Installing skills → $target_dir"
    mkdir -p "$target_dir"

    # Copy _shared convention files
    local shared_src="$SKILLS_SRC/_shared"
    local shared_target="$target_dir/_shared"
    if [ -d "$shared_src" ]; then
        mkdir -p "$shared_target"
        cp "$shared_src"/*.md "$shared_target/" 2>/dev/null || true
        ok "_shared conventions"
    fi

    local count=0

    # Copy all cells-* skills (phase + specialist)
    for skill_dir in "$SKILLS_SRC"/cells-*/; do
        [ -d "$skill_dir" ] || continue
        install_skill_directory "${skill_dir%/}" "$target_dir"
        count=$((count + 1))
    done

    # Copy skill-registry if present
    if [ -d "$SKILLS_SRC/skill-registry" ]; then
        install_skill_directory "$SKILLS_SRC/skill-registry" "$target_dir"
        count=$((count + 1))
    fi

    # Copy agent-browser if present
    if [ -d "$SKILLS_SRC/agent-browser" ]; then
        install_skill_directory "$SKILLS_SRC/agent-browser" "$target_dir"
        count=$((count + 1))
    fi

    ok "$count skills installed"
}

# ============================================================================
# Setup Orchestrator Prompt (idempotent with markers)
# ============================================================================

extract_orchestrator_content() {
    local example_file="$1"
    local content

    content=$(awk '
        BEGIN { start=0 }
        /^## (Spec-Driven Development|Agent Teams)/ { start=1 }
        { if (start) print }
    ' "$example_file")

    if [ -z "${content// }" ]; then
        cat "$example_file"
    else
        printf '%s\n' "$content"
    fi
}

replace_marked_block() {
    local prompt_path="$1"
    local begin_marker="$2"
    local end_marker="$3"
    local content_file="$4"
    local output_file

    output_file=$(mktemp)

    awk \
        -v begin="$begin_marker" \
        -v end="$end_marker" \
        -v new_begin="$MARKER_BEGIN" \
        -v new_end="$MARKER_END" \
        -v content_file="$content_file" '
        $0 == begin {
            print new_begin
            while ((getline line < content_file) > 0) print line
            close(content_file)
            skip=1
            next
        }
        $0 == end {
            if (skip == 1) {
                print new_end
                skip=0
                next
            }
        }
        skip != 1 { print }
    ' "$prompt_path" > "$output_file"

    mv "$output_file" "$prompt_path"
}

setup_orchestrator() {
    local prompt_path="$1"
    local example_file="$2"

    [ -n "$example_file" ] || return 0
    [ -f "$example_file" ] || { warn "Example file not found: $example_file"; return 0; }

    local prompt_dir
    prompt_dir="$(dirname "$prompt_path")"
    mkdir -p "$prompt_dir"

    local content_file
    content_file=$(mktemp)
    extract_orchestrator_content "$example_file" > "$content_file"

    if [ -f "$prompt_path" ]; then
        if grep -qF "$MARKER_BEGIN" "$prompt_path"; then
            replace_marked_block "$prompt_path" "$MARKER_BEGIN" "$MARKER_END" "$content_file"
            ok "Orchestrator updated in $prompt_path"
        elif grep -qF "$OLD_MARKER_BEGIN" "$prompt_path"; then
            replace_marked_block "$prompt_path" "$OLD_MARKER_BEGIN" "$OLD_MARKER_END" "$content_file"
            ok "Orchestrator updated in $prompt_path (upgraded old markers)"
        elif grep -qF "$GAI_MARKER_BEGIN" "$prompt_path"; then
            replace_marked_block "$prompt_path" "$GAI_MARKER_BEGIN" "$GAI_MARKER_END" "$content_file"
            ok "Orchestrator updated in $prompt_path (replaced gentle-ai section)"
        else
            local already_present=false
            for heading in "${ORCHESTRATOR_HEADINGS[@]}"; do
                if grep -qF "$heading" "$prompt_path"; then
                    already_present=true
                    break
                fi
            done

            if $already_present; then
                warn "Orchestrator already present in $prompt_path (no markers found)"
                info "To enable auto-updates, wrap the SDD section with:"
                info "  $MARKER_BEGIN"
                info "  $MARKER_END"
            else
                {
                    echo ""
                    echo "$MARKER_BEGIN"
                    cat "$content_file"
                    echo "$MARKER_END"
                } >> "$prompt_path"
                ok "Orchestrator appended to $prompt_path"
            fi
        fi
    else
        {
            echo "$MARKER_BEGIN"
            cat "$content_file"
            echo "$MARKER_END"
        } > "$prompt_path"
        ok "Orchestrator created at $prompt_path"
    fi

    rm -f "$content_file"
}

# ============================================================================
# OpenCode Special Handling
# ============================================================================

ask_opencode_mode() {
    # If already set via flag, skip
    [[ -n "$OPENCODE_MODE" ]] && return

    # Non-interactive defaults to single
    if $NON_INTERACTIVE; then
        OPENCODE_MODE="single"
        return
    fi

    echo ""
    echo -e "  ${BOLD}OpenCode agent mode:${NC}"
    echo ""
    echo "  1) Single model  — one agent handles all phases (simple, recommended)"
    echo "  2) Multi-model   — one agent per phase, each with its own model"
    echo ""
    read -rp "  Choice [1]: " mode_choice
    mode_choice="${mode_choice:-1}"

    case "$mode_choice" in
        2|multi)  OPENCODE_MODE="multi" ;;
        *)        OPENCODE_MODE="single" ;;
    esac
}

map_multi_phase_agent() {
    local command_name="$1"
    case "$command_name" in
        cells-init|cells-explore|cells-apply|cells-verify|cells-archive)
            echo "$command_name"
            ;;
        *)
            echo ""
            ;;
    esac
}

setup_opencode() {
    local home
    home="$(home_dir)"
    local commands_src="$EXAMPLES_DIR/opencode/commands"
    local commands_target="$home/.config/opencode/commands"
    local config_file="$home/.config/opencode/opencode.json"

    # Determine mode and pick the right config template
    ask_opencode_mode
    local example_config="$EXAMPLES_DIR/opencode/opencode.${OPENCODE_MODE}.json"
    if [ ! -f "$example_config" ] && [ "$OPENCODE_MODE" = "single" ]; then
        example_config="$EXAMPLES_DIR/opencode/opencode.json"
    fi

    info "OpenCode mode: $OPENCODE_MODE"

    # Install commands
    if [ -d "$commands_src" ]; then
        mkdir -p "$commands_target"
        local count=0

        for cmd_file in "$commands_src"/cells-*.md; do
            [ -f "$cmd_file" ] || continue
            local cmd_name
            cmd_name="$(basename "$cmd_file" .md)"

            if [[ "$OPENCODE_MODE" == "multi" ]] && grep -q "^subtask:" "$cmd_file"; then
                local target_agent
                target_agent="$(map_multi_phase_agent "$cmd_name")"
                if [[ -n "$target_agent" ]]; then
                    sed "s/^agent: cells-orchestrator/agent: $target_agent/" "$cmd_file" > "$commands_target/$(basename "$cmd_file")"
                else
                    cp "$cmd_file" "$commands_target/"
                fi
            else
                cp "$cmd_file" "$commands_target/"
            fi

            count=$((count + 1))
        done

        ok "$count OpenCode commands installed ($OPENCODE_MODE mode)"
    fi

    # Merge opencode.json agent config
    if command -v jq &>/dev/null && [ -f "$example_config" ]; then
        if [ -f "$config_file" ]; then
            local example_agents
            example_agents=$(jq '.agent // {}' "$example_config")

            local merged
            merged=$(jq --argjson new_agents "$example_agents" '
                # Preserve user model choices on existing phase agents
                (reduce ((.agent // {}) | to_entries[] |
                    select((.key | startswith("cells-")) or (.key | startswith("sdd-"))) |
                    select(.value.model)) as $e
                    ({}; . + {($e.key): $e.value.model})) as $saved_models |

                # Remove old cells/sdd agents, preserve user custom non-cells agents
                .agent = (
                    ((.agent // {}) | with_entries(select(((.key | startswith("cells-")) or (.key | startswith("sdd-"))) | not)))
                    + $new_agents
                ) |

                # Restore saved model values if same key still exists
                reduce ($saved_models | to_entries[]) as $m (.;
                    if .agent[$m.key] then .agent[$m.key].model = $m.value else . end
                ) |

                # Clean stale plural key from old versions
                del(.agents)
            ' "$config_file")

            echo "$merged" > "$config_file"
            ok "Agent config merged into $config_file ($OPENCODE_MODE mode)"
        else
            mkdir -p "$(dirname "$config_file")"
            cp "$example_config" "$config_file"
            ok "Config created at $config_file ($OPENCODE_MODE mode)"
        fi
    else
        if ! command -v jq &>/dev/null; then
            warn "jq not found — cannot auto-merge opencode.json"
        fi
        warn "Merge manually: copy agent block from examples/opencode/opencode.${OPENCODE_MODE}.json"
        info "Into: $config_file"
    fi
}

# ============================================================================
# Full Setup for One Agent
# ============================================================================

setup_agent() {
    local agent="$1"
    header "Setting up $agent"

    local skills_path
    skills_path="$(get_skills_path "$agent")"
    install_skills "$skills_path"

    local prompt_path example_file
    prompt_path="$(get_prompt_path "$agent")"
    example_file="$(get_example_file "$agent")"

    if [[ "$agent" == "opencode" ]]; then
        setup_opencode
    else
        setup_orchestrator "$prompt_path" "$example_file"
    fi
}

# ============================================================================
# Summary
# ============================================================================

INSTALLED_AGENTS=()

show_summary() {
    header "Setup Complete"
    echo ""
    for agent in "${INSTALLED_AGENTS[@]}"; do
        local skills_path prompt_path
        skills_path="$(get_skills_path "$agent")"
        prompt_path="$(get_prompt_path "$agent")"
        echo -e "  ${GREEN}✓${NC} ${BOLD}$agent${NC}"
        echo -e "    Skills: $skills_path"
        echo -e "    Prompt: $prompt_path"
    done

    echo ""
    echo -e "${GREEN}${BOLD}Done!${NC} Start using Cells workflow commands like ${CYAN}/cells-init${NC}"
    echo ""
    echo -e "${YELLOW}Recommended:${NC} Install ${BOLD}Engram${NC} for cross-session persistence"
    echo -e "  ${CYAN}https://github.com/gentleman-programming/engram${NC}"
    echo ""
}

# ============================================================================
# Interactive Menu
# ============================================================================

interactive_menu() {
    if [[ ${#DETECTED_AGENTS[@]} -eq 0 ]]; then
        echo ""
        warn "No agents detected. Use ./install.sh for manual installation."
        exit 0
    fi

    echo ""
    echo -e "${BOLD}Set up all detected agents? [Y/n]${NC} "
    read -r answer
    answer="${answer:-Y}"

    if [[ "$answer" =~ ^[Yy] ]]; then
        for agent in "${DETECTED_AGENTS[@]}"; do
            setup_agent "$agent"
            INSTALLED_AGENTS+=("$agent")
        done
    else
        echo ""
        echo -e "${BOLD}Select agents to set up (space-separated numbers):${NC}"
        echo ""
        local i=1
        for agent in "${DETECTED_AGENTS[@]}"; do
            echo "  $i) $agent"
            i=$((i + 1))
        done
        echo ""
        read -rp "Choice: " choices

        for choice in $choices; do
            local idx=$((choice - 1))
            if [[ $idx -ge 0 ]] && [[ $idx -lt ${#DETECTED_AGENTS[@]} ]]; then
                local agent="${DETECTED_AGENTS[$idx]}"
                setup_agent "$agent"
                INSTALLED_AGENTS+=("$agent")
            fi
        done
    fi
}

# ============================================================================
# Main
# ============================================================================

detect_os
setup_colors

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║    Cells Agent Bundle — Full Setup       ║${NC}"
echo -e "${CYAN}${BOLD}║   Detect • Install • Configure           ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════╝${NC}"

# Parse arguments
AGENT=""
ALL=false
NON_INTERACTIVE=false
OPENCODE_MODE=""  # "", "single", or "multi"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --agent)
            AGENT="$2"
            shift 2
            ;;
        --all)
            ALL=true
            shift
            ;;
        --non-interactive)
            NON_INTERACTIVE=true
            ALL=true
            shift
            ;;
        --opencode-mode)
            if [[ "$2" == "single" || "$2" == "multi" ]]; then
                OPENCODE_MODE="$2"
                shift 2
            else
                echo "Invalid opencode mode: $2 (use 'single' or 'multi')"
                exit 1
            fi
            ;;
        -h|--help)
            echo "Usage: setup.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --all               Auto-detect and install for all found agents"
            echo "  --agent NAME        Install for a specific agent"
            echo "  --opencode-mode M   OpenCode agent mode: 'single' or 'multi' (per-phase models)"
            echo "  --non-interactive   No prompts (for external installers)"
            echo "  -h, --help          Show this help"
            echo ""
            echo "Agents: claude-code, opencode, gemini-cli, cursor, vscode, codex"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -n "$AGENT" ]]; then
    case "$AGENT" in
        claude-code|opencode|gemini-cli|cursor|vscode|codex)
            ;;
        *)
            fail "Unknown agent: $AGENT"
            echo "Valid agents: claude-code, opencode, gemini-cli, cursor, vscode, codex"
            exit 1
            ;;
    esac
fi

# Validate source
if [ ! -d "$SKILLS_SRC/_shared" ]; then
    fail "Missing: skills/_shared"
    fail "Is this a complete clone of cells-teams?"
    exit 1
fi

found_cells_skill=false
for skill_dir in "$SKILLS_SRC"/cells-*/; do
    [ -d "$skill_dir" ] || continue
    found_cells_skill=true
    if [ ! -f "$skill_dir/SKILL.md" ]; then
        fail "Missing: $(basename "$skill_dir")/SKILL.md"
        exit 1
    fi
done

if ! $found_cells_skill; then
    fail "No cells-* skills found in $SKILLS_SRC"
    exit 1
fi

if [[ -n "$AGENT" ]]; then
    setup_agent "$AGENT"
    INSTALLED_AGENTS+=("$AGENT")
elif $ALL; then
    detect_agents
    for agent in "${DETECTED_AGENTS[@]}"; do
        setup_agent "$agent"
        INSTALLED_AGENTS+=("$agent")
    done
else
    detect_agents
    interactive_menu
fi

if [[ ${#INSTALLED_AGENTS[@]} -gt 0 ]]; then
    show_summary
else
    echo ""
    warn "No agents were set up."
fi

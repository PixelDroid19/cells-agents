#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Agent Teams Lite — Install Script Tests
# Run: bash scripts/install_test.sh
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
INSTALL_SCRIPT="$SCRIPT_DIR/install.sh"

# ============================================================================
# Test state
# ============================================================================

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
FAILURES=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Expected skills from the source tree (all skill folders with SKILL.md, excluding _shared)
EXPECTED_SKILLS=()
for skill_dir in "$REPO_DIR"/skills/*; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    [[ "$skill_name" == "_shared" ]] && continue
    [[ -f "$skill_dir/SKILL.md" ]] || continue
    EXPECTED_SKILLS+=("$skill_name")
done
EXPECTED_SKILL_COUNT="${#EXPECTED_SKILLS[@]}"
EXPECTED_COMMAND_COUNT=$(find "$REPO_DIR/examples/opencode/commands" -name "cells-*.md" | wc -l | tr -d ' ')

# ============================================================================
# Test helpers
# ============================================================================

setup() {
    TEST_TMPDIR="$(mktemp -d)"
    export HOME="$TEST_TMPDIR/home"
    mkdir -p "$HOME"
    # Fake Windows-style env vars for cross-platform path tests
    export USERPROFILE="$TEST_TMPDIR/home"
    export APPDATA="$TEST_TMPDIR/appdata"
    mkdir -p "$APPDATA"
}

teardown() {
    rm -rf "$TEST_TMPDIR"
}

assert_eq() {
    local expected="$1"
    local actual="$2"
    local msg="${3:-}"
    if [[ "$expected" == "$actual" ]]; then
        return 0
    fi
    echo "  Expected: $expected"
    echo "  Actual:   $actual"
    [[ -n "$msg" ]] && echo "  Message:  $msg"
    return 1
}

assert_file_exists() {
    local file="$1"
    if [[ -f "$file" ]]; then
        return 0
    fi
    echo "  File not found: $file"
    return 1
}

assert_dir_exists() {
    local dir="$1"
    if [[ -d "$dir" ]]; then
        return 0
    fi
    echo "  Directory not found: $dir"
    return 1
}

assert_file_not_empty() {
    local file="$1"
    local min_bytes="${2:-100}"
    if [[ ! -f "$file" ]]; then
        echo "  File not found: $file"
        return 1
    fi
    local size
    size=$(wc -c < "$file" | tr -d ' ')
    if [[ "$size" -lt "$min_bytes" ]]; then
        echo "  File too small: $file ($size bytes, expected >= $min_bytes)"
        return 1
    fi
    return 0
}

assert_file_contains() {
    local file="$1"
    local pattern="$2"
    if [[ ! -f "$file" ]]; then
        echo "  File not found: $file"
        return 1
    fi
    if grep -q "$pattern" "$file"; then
        return 0
    fi
    echo "  Pattern '$pattern' not found in: $file"
    return 1
}

assert_all_skills_installed() {
    local base_dir="$1"
    for skill in "${EXPECTED_SKILLS[@]}"; do
        assert_dir_exists "$base_dir/$skill" || return 1
        assert_file_exists "$base_dir/$skill/SKILL.md" || return 1
        assert_file_not_empty "$base_dir/$skill/SKILL.md" || return 1
        if [[ "$skill" == "cells-components-catalog" ]]; then
            assert_file_exists "$base_dir/$skill/scripts/build_index.py" || return 1
            assert_file_exists "$base_dir/$skill/scripts/search_docs.py" || return 1
            assert_file_exists "$base_dir/$skill/assets/component_manifest.json" || return 1
            assert_file_exists "$base_dir/$skill/assets/bbva_cells_components.db" || return 1
        fi
    done
    return 0
}

run_test() {
    local name="$1"
    local func="$2"
    TESTS_RUN=$((TESTS_RUN + 1))
    setup
    echo -n "  $name ... "
    local output
    if output=$($func 2>&1); then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}"
        if [[ -n "$output" ]]; then
            echo "$output" | sed 's/^/    /'
        fi
        TESTS_FAILED=$((TESTS_FAILED + 1))
        FAILURES="$FAILURES\n  - $name"
    fi
    teardown
}

# ============================================================================
# Tests — Help & Error Handling
# ============================================================================

test_help_flag() {
    local output
    output=$(bash "$INSTALL_SCRIPT" --help 2>&1)
    echo "$output" | grep -q "Usage:" || { echo "Help output missing 'Usage:'"; return 1; }
    echo "$output" | grep -q "claude-code" || { echo "Help output missing 'claude-code'"; return 1; }
    echo "$output" | grep -q "opencode" || { echo "Help output missing 'opencode'"; return 1; }
    echo "$output" | grep -q "all-global" || { echo "Help output missing 'all-global'"; return 1; }
    echo "$output" | grep -q "\-\-agent" || { echo "Help output missing '--agent'"; return 1; }
    echo "$output" | grep -q "\-\-path" || { echo "Help output missing '--path'"; return 1; }
}

test_help_exits_zero() {
    bash "$INSTALL_SCRIPT" --help > /dev/null 2>&1
    # If we get here, exit code was 0
    return 0
}

test_invalid_agent() {
    if bash "$INSTALL_SCRIPT" --agent nonexistent > /dev/null 2>&1; then
        echo "Expected non-zero exit for invalid agent, but got 0"
        return 1
    fi
    return 0
}

test_invalid_option() {
    if bash "$INSTALL_SCRIPT" --bogus-flag > /dev/null 2>&1; then
        echo "Expected non-zero exit for unknown option, but got 0"
        return 1
    fi
    return 0
}

# ============================================================================
# Tests — Claude Code
# ============================================================================

test_install_claude_code() {
    bash "$INSTALL_SCRIPT" --agent claude-code > /dev/null 2>&1
    assert_all_skills_installed "$HOME/.claude/skills"
}

test_claude_code_skill_count() {
    bash "$INSTALL_SCRIPT" --agent claude-code > /dev/null 2>&1
    local count
    count=$(find "$HOME/.claude/skills" -name "SKILL.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_SKILL_COUNT" "$count" "Expected exactly $EXPECTED_SKILL_COUNT skills for Claude Code"
}

# ============================================================================
# Tests — OpenCode
# ============================================================================

test_install_opencode() {
    bash "$INSTALL_SCRIPT" --agent opencode > /dev/null 2>&1
    assert_all_skills_installed "$HOME/.config/opencode/skills"
}

test_opencode_skill_count() {
    bash "$INSTALL_SCRIPT" --agent opencode > /dev/null 2>&1
    local count
    count=$(find "$HOME/.config/opencode/skills" -name "SKILL.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_SKILL_COUNT" "$count" "Expected exactly $EXPECTED_SKILL_COUNT skills for OpenCode"
}

test_opencode_commands() {
    bash "$INSTALL_SCRIPT" --agent opencode > /dev/null 2>&1
    local commands_dir="$HOME/.config/opencode/commands"
    assert_dir_exists "$commands_dir" || return 1
    assert_file_exists "$commands_dir/cells-init.md" || return 1
    assert_file_exists "$commands_dir/cells-apply.md" || return 1
    assert_file_exists "$commands_dir/cells-explore.md" || return 1
    assert_file_exists "$commands_dir/cells-verify.md" || return 1
    assert_file_exists "$commands_dir/cells-archive.md" || return 1
    assert_file_exists "$commands_dir/cells-new.md" || return 1
    assert_file_exists "$commands_dir/cells-author.md" || return 1
    assert_file_exists "$commands_dir/cells-ff.md" || return 1
    assert_file_exists "$commands_dir/cells-continue.md" || return 1
    assert_file_exists "$commands_dir/cells-coverage.md" || return 1
    assert_file_exists "$commands_dir/cells-i18n.md" || return 1
    local count
    count=$(find "$commands_dir" -name "cells-*.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_COMMAND_COUNT" "$count" "Expected exactly $EXPECTED_COMMAND_COUNT OpenCode commands"
}

# ============================================================================
# Tests — Gemini CLI
# ============================================================================

test_install_gemini_cli() {
    bash "$INSTALL_SCRIPT" --agent gemini-cli > /dev/null 2>&1
    assert_all_skills_installed "$HOME/.gemini/skills"
}

test_gemini_cli_skill_count() {
    bash "$INSTALL_SCRIPT" --agent gemini-cli > /dev/null 2>&1
    local count
    count=$(find "$HOME/.gemini/skills" -name "SKILL.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_SKILL_COUNT" "$count" "Expected exactly $EXPECTED_SKILL_COUNT skills for Gemini CLI"
}

# ============================================================================
# Tests — Codex
# ============================================================================

test_install_codex() {
    bash "$INSTALL_SCRIPT" --agent codex > /dev/null 2>&1
    assert_all_skills_installed "$HOME/.codex/skills"
}

test_codex_skill_count() {
    bash "$INSTALL_SCRIPT" --agent codex > /dev/null 2>&1
    local count
    count=$(find "$HOME/.codex/skills" -name "SKILL.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_SKILL_COUNT" "$count" "Expected exactly $EXPECTED_SKILL_COUNT skills for Codex"
}

# ============================================================================
# Tests — VS Code (project-local .github/)
# ============================================================================

test_install_vscode() {
    local project="$TEST_TMPDIR/vscode-project"
    mkdir -p "$project"
    (cd "$project" && bash "$INSTALL_SCRIPT" --agent vscode > /dev/null 2>&1)
    assert_all_skills_installed "$project/.github/skills"
}

test_vscode_skill_count() {
    local project="$TEST_TMPDIR/vscode-project"
    mkdir -p "$project"
    (cd "$project" && bash "$INSTALL_SCRIPT" --agent vscode > /dev/null 2>&1)
    local count
    count=$(find "$project/.github/skills" -name "SKILL.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_SKILL_COUNT" "$count" "Expected exactly $EXPECTED_SKILL_COUNT skills for VS Code"
}

# ============================================================================
# Tests — Antigravity (~/.gemini/antigravity/skills/)
# ============================================================================

test_install_antigravity() {
    bash "$INSTALL_SCRIPT" --agent antigravity > /dev/null 2>&1
    assert_all_skills_installed "$HOME/.gemini/antigravity/skills"
}

test_antigravity_skill_count() {
    bash "$INSTALL_SCRIPT" --agent antigravity > /dev/null 2>&1
    local count
    count=$(find "$HOME/.gemini/antigravity/skills" -name "SKILL.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_SKILL_COUNT" "$count" "Expected exactly $EXPECTED_SKILL_COUNT skills for Antigravity"
}

# ============================================================================
# Tests — Cursor
# ============================================================================

test_install_cursor() {
    bash "$INSTALL_SCRIPT" --agent cursor > /dev/null 2>&1
    assert_all_skills_installed "$HOME/.cursor/skills"
}

test_cursor_skill_count() {
    bash "$INSTALL_SCRIPT" --agent cursor > /dev/null 2>&1
    local count
    count=$(find "$HOME/.cursor/skills" -name "SKILL.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_SKILL_COUNT" "$count" "Expected exactly $EXPECTED_SKILL_COUNT skills for Cursor"
}

# ============================================================================
# Tests — Project-local
# ============================================================================

test_install_project_local() {
    local project="$TEST_TMPDIR/local-project"
    mkdir -p "$project"
    (cd "$project" && bash "$INSTALL_SCRIPT" --agent project-local > /dev/null 2>&1)
    assert_all_skills_installed "$project/skills"
}

test_project_local_skill_count() {
    local project="$TEST_TMPDIR/local-project"
    mkdir -p "$project"
    (cd "$project" && bash "$INSTALL_SCRIPT" --agent project-local > /dev/null 2>&1)
    local count
    count=$(find "$project/skills" -name "SKILL.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_SKILL_COUNT" "$count" "Expected exactly $EXPECTED_SKILL_COUNT skills for project-local"
}

# ============================================================================
# Tests — Custom path
# ============================================================================

test_custom_path() {
    local custom="$TEST_TMPDIR/custom-skills"
    bash "$INSTALL_SCRIPT" --agent custom --path "$custom" > /dev/null 2>&1
    assert_all_skills_installed "$custom"
}

test_custom_path_skill_count() {
    local custom="$TEST_TMPDIR/custom-skills"
    bash "$INSTALL_SCRIPT" --agent custom --path "$custom" > /dev/null 2>&1
    local count
    count=$(find "$custom" -name "SKILL.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_SKILL_COUNT" "$count" "Expected exactly $EXPECTED_SKILL_COUNT skills for custom path"
}

# ============================================================================
# Tests — All-global
# ============================================================================

test_all_global() {
    bash "$INSTALL_SCRIPT" --agent all-global > /dev/null 2>&1
    # Claude Code
    assert_all_skills_installed "$HOME/.claude/skills" || return 1
    # OpenCode
    assert_all_skills_installed "$HOME/.config/opencode/skills" || return 1
    # Gemini CLI
    assert_all_skills_installed "$HOME/.gemini/skills" || return 1
    # Codex
    assert_all_skills_installed "$HOME/.codex/skills" || return 1
    # Cursor
    assert_all_skills_installed "$HOME/.cursor/skills" || return 1
}

test_all_global_total_skill_count() {
    bash "$INSTALL_SCRIPT" --agent all-global > /dev/null 2>&1
    # 5 targets x expected skills
    local total=0
    for dir in \
        "$HOME/.claude/skills" \
        "$HOME/.config/opencode/skills" \
        "$HOME/.gemini/skills" \
        "$HOME/.codex/skills" \
        "$HOME/.cursor/skills"; do
        local count
        count=$(find "$dir" -name "SKILL.md" | wc -l | tr -d ' ')
        assert_eq "$EXPECTED_SKILL_COUNT" "$count" "Expected $EXPECTED_SKILL_COUNT skills in $dir" || return 1
        total=$((total + count))
    done
    assert_eq "$((EXPECTED_SKILL_COUNT * 5))" "$total" "Expected $((EXPECTED_SKILL_COUNT * 5)) total SKILL.md files across all targets"
}

test_all_global_opencode_commands() {
    bash "$INSTALL_SCRIPT" --agent all-global > /dev/null 2>&1
    local commands_dir="$HOME/.config/opencode/commands"
    assert_dir_exists "$commands_dir" || return 1
    local count
    count=$(find "$commands_dir" -name "cells-*.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_COMMAND_COUNT" "$count" "Expected $EXPECTED_COMMAND_COUNT OpenCode commands with all-global"
}

# ============================================================================
# Tests — Idempotency
# ============================================================================

test_idempotent_claude_code() {
    bash "$INSTALL_SCRIPT" --agent claude-code > /dev/null 2>&1
    bash "$INSTALL_SCRIPT" --agent claude-code > /dev/null 2>&1
    assert_all_skills_installed "$HOME/.claude/skills"
    local count
    count=$(find "$HOME/.claude/skills" -name "SKILL.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_SKILL_COUNT" "$count" "Expected exactly $EXPECTED_SKILL_COUNT skills after double install"
}

test_idempotent_opencode() {
    bash "$INSTALL_SCRIPT" --agent opencode > /dev/null 2>&1
    bash "$INSTALL_SCRIPT" --agent opencode > /dev/null 2>&1
    assert_all_skills_installed "$HOME/.config/opencode/skills" || return 1
    local skill_count
    skill_count=$(find "$HOME/.config/opencode/skills" -name "SKILL.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_SKILL_COUNT" "$skill_count" "Expected exactly $EXPECTED_SKILL_COUNT skills after double install" || return 1
    local cmd_count
    cmd_count=$(find "$HOME/.config/opencode/commands" -name "cells-*.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_COMMAND_COUNT" "$cmd_count" "Expected exactly $EXPECTED_COMMAND_COUNT commands after double install"
}

test_idempotent_all_global() {
    bash "$INSTALL_SCRIPT" --agent all-global > /dev/null 2>&1
    bash "$INSTALL_SCRIPT" --agent all-global > /dev/null 2>&1
    for dir in \
        "$HOME/.claude/skills" \
        "$HOME/.config/opencode/skills" \
        "$HOME/.gemini/skills" \
        "$HOME/.codex/skills" \
        "$HOME/.cursor/skills"; do
        local count
        count=$(find "$dir" -name "SKILL.md" | wc -l | tr -d ' ')
        assert_eq "$EXPECTED_SKILL_COUNT" "$count" "Expected $EXPECTED_SKILL_COUNT skills in $dir after double install" || return 1
    done
}

# ============================================================================
# Tests — Content integrity
# ============================================================================

test_skill_content_matches_source() {
    bash "$INSTALL_SCRIPT" --agent claude-code > /dev/null 2>&1
    local source_dir="$REPO_DIR/skills"
    for skill in "${EXPECTED_SKILLS[@]}"; do
        local src="$source_dir/$skill/SKILL.md"
        local dst="$HOME/.claude/skills/$skill/SKILL.md"
        if ! diff -q "$src" "$dst" > /dev/null 2>&1; then
            echo "Content mismatch: $skill/SKILL.md"
            echo "  Source: $src"
            echo "  Dest:   $dst"
            return 1
        fi
    done
    return 0
}

test_opencode_command_content_matches_source() {
    bash "$INSTALL_SCRIPT" --agent opencode > /dev/null 2>&1
    local source_dir="$REPO_DIR/examples/opencode/commands"
    local target_dir="$HOME/.config/opencode/commands"
    for cmd_file in "$source_dir"/cells-*.md; do
        local name
        name=$(basename "$cmd_file")
        if ! diff -q "$cmd_file" "$target_dir/$name" > /dev/null 2>&1; then
            echo "Content mismatch: commands/$name"
            return 1
        fi
    done
    return 0
}

# ============================================================================
# Tests — Output verification
# ============================================================================

test_output_shows_skill_names() {
    local output
    output=$(bash "$INSTALL_SCRIPT" --agent claude-code 2>&1)
    for skill in "${EXPECTED_SKILLS[@]}"; do
        echo "$output" | grep -q "$skill" || {
            echo "Output missing skill name: $skill"
            return 1
        }
    done
    return 0
}

test_output_shows_done_message() {
    local output
    output=$(bash "$INSTALL_SCRIPT" --agent claude-code 2>&1)
    echo "$output" | grep -q "Done!" || {
        echo "Output missing 'Done!' message"
        return 1
    }
}

test_output_shows_install_count() {
    local output
    output=$(bash "$INSTALL_SCRIPT" --agent claude-code 2>&1)
    echo "$output" | grep -q "$EXPECTED_SKILL_COUNT skills installed" || {
        echo "Output missing '$EXPECTED_SKILL_COUNT skills installed' message"
        return 1
    }
}

test_output_shows_next_step() {
    local output
    output=$(bash "$INSTALL_SCRIPT" --agent claude-code 2>&1)
    echo "$output" | grep -q "Next step" || {
        echo "Output missing 'Next step' guidance"
        return 1
    }
}

test_output_shows_engram_note() {
    local output
    output=$(bash "$INSTALL_SCRIPT" --agent claude-code 2>&1)
    echo "$output" | grep -q "Engram" || {
        echo "Output missing Engram recommendation"
        return 1
    }
}

# ============================================================================
# Tests — OS detection (limited — we can only test the current OS)
# ============================================================================

test_os_detection_runs() {
    local output
    output=$(bash "$INSTALL_SCRIPT" --help 2>&1 || true)
    [[ -n "$output" ]] || { echo "No output from --help"; return 1; }
}

test_header_shows_detected_os() {
    local output
    output=$(bash "$INSTALL_SCRIPT" --agent claude-code 2>&1)
    echo "$output" | grep -q "Detected:" || {
        echo "Output missing 'Detected:' OS label"
        return 1
    }
}

# ============================================================================
# Tests — Edge cases
# ============================================================================

test_pre_existing_dir_not_clobbered() {
    # Create a pre-existing file that should NOT be deleted
    mkdir -p "$HOME/.claude/skills/my-custom-skill"
    echo "custom content" > "$HOME/.claude/skills/my-custom-skill/SKILL.md"
    bash "$INSTALL_SCRIPT" --agent claude-code > /dev/null 2>&1
    # SDD skills should be installed
    assert_all_skills_installed "$HOME/.claude/skills" || return 1
    # Custom skill should still exist
    assert_file_exists "$HOME/.claude/skills/my-custom-skill/SKILL.md" || return 1
    local content
    content=$(cat "$HOME/.claude/skills/my-custom-skill/SKILL.md")
    assert_eq "custom content" "$content" "Custom skill content should be preserved"
}

test_overwrite_stale_skill() {
    # Pre-create a stale SKILL.md
    mkdir -p "$HOME/.claude/skills/cells-apply"
    echo "stale" > "$HOME/.claude/skills/cells-apply/SKILL.md"
    bash "$INSTALL_SCRIPT" --agent claude-code > /dev/null 2>&1
    # Should be replaced with actual content (not "stale")
    local content
    content=$(head -c 5 "$HOME/.claude/skills/cells-apply/SKILL.md")
    if [[ "$content" == "stale" ]]; then
        echo "SKILL.md was NOT overwritten — still contains stale data"
        return 1
    fi
    assert_file_not_empty "$HOME/.claude/skills/cells-apply/SKILL.md"
}

test_nested_custom_path() {
    local deep="$TEST_TMPDIR/a/b/c/d/skills"
    bash "$INSTALL_SCRIPT" --agent custom --path "$deep" > /dev/null 2>&1
    assert_all_skills_installed "$deep"
}

# ============================================================================
# Tests — VS Code Copilot assets
# ============================================================================

test_vscode_assets_exist_in_repo() {
    assert_file_exists "$REPO_DIR/.github/instructions/copilot-instructions.md" || return 1
    assert_file_exists "$REPO_DIR/.github/docs/README.md" || return 1
    assert_file_exists "$REPO_DIR/.github/docs/hooks.md" || return 1
    assert_file_exists "$REPO_DIR/.github/docs/models.md" || return 1
    assert_file_exists "$REPO_DIR/.github/prompts/README.md" || return 1
    assert_file_exists "$REPO_DIR/.github/prompts/cells-explore.md" || return 1
    assert_file_exists "$REPO_DIR/.github/prompts/cells-propose.md" || return 1
    assert_file_exists "$REPO_DIR/.github/prompts/cells-spec.md" || return 1
    assert_file_exists "$REPO_DIR/.github/prompts/cells-design.md" || return 1
    assert_file_exists "$REPO_DIR/.github/prompts/cells-tasks.md" || return 1
    assert_file_exists "$REPO_DIR/.github/prompts/cells-apply.md" || return 1
    assert_file_exists "$REPO_DIR/.github/prompts/cells-verify.md" || return 1
    assert_file_exists "$REPO_DIR/.github/prompts/cells-archive.md" || return 1
    assert_file_exists "$REPO_DIR/.github/prompts/cells-fallback.md" || return 1
    assert_file_exists "$REPO_DIR/.github/agents/analysis-agent.md" || return 1
    assert_file_exists "$REPO_DIR/.github/agents/implementation-agent.md" || return 1
    assert_file_exists "$REPO_DIR/.github/agents/verification-agent.md" || return 1
    assert_dir_exists "$REPO_DIR/.github/skills" || return 1
    assert_file_exists "$REPO_DIR/.github/skills/cells-governance-contract.md" || return 1
    assert_file_exists "$REPO_DIR/.github/skills/cells-policy-matrix.yaml" || return 1
    assert_file_exists "$REPO_DIR/scripts/validate_vscode_copilot_assets.py" || return 1
}

test_vscode_assets_contain_required_markers() {
    assert_file_contains "$REPO_DIR/.github/instructions/copilot-instructions.md" "Layered Precedence" || return 1
    assert_file_contains "$REPO_DIR/.github/instructions/copilot-instructions.md" "fallback is used, record source decision trace" || return 1
    assert_file_contains "$REPO_DIR/.github/prompts/cells-fallback.md" "WARNING: Dedicated prompt for this SDD phase is missing" || return 1
    assert_file_contains "$REPO_DIR/.github/docs/README.md" "Layered precedence" || return 1
}

test_vscode_catalog_first_and_fallback_order_behavior() {
    python "$REPO_DIR/scripts/validate_governance_behavior.py" --scenario catalog-first-available > /dev/null 2>&1 || return 1
    python "$REPO_DIR/scripts/validate_governance_behavior.py" --scenario primary-catalog-unavailable > /dev/null 2>&1 || return 1
    python "$REPO_DIR/scripts/validate_governance_behavior.py" --scenario fallback-order-respected > /dev/null 2>&1 || return 1
}

test_vscode_blocked_partial_escalation_behavior() {
    python "$REPO_DIR/scripts/validate_governance_behavior.py" --scenario escalation-blocked-partial > /dev/null 2>&1 || return 1
}

test_vscode_coverage_policy_exemption_behavior() {
    python "$REPO_DIR/scripts/validate_governance_behavior.py" --scenario coverage-policy-exemption > /dev/null 2>&1 || return 1
}

test_vscode_baseline_applies_in_normal_session() {
    assert_file_contains "$REPO_DIR/.github/instructions/copilot-instructions.md" "You are the SDD orchestrator" || return 1
    assert_file_contains "$REPO_DIR/.github/instructions/copilot-instructions.md" "Delegate-only" || return 1
    assert_file_contains "$REPO_DIR/.github/instructions/copilot-instructions.md" "Response format for delegated phases MUST return" || return 1
}

test_vscode_baseline_blocks_unsafe_automation() {
    assert_file_contains "$REPO_DIR/.github/instructions/copilot-instructions.md" "Do not suggest or default to generic external commands" || return 1
    assert_file_contains "$REPO_DIR/.github/docs/hooks.md" "Never default to force push, hard reset" || return 1
}

test_vscode_known_sdd_phase_prompts_are_usable() {
    local phase
    for phase in explore propose spec design tasks apply verify archive; do
        assert_file_exists "$REPO_DIR/.github/prompts/cells-$phase.md" || return 1
        assert_file_contains "$REPO_DIR/.github/prompts/cells-$phase.md" "## Goal" || return 1
        assert_file_contains "$REPO_DIR/.github/prompts/cells-$phase.md" "## Output envelope" || return 1
    done
}

test_vscode_specialized_roles_available() {
    assert_file_contains "$REPO_DIR/.github/agents/analysis-agent.md" "## Responsibility" || return 1
    assert_file_contains "$REPO_DIR/.github/agents/implementation-agent.md" "## Responsibility" || return 1
    assert_file_contains "$REPO_DIR/.github/agents/verification-agent.md" "## Responsibility" || return 1
}

test_vscode_agent_output_envelope_deterministic() {
    local agent
    for agent in analysis-agent implementation-agent verification-agent; do
        assert_file_contains "$REPO_DIR/.github/agents/$agent.md" '^Return: `status`, `executive_summary`, `artifacts`, `next_recommended`, `risks`\.$' || return 1
    done
}

test_vscode_hooks_define_non_destructive_policy() {
    assert_file_contains "$REPO_DIR/.github/docs/hooks.md" "Prefer validation checks over destructive automation" || return 1
    assert_file_contains "$REPO_DIR/.github/docs/hooks.md" "Never default to force push, hard reset" || return 1
}

test_vscode_hooks_define_failure_behavior() {
    assert_file_contains "$REPO_DIR/.github/docs/hooks.md" 'status: warning | blocked' || return 1
    assert_file_contains "$REPO_DIR/.github/docs/hooks.md" "Do not continue to archive/closeout when critical checks fail" || return 1
}

test_vscode_model_policy_matches_task_profile() {
    assert_file_contains "$REPO_DIR/.github/docs/models.md" "Use smaller/faster models for low-risk" || return 1
    assert_file_contains "$REPO_DIR/.github/docs/models.md" "Use deeper-reasoning models for architecture" || return 1
}

test_vscode_model_fallback_is_explicit() {
    assert_file_contains "$REPO_DIR/.github/docs/models.md" "Keep fallback path explicit" || return 1
    assert_file_contains "$REPO_DIR/.github/docs/models.md" '^\- If fallback is used, note it in `risks` or `executive_summary` when relevant\.$' || return 1
}

test_vscode_docs_describe_layered_runtime_layout() {
    assert_file_contains "$REPO_DIR/.github/docs/README.md" "Apply layers in this exact order" || return 1
    assert_file_contains "$REPO_DIR/.github/docs/README.md" '../instructions/copilot-instructions.md' || return 1
    assert_file_contains "$REPO_DIR/.github/docs/README.md" '../prompts/cells-' || return 1
    assert_file_contains "$REPO_DIR/.github/docs/README.md" '../agents/' || return 1
}

test_vscode_docs_include_maintenance_guidance() {
    assert_file_contains "$REPO_DIR/.github/docs/README.md" "## Maintenance checklist" || return 1
    assert_file_contains "$REPO_DIR/.github/docs/README.md" "Keep prompts aligned with current Cells command canon" || return 1
    assert_file_contains "$REPO_DIR/.github/docs/README.md" "python scripts/validate_vscode_copilot_assets.py" || return 1
}

test_vscode_assets_validator_passes() {
    if command -v python3 > /dev/null 2>&1; then
        if python3 "$REPO_DIR/scripts/validate_vscode_copilot_assets.py" > /dev/null 2>&1; then
            return 0
        fi
    fi

    if command -v python > /dev/null 2>&1; then
        python "$REPO_DIR/scripts/validate_vscode_copilot_assets.py" > /dev/null 2>&1
    else
        echo "  Python interpreter not available for validator"
        return 1
    fi
}

# ============================================================================
# Run all tests
# ============================================================================

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║    Agent Teams Lite — Install Tests      ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BOLD}Help & Error Handling${NC}"
run_test "--help flag shows usage info" test_help_flag
run_test "--help exits with code 0" test_help_exits_zero
run_test "Invalid agent exits non-zero" test_invalid_agent
run_test "Unknown option exits non-zero" test_invalid_option
echo ""

echo -e "${BOLD}Claude Code${NC}"
run_test "Installs all 9 skills to ~/.claude/skills" test_install_claude_code
run_test "Exactly 9 SKILL.md files" test_claude_code_skill_count
echo ""

echo -e "${BOLD}OpenCode${NC}"
run_test "Installs all 9 skills to ~/.config/opencode/skills" test_install_opencode
run_test "Exactly 9 SKILL.md files" test_opencode_skill_count
run_test "Installs 8 command files" test_opencode_commands
echo ""

echo -e "${BOLD}Gemini CLI${NC}"
run_test "Installs all 9 skills to ~/.gemini/skills" test_install_gemini_cli
run_test "Exactly 9 SKILL.md files" test_gemini_cli_skill_count
echo ""

echo -e "${BOLD}Codex${NC}"
run_test "Installs all 9 skills to ~/.codex/skills" test_install_codex
run_test "Exactly 9 SKILL.md files" test_codex_skill_count
echo ""

echo -e "${BOLD}VS Code (project-local)${NC}"
run_test "Installs all 9 skills to .github/skills/" test_install_vscode
run_test "Exactly 9 SKILL.md files" test_vscode_skill_count
echo ""

echo -e "${BOLD}Antigravity${NC}"
run_test "Installs all 9 skills to ~/.gemini/antigravity/skills/" test_install_antigravity
run_test "Exactly 9 SKILL.md files" test_antigravity_skill_count
echo ""

echo -e "${BOLD}Cursor${NC}"
run_test "Installs all 9 skills to ~/.cursor/skills" test_install_cursor
run_test "Exactly 9 SKILL.md files" test_cursor_skill_count
echo ""

echo -e "${BOLD}Project-local${NC}"
run_test "Installs all 9 skills to ./skills/" test_install_project_local
run_test "Exactly 9 SKILL.md files" test_project_local_skill_count
echo ""

echo -e "${BOLD}Custom path${NC}"
run_test "Installs to arbitrary custom path" test_custom_path
run_test "Exactly 9 SKILL.md files" test_custom_path_skill_count
run_test "Handles deeply nested custom path" test_nested_custom_path
echo ""

echo -e "${BOLD}All-global${NC}"
run_test "Installs to all 5 global targets" test_all_global
run_test "45 total SKILL.md files (5×9)" test_all_global_total_skill_count
run_test "Also installs OpenCode commands" test_all_global_opencode_commands
echo ""

echo -e "${BOLD}Idempotency${NC}"
run_test "Claude Code: double install is safe" test_idempotent_claude_code
run_test "OpenCode: double install is safe" test_idempotent_opencode
run_test "All-global: double install is safe" test_idempotent_all_global
echo ""

echo -e "${BOLD}Content integrity${NC}"
run_test "Skills match source files exactly" test_skill_content_matches_source
run_test "Commands match source files exactly" test_opencode_command_content_matches_source
echo ""

echo -e "${BOLD}Output verification${NC}"
run_test "Output lists all skill names" test_output_shows_skill_names
run_test "Output shows Done! message" test_output_shows_done_message
run_test "Output shows install count" test_output_shows_install_count
run_test "Output shows next-step guidance" test_output_shows_next_step
run_test "Output recommends Engram" test_output_shows_engram_note
echo ""

echo -e "${BOLD}OS detection${NC}"
run_test "--help runs without error" test_os_detection_runs
run_test "Header shows detected OS" test_header_shows_detected_os
echo ""

echo -e "${BOLD}Edge cases${NC}"
run_test "Pre-existing custom skill not clobbered" test_pre_existing_dir_not_clobbered
run_test "Stale SKILL.md is overwritten" test_overwrite_stale_skill
echo ""

echo -e "${BOLD}VS Code Copilot assets${NC}"
run_test "VS Code asset files exist" test_vscode_assets_exist_in_repo
run_test "VS Code assets include required markers" test_vscode_assets_contain_required_markers
run_test "Scenario: Catalog-first and fallback order behavior is executable" test_vscode_catalog_first_and_fallback_order_behavior
run_test "Scenario: Blocked/partial escalation behavior is executable" test_vscode_blocked_partial_escalation_behavior
run_test "Scenario: Coverage exemption policy behavior is executable" test_vscode_coverage_policy_exemption_behavior
run_test "Scenario: Baseline applies in normal coding session" test_vscode_baseline_applies_in_normal_session
run_test "Scenario: Baseline blocks unsafe automation" test_vscode_baseline_blocks_unsafe_automation
run_test "Scenario: User invokes a known SDD phase" test_vscode_known_sdd_phase_prompts_are_usable
run_test "Scenario: Specialized analysis/implementation/verification roles are available" test_vscode_specialized_roles_available
run_test "Scenario: Agent output envelope stays deterministic" test_vscode_agent_output_envelope_deterministic
run_test "Scenario: Hooks enforce non-destructive policy" test_vscode_hooks_define_non_destructive_policy
run_test "Scenario: Hook failures produce actionable blocked/warning behavior" test_vscode_hooks_define_failure_behavior
run_test "Scenario: Model policy applies to task profile" test_vscode_model_policy_matches_task_profile
run_test "Scenario: Model fallback remains explicit and safe" test_vscode_model_fallback_is_explicit
run_test "Scenario: Layered runtime documentation is explicit" test_vscode_docs_describe_layered_runtime_layout
run_test "Scenario: Maintenance guidance is explicit" test_vscode_docs_include_maintenance_guidance
run_test "VS Code assets validator passes" test_vscode_assets_validator_passes
echo ""

# ============================================================================
# Summary
# ============================================================================

echo -e "${BOLD}════════════════════════════════════════════${NC}"
echo -e "${BOLD}Results: $TESTS_PASSED/$TESTS_RUN passed${NC}"
if [[ $TESTS_FAILED -gt 0 ]]; then
    echo -e "${RED}${BOLD}$TESTS_FAILED test(s) failed:${NC}${FAILURES}"
    exit 1
fi
echo -e "${GREEN}${BOLD}All tests passed!${NC}"
echo ""

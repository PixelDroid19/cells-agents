#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Cells Agent Bundle — Install Script Tests
# Run: bash scripts/install_test.sh
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
INSTALL_SCRIPT="$SCRIPT_DIR/install.sh"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
FAILURES=""

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

EXPECTED_SKILLS=()
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

for skill_dir in "$REPO_DIR"/skills/*; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    [[ "$skill_name" == "_shared" ]] && continue
    [[ -f "$skill_dir/SKILL.md" ]] || continue
    EXPECTED_SKILLS+=("$skill_name")
done
EXPECTED_SKILL_COUNT="${#EXPECTED_SKILLS[@]}"
EXPECTED_COMMAND_COUNT="${#CORE_WORKFLOW_COMMANDS[@]}"

setup() {
    TEST_TMPDIR="$(mktemp -d)"
    export HOME="$TEST_TMPDIR/home"
    export USERPROFILE="$TEST_TMPDIR/home"
    export APPDATA="$TEST_TMPDIR/appdata"
    mkdir -p "$HOME" "$APPDATA"
}

teardown() {
    rm -rf "$TEST_TMPDIR"
}

assert_eq() {
    local expected="$1"
    local actual="$2"
    local msg="${3:-}"
    [[ "$expected" == "$actual" ]] && return 0
    echo "  Expected: $expected"
    echo "  Actual:   $actual"
    [[ -n "$msg" ]] && echo "  Message:  $msg"
    return 1
}

assert_file_exists() { [[ -f "$1" ]]; }
assert_dir_exists() { [[ -d "$1" ]]; }

assert_all_skills_installed() {
    local base_dir="$1"
    for skill in "${EXPECTED_SKILLS[@]}"; do
        assert_dir_exists "$base_dir/$skill" || { echo "  Missing dir: $base_dir/$skill"; return 1; }
        assert_file_exists "$base_dir/$skill/SKILL.md" || { echo "  Missing file: $base_dir/$skill/SKILL.md"; return 1; }
    done
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
        [[ -n "$output" ]] && echo "$output" | sed 's/^/    /'
        TESTS_FAILED=$((TESTS_FAILED + 1))
        FAILURES="$FAILURES\n  - $name"
    fi
    teardown
}

# Help and errors

test_help_flag() {
    local output
    output=$(bash "$INSTALL_SCRIPT" --help 2>&1)
    echo "$output" | grep -q "Usage:" || return 1
    echo "$output" | grep -q "opencode" || return 1
    echo "$output" | grep -q "vscode" || return 1
    echo "$output" | grep -q "project-local" || return 1
    echo "$output" | grep -q "all-global" || return 1
}

test_invalid_agent() {
    if bash "$INSTALL_SCRIPT" --agent unsupported-agent > /dev/null 2>&1; then
        echo "Expected non-zero exit for unsupported agent"
        return 1
    fi
}

# OpenCode

test_install_opencode() {
    bash "$INSTALL_SCRIPT" --agent opencode > /dev/null 2>&1
    assert_all_skills_installed "$HOME/.config/opencode/skills"
}

test_opencode_commands() {
    bash "$INSTALL_SCRIPT" --agent opencode > /dev/null 2>&1
    local commands_dir="$HOME/.config/opencode/commands"
    assert_dir_exists "$commands_dir" || return 1
    local count
    count=$(find "$commands_dir" -name "cells-*.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_COMMAND_COUNT" "$count"
}

# VS Code

test_install_vscode() {
    local project="$TEST_TMPDIR/vscode-project"
    mkdir -p "$project"
    (cd "$project" && bash "$INSTALL_SCRIPT" --agent vscode > /dev/null 2>&1)
    assert_all_skills_installed "$project/.github/skills"
}

# Project-local

test_install_project_local() {
    local project="$TEST_TMPDIR/local-project"
    mkdir -p "$project"
    (cd "$project" && bash "$INSTALL_SCRIPT" --agent project-local > /dev/null 2>&1)
    assert_all_skills_installed "$project/skills"
}

# Custom

test_custom_path() {
    local custom="$TEST_TMPDIR/custom-skills"
    bash "$INSTALL_SCRIPT" --agent custom --path "$custom" > /dev/null 2>&1
    assert_all_skills_installed "$custom"
}

# All-global (OpenCode only)

test_all_global() {
    bash "$INSTALL_SCRIPT" --agent all-global > /dev/null 2>&1
    assert_all_skills_installed "$HOME/.config/opencode/skills" || return 1
    local cmd_count
    cmd_count=$(find "$HOME/.config/opencode/commands" -name "cells-*.md" | wc -l | tr -d ' ')
    assert_eq "$EXPECTED_COMMAND_COUNT" "$cmd_count"
}

# Idempotency

test_idempotent_opencode() {
    bash "$INSTALL_SCRIPT" --agent opencode > /dev/null 2>&1
    bash "$INSTALL_SCRIPT" --agent opencode > /dev/null 2>&1
    assert_all_skills_installed "$HOME/.config/opencode/skills"
}

test_idempotent_vscode() {
    local project="$TEST_TMPDIR/vscode-project"
    mkdir -p "$project"
    (cd "$project" && bash "$INSTALL_SCRIPT" --agent vscode > /dev/null 2>&1)
    (cd "$project" && bash "$INSTALL_SCRIPT" --agent vscode > /dev/null 2>&1)
    assert_all_skills_installed "$project/.github/skills"
}

# Output checks

test_output_shows_done_message() {
    local output
    output=$(bash "$INSTALL_SCRIPT" --agent opencode 2>&1)
    echo "$output" | grep -q "Done!"
}

test_output_shows_detected_os() {
    local output
    output=$(bash "$INSTALL_SCRIPT" --agent opencode 2>&1)
    echo "$output" | grep -q "Detected:"
}

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║    Cells Agent Bundle — Install Tests    ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

run_test "--help muestra uso" test_help_flag
run_test "Agente no soportado falla" test_invalid_agent
run_test "Instala OpenCode" test_install_opencode
run_test "Instala comandos de OpenCode" test_opencode_commands
run_test "Instala VS Code" test_install_vscode
run_test "Instala project-local" test_install_project_local
run_test "Instala custom path" test_custom_path
run_test "Instala all-global" test_all_global
run_test "OpenCode idempotente" test_idempotent_opencode
run_test "VS Code idempotente" test_idempotent_vscode
run_test "Salida incluye Done" test_output_shows_done_message
run_test "Salida incluye OS detectado" test_output_shows_detected_os

echo -e "${BOLD}════════════════════════════════════════════${NC}"
echo -e "${BOLD}Results: $TESTS_PASSED/$TESTS_RUN passed${NC}"
if [[ $TESTS_FAILED -gt 0 ]]; then
    echo -e "${RED}${BOLD}$TESTS_FAILED test(s) failed:${NC}${FAILURES}"
    exit 1
fi
echo -e "${GREEN}${BOLD}All tests passed!${NC}"
echo ""

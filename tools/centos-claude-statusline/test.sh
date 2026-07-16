#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
STATUSLINE="$ROOT_DIR/statusline-command.sh"
INSTALLER="$ROOT_DIR/install.sh"

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local haystack=$1
  local needle=$2
  printf '%s' "$haystack" | grep -Fq "$needle" || fail "missing output: $needle"
}

[ -x "$STATUSLINE" ] || fail "statusline-command.sh is missing or not executable"
[ -x "$INSTALLER" ] || fail "install.sh is missing or not executable"
command -v jq >/dev/null 2>&1 || fail "jq is required to run the tests"

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

export HOME="$tmp_dir/home"
mkdir -p "$HOME/.claude/skills/alpha" "$HOME/.claude/skills/beta" "$tmp_dir/project"
touch "$HOME/.claude/skills/alpha/SKILL.md" "$HOME/.claude/skills/beta/SKILL.md"

git_in_project() {
  (cd "$tmp_dir/project" && git "$@")
}

git_in_project init -q
git_in_project config user.name test
git_in_project config user.email test@example.invalid
printf 'base\n' > "$tmp_dir/project/tracked.txt"
git_in_project add tracked.txt
git_in_project commit -qm init
printf 'change\n' >> "$tmp_dir/project/tracked.txt"
printf 'new\n' > "$tmp_dir/project/untracked.txt"
branch=$(git_in_project symbolic-ref --short HEAD)

payload=$(jq -nc \
  --arg cwd "$tmp_dir/project" \
  '{
    session_id: "test-session",
    workspace: {current_dir: $cwd},
    model: {display_name: "Claude Test"},
    context_window: {
      used_percentage: 15,
      total_input_tokens: 20000,
      total_output_tokens: 10000,
      context_window_size: 200000
    }
  }')

output=$(printf '%s' "$payload" | "$STATUSLINE")
plain_output=$(printf '%s' "$output" | sed $'s/\033\[[0-9;]*m//g')

[ "$(printf '%s\n' "$plain_output" | wc -l | tr -d ' ')" = 4 ] || fail "status line must contain exactly four lines"
assert_contains "$plain_output" "模型: Claude Test"
assert_contains "$plain_output" "Git: +1 -0 ?1"
assert_contains "$plain_output" "分支: $branch"
assert_contains "$plain_output" "技能: 2"
assert_contains "$plain_output" "cwd: $tmp_dir/project"
assert_contains "$plain_output" "30k/200k (15%)"
assert_contains "$plain_output" "[██░░░░░░░░░░░░░░]"

printf '{"theme":"dark"}\n' > "$HOME/.claude/settings.json"
"$INSTALLER" >/dev/null

[ -x "$HOME/.claude/statusline-command.sh" ] || fail "installer did not install the status line"
jq -e '.theme == "dark"' "$HOME/.claude/settings.json" >/dev/null || fail "installer did not preserve existing settings"
jq -e '.statusLine == {"type":"command","command":"bash ~/.claude/statusline-command.sh"}' \
  "$HOME/.claude/settings.json" >/dev/null || fail "installer did not configure Claude Code"

"$INSTALLER" >/dev/null
find "$HOME/.claude/backups" -mindepth 1 -maxdepth 1 -type d | grep -q . || fail "reinstall did not create a backup"

printf 'PASS: status line output and installer behavior\n'

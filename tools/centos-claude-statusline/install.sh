#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SOURCE_SCRIPT="$ROOT_DIR/statusline-command.sh"
CLAUDE_DIR="$HOME/.claude"
TARGET_SCRIPT="$CLAUDE_DIR/statusline-command.sh"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"

if ! command -v jq >/dev/null 2>&1; then
  printf 'Error: jq is required. On CentOS 7, enable EPEL and install jq.\n' >&2
  exit 1
fi

[ -f "$SOURCE_SCRIPT" ] || {
  printf 'Error: %s is missing.\n' "$SOURCE_SCRIPT" >&2
  exit 1
}

umask 077
mkdir -p "$CLAUDE_DIR"

if [ -e "$TARGET_SCRIPT" ] || [ -e "$SETTINGS_FILE" ]; then
  backup_root="$CLAUDE_DIR/backups"
  backup_dir="$backup_root/statusline-$(date -u +%Y%m%dT%H%M%SZ)"
  suffix=0
  while [ -e "$backup_dir" ]; do
    suffix=$((suffix + 1))
    backup_dir="$backup_root/statusline-$(date -u +%Y%m%dT%H%M%SZ)-$suffix"
  done
  mkdir -p "$backup_dir"
  [ ! -e "$TARGET_SCRIPT" ] || cp -p "$TARGET_SCRIPT" "$backup_dir/"
  [ ! -e "$SETTINGS_FILE" ] || cp -p "$SETTINGS_FILE" "$backup_dir/"
  printf 'Backup: %s\n' "$backup_dir"
fi

install -m 0700 "$SOURCE_SCRIPT" "$TARGET_SCRIPT"

if [ ! -e "$SETTINGS_FILE" ]; then
  printf '{}\n' > "$SETTINGS_FILE"
fi
if ! jq -e 'type == "object"' "$SETTINGS_FILE" >/dev/null 2>&1; then
  printf 'Error: %s must contain a JSON object. The file was not changed.\n' "$SETTINGS_FILE" >&2
  exit 1
fi

settings_tmp=$(mktemp "$CLAUDE_DIR/.settings.json.XXXXXX")
trap 'rm -f "$settings_tmp"' EXIT
jq '.statusLine = {"type":"command","command":"bash ~/.claude/statusline-command.sh"}' \
  "$SETTINGS_FILE" > "$settings_tmp"
chmod 0600 "$settings_tmp"
mv "$settings_tmp" "$SETTINGS_FILE"
trap - EXIT

printf 'Installed: %s\n' "$TARGET_SCRIPT"
printf 'Configured: %s\n' "$SETTINGS_FILE"

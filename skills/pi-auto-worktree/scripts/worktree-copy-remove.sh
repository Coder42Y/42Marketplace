#!/usr/bin/env bash
# WorktreeRemove hook（可选）：删除快照复制出来的工作区。只删带 .auto-worktree-origin 标记的目录，防误删。
set -euo pipefail
p=$(cat | jq -r '.worktree_path // empty')
[ -n "$p" ] && [ -f "$p/.auto-worktree-origin" ] && rm -rf "$p"
exit 0

#!/usr/bin/env bash
# 移除 auto-worktree 注册的全部 hook（SessionStart / WorktreeCreate / WorktreeRemove）；不动 gitignore、不删 skill 目录
set -euo pipefail
SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"
jq '
  def drop(ev): if .hooks[ev] then .hooks[ev] |= map(select((.hooks // []) | any(.command | test("auto-worktree")) | not))
                   | (if .hooks[ev] == [] then del(.hooks[ev]) else . end) else . end;
  drop("SessionStart") | drop("WorktreeCreate") | drop("WorktreeRemove")
  | if .hooks == {} then del(.hooks) else . end
' "$SETTINGS" > "$SETTINGS.tmp" && mv "$SETTINGS.tmp" "$SETTINGS"
echo "✔ auto-worktree 的 hook 已全部移除；skill 目录保留，需要时手动删除"

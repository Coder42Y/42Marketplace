#!/usr/bin/env bash
# WorktreeCreate hook（可选）：非 git 目录的 VCS-agnostic 隔离——把 cwd 快照复制到 ~/.claude/worktrees/<name>
# 契约：stdin JSON {name, cwd}；stdout 最后一行 = 新工作区绝对路径；其余输出走 stderr。
set -euo pipefail
input=$(cat)
name=$(printf '%s' "$input" | jq -r '.name')
cwd=$(printf '%s' "$input" | jq -r '.cwd // empty'); [ -z "$cwd" ] && cwd=$PWD
limit_mb="${CLAUDE_COPY_WORKTREE_LIMIT_MB:-500}"

# 体积保护：排除常见依赖/构建目录后仍超过阈值则拒绝
size_mb=$(du -sm --exclude=node_modules --exclude=.venv --exclude=target --exclude=dist --exclude=build --exclude=.claude "$cwd" | cut -f1)
if [ "$size_mb" -gt "$limit_mb" ]; then
  echo "auto-worktree: $cwd 约 ${size_mb}MB，超过 ${limit_mb}MB 阈值，拒绝快照复制（可设 CLAUDE_COPY_WORKTREE_LIMIT_MB 调整）" >&2
  exit 1
fi

dest="$HOME/.claude/worktrees/$(basename "$cwd")/$name"
mkdir -p "$dest"
rsync -a --exclude node_modules --exclude .venv --exclude target --exclude dist --exclude build --exclude .claude/worktrees "$cwd/" "$dest/" >&2
printf '%s\n' "$cwd" > "$dest/.auto-worktree-origin"
echo "$dest"

#!/usr/bin/env bash
# 一键安装 auto-worktree：注册 SessionStart hook + 全局 gitignore。幂等，可重复执行。
# 用法：bash <skill目录>/scripts/install.sh [--base-ref head|fresh] [--with-copy-hooks]
#   hook 命令以本脚本所在目录的绝对路径写入 settings，plugin / 软链 / 直拷三种安装方式都适用
#   --with-copy-hooks  额外注册 WorktreeCreate/WorktreeRemove，让纯非 git 目录也能用「快照复制」隔离（默认不开）
set -euo pipefail
SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
HOOK_CMD="bash $HERE/session-start-worktree.sh"
BASE_REF=""; COPY_HOOKS=0
while [ $# -gt 0 ]; do
  case "$1" in
    --base-ref) BASE_REF="$2"; shift 2;;
    --with-copy-hooks) COPY_HOOKS=1; shift;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done
command -v jq >/dev/null || { echo "需要 jq：sudo apt install jq" >&2; exit 1; }
[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
cp "$SETTINGS" "$SETTINGS.bak-auto-worktree"

jq --arg cmd "$HOOK_CMD" --arg ref "$BASE_REF" '
  .hooks.SessionStart = ((.hooks.SessionStart // []) | map(select((.hooks // []) | any(.command | test("session-start-worktree\\.sh")) | not)))
    + [{"matcher":"startup","hooks":[{"type":"command","command":$cmd}]}]
  | if $ref != "" then .worktree.baseRef = $ref else . end
' "$SETTINGS" > "$SETTINGS.tmp" && mv "$SETTINGS.tmp" "$SETTINGS"

if [ "$COPY_HOOKS" = 1 ]; then
  jq --arg c "bash $HERE/worktree-copy-create.sh" --arg r "bash $HERE/worktree-copy-remove.sh" \
    '.hooks.WorktreeCreate = [{"hooks":[{"type":"command","command":$c}]}]
     | .hooks.WorktreeRemove = [{"hooks":[{"type":"command","command":$r}]}]' \
    "$SETTINGS" > "$SETTINGS.tmp" && mv "$SETTINGS.tmp" "$SETTINGS"
  echo "✔ 已注册 WorktreeCreate/WorktreeRemove 快照复制 hook（非 git 目录可用）"
fi

IGN="${XDG_CONFIG_HOME:-$HOME/.config}/git/ignore"
custom=$(git config --global core.excludesFile 2>/dev/null || true)
[ -n "$custom" ] && IGN="${custom/#\~/$HOME}"
mkdir -p "$(dirname "$IGN")"; touch "$IGN"
grep -qx '.claude/worktrees/' "$IGN" || echo '.claude/worktrees/' >> "$IGN"

chmod +x "$HERE"/*.sh
echo "✔ SessionStart hook 已注册到 $SETTINGS（备份 $SETTINGS.bak-auto-worktree）"
echo "✔ 全局 gitignore 已包含 .claude/worktrees/（$IGN）"
[ -n "$BASE_REF" ] && echo "✔ worktree.baseRef = $BASE_REF"
echo "关闭：CLAUDE_AUTO_WORKTREE=0 claude 或 touch .claude/no-auto-worktree；卸载：scripts/uninstall.sh"

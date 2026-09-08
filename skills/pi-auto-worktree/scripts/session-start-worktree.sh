#!/usr/bin/env bash
# SessionStart hook（matcher: startup）
# 目的：复刻 Claude GUI 的行为——每次新会话在 git 仓库内启动时，自动进入独立 worktree。
# 机制：本脚本只做检测 + 注入 additionalContext；真正的创建由 Claude 调用 EnterWorktree 完成，
#       这样 worktree 由 harness 托管（退出时会提示 keep/remove），不会产生 harness 看不见的幽灵目录。
#
# 关闭方式：
#   - 环境变量  CLAUDE_AUTO_WORKTREE=0 claude
#   - 项目级    touch .claude/no-auto-worktree
set -u

[ "${CLAUDE_AUTO_WORKTREE:-1}" = "0" ] && exit 0

input=$(cat 2>/dev/null || true)
cwd=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null || true)
[ -z "$cwd" ] && cwd=$PWD
cd "$cwd" 2>/dev/null || exit 0

# 非 git 目录：若下面一层有 git 仓库，视为「多仓库工作区」，注入 nested-repo 指令；否则静默跳过
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  [ -f .claude/no-auto-worktree ] && exit 0
  repos=$(for d in */; do [ -e "$d.git" ] && printf '%s ' "${d%/}"; done)
  if [ -z "$repos" ]; then
    # 纯非 git 目录：仅当用户装了 WorktreeCreate hook（快照复制模式）时才提示进 worktree
    settings="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"
    jq -e '.hooks.WorktreeCreate | length > 0' "$settings" >/dev/null 2>&1 || exit 0
    suggested="s-$(date +%Y%m%d-%H%M)"
    ctx="[auto-worktree] 当前目录 \`$cwd\` 不是 git 仓库，但已配置 WorktreeCreate hook（快照复制隔离）。
在处理用户第一条消息之前，若消息涉及改文件，先调用 EnterWorktree（name 用任务的 kebab-case 概括，否则 \`$suggested\`）；纯问答或用户明确说不要 worktree 则不建。
进入后一行告知路径，并提醒用户：这是目录快照，改动不会自动同步回原目录，结束时需手动 diff/复制回去。"
    jq -n --arg ctx "$ctx" '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$ctx}}'
    exit 0
  fi
  suggested="s-$(date +%Y%m%d-%H%M)"
  ctx="[auto-worktree] 当前目录 \`$cwd\` 不是 git 仓库，但它是一个多仓库工作区，包含子仓库：$repos
规则：
- 用户第一条消息若指向其中某个子仓库 <repo>，在动手改代码之前先在该子仓库里建 worktree 并进入（EnterWorktree 的 name 模式在这里不可用，必须走 path 模式）：
    git -C <repo> worktree add .claude/worktrees/<name> -b <name>
    然后调用 EnterWorktree，参数 path=<cwd>/<repo>/.claude/worktrees/<name>
  <name> 用任务的 kebab-case 概括，概括不出来用 \`$suggested\`。
- 用户的消息不涉及任何子仓库的代码改动（纯问答、只读、或跨仓库操作）→ 不建 worktree，正常回答。
- 用户明确说不要 worktree → 不建，不追问。
- 进入后一行告知路径与分支；这种 path 模式进入的 worktree 退出会话时不会自动清理，任务结束时提醒用户可用 \`git -C <repo> worktree remove\` 清理。
细则见 skill: pi-auto-worktree。"
  jq -n --arg ctx "$ctx" '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$ctx}}'
  exit 0
fi

# 项目级 opt-out
[ -f .claude/no-auto-worktree ] && exit 0

# 已经在 linked worktree 里（且不是 submodule）：跳过
git_dir=$(cd "$(git rev-parse --git-dir)" && pwd -P)
common_dir=$(cd "$(git rev-parse --git-common-dir)" && pwd -P)
if [ "$git_dir" != "$common_dir" ] && [ -z "$(git rev-parse --show-superproject-working-tree 2>/dev/null)" ]; then
  exit 0
fi

branch=$(git branch --show-current 2>/dev/null || echo detached)
suggested="s-$(date +%Y%m%d-%H%M)"

ctx="[auto-worktree] 本会话在 git 仓库 \`$cwd\`（分支 $branch）的主工作区启动，尚未进入 worktree。
在处理用户第一条消息之前，先做且只做一件事：调用 EnterWorktree 工具进入新 worktree。
- name 规则：用用户第一条消息的任务概括成 kebab-case 短名（如 fix-login-timeout）；概括不出来就用 \`$suggested\`。
- 例外：用户第一条消息明确说不要 worktree / 在当前目录做 → 不创建，并且不要再问。
- 进入后用一行告知用户 worktree 路径与分支，然后继续正常处理用户的消息。
- 会话中途不要主动调用 ExitWorktree；退出会话时 harness 会询问 keep/remove。
细则见 skill: pi-auto-worktree。"

jq -n --arg ctx "$ctx" '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$ctx}}'

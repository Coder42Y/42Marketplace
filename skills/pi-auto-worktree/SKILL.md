---
name: pi-auto-worktree
description: 让 Claude Code TUI 像 GUI 一样每个新会话自动进入独立 worktree。当会话上下文出现 `[auto-worktree]`、用户说「自动 worktree」「每次开会话自动建 worktree」「安装/关闭 auto worktree」「进入/退出 worktree」「为什么没建 worktree」时触发；覆盖 git 仓库、多仓库工作区、纯非 git 目录三种启动位置。不用于普通的切分支、建分支需求。
version: 1.0.0
metadata:
  requires:
    bins: ["jq", "git", "rsync"]
  platform: claude-code
---

# Auto Worktree（TUI 复刻 GUI 的自动 worktree）

## Overview

Claude GUI 每开一个会话就自动建一个 worktree。TUI 里 skill 无法自行在启动时触发，
所以本 skill = **SessionStart hook（检测 + 注入指令）+ 原生 EnterWorktree（真正创建）+ 本文（规则）**。

**核心原则：worktree 要由 harness 托管。** 能用 `EnterWorktree` 的场景绝不手工 `git worktree add`；
手工建的目录 harness 看不见，会话 cwd 不会切换，退出时也不会提示清理。

## 安装 / 卸载（用户说「安装 auto worktree」时执行）

`<skill目录>` 指本 SKILL.md 所在目录（plugin 安装、软链、直拷均可）：

```bash
bash <skill目录>/scripts/install.sh                     # 基础：SessionStart hook + 全局 gitignore
bash <skill目录>/scripts/install.sh --base-ref head     # 本地无 origin 的仓库建议加
bash <skill目录>/scripts/install.sh --with-copy-hooks   # 可选：纯非 git 目录也隔离（快照复制）
bash <skill目录>/scripts/uninstall.sh
```

依赖 `jq`（快照模式另需 `rsync`）。脚本幂等，重复执行不会产生重复 hook。仅 Claude Code 可用：依赖 SessionStart hook 与 `EnterWorktree` 工具，Codex 无对应机制。

## 启动目录的三种情况

| 启动目录 | hook 行为 | 你要做的 |
|----------|-----------|----------|
| **git 仓库主工作区** | 注入 `[auto-worktree]` | 处理第一条消息前调用 `EnterWorktree(name=<任务kebab-case>)` |
| **多仓库工作区**（本身非 git，下一层有 `.git`） | 注入子仓库列表 | 消息指向某子仓库且要改代码时：`git -C <repo> worktree add .claude/worktrees/<name> -b <name>`，再 `EnterWorktree(path=<repo>/.claude/worktrees/<name>)`。path 模式 harness 会要用户确认一次，属正常 |
| **纯非 git 目录** | 默认静默；装了 `--with-copy-hooks` 才注入 | 涉及改文件时 `EnterWorktree(name=...)`，harness 通过 WorktreeCreate hook 把目录快照到 `~/.claude/worktrees/<dir>/<name>`；必须提醒用户改动不会自动同步回原目录 |

进入后一律用一行告知路径与分支，然后继续处理用户的原始消息。不要因为建了 worktree 就跑依赖安装或测试。

## 跳过条件（hook 已处理，这里是为了让你不要「补建」）

| 情况 | 行为 |
|------|------|
| 已在 linked worktree（`git rev-parse --git-dir` ≠ `--git-common-dir`，且非 submodule） | 不建 |
| 项目存在 `.claude/no-auto-worktree` | 不建 |
| 启动时 `CLAUDE_AUTO_WORKTREE=0` | 不建 |
| 第一条消息是纯问答 / 只读 / 明确说「不要 worktree、就在这里改」 | 不建，不追问 |
| `--continue` / `--resume` 恢复的会话 | matcher 是 `startup`，不触发 |
| 快照模式下目录超过 `CLAUDE_COPY_WORKTREE_LIMIT_MB`（默认 500） | WorktreeCreate 拒绝，告知用户后在原目录工作 |

## 退出

- 用户说「退出 worktree / 回主目录」→ `ExitWorktree`；有未提交改动用 `keep`，除非用户明确说丢弃。
- name 模式创建的 worktree：退出会话时 harness 询问 keep/remove，不要自己提前 remove。
- path 模式（多仓库工作区）进入的 worktree：harness 不会清理，任务结束时提醒用户 `git -C <repo> worktree remove <path>`。
- 快照模式：WorktreeRemove hook 只删带 `.auto-worktree-origin` 标记的目录；改动需用户手动 diff/复制回原目录。

## 配置项

- `worktree.baseRef`：`fresh`（默认，从 `origin/<默认分支>` 切）或 `head`（从本地 HEAD 切）。
- 原生 worktree 落盘在 `<repo>/.claude/worktrees/<name>`；快照模式落盘在 `~/.claude/worktrees/<目录名>/<name>`。
- 也可以不用 hook，直接 `claude --worktree [name]` 启动，但非 git 目录会报错退出。
- hook 契约（WorktreeCreate 的 stdin / stdout 约定等）见 `references/hook-contract.md`。

## Common Mistakes

| 错误 | 纠正 |
|------|------|
| 先回答用户的问题，最后才想起进 worktree | 顺序错了：先进 worktree 再动手，否则改动留在主工作区 |
| 在 git 仓库里用 `git worktree add` + `cd` | 会话 cwd 不会真的切换。只有多仓库工作区的 path 模式才需要先 `git worktree add` |
| 多仓库工作区里对 `EnterWorktree` 传 `name` | cwd 不是 git 仓库，name 模式会失败；必须用 path |
| 快照模式下不提醒「改动不回流」 | 用户会以为原目录已改。每次进入都要提醒 |
| 用户说「别建 worktree」后又问一遍 | 直接在当前目录工作 |
| 任务结束时主动 `ExitWorktree remove` | 不要。退出会话时 harness 会问用户 |

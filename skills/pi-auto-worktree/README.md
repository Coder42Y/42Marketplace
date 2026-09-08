【pi-auto-worktree】

本包是 auto-worktree 的 Claude Code（CC）版，仅发布名为 `pi-auto-worktree`，不是 pi 启动器版。保留上游的环境变量、关闭标记与 hook 行为。

> 让 Claude Code TUI 像 GUI 一样，每个新会话自动进入独立 worktree 再开始改代码；给所有在终端里用 Claude Code 的同事。

**版本:** `v1.0.0` ｜ **状态:** `stable` ｜ **兼容:** Claude Code（Codex 不适用）

---

## 它解决什么

Claude GUI 每开一个会话都会自动建 worktree，主工作区永远干净；TUI 默认没有这个行为。本 skill 用一个 `SessionStart` hook 补上：新会话启动时检测环境，让 Claude 在处理你第一条消息之前先调用原生 `EnterWorktree`，worktree 仍由 Claude Code 托管（退出会话时照常询问 keep / remove）。

## 快速开始

```bash
# 1. 装 skill（三选一）
/plugin marketplace add Coder42Y/42Marketplace
/plugin install pi-auto-worktree@42marketplace          # 方式一：plugin
ln -sf ~/42Marketplace/skills/pi-auto-worktree ~/.claude/skills/   # 方式二：软链
# 方式三：整个目录拷到 ~/.claude/skills/

# 2. 注册 hook（幂等，可重复跑）
bash <skill目录>/scripts/install.sh
#    可选参数：--base-ref head（本地无 origin 的仓库建议加）
#              --with-copy-hooks（纯非 git 目录也隔离，见下）
```

之后正常 `claude` 启动即生效。第一条消息发出后，Claude 会先进 worktree，用一行告诉你路径和分支，再处理你的消息。

## 工作原理

```
claude 启动
  └─ SessionStart hook(matcher: startup)
       ├─ 非 git、无子仓库、未开快照 ──► 静默退出,什么都不做
       ├─ 已在 worktree / 项目 opt-out / 环境变量关闭 ──► 静默退出
       └─ 否则注入 [auto-worktree] 上下文
            └─ Claude 收到你第一条消息时先调用 EnterWorktree
                 ├─ git 仓库:name 模式 ──► <repo>/.claude/worktrees/<任务名>
                 ├─ 多仓库工作区:先 git worktree add,再 path 模式进入
                 └─ 非 git + 快照 hook:WorktreeCreate 复制目录
```

hook 本身只做检测和提示,不碰 git;创建、切换 cwd、退出时的 keep / remove 都由 Claude Code 原生托管。

## 三种启动位置

| 你在哪启动 | 行为 |
|---|---|
| git 仓库 | 自动 `EnterWorktree`，落在 `<repo>/.claude/worktrees/<任务名>` |
| 多仓库工作区（本身非 git，子目录是仓库） | 第一条消息指向某个子仓库时，在该子仓库建 worktree 并进入；进入前 Claude Code 会弹一次确认 |
| 纯非 git 目录 | 默认不做任何事；装了 `--with-copy-hooks` 后改为目录快照复制到 `~/.claude/worktrees/<目录名>/<任务名>`，改动不会自动回流，需手动 diff 复制回去 |

## 关闭 / 卸载

- 临时关闭：`CLAUDE_AUTO_WORKTREE=0 claude`
- 项目级关闭：`touch .claude/no-auto-worktree`
- 第一条消息直接说「不要 worktree」也会跳过
- 卸载：`bash <skill目录>/scripts/uninstall.sh`

## 前置依赖

- Claude Code ≥ 2.1（需要 `EnterWorktree` 工具与 `SessionStart` hook）
- `jq`、`git`；快照模式另需 `rsync`
- 安装脚本会向 `~/.claude/settings.json` 写入 hook（自动备份为 `settings.json.bak-auto-worktree`），并把 `.claude/worktrees/` 加进全局 gitignore

## 验证记录

以下为上游记录，本次发布未重新执行真实 Claude Code 会话验证。上游使用真实 `claude -p` 会话在临时仓库上的结果(2026-09-02,Claude Code 2.1.258):

| 场景 | 结果 |
|---|---|
| git 仓库,hook 关闭(基线) | 文件写进主工作区,无 worktree |
| git 仓库,hook 开启 | 自动进入 `.claude/worktrees/<任务名>`,主工作区零改动 |
| 多仓库工作区 | 在子仓库建 worktree,path 模式进入前等待用户确认 |
| 纯目录,未开快照 | 静默跳过 |
| 纯目录,开快照 | 原目录不变,改动只在快照里,并主动提醒不回流 |
| 第一条消息说「不要 worktree」 | 跳过不追问 |
| install.sh 连跑两次 / uninstall.sh | hook 条目不重复;卸载后 settings 复原 |

## 注意事项

- `claude -p` 脚本化调用同样会触发，跑批处理时记得 `CLAUDE_AUTO_WORKTREE=0`
- `--continue` / `--resume` 恢复的会话不触发
- 快照模式有 500MB 体积保护（`CLAUDE_COPY_WORKTREE_LIMIT_MB` 可调），超出会拒绝复制并回落到原目录工作

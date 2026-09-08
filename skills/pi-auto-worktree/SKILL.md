---
name: pi-auto-worktree
description: 管理 pi CLI 启动时的自动 Git worktree 隔离和首条任务命名；用户提到自动工作区、每次启动新建 worktree、安装或关闭隔离、恢复、命名和清理时使用。仅 pi 和 Git 工作目录生效，非 Git 目录严格跳过，不适用于 Claude Code。
version: 1.0.0
compatibility: Linux/macOS，Python 3.9+，Git 2.31+，pi CLI；已在 Linux + pi 0.85.1 验证，macOS 未实测。
license: MIT
---

# pi-auto-worktree

这是 pi 版，不是 Claude Code 的 `cc-auto-worktree`。不能调用 CC 的 EnterWorktree、ExitWorktree，也不写 `.claude/settings.json`。

## 机制与安装

启动器在原生 pi 初始化前创建 Git worktree、切换 cwd，再 exec 原生 pi。所有内置工具、会话目录和项目资源由 pi 在新 cwd 初始化。不要用 bash 的 `cd` 或 `process.chdir()` 冒充整个会话的 cwd 切换。

本文件所在目录记为 `<skill目录>`：

```bash
bash <skill目录>/scripts/install.sh
# pi 不在 PATH 时显式指定原生入口：
bash <skill目录>/scripts/install.sh --real-pi /path/to/pi
hash -r
```

安装脚本注册 `~/.local/bin/pi`、全局技能和命名扩展的软链，保存安装记录及旧入口；不改 shell 配置或 pi settings。确保 `~/.local/bin` 排在 PATH 最前面。源码目录须保留，移动前先卸载。
支持 `PI_CODING_AGENT_DIR` 自定义全局资源目录；安装、运行和卸载应使用同一个值。
发现不同的已有入口/技能/扩展时拒绝覆盖，不要强制删除用户文件。仅软链 SKILL.md 或 `pi install` 不会完成启动器安装。

## 启动行为

1. 从当前本地 HEAD 新建分支 `pi/s-日期-时间-随机ID`。
2. 目录 `<仓库>/.pi/worktrees/<name>`。只写 Git 本地 `info/exclude`，不修改已跟踪 `.gitignore`。
3. 保留启动子目录；若它不在已提交版本中，回到新 worktree 根目录。
4. 不 fetch、不提交、不安装依赖、不运行项目测试，不复制未提交/未跟踪/忽略文件。未提交项目配置和本地依赖也不会复制。
5. 创建失败时中止，不悄悄在主工作区继续。退出后保留 worktree、分支与会话。

这是启动前隔离，纯问答也会创建；在第一条消息中说“别建”已经太晚，要用启动开关。

## 命名

- `pi --name fix-login-timeout` / `pi -n fix-login-timeout`：创建时使用清洗后的任务名加 10 位随机后缀，会话标题由 pi 原生参数设置。
- 未指定名字：启动时临时命名。命名扩展在首次任务前提示模型调用 `name_worktree_task`：英文 kebab-case 分支名、可读会话标题（可用中文）。不要包含秘密和个人标识；任务不明确时用 `general-discussion` 等中性名称。
- 仅改分支名与空会话标题，**目录永久保持不变**。后缀保留，防止同名任务冲突。
- 元数据位于该 worktree 的 Git 管理目录 `pi-auto-worktree.json`，不进入版本控制。
- 已成功命名、已手动换分支、已存在会话标题时，不重复命名或覆盖用户选择。
- 模型未调用工具、禁用扩展/工具、没有发送消息时保留临时名；不额外发起独立模型请求。命名失败不影响现有隔离工作区，禁止强制覆盖重名分支。
- 命名使用跨进程排他锁。强制杀进程后若遗留 `.lock`，确认没有其他会话在命名后才可移除。

## 跳过条件

- 当前目录非 Git worktree（即使下层包含多个仓库），不扫描子仓库、不复制快照。
- bare repo、没有首次提交的仓库。
- 已在 linked worktree：沿用当前隔离目录，不嵌套创建。
- `PI_AUTO_WORKTREE=0 pi`（同时跳过当前进程的自动命名）。
- 启动目录或仓库根目录有 `.pi/no-auto-worktree` 或 `.claude/no-auto-worktree`。
- 恢复/选择/复制旧会话参数 `-c`、`--continue`、`-r`、`--resume`、`--session`、`--fork`。
- help/version、模型列表、export、install/update/list/config 等管理操作。

## 边界与恢复

- 只覆盖通过安装入口启动的新进程；print/JSON/RPC 也适用。SDK、IDE 和直接调用原生 pi 不经过启动器。
- 会话内 `/new`、`/fork`、`/clone` 不会创建新的 worktree。需要隔离时退出，在主仓库重新启动 pi。
- 会话按 worktree cwd 保存。从原主目录 `pi -c` 不一定找到它；应 `cd <原worktree启动目录> && pi -c`，或使用 `--session <绝对会话文件>` / 跨目录会话选择器。
- CLI 的 `@file` 和已存在的相对资源路径会锚定原启动目录；它们是用户显式输入，不是文件同步。
- 新 worktree 不自动继承未提交配置、`.env`、依赖目录和信任决定。不要自动复制秘密文件或绕过项目 trust。
- Git worktree 不是安全沙箱，模型仍可使用其他绝对路径。

## 关闭、卸载与清理

```bash
PI_AUTO_WORKTREE=0 pi
# 或在主仓库根目录：
mkdir -p .pi && touch .pi/no-auto-worktree
# 卸载（保留工作成果）：
bash <skill目录>/scripts/uninstall.sh
hash -r
```

恢复项目自动创建：删除相应禁用标记（也检查 `.claude/no-auto-worktree`）。
卸载只移除本工具拥有的软链并恢复原入口，不删除已有 worktree/分支/会话/本地忽略规则。

清理前查看 `git worktree list`、目标工作区 `git status --short` 和分支提交，确认不再被会话使用并征得用户确认。从工作区外运行：

```bash
git -C <主仓库> worktree remove <目标worktree>
# 用户还要求删分支时，先确认提交已保存/合并：
git -C <主仓库> branch -d <分支>
```

禁止自动 `--force`、`branch -D`、`reset --hard` 或清理其他工作区。

用户文档和测试方法见 [README.md](README.md)。

# CentOS Claude Statusline

> A lightweight, four-line Claude Code status line for CentOS 7 and older Linux environments.
> 适用于 CentOS 7 和旧版 Linux 环境的轻量级 Claude Code 四行状态栏。

Inspired by the multi-line layout of `ccstatusline-zh`, this tool is independently reimplemented with Bash and `jq`. It is not a source-code fork and does not require Node.js, npm, or network access at runtime.

本工具受 `ccstatusline-zh` 多行布局启发，使用 Bash + `jq` 独立实现，并非其源码分支。运行时不依赖 Node.js、npm 或网络访问。

## Display / 显示内容

```text
模型: Claude Sonnet 4.5 | 内存: 6.8G/7.6G | Git: +12 -3 ?1
分支: main | 会话: 18分 | 技能: 22
cwd: ~/projects/example
上下文: [██████░░░░░░░░░░] 74k/200k (37%)
```

- Model, available/total memory, and Git line changes
- Branch, current session duration, and installed skill count
- Current working directory
- Context token usage with a fixed 16-cell progress bar
- 模型、可用/总内存、Git 行变更
- 分支、当前会话时长、已安装技能数量
- 当前工作目录
- 上下文 Token 用量和固定 16 格进度条

## Requirements / 环境要求

- Claude Code with `statusLine` command support
- Bash 3.2 or newer
- `jq` 1.5 or newer
- Git is optional; Git fields show a fallback outside a repository
- Linux is recommended; memory shows `n/a` when `/proc/meminfo` is unavailable

CentOS 7 dependencies / CentOS 7 依赖：

```bash
sudo yum install -y epel-release
sudo yum install -y jq git
```

## Install / 安装

```bash
git clone https://github.com/Coder42Y/42Marketplace.git
cd 42Marketplace/tools/centos-claude-statusline
./install.sh
```

The installer:

1. checks that `jq` is available;
2. backs up an existing status-line script and `settings.json` under `~/.claude/backups/`;
3. installs the script as `~/.claude/statusline-command.sh` with mode `0700`;
4. updates only the `statusLine` field in `~/.claude/settings.json`.

安装脚本会检查 `jq`、备份旧文件、以 `0700` 权限安装脚本，并只更新 `settings.json` 中的 `statusLine` 字段。重复运行是安全的。

Restart Claude Code after installation. 安装后重新启动 Claude Code。

## Test / 测试

```bash
./test.sh
```

The test creates an isolated temporary home and Git repository. It does not modify your real Claude Code configuration.

测试使用临时 HOME 和临时 Git 仓库，不会修改真实的 Claude Code 配置。

## Uninstall / 卸载

Remove `~/.claude/statusline-command.sh`, then delete the `statusLine` field from `~/.claude/settings.json` or restore the latest directory under `~/.claude/backups/`.

删除 `~/.claude/statusline-command.sh`，再从 `~/.claude/settings.json` 删除 `statusLine` 字段；也可以恢复 `~/.claude/backups/` 中最近一次备份。

## License

GPL-3.0

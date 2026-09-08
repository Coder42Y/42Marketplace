# 🌳 pi-auto-worktree

> 每次从主仓库启动 pi，自动进入独立工作区，并根据首条任务命名分支和会话。

| | |
|:---|:---|
| **版本** | `v1.0.0` |
| **状态** | `beta` |
| **兼容** | pi CLI（已验证 `0.85.1`）；Linux，macOS 待验证 |
| **最近更新** | `2026-09-08` |

**一句话：**让多个 pi 任务各自在独立目录里工作，不把尚未完成的改动混在主工作区。

---

## 快速开始

前置：已安装 pi CLI、Python 3.9+、Git 2.31+、Bash；无需额外 Python/npm 依赖。安装前请阅读脚本，启动器和扩展以当前用户权限运行。

```bash
# 1. 获取并安装（已克隆仓库时跳过 clone）
git clone https://github.com/Coder42Y/42Marketplace.git ~/42Marketplace
bash ~/42Marketplace/skills/pi-auto-worktree/scripts/install.sh

# 2. 确保启动入口优先，再进入你的主仓库运行 pi
export PATH="$HOME/.local/bin:$PATH"
hash -r
cd /path/to/your/repo
pi
# 在会话里说：“帮我修复登录超时问题”

# 3. 安装记录（通常不需要手动编辑）
# ~/.pi/agent/pi-auto-worktree-install.json
```

pi 不在 PATH 时：`bash ~/42Marketplace/skills/pi-auto-worktree/scripts/install.sh --real-pi /path/to/pi`。
安装脚本不修改 shell 配置；如有需要，自行将 PATH 配置加入 shell 启动文件。`command -v pi` 应显示 `~/.local/bin/pi` 对应的绝对路径。

**这是 pi 专用工具，不要用 Claude Code 的 `/plugin install` 安装。** Claude Code 用户请使用 [cc-auto-worktree](../cc-auto-worktree/)。仅将技能软链进目录也不够：启动器与命名扩展需要一起安装。

## 特性亮点

- 🌱 **真正切换启动目录** — 先创建并进入 worktree，再启动 pi；工具、会话和项目资源从同一目录初始化。
- 🏷️ **任务命名** — 支持 `--name`；未指定时让模型在首条任务前命名分支与会话。
- 🧭 **目录稳定** — 后续只改分支和会话名称，不移动工作目录。
- 🛡️ **保护已有内容** — 不复制或改写主工作区的未提交文件；退出不自动删除成果。
- ⏭️ **非 Git 严格跳过** — 非仓库目录、多仓库父目录均不创建、不复制。

## 命名示例

| 启动方式 | 目录 | 分支与会话 |
|:---|:---|:---|
| `pi --name fix-login-timeout` | `.pi/worktrees/fix-login-timeout-<ID>` | 分支 `pi/fix-login-timeout-<ID>`，会话 `fix-login-timeout` |
| `pi`，随后描述登录超时任务 | `.pi/worktrees/s-<时间>-<ID>`，始终不变 | 模型调用工具后，分支改为 `pi/fix-login-timeout-<ID>`，会话如 `修复登录超时` |

`<ID>` 是 10 位随机后缀，始终保留。`--name` 可用中文，路径会清洗非法字符。
语义命名由当前模型调用专用工具完成，不额外请求另一个模型。未发消息、模型未调用、禁用扩展或工具时，保持临时名。已有标题或手动更换的分支不会被覆盖。

## 创建和跳过规则

从本地 **HEAD** 创建，不 fetch、不自动提交，不安装依赖或运行项目测试。目录加入 Git 本地 `info/exclude`，不改项目 `.gitignore`。

| 情况 | 行为 |
|:---|:---|
| 主工作区或已提交子目录启动新 pi | 创建独立 worktree，尽量保留相对子目录 |
| 非 Git 目录（包括多仓库父目录） | 严格跳过 |
| 已在 linked worktree | 沿用当前目录，不嵌套创建 |
| bare repo / 无首次提交 | 跳过 |
| `pi -c` / `pi -r` / `--session` / `--fork` | 不创建，交给 pi 处理旧会话 |
| `pi --help` / `--version` / install / update 等 | 不创建 |
| 创建失败 | 中止启动，不回退到主工作区编辑 |
| 退出 pi | 保留 worktree、分支和会话 |

## 配置与边界

```bash
# 单次关闭创建和自动命名
PI_AUTO_WORKTREE=0 pi

# 在主仓库根目录关闭自动创建
mkdir -p .pi && touch .pi/no-auto-worktree
```

兼容 `.claude/no-auto-worktree` 标记。启动时已创建工作区，所以第一条消息说“别建”来不及；请使用上述开关。

- **只覆盖重新启动进程**：会话内 `/new`、`/fork`、`/clone` 不创建新的 worktree。需要隔离时，退出后从主仓库重新启动 pi。
- **恢复目录**：进入原 worktree 的启动目录后运行 `pi -c`，或使用 `--session <绝对会话文件>`。在主目录 `pi -c` 不保证找到 worktree 会话。
- **干净副本**：不带入未提交文件、`.env`、忽略文件、本地依赖和未提交的项目 `.pi` 配置。不会自动复制秘密文件、授权项目 trust。
- **不是沙箱**：分离工作文件不等于限制系统访问，模型仍能访问其他绝对路径。
- **入口范围**：print/JSON/RPC 新进程也适用；直接调用原生 pi、SDK 或 IDE 绕过启动器时不适用。
- **自定义配置目录**：支持 `PI_CODING_AGENT_DIR`；安装、运行、卸载应使用同一个值。`PI_AUTO_WORKTREE_REAL_PI` 可临时指定原生入口。

## 安装内容、更新与卸载

安装器建立三处软链：

```text
~/.local/bin/pi                           → scripts/launch.py
~/.pi/agent/skills/pi-auto-worktree        → 本技能目录
~/.pi/agent/extensions/pi-auto-worktree-name.ts → extensions/auto-worktree-name.ts
```

原入口存在时备份为 `~/.local/bin/pi.before-pi-auto-worktree`；安装记录在 `~/.pi/agent/pi-auto-worktree-install.json`。遇到不属于本工具的文件或旧版命名扩展会拒绝覆盖。安装是可重复的，不修改 pi settings。

源码目录需要保留。更新用 `git -C ~/42Marketplace pull --ff-only`，软链跟随更新；下一次启动生效。迁移源码目录前先卸载。

```bash
bash ~/42Marketplace/skills/pi-auto-worktree/scripts/uninstall.sh
hash -r
```

卸载恢复原入口并移除本工具软链，保留已有 worktree、分支、会话与 Git 本地忽略规则。不会清理用户成果。若旧入口或资源被其他程序改动，会停止并报告，不强制覆盖。

## 手动清理

先退出相关会话，检查目标工作区改动和分支提交，确认需要清理，再从工作区外执行：

```bash
git -C /path/to/main-repo worktree list
git -C /path/to/worktree status --short
git -C /path/to/main-repo worktree remove /path/to/worktree
# 仅在确认提交已保存或合并、并且还需要删分支时：
git -C /path/to/main-repo branch -d pi/task-name-ID
```

不要用 `--force` 或 `branch -D` 绕过保护。命名进程被强制终止时可能留下 Git 管理目录中的 `pi-auto-worktree.json.lock`；确认没有会话仍在命名后，才可手动移除。

## 验证

```bash
python3 -m unittest discover -s ~/42Marketplace/skills/pi-auto-worktree/scripts -p 'test_*.py' -v
```

15 项测试覆盖创建、跳过、未提交文件保护、并发隔离、名字清洗、真实 pi 扩展加载/工具激活、命名与重名拒绝、目录/提交不变、安装卸载与冲突保护。测试使用临时目录，不调用模型。找不到原生 pi 时，两个 pi 集成测试会标记跳过；可设置 `PI_AUTO_WORKTREE_REAL_PI=/path/to/pi` 后补跑。

发布验证环境：Linux、pi `0.85.1`。macOS 尚未实测，因此标记为 beta。

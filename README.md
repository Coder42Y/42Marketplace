<div align="center">

<img src="logo.svg" width="120" alt="42 Marketplace logo">

# 🎯 42 Marketplace

为 Claude Code、Codex 和 pi 打造的开源技能集合

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-Claude%20Code%20%7C%20Codex%20%7C%20pi-blue.svg)](#skills)
[![Type](https://img.shields.io/badge/type-skill%20collection-purple.svg)](#skills)

简体中文 ｜ [English](./README.en.md)

</div>

---

## Why 42 Marketplace?

每个 skill 是一个即拷即用的**能力包**，给 AI 装上特定技能，一句话触发。纯 prompt 技能零依赖，带脚本的注明前置条件，按需安装即可。

大部分技能采用通用 `SKILL.md` 格式；涉及启动器、hooks 或特定工具的技能有平台限制，请先查看各自 README。

## Features

- 📦 **按需安装** — 纯 prompt 技能 clone 后软链即可使用。
- 🎯 **多平台收录** — 支持 Claude Code、Codex 和 pi；专用技能单独标注。
- 🧪 **实战迭代** — 技能文档标明状态和验证范围，实验功能不冒充稳定支持。
- 🔓 **开源 MIT** — 自由使用和修改。

## Quickstart

### 方式一：Claude Code plugin marketplace

在 Claude Code 会话中执行，按需安装插件：

```text
/plugin marketplace add Coder42Y/42Marketplace
/plugin install algo-solver@42marketplace
/reload-plugins
```

安装后可在 `/plugins` 中查看 `42marketplace`。技能使用插件命名空间，也可通过自然语言触发。

> `cc-auto-worktree` 安装后还需要运行它的 `scripts/install.sh`。`pi-auto-worktree` 是 pi 专用技能，不在 CC 插件清单内。

### 方式二：Claude Code / Codex 独立技能

先克隆仓库一次；已有副本请直接更新，不要重复 clone：

```bash
git clone https://github.com/Coder42Y/42Marketplace.git ~/42Marketplace
```

选择平台，安装需要的技能。以下以 `algo-solver` 为例，可替换为兼容当前平台的技能名。

**Claude Code：**

```bash
mkdir -p ~/.claude/skills
ln -s ~/42Marketplace/skills/algo-solver ~/.claude/skills/algo-solver
```

**Codex：**

```bash
mkdir -p ~/.codex/skills
ln -s ~/42Marketplace/skills/algo-solver ~/.codex/skills/algo-solver
```

同名路径已存在时，请先检查，不要强制覆盖。不要把平台专用技能批量装到其他平台。

### 方式三：pi 自动 worktree

先按上一步克隆仓库，再安装 pi 启动器、技能和命名扩展：

```bash
bash ~/42Marketplace/skills/pi-auto-worktree/scripts/install.sh
export PATH="$HOME/.local/bin:$PATH"
hash -r
```

之后从 Git 主工作区运行 `pi` 即可。非 Git 目录严格跳过。完整依赖、命名与恢复规则见 [pi-auto-worktree 文档](./skills/pi-auto-worktree/)。

### 更新

```bash
git -C ~/42Marketplace pull --ff-only
```

以上独立安装方式使用软链，源码更新会自动跟随；重新启动对应工具生效。CC 插件安装方式请通过插件管理功能更新。

## How it works

每个技能由 `SKILL.md` 和可选脚本、资源组成。工具发现技能后，根据用户请求按需读取定义并执行。

普通技能软链即可使用；平台专用功能可能需要额外安装。比如 `cc-auto-worktree` 注册 Claude Code hook，`pi-auto-worktree` 则在 pi 启动前创建并进入工作区。两者不能互换。

## Usage

安装后，对 AI 用自然语言触发：

```text
“帮我沉淀一下这个登录方案的设计 HTML”  → design-html
“讲一下力扣 300 最长递增子序列”        → algo-solver
“把这篇文章生成小红书图文”             → xhs-image-gen
“帮我提个 MR”                         → submit-gitlab-mr
```

## Skills

### 平台专用

- 🌳 [cc-auto-worktree](./skills/cc-auto-worktree/) — **Claude Code 专用**：新会话自动进入独立 worktree；安装技能后需运行其安装脚本。
- 🌱 [pi-auto-worktree](./skills/pi-auto-worktree/) — **pi 专用**：启动前隔离工作区，首条任务命名分支和会话；非 Git 跳过，目录保持稳定。`beta`

### 通用技能与工具集成

通用格式不代表没有外部依赖；请以各技能 README 的兼容性和前置条件为准。

- 🎨 [design-html](./skills/design-html/) — 把 idea 沉淀成 Anthropic 暖色风设计说明 HTML。
- ✍️ [zhihu-notes](./skills/zhihu-notes/) — 知乎风格长文生成。
- 🌺 [elder-blessing-comments](./skills/elder-blessing-comments/) — 长辈风祝福文案。
- 🔀 [submit-gitlab-mr](./skills/submit-gitlab-mr/) — GitLab MR 提交，需要 glab CLI。
- 🧮 [algo-solver](./skills/algo-solver/) — 算法题解，支持 Python 3 和 Java。
- 📱 [xhs-image-gen](./skills/xhs-image-gen/) — 小红书图文卡片。`beta`
- 🎯 [daily-pulse](./skills/daily-pulse/) — 每日热点推送与按需查询。
- 🔍 [deep-repo-research](./skills/deep-repo-research/) — 自动调研 GitHub / GitLab 仓库并生成报告。
- 📝 [ntn-todo](./skills/ntn-todo/) — 查询管理 Notion 待办，维护本周进度概览，首次自动引导。
- 🎬 [vid2report](./skills/vid2report/) — B 站 / YouTube 视频转结构化研究报告。

### 独立仓库

- 🛡️ [vps-proxy-deploy](https://github.com/Coder42Y/vps-proxy-deploy) — 在 VPS 上安全部署网络中转，支持 Hysteria2 / VLESS 等。

## Contributing

1. 技能放在 `skills/<name>/`，独立工具放在 `tools/<name>/`。
2. 每个技能包含 `SKILL.md`（技能定义）和 `README.md`（用户文档）。
3. 遵循 [`DESIGN.md`](./DESIGN.md) 的文档设计规范，并注明平台、依赖和验证范围。

## License

[MIT](./LICENSE)

## 隐私

公开代码和文档不应包含个人信息、API key、token、密码或私有配置。提交前请检查并清理；个人文件应通过 `.gitignore` 排除。

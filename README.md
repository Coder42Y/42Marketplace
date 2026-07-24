<div align="center">

<h1>🎯 42 Marketplace</h1>

<p>
  <b>为 Claude Code、OpenClaw 及更多 AI 工具打造的开源技能与工具集合</b><br>
  <em>An open-source collection of skills and tools for Claude Code, OpenClaw &amp; more</em>
</p>

<p>
  <a href="#-简体中文"><kbd>🀄&nbsp;&nbsp;简体中文</kbd></a>
  &nbsp;&nbsp;
  <a href="#-english"><kbd>🇬🇧&nbsp;&nbsp;English</kbd></a>
</p>

<br>

</div>

---

<a id="简体中文"></a>

<h2>🀄 简体中文</h2>

### 简介

**42 Marketplace** 是一个面向 **Claude Code**、**OpenClaw** 及其他 AI 开发环境的开源技能与工具集合。`skills/` 中的技能可独立安装，`tools/` 中的程序可单独运行。

### 技能列表

| 技能 | 描述 | 版本 |
|------|------|------|
| [🎯 daily-pulse](./skills/daily-pulse/) | 每日热点推送 + 按需查询，结构化预抓取 + Agent 评分排版 | `v3.0.0` |
| [🔍 deep-repo-research](./skills/deep-repo-research/) | 自动调研 GitHub/GitLab 仓库并生成结构化 Markdown 报告。支持 Go / Node.js / Python / Java / Rust / Ruby 项目，四种报告风格，含私有仓库支持 | `v0.2.0` |
| [🎬 vid2report](./skills/vid2report/) | 一键将 B站/YouTube 视频变为结构化研究报告。提取文案 → 语音转录 → AI 深度分析 → 存档 Obsidian。自带 Express 后端 + Claude Code `/av` 命令 | `v1.0.0` |
| [🎨 design-html](./skills/design-html/) | 把 idea/方案沉淀成 Anthropic 暖色风的设计说明 HTML，讲思路不堆代码，自带 SVG 架构图 | `v0.1.0` |
| [✍️ zhihu-notes](./skills/zhihu-notes/) | 生成知乎风格的优质长文，标准结构 + 文风规范，直接可发 | `v0.1.0` |
| [🌺 elder-blessing-comments](./skills/elder-blessing-comments/) | 生成长辈风社交媒体祝福文案（抖音/微信群/朋友圈），emoji 拉满，直接复制粘贴 | `v0.1.0` |
| [🔀 submit-gitlab-mr](./skills/submit-gitlab-mr/) | 冲突检查 + 快速提交 GitLab MR，只卡 Git 冲突这一个 gate，需 glab CLI | `v0.1.0` |
| [🧮 algo-solver](./skills/algo-solver/) | 算法题讲解与题解生成（面试备战），Python3+Java 双语言，自动落盘结构化笔记 | `v0.1.0` |
| [📱 xhs-image-gen](./skills/xhs-image-gen/) | 小红书图文卡片生成器，文案/文章转 1-10 张 PNG，3 种风格（anthropic/notion/minimal） | `v0.1.0` |

### 工具列表

| 工具 | 描述 | 版本 |
|------|------|------|
| [📊 centos-claude-statusline](./tools/centos-claude-statusline/) | 受 ccstatusline-zh 多行布局启发，为 CentOS 7 和旧版 Linux 使用 Bash + jq 独立实现的 Claude Code 四行状态栏 | `v1.0.0` |

### 快速开始

```bash
git clone https://github.com/Coder42Y/42Marketplace.git
cd 42Marketplace
```

**Claude Code 用户：** 将技能目录软链接到 `~/.claude/skills/`：

```bash
ln -s $(pwd)/skills/daily-pulse ~/.claude/skills/daily-pulse
ln -s $(pwd)/skills/deep-repo-research ~/.claude/skills/deep-repo-research
ln -s $(pwd)/skills/vid2report ~/.claude/skills/vid2report
ln -s $(pwd)/skills/design-html ~/.claude/skills/design-html
ln -s $(pwd)/skills/zhihu-notes ~/.claude/skills/zhihu-notes
ln -s $(pwd)/skills/elder-blessing-comments ~/.claude/skills/elder-blessing-comments
ln -s $(pwd)/skills/submit-gitlab-mr ~/.claude/skills/submit-gitlab-mr
ln -s $(pwd)/skills/algo-solver ~/.claude/skills/algo-solver
ln -s $(pwd)/skills/xhs-image-gen ~/.claude/skills/xhs-image-gen
```

**OpenClaw 用户：** 将技能目录复制到 `~/.openclaw/workspace/skills/`。

进入你想使用的技能目录，按该技能的 README 安装即可。

### 设计规范

所有 Skill README 遵循统一的设计规范，见 [`DESIGN.md`](DESIGN.md)。

### 贡献指南

1. 技能放在 `skills/<skill-name>/`，独立程序放在 `tools/<tool-name>/`
2. 每个技能包含 `SKILL.md`（Claude 读取的技能定义）和 `README.md`（用户文档）
3. 每个项目提供完整的测试和安装说明

### 隐私声明

本仓库公开的代码和文档均经过清理，不含个人身份信息、API key / token / 密码、私有配置。个人隐私文件通过 `.gitignore` 排除。


---

<a id="english"></a>

<h2>🇬🇧 English</h2>

### About

**42 Marketplace** is an open-source collection of skills and tools for **Claude Code**, **OpenClaw**, and other AI development environments. Skills under `skills/` are independently installable; programs under `tools/` run standalone.

### Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [🎯 daily-pulse](./skills/daily-pulse/) | Daily hot topics push + on-demand query, structured pre-fetching + Agent scoring | `v3.0.0` |
| [🔍 deep-repo-research](./skills/deep-repo-research/) | Research GitHub/GitLab repos and generate structured Markdown reports. Supports Go / Node.js / Python / Java / Rust / Ruby, four report styles, with private repo support | `v0.2.0` |
| [🎬 vid2report](./skills/vid2report/) | Turn any Bilibili/YouTube video into a structured research report. Extract → transcribe → AI analysis → Obsidian. Includes Express backend + Claude Code `/av` command | `v1.0.0` |
| [🎨 design-html](./skills/design-html/) | Turn an idea/architecture/plan into an Anthropic warm-tone design HTML doc - focus on reasoning, no code dumps, with SVG diagrams | `v0.1.0` |
| [✍️ zhihu-notes](./skills/zhihu-notes/) | Generate Zhihu-style long-form articles with standard structure and tone, ready to publish | `v0.1.0` |
| [🌺 elder-blessing-comments](./skills/elder-blessing-comments/) | Generate elder-style Chinese social-media blessing comments (Douyin/WeChat/Xiaohongshu), emoji-heavy, copy-paste ready | `v0.1.0` |
| [🔀 submit-gitlab-mr](./skills/submit-gitlab-mr/) | Conflict-checked GitLab MR submission - only gates on Git conflicts, requires glab CLI | `v0.1.0` |
| [🧮 algo-solver](./skills/algo-solver/) | Algorithm problem explanation & solution generation (interview prep), Python3+Java, auto-saves structured notes | `v0.1.0` |
| [📱 xhs-image-gen](./skills/xhs-image-gen/) | Xiaohongshu card generator - turn text/articles into 1-10 PNGs, 3 styles (anthropic/notion/minimal) | `v0.1.0` |

### Tools

| Tool | Description | Version |
|------|-------------|---------|
| [📊 centos-claude-statusline](./tools/centos-claude-statusline/) | A four-line Claude Code status line independently built with Bash + jq for CentOS 7 and older Linux, inspired by ccstatusline-zh's multi-line layout | `v1.0.0` |

### Quick Start

```bash
git clone https://github.com/Coder42Y/42Marketplace.git
cd 42Marketplace
```

**Claude Code users:** Symlink skill directories into `~/.claude/skills/`:

```bash
ln -s $(pwd)/skills/daily-pulse ~/.claude/skills/daily-pulse
ln -s $(pwd)/skills/deep-repo-research ~/.claude/skills/deep-repo-research
ln -s $(pwd)/skills/vid2report ~/.claude/skills/vid2report
ln -s $(pwd)/skills/design-html ~/.claude/skills/design-html
ln -s $(pwd)/skills/zhihu-notes ~/.claude/skills/zhihu-notes
ln -s $(pwd)/skills/elder-blessing-comments ~/.claude/skills/elder-blessing-comments
ln -s $(pwd)/skills/submit-gitlab-mr ~/.claude/skills/submit-gitlab-mr
ln -s $(pwd)/skills/algo-solver ~/.claude/skills/algo-solver
ln -s $(pwd)/skills/xhs-image-gen ~/.claude/skills/xhs-image-gen
```

**OpenClaw users:** Copy skill directories into `~/.openclaw/workspace/skills/`.

Navigate to any skill directory and follow its README for installation.

### Design Guidelines

All skill READMEs follow a unified design system. See [`DESIGN.md`](DESIGN.md).

### Contributing

1. Place skills in `skills/<skill-name>/` and standalone programs in `tools/<tool-name>/`
2. Include `SKILL.md` (Claude skill definition) and `README.md` (user docs) with each skill
3. Provide complete tests and installation instructions for every project

### Privacy

All published code and docs are sanitized. No personal info, API keys, tokens, or private configs are included. Personal files are excluded via `.gitignore`.

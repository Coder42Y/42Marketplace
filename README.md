<div align="center">

<h1>🎯 <code>KrisVault</code></h1>

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

**KrisVault** 是一个面向 **Claude Code**、**OpenClaw** 及其他 AI 开发环境的开源技能与工具集合。`skills/` 中的技能可独立安装，`tools/` 中的程序可单独运行。

### 技能列表

| 技能 | 描述 | 版本 |
|------|------|------|
| [🎯 daily-pulse](./skills/daily-pulse/) | 每日热点推送 + 按需查询，结构化预抓取 + Agent 评分排版 | `v3.0.0` |
| [🔍 deep-repo-research](./skills/deep-repo-research/) | 自动调研 GitHub/GitLab 仓库并生成结构化 Markdown 报告。支持 Go / Node.js / Python / Java / Rust / Ruby 项目，四种报告风格，含私有仓库支持 | `v0.2.0` |
| [🎬 vid2report](./skills/vid2report/) | 一键将 B站/YouTube 视频变为结构化研究报告。提取文案 → 语音转录 → AI 深度分析 → 存档 Obsidian。自带 Express 后端 + Claude Code `/av` 命令 | `v1.0.0` |

### 工具列表

| 工具 | 描述 | 版本 |
|------|------|------|
| [📊 centos-claude-statusline](./tools/centos-claude-statusline/) | 受 ccstatusline-zh 多行布局启发，为 CentOS 7 和旧版 Linux 使用 Bash + jq 独立实现的 Claude Code 四行状态栏 | `v1.0.0` |

### 快速开始

```bash
git clone https://github.com/Coder42Y/KrisVault.git
cd KrisVault
```

**Claude Code 用户：** 将技能目录软链接到 `~/.claude/skills/`：

```bash
ln -s $(pwd)/skills/daily-pulse ~/.claude/skills/daily-pulse
ln -s $(pwd)/skills/deep-repo-research ~/.claude/skills/deep-repo-research
ln -s $(pwd)/skills/vid2report ~/.claude/skills/vid2report
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

**KrisVault** is an open-source collection of skills and tools for **Claude Code**, **OpenClaw**, and other AI development environments. Skills under `skills/` are independently installable; programs under `tools/` run standalone.

### Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [🎯 daily-pulse](./skills/daily-pulse/) | Daily hot topics push + on-demand query, structured pre-fetching + Agent scoring | `v3.0.0` |
| [🔍 deep-repo-research](./skills/deep-repo-research/) | Research GitHub/GitLab repos and generate structured Markdown reports. Supports Go / Node.js / Python / Java / Rust / Ruby, four report styles, with private repo support | `v0.2.0` |
| [🎬 vid2report](./skills/vid2report/) | Turn any Bilibili/YouTube video into a structured research report. Extract → transcribe → AI analysis → Obsidian. Includes Express backend + Claude Code `/av` command | `v1.0.0` |

### Tools

| Tool | Description | Version |
|------|-------------|---------|
| [📊 centos-claude-statusline](./tools/centos-claude-statusline/) | A four-line Claude Code status line independently built with Bash + jq for CentOS 7 and older Linux, inspired by ccstatusline-zh's multi-line layout | `v1.0.0` |

### Quick Start

```bash
git clone https://github.com/Coder42Y/KrisVault.git
cd KrisVault
```

**Claude Code users:** Symlink skill directories into `~/.claude/skills/`:

```bash
ln -s $(pwd)/skills/daily-pulse ~/.claude/skills/daily-pulse
ln -s $(pwd)/skills/deep-repo-research ~/.claude/skills/deep-repo-research
ln -s $(pwd)/skills/vid2report ~/.claude/skills/vid2report
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

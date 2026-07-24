# 🔍 deep-repo-research

> 给一个仓库 URL，自动抓取核心源码、分析架构和部署模式，生成结构化 Markdown 调研报告

| | |
|:---|:---|
| **版本** | `v0.2.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `Codex` |

---

## Why

手动翻一个陌生仓库要花一两个小时:看 README、找入口文件、追数据流、读配置、想清楚怎么部署。这个 skill 把这套流程固化下来——**输入一个 URL,几分钟后拿到一份结构化研究报告**,省下来的时间用来决策而不是爬代码。

---

## Features

- **多平台** — GitHub + GitLab,公开 + 私有仓库
- **四种报告风格** — `overview` / `architecture` / `deployment` / `full`,按需取用
- **多语言识别** — Go / Node.js / Python / Java / Rust / Ruby 项目自动适配
- **私有仓库支持** — 通过 `GITHUB_TOKEN` / `GITLAB_TOKEN` 环境变量鉴权
- **Token 节流可控** — 默认抓 15 个核心文件、每文件 200 行,大仓库靠结构推断而非暴力读
- **模板可覆盖** — 用户模板放 `~/.deep-repo-research/templates/` 即可覆盖默认 Jinja2 模板

---

## Quickstart

```bash
# 1. 安装依赖
git clone https://github.com/Coder42Y/42Marketplace.git
cd 42Marketplace/skills/deep-repo-research
pip install -r requirements.txt

# 2. 软链到 Claude Code skills 目录(也可软链到 Codex 等其他 agent)
ln -s $(pwd) ~/.claude/skills/deep-repo-research

# 3. 在 Claude Code 对话中触发
"调研一下 https://github.com/octocat/Hello-World"
"帮我分析这个仓库的架构"
"给这个项目写一份部署指南"
```

或者直接用命令:

```
/github-research https://github.com/octocat/Hello-World --style architecture
```

---

## Usage

### 报告风格

| 风格 | 内容 | 阅读时长 |
|------|------|----------|
| `overview` | 项目简介 + 技术栈 | 2-3 min |
| `architecture` | 架构模式 + 数据流 + 核心源码分析 | 5-8 min |
| `deployment` | 部署方式 + 配置 + 示例 | 5 min |
| `full` | 全部整合 | 10-15 min |

### 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `repo-url` | 仓库地址(GitHub 或 GitLab) | 必填 |
| `--style` | 报告风格 | `full` |
| `--auto` | 跳过文件列表确认,自动执行 | 否 |
| `--max-files` | 最多分析文件数 | `15` |

### 私有仓库

```bash
export GITHUB_TOKEN=ghp_xxx   # GitHub
export GITLAB_TOKEN=glpat-xxx # GitLab
```

### 自定义模板

```bash
mkdir -p ~/.deep-repo-research/templates
cp templates/full.md.j2 ~/.deep-repo-research/templates/
# 编辑后同名覆盖即可
```

---

## 前置依赖

- **Python** `>= 3.9`
- **GitHub Token** / **GitLab Token**(可选,以下场景需要)
  - 访问私有仓库
  - 提高 API rate limit(公开仓库匿名调用每小时 60 次,带 token 可到 5000 次)

---

## License

MIT

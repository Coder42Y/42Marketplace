# 🔍 deep-repo-research

> 自动调研 GitHub/GitLab 仓库并生成结构化 Markdown 报告

| | |
|:---|:---|
| **版本** | `v0.2.0` |
| **状态** | `beta` |
| **兼容** | `Claude Code`, `Codex` |
| **最近更新** | `2026-05-08` |

**一句话：**给一个仓库 URL，自动抓取核心源码、分析架构和部署模式，生成结构化研究报告。支持 6 种语言、4 种报告风格、私有仓库。

---

## 快速开始

```bash
# 1. 克隆并安装
git clone https://github.com/Coder42Y/42Marketplace.git
cd 42Marketplace/skills/deep-repo-research
pip install -r requirements.txt

# 2. 链接到 Claude Code skills 目录
ln -s $(pwd) ~/.claude/skills/deep-repo-research

# 3. 触发（在 Claude Code 对话中）
"调研一下 https://github.com/octocat/Hello-World"
"帮我分析这个仓库的架构"
"给这个项目写一份部署指南"
```

---

## 特性

- **🌍 多平台** — GitHub + GitLab，公开 + 私有仓库
- **📊 四种报告** — 概览 / 架构分析 / 部署指南 / 完整报告
- **🐍 多语言** — Go / Node.js / Python / Java / Rust / Ruby 项目自动识别
- **🔐 私有仓库** — 支持 GITHUB_TOKEN / GITLAB_TOKEN 环境变量

---

## 使用

### 报告风格

| 风格 | 说明 | 阅读时长 |
|------|------|----------|
| `overview` | 项目简介 + 技术栈 | 2-3 min |
| `architecture` | 架构模式 + 数据流 + 核心源码分析 | 5-8 min |
| `deployment` | 部署方式 + 配置 + 示例 | 5 min |
| `full` | 以上全部整合 | 10-15 min |

### 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `repo-url` | 仓库地址（GitHub 或 GitLab） | 必填 |
| `--style` | 报告风格：`overview`, `architecture`, `deployment`, `full` | `full` |
| `--auto` | 跳过文件列表确认，自动执行 | 否 |
| `--max-files` | 最多分析文件数 | 15 |

### 私有仓库

```bash
# GitHub
export GITHUB_TOKEN=ghp_xxx

# GitLab
export GITLAB_TOKEN=glpat-xxx
```

---

## 项目结构

```
deep-repo-research/
├── SKILL.md                  # Claude 读取的 skill 定义
├── README.md                 # 本文档
├── requirements.txt
├── scripts/
│   ├── fetch_repo.py         # 下载仓库文件
│   ├── analyze_structure.py  # 识别核心文件
│   └── generate_report.py    # 生成 Markdown 报告
├── templates/
│   ├── overview.md.j2
│   ├── architecture.md.j2
│   ├── deployment.md.j2
│   └── full.md.j2
└── tests/
    ├── test_fetch_repo.py
    ├── test_analyze_structure.py
    └── test_generate_report.py
```

---

## 开发

```bash
# 运行测试
pytest tests/ -v

# 手动测试 fetch
python scripts/fetch_repo.py https://github.com/octocat/Hello-World --list-only

# 手动测试分析
python scripts/fetch_repo.py https://github.com/octocat/Hello-World --list-only > tree.json
python scripts/analyze_structure.py tree.json --max-files 10

# 手动测试报告生成
python scripts/generate_report.py analysis_result.json --style full
```

---

## 自定义模板

在 `~/.deep-repo-research/templates/` 下创建同名模板文件即可覆盖默认模板：

```bash
mkdir -p ~/.deep-repo-research/templates
cp templates/full.md.j2 ~/.deep-repo-research/templates/
# 编辑自定义模板
```

---

## 要求

- **Python** `>= 3.9`
- **GitHub Token**（可选，用于私有仓库或提高 rate limit）

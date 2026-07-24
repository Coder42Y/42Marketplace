# 🎯 daily-pulse

> 每日热点推送 + 按需查询：Node 预抓取 + Agent 评分排版，5 秒全网覆盖、节省 90% token。

| | |
|:---|:---|
| **版本** | `v3.0.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `Codex` |
| **最近更新** | `2026-04-22` |

---

## Why

v2 是纯 LLM 驱动：Agent 自己决定搜什么、怎么合并。每次推送 25 次工具调用、44K tokens、183 秒 —— 慢、贵、对弱模型不友好。

v3 把**搜索与评分**从 LLM 手里拿回来，写成零依赖 Node.js 脚本。LLM 只做它擅长的事：摘要与排版。耗时 20-40s、tokens 2-4K，弱模型也能稳定输出。

---

## Features

- **⚡ 5 秒预抓取** — `fetch.js` 并行拉取所有源，纯 Node.js 内置模块，零外部依赖
- **📊 结构化评分** — `source_weight × time_decay × social_bonus × (1 + ai_semantic_bonus)`
- **🎯 7 个预设板块** — 热点新闻 / AI / 财经 / 电竞 / 足球 / GitHub / 科技数码，支持自定义
- **🔍 按需查询** — "给我看看 AI"、"CS2 赛程"、"GitHub 热门"，实时返回指定板块
- **⏰ 定时推送** — Cron 每天 9:30 自动推送（需 OpenClaw）

---

## Quickstart

```bash
# 1. 克隆
git clone https://github.com/Coder42Y/42Marketplace.git
cd 42Marketplace/skills/daily-pulse

# 2. 软链到你的 Agent(按需选)
# Claude Code
ln -s $(pwd) ~/.claude/skills/daily-pulse
# Codex
ln -s $(pwd) ~/.codex/skills/daily-pulse
```

触发试试：

```
"推热点"
"给我看看 AI"
"GitHub 热门"
```

配置文件：`~/.openclaw/cron/hot-topics-prefs.json`

---

## Usage

### 定时推送（Cron）

每天 9:30 自动执行，payload：`请执行每日热点推送`。**需 OpenClaw**。

### 一键催推

```
推热点 / 立即推送 / 今日热点 / 热点日报 / 催一下
```

### 按需查询

| 你说 | 返回 |
|------|------|
| "给我看看 AI" / "AI 简讯" | `ai` 板块 |
| "查一下财经" / "股市动态" | `finance` 板块 |
| "GitHub 热门" / "开源趋势" | `github` 板块 |
| "CS2 赛程" / "电竞赛果" | `esports` 板块 |
| "AI 和财经简讯" | `ai` + `finance` 多板块 |

更多触发词、模糊匹配规则、自定义板块、评分公式与完整配置 schema，见 **[SKILL.md](./SKILL.md)**。

---

## 前置依赖

- **Node.js** `>= 18`（仅用内置 `https` / `http` / `fs`，零外部依赖）
- **Agent**：Claude Code 或 Codex
- **Cron 定时推送**：仅 OpenClaw 支持；Claude Code / Codex 走手动触发或外部调度

---

## License

MIT

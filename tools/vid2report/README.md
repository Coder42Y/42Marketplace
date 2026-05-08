# vid2report

> Turn any Bilibili or YouTube video into a structured research report — fully automated, headless, no browser.
> 一键将 B站/YouTube 视频变成结构化研究报告 — 全自动、无前端、无需浏览器。

```
Video URL → Extract transcript → Transcribe if needed → AI deep analysis → Markdown report → Obsidian
视频链接 → 提取文案 → 语音转录(如需) → AI 深度分析 → Markdown 报告 → 存档 Obsidian
```

---

## Quick Start / 快速开始

```bash
cd tools/vid2report/server
./setup.sh your-api-key-here
npm start
```

Server running at `http://localhost:3550`. 就这些。

**Supported providers**：MiniMax, OpenAI, DeepSeek, Moonshot, SiliconFlow — any OpenAI-compatible endpoint.

**Dependencies handled automatically**：`yt-dlp`, `faster-whisper`, `npm packages`. If auto-install fails:
```bash
brew install yt-dlp
pip3 install faster-whisper
```

---

## Usage / 使用方式

| Channel | Command |
|---------|---------|
| Claude Code | `/av https://www.bilibili.com/video/BVxxx` |
| CLI | `./analyze-video.sh BVxxx` |
| HTTP | `curl -X POST :3550/api/save-transcript -d '{...}'` |

---

## How it works / 工作原理

```
 POST /api/save-transcript
         │
    ┌────▼─────────────────────────────────────────┐
    │  Phase 1  Extract / 提取文案                  │
    │    Bilibili API / YouTube yt-dlp              │
    │    ├─ ≥ 500 chars → use directly / 直接用    │
    │    └─ < 500 chars → Phase 2 / 走转录         │
    │                                              │
    │  Phase 2  Transcribe / 语音转录               │
    │    Download audio → faster-whisper (local)    │
    │    → ~5 min for 10-min video on CPU           │
    │                                              │
    │  Phase 3  AI Analysis / AI 分析               │
    │    OpenAI-compatible provider / 兼容接口      │
    │    → Structured Chinese research report       │
    │                                              │
    │  Phase 4  Save / 存档                         │
    │    YAML frontmatter + Markdown                │
    │    → Obsidian Clippings                       │
    └──────────────────────────────────────────────┘
```

---

## Output / 输出示例

```markdown
---
title: "食堂自救指南：水果拯救宿舍"
source: "https://www.bilibili.com/video/BV..."
date: "2026-05-07"
tags: [视频分析, AI报告]
---

## 概述
本视频以大学生宿舍生活为背景，系统论证了水果作为...

## 核心主题
### 🍎 为什么从流行病学角度必须吃水果
...

### 💪 吃水果的直接健康好处
...

## 关键洞察
1. 水果摄入不足的危害被严重低估
...

## 行动建议
...

## 金句摘录
> "水果作为可以直接购买，无需烹饪的营养压缩包..."
```

---

## Environment / 环境变量

```env
OPENAI_COMPATIBLE_API_KEY=sk-xxx        # Required
OPENAI_COMPATIBLE_BASE_URL=https://api.minimaxi.com/v1
OPENAI_COMPATIBLE_MODEL=MiniMax-M2.7-highspeed
PORT=3550                                # Optional
```

---

## Performance / 性能

| Phase | Time |
|-------|------|
| Extract | < 5s |
| Transcribe | 5–10 min |
| AI analysis | 1–3 min |
| **Total** | **8–15 min** |

---

## Architecture / 项目结构

```
server/
├── setup.sh              # One-command install
├── analyze-video.sh      # CLI script
├── index.js              # Express API (:3550)
└── lib/
    ├── bilibili.js       # B站 subtitle + DASH audio
    ├── youtube.js        # YouTube subtitle (yt-dlp)
    ├── transcribe.js     # Local faster-whisper STT
    ├── analyze.js        # MiniMax/OpenAI-compatible analysis
    └── prompt.js         # Structured prompt template
```

594 lines of JS. 3 npm dependencies. Zero frontend.

## Claude Code Skill

The `/av` slash command is at [`skills/vid2report/`](../../skills/vid2report/SKILL.md).

## License

GPL-3.0

# 🎬 vid2report

> 一键把 B 站 / YouTube 视频变成结构化中文研究报告：提取文案 → 语音转录 → AI 深度分析 → 存档 Obsidian。

| | |
|:---|:---|
| **版本** | `v1.0.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code`, `Codex` |
| **最近更新** | `2026-05-08` |

---

## Why

拿到一个 B 站 / YouTube 视频链接，想要的不是"看一遍"，而是一份能直接存档、引用、二次阅读的结构化研究报告。手动提取字幕、听音频、敲总结、写 Markdown 整套流程耗时数小时。**vid2report** 把这条流水线收成一个命令：视频链接进去，结构化报告（含概述、核心主题、关键洞察、行动建议、金句摘录）落到 Obsidian Clippings，全自动完成。

---

## Features

- **双平台** — B 站 API 提取字幕 + YouTube yt-dlp 拉取
- **本地转录** — 字幕不足 500 字时自动下载音频并用 faster-whisper 离线转录，音频不上云
- **AI 深度分析** — 兼容 OpenAI 接口的模型（MiniMax / DeepSeek / Moonshot / SiliconFlow）生成结构化中文报告
- **Obsidian 存档** — 输出含 YAML frontmatter 的 Markdown，自动写入 Obsidian Clippings
- **Express 后端** — 独立 :3550 服务，CLI / HTTP / Claude Code `/av` 三种触发方式

---

## Quickstart

```bash
# 1. 软链 skill 到 Claude Code / Codex
ln -s ~/42Marketplace/skills/vid2report ~/.claude/skills/vid2report
ln -s ~/42Marketplace/skills/vid2report ~/.codex/skills/vid2report

# 2. 启动后端服务（首次需安装依赖并配置 API key）
cd tools/vid2report/server
cp .env.example .env       # 填入 OPENAI_COMPATIBLE_API_KEY
npm install
npm start                  # 监听 :3550

# 3. 触发视频分析
/av https://www.bilibili.com/video/BVxxx
```

报告生成后，路径会回显到终端，Markdown 已落盘到 Obsidian Clippings 目录。

---

## Usage

### 视频分析

| 渠道 | 命令 |
|------|------|
| Claude Code / Codex | `/av https://www.bilibili.com/video/BVxxx` |
| CLI | `cd tools/vid2report/server && ./analyze-video.sh BVxxx` |
| HTTP | `curl -X POST :3550/api/save-transcript -d '{"videoConfig":{"videoId":"BVxxx","service":"bilibili"}}'` |

### Pipeline 耗时参考

| 阶段 | 说明 | 耗时 |
|------|------|------|
| Extract | 从 B 站 / YouTube API 获取字幕 | < 5s |
| Transcribe | 字幕不足 500 字时下载音频并用本地 Whisper 转录 | 5–10 min |
| Analyze | AI 生成结构化中文研究报告 | 1–3 min |
| Save | Markdown 写入 Obsidian Clippings | < 1s |

### 报告结构

输出 Markdown 固定包含五段：**概述 → 核心主题 → 关键洞察 → 行动建议 → 金句摘录**。金句摘录必须来自原始转录文本，body 不含 `<think>` 标签。

---

## 前置依赖

- **Node.js** ≥ 18（Express 后端）
- **ffmpeg** — 音频提取（Whisper 前置）
- **MiniMax API Key**（或任意 OpenAI 兼容服务：DeepSeek / Moonshot / SiliconFlow）
- **Obsidian Vault** — 用于存档 Clippings（如未配置可仅生成 Markdown 文件）

环境变量（写入 `tools/vid2report/server/.env`）：

```env
OPENAI_COMPATIBLE_API_KEY=sk-xxx         # Required
OPENAI_COMPATIBLE_BASE_URL=https://api.minimaxi.com/v1
OPENAI_COMPATIBLE_MODEL=MiniMax-M2.7-highspeed
PORT=3550                                 # Optional
```

---

## 更多文档

完整服务端文档、API 契约与项目结构见 [`tools/vid2report/README.md`](../../tools/vid2report/README.md)。

---

## License

MIT

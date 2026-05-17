# 🎬 vid2report

> 一键将 B站/YouTube 视频变为结构化研究报告：提取文案 → 语音转录 → AI 深度分析 → 存档 Obsidian

| | |
|:---|:---|
| **版本** | `v1.0.0` |
| **状态** | `stable` |
| **兼容** | `Claude Code` |
| **最近更新** | `2026-05-08` |

**一句话：**给一个 B站或 YouTube 链接，全自动提取文案、离线语音转录、AI 生成中文研究报告，并存入 Obsidian。

---

## 快速开始

```bash
# 1. 启动后端服务
cd tools/vid2report/server
./setup.sh your-api-key-here
npm start

# 2. 触发（在 Claude Code 对话中）
/av https://www.bilibili.com/video/BVxxx
```

---

## 特性

- **🎬 双平台** — B站 API 提取字幕 + YouTube yt-dlp 提取
- **🎙️ 本地转录** — faster-whisper 离线语音识别，不上传音频
- **🤖 AI 分析** — 兼容 OpenAI 接口（MiniMax / DeepSeek / Moonshot / SiliconFlow）
- **📝 结构化报告** — YAML frontmatter + Markdown，自动存入 Obsidian Clippings

---

## Pipeline

```
Video URL → Extract transcript → Transcribe (local Whisper) → AI analysis → Markdown → Obsidian
```

| 阶段 | 说明 | 耗时 |
|------|------|------|
| Extract | 从 B站/YouTube API 获取字幕 | < 5s |
| Transcribe | 字幕不足 500 字时，下载音频 → 本地 Whisper | 5-10 min |
| Analyze | AI 生成结构化中文研究报告 | 1-3 min |
| Save | Markdown 写入 Obsidian Clippings | < 1s |

---

## 使用方式

| 渠道 | 命令 |
|------|------|
| Claude Code | `/av https://www.bilibili.com/video/BVxxx` |
| CLI | `cd tools/vid2report/server && ./analyze-video.sh BVxxx` |
| HTTP | `curl -X POST :3550/api/save-transcript -d '{...}'` |

---

## 环境变量

```env
OPENAI_COMPATIBLE_API_KEY=sk-xxx        # Required
OPENAI_COMPATIBLE_BASE_URL=https://api.minimaxi.com/v1
OPENAI_COMPATIBLE_MODEL=MiniMax-M2.7-highspeed
PORT=3550                                # Optional
```

---

## 更多文档

完整服务端文档和项目结构见 [`tools/vid2report/README.md`](../../tools/vid2report/README.md)。

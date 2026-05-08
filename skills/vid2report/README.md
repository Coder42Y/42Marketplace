# 🎬 vid2report

> Turn any Bilibili or YouTube video into a structured research report — `/av <url>`

## Quick Install

```bash
cd tools/vid2report/server
./setup.sh your-api-key
npm start
```

## Usage

| Channel | Command |
|---------|---------|
| Claude Code | `/av https://www.bilibili.com/video/BVxxx` |
| CLI | `cd tools/vid2report/server && ./analyze-video.sh BVxxx` |
| HTTP | `curl -X POST :3550/api/save-transcript -d '{...}'` |

## Pipeline

`URL → Extract transcript → Transcribe audio (local Whisper) → AI analysis → Markdown → Obsidian`

Full docs：[`tools/vid2report/README.md`](../../tools/vid2report/README.md)

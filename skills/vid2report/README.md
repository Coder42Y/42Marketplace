# 🎬 vid2report

> Turn any Bilibili or YouTube video into a structured research report.

`/av <url>` — extract transcript, transcribe audio, AI deep analysis, save to Obsidian.

## Install

```bash
cd tools/vid2report
./setup.sh your-api-key
npm start
```

## Usage

| Channel | Command |
|---------|---------|
| Claude Code | `/av <video-url>` |
| CLI | `./tools/vid2report/bin/analyze-video.sh <url>` |
| HTTP | `POST :3550/api/save-transcript` |

See [`tools/vid2report/`](../../tools/vid2report/) for full docs.

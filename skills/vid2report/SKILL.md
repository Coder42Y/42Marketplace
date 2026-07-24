---
name: analyze-video
description: >-
  Use when the user provides a B站 or YouTube video link and wants it analyzed,
  summarized, transcribed, or archived. Full pipeline: extract → transcribe →
  AI deep analysis → structured report saved to Obsidian Clippings.
  触发词: "分析视频" "视频分析" "提取文案" "总结视频" "help me summarize" "analyze this video".
---

# Analyze Video

Run the full video analysis pipeline via the standalone server at `http://localhost:3550`.

## Workflow

1. Parse the user's URL → extract `videoId` and `service` (bilibili / youtube)
2. Ensure the server is running: check `GET http://localhost:3550/ping`. If not running, start it from the 42 Marketplace repo root: `cd tools/vid2report/server && npm start &`
3. Call the API (timeout 600s):
   ```
   curl -s -X POST http://localhost:3550/api/save-transcript \
     -H "Content-Type: application/json" \
     -d '{"videoConfig":{"videoId":"<ID>","service":"<SERVICE>"}}' \
     --max-time 600
   ```
4. Wait for the response (`{"success":true,"filepath":"...","analysisLength":...,...}`)
5. If successful, read the generated .md file from the returned `filepath`
6. Review the report: no `<think>` tags, quotes are from source, structure complete
7. Present summary to user: title, method (subtitle/transcription), transcript length, analysis length, file path, key findings preview

## Pipeline Stages

| Stage | What happens | Duration |
|-------|-------------|----------|
| Extract | Fetch subtitles from Bilibili/YouTube API | <5s |
| Transcribe | If subtitles <500 chars: download audio → local Whisper | 5-10min |
| Analyze | MiniMax AI generates structured report | 1-3min |
| Save | Markdown written to Obsidian Clippings | <1s |

## Quality Checks

After reading the report, verify:
- No `<think>` tags in body
- 金句摘录 quotes are actual sentences from the transcript
- Short transcript notes are present when applicable
- Structure: 概述 → 核心主题 → 关键洞察 → 行动建议 → 金句摘录

## Server Setup

```bash
cd server
cp .env.example .env    # fill in API key
npm install
npm start               # runs on :3550
```

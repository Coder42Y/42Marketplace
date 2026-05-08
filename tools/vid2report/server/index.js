require('dotenv').config()

const express = require('express')
const fs = require('fs')
const path = require('path')
const os = require('os')
const { analyzeTranscript } = require('./lib/analyze')
const { fetchBilibiliTranscript } = require('./lib/bilibili')
const { fetchYoutubeTranscript } = require('./lib/youtube')
const { transcribeVideo } = require('./lib/transcribe')

const app = express()
const PORT = process.env.PORT || 3550

const OUTPUT_DIR = path.join(os.homedir(), 'Library/Mobile Documents/iCloud~md~obsidian/Documents/Clippings')

app.use(express.json())

// ── Helpers ──────────────────────────────────────────────

function sanitizeFilename(title) {
  return title
    .replace(/[\\/:*?"<>|]/g, '-')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 60)
}

function formatTimestamp(seconds) {
  const s = Number(seconds) || 0
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = Math.floor(s % 60)
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
  return `${m}:${String(sec).padStart(2, '0')}`
}

function buildSourceText(transcript, hasTranscribed) {
  if (hasTranscribed) return typeof transcript === 'string' ? transcript : ''
  if (!Array.isArray(transcript)) return String(transcript || '')

  return transcript
    .sort((a, b) => (a.index || 0) - (b.index || 0))
    .map((item) => {
      const ts = item.s ? `[${formatTimestamp(item.s)}] ` : ''
      return `${ts}${item.text || ''}`
    })
    .join('\n\n')
}

function getSourceUrl(service, videoId) {
  if (service === 'youtube') return `https://www.youtube.com/watch?v=${videoId}`
  return `https://www.bilibili.com/video/${videoId}`
}

// ── API ──────────────────────────────────────────────────

app.post('/api/save-transcript', async (req, res) => {
  const { videoConfig } = req.body || {}
  if (!videoConfig?.videoId) {
    return res.status(400).json({ error: 'Missing videoConfig.videoId' })
  }

  const { service = 'bilibili', videoId } = videoConfig
  const sourceUrl = getSourceUrl(service, videoId)

  console.log(`\n[analyze] ========================================`)
  console.log(`[analyze] 视频: ${sourceUrl}`)

  try {
    // Phase 1: Extract transcript
    console.log(`[analyze] 阶段1: 提取文案...`)
    const { title, transcript, hasSubtitles } =
      service === 'youtube'
        ? await fetchYoutubeTranscript(videoId)
        : await fetchBilibiliTranscript(videoId)

    let fullTranscript = ''
    let hasTranscribed = false
    let finalTranscript = []

    if (transcript && transcript.length > 0) {
      fullTranscript = buildSourceText(transcript, false)
      if (fullTranscript.length < 500) {
        console.log(`[analyze] 字幕过短(${fullTranscript.length}字)，启动语音转录...`)
        try {
          fullTranscript = await transcribeVideo(service, videoId)
          hasTranscribed = true
        } catch (err) {
          console.log(`[analyze] 转录失败，使用短字幕: ${err.message}`)
          finalTranscript = transcript
        }
      } else {
        finalTranscript = transcript
      }
    } else {
      console.log(`[analyze] 无字幕，启动语音转录...`)
      try {
        fullTranscript = await transcribeVideo(service, videoId)
        hasTranscribed = true
      } catch (err) {
        return res.status(501).json({ error: `No subtitle and transcription failed: ${err.message}` })
      }
    }

    if (!hasTranscribed) {
      fullTranscript = buildSourceText(finalTranscript, false)
    }

    console.log(`[analyze] 文案长度: ${fullTranscript.length} 字符`)

    // Phase 2: AI deep analysis
    const analysisTranscript =
      fullTranscript.length > 4000
        ? fullTranscript.slice(0, 4000) + '\n\n[... 后续内容已截断]'
        : fullTranscript

    console.log(`[analyze] 阶段2: AI 深度分析 (传入${analysisTranscript.length}字)...`)
    const analysis = await analyzeTranscript(title || videoId, analysisTranscript, sourceUrl)
    console.log(`[analyze] 分析完成，长度: ${analysis.length} 字符`)

    // Phase 3: Build report
    const now = new Date()
    const dateStr = now.toISOString().split('T')[0]
    const videoTitle = title || videoId

    const markdown = `---
title: "${videoTitle}"
source: "${sourceUrl}"
service: "${service}"
videoId: "${videoId}"
date: "${dateStr}"
tags: [视频分析, AI报告]
---

# ${videoTitle}

> 来源: ${sourceUrl}
> 服务: ${service}
> 分析时间: ${now.toLocaleString('zh-CN')}
> 文案方式: ${hasTranscribed ? '语音转录' : '字幕抓取'}

---

${analysis}

---

## 原始文案

${hasTranscribed ? fullTranscript : buildSourceText(finalTranscript, false)}
`

    // Phase 4: Save
    console.log(`[analyze] 阶段3: 存档...`)
    fs.mkdirSync(OUTPUT_DIR, { recursive: true })
    const filename = `${sanitizeFilename(videoTitle)}-${dateStr}.md`
    const filepath = path.join(OUTPUT_DIR, filename)
    fs.writeFileSync(filepath, markdown, 'utf-8')

    console.log(`[analyze] ✅ 已保存: ${filepath}`)
    console.log(`[analyze] 📊 报告: ${analysis.length} 字符 | 文案: ${fullTranscript.length} 字符`)
    console.log(`[analyze] ========================================\n`)

    return res.json({
      success: true,
      filepath,
      filename,
      title: videoTitle,
      analysisLength: analysis.length,
      transcriptLength: fullTranscript.length,
      hasTranscribed,
    })
  } catch (err) {
    console.error(`[analyze] ❌ 失败: ${err.message}`)
    return res.status(500).json({ error: err.message || 'Internal Server Error' })
  }
})

// Health check
app.get('/ping', (_, res) => res.json({ ok: true }))

app.listen(PORT, () => {
  console.log(`🎬 视频分析服务 → http://localhost:${PORT}`)
  console.log(`   POST /api/save-transcript`)
  console.log(`   GET  /ping`)
})

/**
 * YouTube subtitle extraction via yt-dlp.
 */

const { exec } = require('child_process')
const { promisify } = require('util')
const fs = require('fs')
const path = require('path')
const os = require('os')
const execAsync = promisify(exec)

/**
 * Parse SRT format into subtitle items.
 */
function parseSRT(srtContent) {
  const items = []
  const blocks = srtContent.trim().split(/\n\s*\n/)
  for (const block of blocks) {
    const lines = block.trim().split('\n')
    if (lines.length < 3) continue
    // line[0] = index, line[1] = timestamp, line[2+] = text
    const text = lines.slice(2).join(' ').replace(/<[^>]+>/g, '').trim()
    if (!text) continue

    // Parse start timestamp
    const timeMatch = lines[1]?.match(/(\d+):(\d+):(\d+)[,.](\d+)/)
    const seconds = timeMatch
      ? Number(timeMatch[1]) * 3600 + Number(timeMatch[2]) * 60 + Number(timeMatch[3]) + Number(timeMatch[4]) / 1000
      : 0

    items.push({ index: items.length, text, s: seconds })
  }
  return items
}

/**
 * Fetch YouTube video metadata and subtitles via yt-dlp.
 * Tries auto-generated Chinese first, then English, then manual subs.
 */
async function fetchYoutubeTranscript(videoId) {
  const tmpDir = path.join(os.tmpdir(), 'vid2report_yt')
  fs.mkdirSync(tmpDir, { recursive: true })

  const url = `https://www.youtube.com/watch?v=${videoId}`
  const outputTmpl = path.join(tmpDir, videoId)

  // Step 1: Get video title
  let title = videoId
  try {
    const { stdout } = await execAsync(`yt-dlp --print title "${url}" 2>/dev/null`, { timeout: 15000 })
    title = stdout.trim() || videoId
  } catch (e) {
    console.log(`[youtube] Could not fetch title: ${e.message?.slice(0, 80)}`)
  }

  // Step 2: Download auto-generated subtitles (Chinese first, English fallback)
  let srtContent = ''
  for (const lang of ['zh-Hans', 'zh', 'en']) {
    try {
      await execAsync(
        `yt-dlp --write-auto-subs --sub-lang ${lang} --convert-subs srt --skip-download -o "${outputTmpl}" "${url}" 2>/dev/null`,
        { timeout: 30000 },
      )
      const srtPath = `${outputTmpl}.${lang}.srt`
      if (fs.existsSync(srtPath)) {
        srtContent = fs.readFileSync(srtPath, 'utf-8')
        try { fs.unlinkSync(srtPath) } catch {}
        break
      }
    } catch (e) {
      // Try next language
    }
  }

  // Step 3: Parse SRT
  if (srtContent) {
    const items = parseSRT(srtContent)
    if (items.length > 0) {
      console.log(`[youtube] Got ${items.length} subtitle items from auto-subs`)
      return { title, transcript: items, hasSubtitles: true }
    }
  }

  // Fallback: return title only, transcription will handle the rest
  console.log(`[youtube] No subtitles found, will rely on transcription`)
  return { title, transcript: [], hasSubtitles: false }
}

module.exports = { fetchYoutubeTranscript }

/**
 * Audio transcription via local faster-whisper.
 * Downloads audio from video (Bilibili API or yt-dlp) then
 * runs local Whisper for speech-to-text.
 */

const { exec } = require('child_process')
const { promisify } = require('util')
const fs = require('fs')
const path = require('path')
const os = require('os')
const execAsync = promisify(exec)

const { getBilibiliAudioUrl, downloadAudio } = require('./bilibili')

/**
 * Transcribe a video — download audio, run local Whisper.
 */
async function transcribeVideo(service, videoId) {
  const tmpDir = path.join(os.tmpdir(), 'biligpt_transcribe')
  fs.mkdirSync(tmpDir, { recursive: true })
  const outputPath = path.join(tmpDir, `biligpt_audio_${videoId}.mp3`)

  console.log(`[transcribe] Transcribing: ${service}:${videoId}`)

  try {
    if (service === 'bilibili') {
      const audioUrl = await getBilibiliAudioUrl(videoId)
      console.log(`[transcribe] Downloading Bilibili audio...`)
      await downloadAudio(audioUrl, outputPath)
    } else {
      console.log(`[transcribe] Using yt-dlp...`)
      const videoUrl =
        service === 'youtube'
          ? `https://www.youtube.com/watch?v=${videoId}`
          : `https://www.bilibili.com/video/${videoId}`

      await execAsync(`yt-dlp -x --audio-format mp3 -o "${outputPath}" "${videoUrl}"`, {
        timeout: 300_000,
        maxBuffer: 100 * 1024 * 1024,
      })
    }

    const stats = fs.statSync(outputPath)
    console.log(`[transcribe] Audio: ${(stats.size / 1024 / 1024).toFixed(1)}MB, transcribing...`)

    const text = await runWhisper(outputPath)
    console.log(`[transcribe] Success: ${text.length} chars`)

    try {
      fs.unlinkSync(outputPath)
    } catch {}

    return text
  } catch (err) {
    try {
      fs.unlinkSync(outputPath)
    } catch {}
    throw new Error(`Transcription failed: ${err.message}`)
  }
}

/**
 * Run local faster-whisper for speech recognition.
 */
async function runWhisper(audioPath) {
  const scriptPath = path.join(os.tmpdir(), 'biligpt_whisper.py')
  const script = `import sys
from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, _ = model.transcribe(sys.argv[1], language="zh", beam_size=5)
for seg in segments:
    print(f"[{seg.start:.1f}s] {seg.text.strip()}")
`
  fs.writeFileSync(scriptPath, script)

  console.log(`[transcribe] Running local Whisper (small, CPU)...`)
  const { stdout, stderr } = await execAsync(`python3 "${scriptPath}" "${audioPath}"`, {
    timeout: 600_000,
    maxBuffer: 10 * 1024 * 1024,
  })

  try {
    fs.unlinkSync(scriptPath)
  } catch {}

  const text = stdout.trim()
  if (!text) throw new Error('Empty transcription from local Whisper')
  return text
}

module.exports = { transcribeVideo }

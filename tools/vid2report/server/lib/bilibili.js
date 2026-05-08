/**
 * Bilibili subtitle and audio extraction.
 * Uses the public Bilibili API — no authentication required.
 */

const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
const REFERER = 'https://www.bilibili.com/'

/** Fetch subtitle URLs and metadata from Bilibili */
async function fetchBilibiliSubtitleUrls(videoId) {
  const params = videoId.startsWith('av') ? `aid=${videoId.slice(2)}` : `bvid=${videoId}`
  const url = `https://api.bilibili.com/x/web-interface/view?${params}`

  console.log(`[bilibili] Fetching ${url}`)
  const res = await fetch(url, {
    headers: { 'User-Agent': UA, Referer: REFERER },
  })
  const json = await res.json()

  const data = json?.data || {}
  return {
    title: data.title || '',
    desc: data.desc || '',
    dynamic: data.dynamic || '',
    subtitle: data.subtitle || null,
  }
}

/** Reduce subtitle timestamp format */
function reduceBilibiliSubtitleTimestamp(body, shouldShowTimestamp) {
  if (!Array.isArray(body)) return []
  return body.map((item, i) => ({
    index: i,
    text: item.content || '',
    s: shouldShowTimestamp ? (item.from || 0) : undefined,
  }))
}

/** Fetch and parse Bilibili subtitles */
async function fetchBilibiliSubtitle(videoId) {
  const { title, desc, dynamic, subtitle } = await fetchBilibiliSubtitleUrls(videoId)

  const descriptionText = desc || dynamic ? `${desc || ''} ${dynamic || ''}`.trim() : ''
  const subtitleList = subtitle?.list

  if (!subtitleList || subtitleList.length === 0) {
    return { title, subtitlesArray: null, descriptionText }
  }

  const betterSubtitle =
    subtitleList.find(({ lan }) => lan === 'zh-CN' || lan === 'ai-zh') || subtitleList[0]

  let subtitleUrl = betterSubtitle?.subtitle_url || ''
  if (subtitleUrl.startsWith('//')) subtitleUrl = 'https:' + subtitleUrl

  console.log(`[bilibili] Subtitle URL: ${subtitleUrl}`)

  const subRes = await fetch(subtitleUrl)
  const subtitles = await subRes.json()
  const transcripts = reduceBilibiliSubtitleTimestamp(subtitles?.body, true)

  return { title, subtitlesArray: transcripts, descriptionText }
}

/**
 * Get audio stream URL from Bilibili player API (DASH format).
 * Returns the highest quality audio URL.
 */
async function getBilibiliAudioUrl(videoId) {
  // Step 1: Get cid
  const params = videoId.startsWith('av') ? `aid=${videoId.slice(2)}` : `bvid=${videoId}`
  const infoUrl = `https://api.bilibili.com/x/web-interface/view?${params}`

  const infoRes = await fetch(infoUrl, {
    headers: { 'User-Agent': UA, Referer: REFERER },
  })
  const info = await infoRes.json()
  const cid = info?.data?.cid || info?.data?.pages?.[0]?.cid
  if (!cid) throw new Error('Cannot get Bilibili video cid')

  // Step 2: Get play URL (DASH format)
  const playUrl = `https://api.bilibili.com/x/player/wbi/playurl?bvid=${videoId}&cid=${cid}&fnval=16&fnver=0&fourk=1`
  const playRes = await fetch(playUrl, {
    headers: { 'User-Agent': UA, Referer: REFERER },
  })
  const play = await playRes.json()

  const audioStreams = play?.data?.dash?.audio
  if (!audioStreams || audioStreams.length === 0) {
    throw new Error('No audio stream in Bilibili video')
  }

  const bestAudio = audioStreams.sort((a, b) => (b.bandwidth || 0) - (a.bandwidth || 0))[0]
  const audioUrl = bestAudio?.baseUrl || bestAudio?.base_url || bestAudio?.url
  if (!audioUrl) throw new Error('Cannot extract audio URL from Bilibili')

  return audioUrl
}

/**
 * Download audio from a URL to a local file.
 */
async function downloadAudio(audioUrl, outputPath) {
  const res = await fetch(audioUrl, {
    headers: { 'User-Agent': UA, Referer: REFERER },
  })
  if (!res.ok) throw new Error(`Audio download failed: HTTP ${res.status}`)

  const buffer = Buffer.from(await res.arrayBuffer())
  const fs = require('fs')
  fs.mkdirSync(require('path').dirname(outputPath), { recursive: true })
  fs.writeFileSync(outputPath, buffer)
}

/**
 * Main entry: fetch full transcript for a Bilibili video.
 * Returns { title, transcript: subtitle array, hasSubtitles: boolean }
 */
async function fetchBilibiliTranscript(videoId) {
  const { title, subtitlesArray, descriptionText } = await fetchBilibiliSubtitle(videoId)

  if (subtitlesArray && subtitlesArray.length > 0) {
    return { title, transcript: subtitlesArray, hasSubtitles: true }
  }

  if (descriptionText) {
    return {
      title,
      transcript: [{ index: 0, text: descriptionText }],
      hasSubtitles: false,
    }
  }

  return { title: title || videoId, transcript: [], hasSubtitles: false }
}

module.exports = {
  fetchBilibiliTranscript,
  getBilibiliAudioUrl,
  downloadAudio,
  reduceBilibiliSubtitleTimestamp,
}

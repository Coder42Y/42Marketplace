/**
 * AI deep analysis of video transcripts.
 * Uses MiniMax (OpenAI-compatible) API via the Vercel AI SDK.
 */

const { createOpenAICompatible } = require('@ai-sdk/openai-compatible')
const { generateText } = require('ai')
const { buildPrompt } = require('./prompt')

/**
 * Analyze a video transcript and generate a structured report.
 */
async function analyzeTranscript(title, transcript, sourceUrl) {
  const apiKey = process.env.OPENAI_API_KEY || process.env.OPENAI_COMPATIBLE_API_KEY || ''
  if (!apiKey) throw new Error('Missing API key (set OPENAI_API_KEY or OPENAI_COMPATIBLE_API_KEY)')

  const baseUrl = (process.env.OPENAI_BASE_URL || process.env.OPENAI_COMPATIBLE_BASE_URL || 'https://api.openai.com/v1').replace(/\/+$/, '')
  const modelName = process.env.OPENAI_MODEL || process.env.OPENAI_COMPATIBLE_MODEL || 'gpt-3.5-turbo'

  const provider = createOpenAICompatible({
    baseURL: baseUrl,
    name: process.env.OPENAI_PROVIDER_NAME || 'openai-compatible',
    apiKey,
  })

  const prompt = buildPrompt(title, transcript, sourceUrl)

  const model = provider.chatModel(modelName)
  const result = await generateText({
    model,
    prompt,
    maxOutputTokens: 8000,
  })

  // Strip <think> reasoning blocks
  let text = result.text || ''
  text = text.replace(/<think>[\s\S]*?<\/think>/g, '').trim()
  return text
}

module.exports = { analyzeTranscript }

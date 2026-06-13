/**
 * 前端直连 AI API 服务
 * 绕过后端，浏览器直接调用 OpenAI 兼容 API
 * Author: shuhuNB560 / shuhuNB515
 */

const getSettings = () => {
  try {
    const saved = localStorage.getItem('app_settings')
    console.log('[directApi] localStorage app_settings:', saved ? 'found' : 'not found')
    if (saved) {
      const s = JSON.parse(saved)
      console.log('[directApi] settings keys:', Object.keys(s))
      console.log('[directApi] directApiEnabled:', s.directApiEnabled, 'hasKey:', !!s.directApiKey, 'hasUrl:', !!s.directBaseUrl)
      if (s.directApiEnabled && s.directApiKey && s.directBaseUrl) {
        return s
      }
    }
  } catch (e) {
    console.error('[directApi] getSettings error:', e)
  }
  return null
}

export const isDirectApiEnabled = () => {
  return !!getSettings()
}

/**
 * 调用 chat/completions
 */
export const chatCompletion = async (messages, options = {}) => {
  const settings = getSettings()
  if (!settings) throw new Error('API 直连未配置，请在设置中填写 API Key 和 Base URL')

  const { directApiKey, directChatModel } = settings
  const model = options.model || directChatModel || 'mimo-v2-flash'
  // 规范化 base URL: 去掉末尾斜杠
  const baseUrl = settings.directBaseUrl.replace(/\/+$/, '')

  console.log('[directApi] chatCompletion →', baseUrl, 'model:', model)

  const res = await fetch(`${baseUrl}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${directApiKey}`,
    },
    body: JSON.stringify({
      model,
      messages,
      max_tokens: options.maxTokens || 300,
      temperature: options.temperature || 0.7,
    }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    console.error('[directApi] chatCompletion failed:', res.status, err)
    throw new Error(err.error?.message || `API 错误 (${res.status})`)
  }

  const data = await res.json()
  console.log('[directApi] chatCompletion OK')
  return data.choices?.[0]?.message?.content || ''
}

/**
 * 调用 vision（带图片的对话）
 */
export const visionCompletion = async (text, imageBase64, visionContext = '') => {
  const settings = getSettings()
  if (!settings) throw new Error('API 直连未配置')

  const { directApiKey, directVisionModel } = settings
  const baseUrl = settings.directBaseUrl.replace(/\/+$/, '')
  const model = directVisionModel || 'mimo-v2-omni'
  console.log('[directApi] visionCompletion →', baseUrl, 'model:', model)

  const messages = [
    {
      role: 'system',
      content: 'You are MiMo, an AI assistant developed by Xiaomi. You can see the user\'s camera view. Please give natural, accurate and helpful replies based on visual content. Keep replies concise, usually no more than 3 sentences. Reply in Chinese.',
    },
  ]

  if (visionContext) {
    messages.push({ role: 'system', content: `[当前画面描述] ${visionContext}` })
  }

  messages.push({
    role: 'user',
    content: [
      { type: 'text', text: text },
      {
        type: 'image_url',
        image_url: { url: `data:image/jpeg;base64,${imageBase64}`, detail: 'low' },
      },
    ],
  })

  const res = await fetch(`${baseUrl}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${directApiKey}`,
    },
    body: JSON.stringify({
      model,
      messages,
      max_tokens: 300,
      temperature: 0.7,
    }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    console.error('[directApi] visionCompletion failed:', res.status, err)
    throw new Error(err.error?.message || `API 错误 (${res.status})`)
  }

  const data = await res.json()
  console.log('[directApi] visionCompletion OK')
  return data.choices?.[0]?.message?.content || ''
}

/**
 * 快捷视觉功能
 */
export const quickVision = async (imageBase64, action) => {
  const settings = getSettings()
  if (!settings) throw new Error('API 直连未配置')

  const { directApiKey, directVisionModel } = settings
  const baseUrl = settings.directBaseUrl.replace(/\/+$/, '')
  const model = directVisionModel || 'mimo-v2-omni'

  const prompts = {
    describe: '请简要描述画面内容。',
    ocr: '请识别画面中的所有文字。',
    objects: '请列出画面中的主要物体。',
    translate: '请将画面中的文字翻译成中文。',
    emotion: '请分析画面中人物的情绪。',
  }

  const messages = [
    {
      role: 'user',
      content: [
        { type: 'text', text: prompts[action] || prompts.describe },
        {
          type: 'image_url',
          image_url: { url: `data:image/jpeg;base64,${imageBase64}`, detail: 'low' },
        },
      ],
    },
  ]

  const res = await fetch(`${baseUrl}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${directApiKey}`,
    },
    body: JSON.stringify({ model, messages, max_tokens: 300 }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    console.error('[directApi] quickVision failed:', res.status, err)
    throw new Error(err.error?.message || `API 错误 (${res.status})`)
  }

  const data = await res.json()
  console.log('[directApi] quickVision OK')
  return data.choices?.[0]?.message?.content || ''
}

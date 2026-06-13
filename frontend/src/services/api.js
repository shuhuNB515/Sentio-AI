import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 创建会话
export function createSession() {
  return api.post('/session')
}

// 删除会话
export function deleteSession(sessionId) {
  return api.delete(`/session/${sessionId}`)
}

// 多模态对话（核心接口）
export function multimodalChat(sessionId, message, image = null, tts = false) {
  return api.post('/multimodal', {
    session_id: sessionId,
    message,
    image,
    tts,
  })
}

// 纯文本对话
export function textChat(sessionId, message) {
  return api.post('/chat', {
    session_id: sessionId,
    message,
  })
}

// 视觉分析
export function analyzeVision(sessionId, image, prompt) {
  return api.post('/vision', {
    session_id: sessionId,
    image,
    prompt,
  })
}

// 语音识别
export function speechToText(audioBlob) {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'audio.webm')
  return api.post('/stt', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 15000,
  })
}

// 语音合成
export function textToSpeech(text) {
  return api.post('/tts', { text }, { responseType: 'arraybuffer' })
}

// 用量统计
export function getStats() {
  return api.get('/stats')
}

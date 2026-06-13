import axios from 'axios'

const API_BASE = 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
})

// 请求拦截器 - 自动添加token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 处理401
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.hash = '#/login'
    }
    return Promise.reject(err)
  }
)

// ============ 认证 ============
export const authAPI = {
  register: (username, password) => api.post('/auth/register', { username, password }),
  login: (username, password) => api.post('/auth/login', { username, password }),
  getMe: () => api.get('/auth/me'),
  updateSettings: (data) => api.put('/auth/settings', data),
}

// ============ 会话 ============
export const conversationAPI = {
  create: (title) => api.post('/conversations', { title }),
  list: () => api.get('/conversations'),
  get: (id) => api.get(`/conversations/${id}`),
  update: (id, data) => api.put(`/conversations/${id}`, data),
  delete: (id) => api.delete(`/conversations/${id}`),
}

// ============ 对话 ============
export const chatAPI = {
  send: (sessionId, message, image) => api.post('/chat', { session_id: sessionId, message, image }),
  multimodal: (sessionId, message, image, tts) => api.post('/multimodal', { session_id: sessionId, message, image, tts }),
}

// ============ 快捷视觉 ============
export const visionAPI = {
  quick: (image, action, sessionId) => api.post('/vision/quick', { image, action, session_id: sessionId }),
}

// ============ 语音 ============
export const speechAPI = {
  stt: (audioBlob) => {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.wav')
    return api.post('/stt', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  tts: (text) => api.post('/tts', { text }, { responseType: 'arraybuffer' }),
}

// ============ 截图 ============
export const screenshotAPI = {
  save: (image, description, conversationId) => api.post('/screenshots', { image, description, conversation_id: conversationId }),
  list: () => api.get('/screenshots'),
}

// ============ 统计 ============
export const statsAPI = {
  get: () => api.get('/stats'),
}

export default api

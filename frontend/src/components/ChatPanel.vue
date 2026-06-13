<template>
  <div class="chat-panel">
    <!-- 消息列表 -->
    <div class="chat-messages" ref="messagesEl">
      <!-- 空状态 -->
      <div v-if="messages.length === 0 && !loading" class="empty-state">
        <div class="empty-visual">
          <div class="orbit">
            <div class="orbit-ring r1"><div class="orbit-dot"></div></div>
            <div class="orbit-ring r2"><div class="orbit-dot"></div></div>
            <div class="orbit-center">AI</div>
          </div>
        </div>
        <h3 class="empty-title">开始对话</h3>
        <p class="empty-desc">打开摄像头，语音或文字开始交流</p>
        <div class="empty-chips">
          <span class="chip">👁 视觉</span>
          <span class="chip">🎤 语音</span>
          <span class="chip">💬 文字</span>
        </div>
      </div>

      <!-- 消息列表 -->
      <TransitionGroup name="msg" tag="div" class="messages-list">
        <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
          <div class="msg-avatar" :class="msg.role === 'assistant' ? '' : 'is-user'">
            <template v-if="msg.role === 'assistant'">AI</template>
            <img v-else src="/avatar.png" alt="" />
          </div>
          <div class="msg-content">
            <div class="msg-header">
              <span class="msg-role">{{ msg.role === 'user' ? '你' : '视觉AI' }}</span>
              <span v-if="msg.has_image" class="msg-badge">📷 画面</span>
            </div>
            <!-- 图片预览 -->
            <img v-if="msg.imageDataUrl" :src="msg.imageDataUrl" class="msg-image" />
            <div class="msg-text">{{ msg.content }}</div>
          </div>
        </div>
      </TransitionGroup>

      <!-- 加载 -->
      <div v-if="loading" class="message assistant">
        <div class="msg-avatar">AI</div>
        <div class="msg-content">
          <div class="msg-header">
            <span class="msg-role">视觉AI</span>
          </div>
          <div class="thinking">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区 -->
    <div class="chat-input-area">
      <VoiceInput
        :disabled="loading || !sessionId"
        @transcript="onVoiceTranscript"
        @send-to-chat="(text) => sendMessage(text)"
      />
      <div class="text-input-row">
        <input
          v-model="inputText"
          @keyup.enter="sendMessage"
          :disabled="loading || !sessionId"
          :placeholder="sessionId ? '输入消息...' : '请先新建一个对话'"
          class="text-input"
        />
        <div class="input-actions">
          <button
            @click="toggleTTS"
            :class="['icon-btn', { active: enableTTS }]"
            :title="enableTTS ? '语音合成已开启' : '语音合成已关闭'"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
              <path v-if="enableTTS" d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
              <path v-if="enableTTS" d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
            </svg>
          </button>
          <button @click="sendMessage" :disabled="loading || !inputText.trim() || !sessionId" class="send-btn">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M1 8L15 1L8 15L7 9L1 8Z" fill="currentColor"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import { chatAPI, conversationAPI } from '../api'
import { isDirectApiEnabled, chatCompletion, visionCompletion } from '../services/directApi'
import VoiceInput from './VoiceInput.vue'

// 直连模式性能优化：记录上次调用时间，避免短时间重复请求
let lastDirectCall = 0
const DIRECT_CALL_COOLDOWN = 2000  // ms

const props = defineProps({
  sessionId: String,
  currentFrame: String,
  enableTTS: Boolean,
})

const emit = defineEmits(['toggle-tts', 'transcript'])

const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const messagesEl = ref(null)
const currentFrame = ref(props.currentFrame)  // 本地引用，可被外部方法修改

// 同步props.currentFrame到本地
watch(() => props.currentFrame, (val) => { if (val) currentFrame.value = val })

const userColor = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  return user.avatar_color || '#6366f1'
})

const toggleTTS = () => emit('toggle-tts')

const scrollToBottom = async () => {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

const sendMessage = async (overrideText = null) => {
  const text = (overrideText || inputText.value).trim()
  if (!text || !props.sessionId || loading.value) return

  messages.value.push({
    role: 'user',
    content: text,
    has_image: !!props.currentFrame,
    imageDataUrl: props.currentFrame ? `data:image/jpeg;base64,${props.currentFrame}` : null,
  })
  if (!overrideText) inputText.value = ''
  loading.value = true
  scrollToBottom()

  try {
    let reply

    // 优先使用前端直连 API
    if (isDirectApiEnabled()) {
      // 防抖：2秒内不重复发送
      const now = Date.now()
      if (now - lastDirectCall < DIRECT_CALL_COOLDOWN) return
      lastDirectCall = now

      if (props.currentFrame) {
        reply = await visionCompletion(text, props.currentFrame)
      } else {
        reply = await chatCompletion([{ role: 'user', content: text }])
      }
    } else {
      const res = await chatAPI.multimodal(
        props.sessionId,
        text,
        props.currentFrame,
        props.enableTTS
      )
      reply = res.data.reply

      // 播放TTS
      if (props.enableTTS && res.data.audio) {
        const audio = new Audio(`data:audio/mp3;base64,${res.data.audio}`)
        audio.play().catch(() => {})
      }
    }

    messages.value.push({ role: 'assistant', content: reply, has_image: false })
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: `错误: ${e.response?.data?.error || e.message}`,
      has_image: false
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// 发送图片消息（截图后调用）
const sendImageMessage = async (imageBase64, analysisText) => {
  if (!props.sessionId || loading.value) return

  // 用户消息：显示图片 + "请分析这张图片"
  const imageDataUrl = `data:image/jpeg;base64,${imageBase64}`
  messages.value.push({
    role: 'user',
    content: '📷 截图分析',
    has_image: true,
    imageDataUrl,
  })
  // AI回复：分析结果
  messages.value.push({
    role: 'assistant',
    content: analysisText || '分析完成',
    has_image: false,
  })
  scrollToBottom()

  // 同时设置currentFrame，让后续对话也能带上这张图
  currentFrame.value = imageBase64
}

const onVoiceTranscript = (text) => {
  emit('transcript', text)
  inputText.value = text
  sendMessage()
}

// 暴露方法给父组件
defineExpose({ sendMessage, sendImageMessage })

// 切换会话时加载历史消息
watch(() => props.sessionId, async (newId) => {
  messages.value = []
  if (!newId) return
  try {
    const res = await conversationAPI.get(newId)
    const history = res.data.messages || []
    messages.value = history.map(m => ({
      role: m.role,
      content: m.content,
      has_image: m.has_image || false,
      imageDataUrl: null,
    }))
    scrollToBottom()
  } catch (e) {
    console.warn('[Chat] 加载历史消息失败:', e)
  }
})

watch(messages, () => scrollToBottom(), { deep: true })
</script>

<style scoped>
.chat-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.chat-messages {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 72px;
  overflow-y: auto;
  padding: 16px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  gap: 16px;
  text-align: center;
}

.orbit {
  position: relative;
  width: 80px;
  height: 80px;
}

.orbit-ring {
  position: absolute;
  inset: 0;
  border: 1px dashed var(--border-primary);
  border-radius: 50%;
  animation: spin 8s linear infinite;
}

.orbit-ring.r2 {
  inset: 15px;
  animation-direction: reverse;
  animation-duration: 6s;
}

.orbit-dot {
  position: absolute;
  top: -3px;
  left: 50%;
  width: 6px;
  height: 6px;
  margin-left: -3px;
  background: var(--accent-primary);
  border-radius: 50%;
}

.orbit-center {
  position: absolute;
  inset: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-primary);
  border-radius: 50%;
  font-size: 14px;
  font-weight: 700;
  color: white;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.empty-chips {
  display: flex;
  gap: 8px;
}

.chip {
  padding: 4px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 20px;
  font-size: 12px;
  color: var(--text-secondary);
}

/* 消息 */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 10px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
  background: var(--accent-primary);
  overflow: hidden;
}
.msg-avatar.is-user {
  background: transparent;
  border: 1.5px solid var(--border-primary);
}
.msg-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.msg-content {
  flex: 1;
  min-width: 0;
}

.msg-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.msg-role {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.msg-badge {
  font-size: 10px;
  padding: 1px 6px;
  background: rgba(99,102,241,0.15);
  border-radius: 4px;
  color: var(--accent-primary);
}

.msg-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

/* 消息中的图片 */
.msg-image {
  max-width: 200px;
  max-height: 150px;
  border-radius: var(--radius-sm);
  object-fit: cover;
  border: 1px solid var(--border-primary);
  margin-bottom: 8px;
  cursor: pointer;
  transition: transform 0.2s ease;
}
.msg-image:hover {
  transform: scale(1.03);
}

.message.assistant .msg-text {
  background: var(--bg-tertiary);
  padding: 10px 14px;
  border-radius: 2px var(--radius-md) var(--radius-md) var(--radius-md);
  border: 1px solid var(--border-primary);
}

.message.user .msg-text {
  background: rgba(99,102,241,0.1);
  padding: 10px 14px;
  border-radius: var(--radius-md) 2px var(--radius-md) var(--radius-md);
  border: 1px solid rgba(99,102,241,0.2);
}

/* 思考动画 */
.thinking {
  display: flex;
  gap: 4px;
  padding: 12px 14px;
  background: var(--bg-tertiary);
  border-radius: 2px var(--radius-md) var(--radius-md) var(--radius-md);
  border: 1px solid var(--border-primary);
}

.thinking span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent-primary);
  animation: bounce 1.4s ease-in-out infinite;
}

.thinking span:nth-child(2) { animation-delay: 0.2s; }
.thinking span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* 消息过渡 */
.msg-enter-active { transition: all 0.3s ease; }
.msg-enter-from { opacity: 0; transform: translateY(10px); }

/* 输入区 */
.chat-input-area {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px;
  border-top: 1px solid var(--border-primary);
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  background: var(--bg-secondary);
  z-index: 5;
}

.text-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  padding: 4px 4px 4px 14px;
  transition: var(--transition);
  flex: 1;
}

.text-input-row:focus-within {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.text-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 14px;
  padding: 8px 0;
}

.text-input::placeholder {
  color: var(--text-muted);
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.icon-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 8px;
  border-radius: var(--radius-sm);
  transition: var(--transition);
}

.icon-btn:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.icon-btn.active {
  color: var(--accent-primary);
}

.send-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-primary);
  border: none;
  border-radius: var(--radius-sm);
  color: white;
  cursor: pointer;
  transition: var(--transition);
}

.send-btn:hover:not(:disabled) {
  background: #5558e6;
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ====== 响应式 ====== */
@media (max-width: 768px) {
  .chat-panel { position: relative; }
  .chat-messages { position: relative; bottom: auto; padding: 10px; }
  .chat-input-area { position: relative; padding: 8px 10px; }
  .messages-list { gap: 10px; }
  .msg-avatar { width: 28px; height: 28px; font-size: 10px; }
  .msg-image { max-width: 180px; }
  .msg-text { font-size: 13px; }
  .text-input { font-size: 13px; }
  .send-btn { min-width: 36px; height: 36px; }
  .icon-btn { padding: 6px; }
}
@media (max-width: 400px) {
  .chat-messages { padding: 8px; }
  .chat-input-area { padding: 6px 8px; }
  .msg-content { padding: 8px 10px; }
  .empty-title { font-size: 14px; }
  .empty-desc { font-size: 12px; }
}
</style>

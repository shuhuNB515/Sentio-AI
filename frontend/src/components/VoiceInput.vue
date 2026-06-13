<template>
  <div class="voice-input">
    <!-- 语音按钮 -->
    <button
      @click="toggleRecording"
      :class="['voice-btn', { recording: isRecording, processing: isProcessing, disabled }]"
      :disabled="disabled"
      :title="btnTitle"
    >
      <!-- 录音中：停止图标 -->
      <svg v-if="isRecording" class="mic-icon" width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
        <rect x="6" y="6" width="12" height="12" rx="2" />
      </svg>
      <!-- 处理中：旋转 -->
      <svg v-else-if="isProcessing" class="mic-icon spin" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <circle cx="12" cy="12" r="10" stroke-dasharray="30 60" stroke-linecap="round"/>
      </svg>
      <!-- 默认：麦克风 -->
      <svg v-else class="mic-icon" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        <line x1="12" y1="19" x2="12" y2="23"/>
        <line x1="8" y1="23" x2="16" y2="23"/>
      </svg>

      <span class="voice-label">{{ statusText }}</span>

      <!-- 录音中脉冲环 -->
      <span v-if="isRecording" class="pulse-ring"></span>
      <span v-if="isRecording" class="pulse-ring ring2"></span>
    </button>

    <!-- 取消按钮（识别中显示） -->
    <button
      v-if="isProcessing"
      @click="cancelProcessing"
      class="cancel-btn"
      title="取消识别"
    >
      ✕ 取消
    </button>

    <!-- 声波动画 -->
    <div v-if="isRecording" class="sound-wave">
      <span v-for="i in 7" :key="i" class="bar" :style="{ animationDelay: `${i * 0.08}s` }"></span>
    </div>

    <!-- 录音时长 -->
    <span v-if="isRecording" class="recording-time">{{ formatTime(recordTime) }}</span>

    <!-- 静音倒计时提示 -->
    <Transition name="fade">
      <span v-if="silenceCountdown > 0 && isRecording" class="silence-hint">
        {{ silenceCountdown }}秒后自动发送...
      </span>
    </Transition>

    <!-- 持续模式切换 -->
    <button
      v-if="!isRecording && !isProcessing"
      @click.stop="continuousMode = !continuousMode"
      :class="['mode-toggle', { active: continuousMode }]"
      title="持续对话模式"
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/>
        <polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>
      </svg>
    </button>

    <!-- 识别结果气泡 -->
    <Transition name="fade">
      <div v-if="transcript && !isProcessing" class="transcript-bubble">
        "{{ transcript }}"
      </div>
    </Transition>

    <!-- 错误提示 -->
    <Transition name="fade">
      <div v-if="errorMsg" class="error-bubble">{{ errorMsg }}</div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { speechAPI } from '../api'

const props = defineProps({ disabled: Boolean })
const emit = defineEmits(['transcript', 'error', 'send-to-chat'])

const isRecording = ref(false)
const isProcessing = ref(false)
const transcript = ref('')
const errorMsg = ref('')
const continuousMode = ref(false)  // 默认关闭持续对话，需要手动点击
let mediaRecorder = null
let audioChunks = []
let stream = null
let recordTimer = null
let recordTime = ref(0)
let silenceCountdown = ref(0)
let cancelled = false  // 取消标志

// 音量检测相关
let analyserNode = null
let volumeCheckInterval = null
let lastSoundTime = 0
const SILENCE_DURATION = 20  // 静音20秒后自动发送

const btnTitle = computed(() => {
  if (isRecording.value) return '点击停止录音'
  if (isProcessing.value) return '正在识别...'
  return '点击开始语音输入'
})

const statusText = computed(() => {
  if (isProcessing.value) return '识别中...'
  if (isRecording.value) return '点击停止'
  return '语音'
})

const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0')
  const s = (seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

// ========== 取消识别 ==========
const cancelProcessing = () => {
  cancelled = true
  isProcessing.value = false
  errorMsg.value = '已取消识别'
  setTimeout(() => { errorMsg.value = '' }, 2000)
}

// ========== 将webm音频转为WAV格式 ==========
const convertToWav = async (blob) => {
  const arrayBuffer = await blob.arrayBuffer()
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
  const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer)

  const targetSampleRate = 16000
  const offlineCtx = new OfflineAudioContext(1, Math.ceil(audioBuffer.duration * targetSampleRate), targetSampleRate)
  const source = offlineCtx.createBufferSource()
  source.buffer = audioBuffer
  source.connect(offlineCtx.destination)
  source.start(0)
  const resampled = await offlineCtx.startRendering()

  const numChannels = 1
  const sampleRate = resampled.sampleRate
  const data = resampled.getChannelData(0)
  const dataLength = data.length * numChannels * 2
  const buffer = new ArrayBuffer(44 + dataLength)
  const view = new DataView(buffer)

  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + dataLength, true)
  writeString(view, 8, 'WAVE')
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, numChannels, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * numChannels * 2, true)
  view.setUint16(32, numChannels * 2, true)
  view.setUint16(34, 16, true)
  writeString(view, 36, 'data')
  view.setUint32(40, dataLength, true)

  let offset = 44
  for (let i = 0; i < data.length; i++) {
    const s = Math.max(-1, Math.min(1, data[i]))
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true)
    offset += 2
  }

  audioCtx.close()
  return new Blob([buffer], { type: 'audio/wav' })
}

function writeString(view, offset, str) {
  for (let i = 0; i < str.length; i++) {
    view.setUint8(offset + i, str.charCodeAt(i))
  }
}

// ========== 音量检测 ==========
const startVolumeDetection = () => {
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    const source = audioCtx.createMediaStreamSource(stream)
    analyserNode = audioCtx.createAnalyser()
    analyserNode.fftSize = 512
    source.connect(analyserNode)

    lastSoundTime = Date.now()
    silenceCountdown.value = 0

    volumeCheckInterval = setInterval(() => {
      if (!analyserNode) return
      const dataArray = new Uint8Array(analyserNode.frequencyBinCount)
      analyserNode.getByteFrequencyData(dataArray)

      let sum = 0
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i]
      }
      const avg = sum / dataArray.length

      if (avg > 25) {
        lastSoundTime = Date.now()
        silenceCountdown.value = 0
      } else {
        const silentSec = Math.floor((Date.now() - lastSoundTime) / 1000)
        if (silentSec >= SILENCE_DURATION - 5) {
          silenceCountdown.value = SILENCE_DURATION - silentSec
        }
        if (silentSec >= SILENCE_DURATION && isRecording.value) {
          console.log('[Voice] 静音20秒，自动停止')
          stopRecording()
        }
      }
    }, 200)
  } catch (e) {
    console.warn('[Voice] 音量检测不可用:', e)
  }
}

const stopVolumeDetection = () => {
  if (volumeCheckInterval) {
    clearInterval(volumeCheckInterval)
    volumeCheckInterval = null
  }
  analyserNode = null
}

// ========== 录音控制 ==========
const toggleRecording = () => {
  if (isProcessing.value) return  // 识别中不允许操作
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = async () => {
  try {
    errorMsg.value = ''
    transcript.value = ''
    cancelled = false
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' })
    audioChunks = []

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data)
    }

    mediaRecorder.onstop = async () => {
      stopVolumeDetection()
      stream.getTracks().forEach(t => t.stop())
      clearInterval(recordTimer)

      if (cancelled) return

      if (audioChunks.length === 0) {
        errorMsg.value = '未录制到声音，请检查麦克风'
        return
      }

      const blob = new Blob(audioChunks, { type: 'audio/webm' })
      console.log(`[Voice] 录制完成: ${blob.size} bytes`)

      isProcessing.value = true
      try {
        await transcribe(blob)
      } catch (e) {
        if (!cancelled) {
          errorMsg.value = '识别出错，请重试'
        }
      }
      isProcessing.value = false
    }

    mediaRecorder.start(500)  // 每500ms收集一次数据
    isRecording.value = true

    recordTime.value = 0
    recordTimer = setInterval(() => { recordTime.value++ }, 1000)

    startVolumeDetection()
  } catch (err) {
    console.error('[Voice] 麦克风错误:', err)
    errorMsg.value = '无法访问麦克风，请检查权限设置'
  }
}

const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  isRecording.value = false
  silenceCountdown.value = 0
}

// ========== 语音识别 ==========
const transcribe = async (originalBlob) => {
  // 转WAV
  console.log('[Voice] 转换为WAV格式...')
  const wavBlob = await convertToWav(originalBlob)
  console.log(`[Voice] WAV大小: ${wavBlob.size} bytes`)

  if (cancelled) return

  // 发送到服务器，设置30秒超时
  console.log('[Voice] 发送到服务器识别...')
  const res = await speechAPI.stt(wavBlob)
  console.log('[Voice] 识别结果:', res.data)

  if (cancelled) return

  const text = (res.data.text || '').trim()

  if (text) {
    transcript.value = text
    emit('transcript', text)
    emit('send-to-chat', text)

    setTimeout(() => { transcript.value = '' }, 5000)

    // 持续对话模式
    if (continuousMode.value && !props.disabled) {
      setTimeout(async () => {
        if (!props.disabled && !cancelled) {
          console.log('[Voice] 持续模式 - 开始下一轮录音')
          await startRecording()
        }
      }, 800)
    }
  } else {
    errorMsg.value = '未能识别到文字内容'
    setTimeout(() => { errorMsg.value = '' }, 3000)

    if (continuousMode.value && !props.disabled) {
      setTimeout(async () => {
        if (!props.disabled && !cancelled) await startRecording()
      }, 1500)
    }
  }
}

onUnmounted(() => {
  stopVolumeDetection()
  if (recordTimer) clearInterval(recordTimer)
  if (isRecording.value) stopRecording()
  cancelled = true
})
</script>

<style scoped>
.voice-input {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

/* ====== 语音按钮 ====== */
.voice-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 22px;
  background: var(--bg-tertiary);
  border: 2px solid var(--border-primary);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
  min-height: 56px;
  white-space: nowrap;
}

.voice-btn:hover:not(.disabled):not(.processing) {
  border-color: var(--accent-primary);
  color: var(--text-primary);
  transform: scale(1.03);
  box-shadow: 0 0 20px rgba(167, 139, 250, 0.25);
}

.voice-btn.recording {
  border-color: #ef4444;
  color: #ef4444;
  background: rgba(239, 68, 68, 0.12);
  box-shadow: 0 0 30px rgba(239, 68, 68, 0.2);
  animation: breathe 2s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.15); }
  50% { box-shadow: 0 0 35px rgba(239, 68, 68, 0.35); }
}

.voice-btn.processing {
  border-color: #f59e0b;
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.12);
  cursor: wait;
}

.voice-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.mic-icon {
  flex-shrink: 0;
}
.mic-icon.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.voice-label {
  font-weight: 600;
}

/* 脉冲环 */
.pulse-ring {
  position: absolute;
  inset: -6px;
  border: 2px solid rgba(239, 68, 68, 0.5);
  border-radius: var(--radius-lg);
  animation: pulse-expand 1.5s ease-out infinite;
  pointer-events: none;
}
.ring2 {
  animation-delay: 0.75s;
}

@keyframes pulse-expand {
  0% { opacity: 0.8; transform: scale(1); }
  100% { opacity: 0; transform: scale(1.25); }
}

/* ====== 取消按钮 ====== */
.cancel-btn {
  padding: 8px 16px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-md);
  color: #ef4444;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}
.cancel-btn:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: #ef4444;
}

/* ====== 声波动画 ====== */
.sound-wave {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 32px;
  padding: 0 4px;
}

.bar {
  width: 4px;
  height: 6px;
  background: linear-gradient(to top, #ef4444, #f87171);
  border-radius: 2px;
  animation: wave-bounce 0.6s ease-in-out infinite;
}

@keyframes wave-bounce {
  0%, 100% { height: 6px; }
  50% { height: 26px; }
}

/* ====== 录音时长 ====== */
.recording-time {
  font-size: 16px;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #ef4444;
  padding: 4px 12px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: var(--radius-sm);
  letter-spacing: 1px;
}

/* ====== 静音倒计时 ====== */
.silence-hint {
  font-size: 11px;
  color: #f59e0b;
  padding: 3px 10px;
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: var(--radius-sm);
  font-weight: 600;
  animation: blink 1s ease infinite;
}

@keyframes blink {
  50% { opacity: 0.5; }
}

/* ====== 持续模式切换 ====== */
.mode-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}
.mode-toggle:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}
.mode-toggle.active {
  background: rgba(99, 102, 241, 0.15);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* ====== 结果气泡 ====== */
.transcript-bubble {
  padding: 8px 16px;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--accent-primary);
  font-style: italic;
  max-width: 300px;
}

.error-bubble {
  padding: 8px 16px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: var(--radius-md);
  font-size: 12px;
  color: var(--danger);
  max-width: 300px;
}

.fade-enter-active, .fade-leave-active { transition: all 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }

/* ====== 响应式 ====== */
@media (max-width: 768px) {
  .voice-btn { min-height: 44px; padding: 8px 14px; }
  .voice-btn .mic-icon { width: 22px; height: 22px; }
  .voice-label { font-size: 12px; }
  .recording-time { font-size: 13px; padding: 2px 8px; }
}
@media (max-width: 400px) {
  .voice-btn { min-height: 40px; padding: 6px 10px; }
  .voice-label { display: none; }
  .sound-wave { gap: 2px; height: 24px; }
  .bar { width: 3px; }
}
</style>

<template>
  <div class="creative-toolbar">
    <!-- 提示：需开启摄像头 -->
    <div v-if="!props.cameraActive" class="toolbar-hint">
      开启摄像头后可使用滤镜、语音命令和对比功能
    </div>

    <!-- ========== 1. 滤镜 ========== -->
    <div class="tool-group" :class="{ disabled: !props.cameraActive }">
      <span class="tool-label">滤镜</span>
      <div class="filter-list">
        <button
          v-for="f in filters"
          :key="f.name"
          :class="['filter-btn', { active: currentFilter === f.value }]"
          @click="applyFilter(f.value)"
          :title="f.name"
          :disabled="!props.cameraActive"
        >
          <span class="filter-dot" :style="{ filter: f.value }"></span>
          {{ f.name }}
        </button>
      </div>
    </div>

    <!-- ========== 2. 语音命令 ========== -->
    <div class="tool-group" :class="{ disabled: !props.cameraActive }">
      <button
        @click="toggleVoiceCommand"
        :class="['voice-cmd-btn', { active: voiceCmdActive, listening: isListening }]"
        :title="voiceCmdActive ? '语音命令已开启' : '开启语音命令'"
        :disabled="!props.cameraActive"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          <line x1="12" y1="19" x2="12" y2="23"/>
          <line x1="8" y1="23" x2="16" y2="23"/>
        </svg>
        语音命令{{ isListening ? ' 🟢' : voiceCmdActive ? ' ⏸' : '' }}
      </button>
      <span v-if="voiceCmdResult" class="cmd-result">{{ voiceCmdResult }}</span>
    </div>

    <!-- ========== 3. 前后对比 ========== -->
    <div class="tool-group" :class="{ disabled: !props.cameraActive }">
      <button
        v-if="!beforeImage"
        @click="captureBefore"
        class="compare-btn before"
        title="拍第一张照片"
        :disabled="!props.cameraActive"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/>
        </svg>
        拍前
      </button>
      <button
        v-if="beforeImage && !afterImage"
        @click="captureAfter"
        class="compare-btn after"
        title="拍第二张照片"
        :disabled="!props.cameraActive"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/>
        </svg>
        拍后
      </button>
      <button
        v-if="beforeImage && afterImage"
        @click="doCompare"
        :class="['compare-btn', 'do', { loading: compareLoading }]"
        :disabled="compareLoading"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        {{ compareLoading ? '分析中...' : '对比分析' }}
      </button>
      <button
        v-if="beforeImage"
        @click="resetCompare"
        class="compare-btn reset"
        title="重新对比"
      >
        ✕
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'

const props = defineProps({
  cameraActive: Boolean
})
const emit = defineEmits(['filter-change', 'voice-command', 'compare', 'capture-frame'])

const currentFilter = ref('')
const voiceCmdActive = ref(false)
const isListening = ref(false)
const voiceCmdResult = ref('')
const beforeImage = ref(null)
const afterImage = ref(null)
const compareLoading = ref(false)

let recognition = null

// ========== 滤镜 ==========
const filters = [
  { name: '无', value: '' },
  { name: '赛博', value: 'contrast(1.3) brightness(1.1) hue-rotate(30deg) saturate(1.5)' },
  { name: '复古', value: 'sepia(0.6) contrast(1.1) brightness(0.9)' },
  { name: '素描', value: 'grayscale(1) contrast(1.5) brightness(1.1)' },
  { name: '霓虹', value: 'contrast(1.4) saturate(2) hue-rotate(-10deg) brightness(1.1)' },
  { name: '黑白', value: 'grayscale(1) contrast(1.2)' },
  { name: '冷调', value: 'hue-rotate(200deg) saturate(0.8) brightness(1.1)' },
  { name: '暖调', value: 'hue-rotate(-30deg) saturate(1.3) brightness(1.1)' },
  { name: '反转', value: 'invert(1)' },
  { name: '模糊', value: 'blur(3px) brightness(1.1)' },
  { name: '锐化', value: 'contrast(1.5) brightness(1.1) saturate(0.5)' },
]

const applyFilter = (value) => {
  currentFilter.value = value
  emit('filter-change', value)
}

// ========== 语音命令 ==========
const toggleVoiceCommand = () => {
  if (voiceCmdActive.value) {
    stopVoiceCommand()
  } else {
    startVoiceCommand()
  }
}

const stopVoiceCommand = () => {
  voiceCmdActive.value = false
  isListening.value = false
  if (recognition) {
    recognition.stop()
    recognition = null
  }
}

const startVoiceCommand = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    voiceCmdResult.value = '当前浏览器不支持语音识别（请用Chrome/Edge）'
    setTimeout(() => { voiceCmdResult.value = '' }, 4000)
    return
  }

  try {
    recognition = new SpeechRecognition()
    recognition.lang = 'zh-CN'
    recognition.continuous = true
    recognition.interimResults = false
    recognition.maxAlternatives = 1

    recognition.onaudiostart = () => {
      isListening.value = true
      console.log('[VoiceCmd] 开始监听...')
    }

    recognition.onaudioend = () => {
      console.log('[VoiceCmd] 音频结束')
    }

    recognition.onresult = (event) => {
      let text = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        text += event.results[i][0].transcript
      }
      text = text.trim()
      if (!text) return
      console.log('[VoiceCmd] 识别:', text)

      // 关键词匹配（包含模糊匹配）
      const commands = [
        { kw: ['截图', '拍照', '照相', 'capture'], action: 'capture' },
        { kw: ['描述', '什么', '看', 'describe', 'what'], action: 'describe' },
        { kw: ['识别文字', '文字识别', 'ocr', '识字', '什么字', '写了什么'], action: 'ocr' },
        { kw: ['翻译', 'translate', '译'], action: 'translate' },
        { kw: ['物体', '识别物体', 'objects', '什么东西'], action: 'objects' },
      ]

      for (const cmd of commands) {
        for (const kw of cmd.kw) {
          if (text.toLowerCase().includes(kw.toLowerCase())) {
            voiceCmdResult.value = `听到: "${text}" → ${cmd.action}`
            emit('voice-command', cmd.action)
            setTimeout(() => { voiceCmdResult.value = '' }, 3000)
            return
          }
        }
      }

      voiceCmdResult.value = `"${text}" (未匹配，说"截图/描述/翻译/识别")`
      setTimeout(() => { voiceCmdResult.value = '' }, 3000)
    }

    recognition.onerror = (e) => {
      console.warn('[VoiceCmd] 错误:', e.error, e.message)
      if (e.error === 'no-speech' || e.error === 'aborted') {
        // 自动重启
        if (voiceCmdActive.value && recognition) {
          setTimeout(() => {
            try { recognition.start() } catch (_) {}
          }, 300)
        }
        return
      }
      if (e.error === 'not-allowed') {
        voiceCmdActive.value = false
        isListening.value = false
        voiceCmdResult.value = '请允许麦克风权限后重试'
        setTimeout(() => { voiceCmdResult.value = '' }, 4000)
        return
      }
      voiceCmdActive.value = false
      isListening.value = false
      voiceCmdResult.value = `语音命令出错: ${e.error}`
      setTimeout(() => { voiceCmdResult.value = '' }, 3000)
    }

    recognition.onend = () => {
      console.log('[VoiceCmd] 监听结束, 活跃:', voiceCmdActive.value)
      if (voiceCmdActive.value && recognition) {
        setTimeout(() => {
          try { recognition.start() } catch (_) {}
        }, 200)
      } else {
        isListening.value = false
      }
    }

    recognition.start()
    voiceCmdActive.value = true
    isListening.value = true
    voiceCmdResult.value = '正在听... 说"描述"/"截图"/"翻译"等'
    setTimeout(() => { voiceCmdResult.value = '' }, 2000)
  } catch (e) {
    console.error('[VoiceCmd] 启动失败:', e)
    voiceCmdResult.value = '无法启动语音命令，请使用下方语音按钮'
    setTimeout(() => { voiceCmdResult.value = '' }, 4000)
  }
}

// ========== 前后对比 ==========
const captureBefore = () => {
  emit('capture-frame', 'before')
}

const captureAfter = () => {
  emit('capture-frame', 'after')
}

const setBeforeImage = (frame) => {
  beforeImage.value = frame
}

const setAfterImage = (frame) => {
  afterImage.value = frame
}

const doCompare = () => {
  if (!beforeImage.value || !afterImage.value) return
  compareLoading.value = true
  emit('compare', { before: beforeImage.value, after: afterImage.value })
}

const setCompareLoading = (val) => {
  compareLoading.value = val
}

const resetCompare = () => {
  beforeImage.value = null
  afterImage.value = null
}

defineExpose({ setAfterImage, setBeforeImage, setCompareLoading, resetCompare })

onUnmounted(() => {
  stopVoiceCommand()
})
</script>

<style scoped>
.creative-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  background: rgba(15, 15, 25, 0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-primary);
  flex-shrink: 0;
  overflow-x: auto;
}

.tool-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.tool-group.disabled {
  opacity: 0.4;
  pointer-events: none;
}

.toolbar-hint {
  font-size: 12px;
  color: var(--text-muted);
  padding: 4px 0;
}

.tool-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* ====== 滤镜按钮 ====== */
.filter-list {
  display: flex;
  gap: 4px;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 8px;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.filter-btn:hover {
  border-color: var(--accent-primary);
  color: var(--text-primary);
}

.filter-btn.active {
  background: rgba(99, 102, 241, 0.2);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.filter-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #ffe66d);
}

/* ====== 语音命令按钮 ====== */
.voice-cmd-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.voice-cmd-btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.voice-cmd-btn.active {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  background: rgba(99, 102, 241, 0.15);
}

.voice-cmd-btn.listening {
  border-color: #10b981;
  color: #10b981;
  background: rgba(16, 185, 129, 0.12);
  animation: cmd-pulse 2s ease-in-out infinite;
}

@keyframes cmd-pulse {
  0%, 100% { box-shadow: 0 0 0px rgba(16, 185, 129, 0); }
  50% { box-shadow: 0 0 12px rgba(16, 185, 129, 0.3); }
}

.cmd-result {
  font-size: 11px;
  color: var(--accent-primary);
  padding: 2px 8px;
  background: rgba(99, 102, 241, 0.1);
  border-radius: var(--radius-sm);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ====== 对比按钮 ====== */
.compare-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.compare-btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.compare-btn.before {
  border-color: #3b82f6;
  color: #3b82f6;
}

.compare-btn.after {
  border-color: #f59e0b;
  color: #f59e0b;
}

.compare-btn.do {
  border-color: var(--accent-primary);
  background: rgba(99, 102, 241, 0.2);
  color: var(--accent-primary);
}

.compare-btn.loading {
  opacity: 0.6;
  cursor: wait;
}

.compare-btn.reset {
  border-color: var(--danger);
  color: var(--danger);
  padding: 6px 8px;
}

/* 分隔线 */
.tool-group:not(:last-child)::after {
  content: '';
  width: 1px;
  height: 20px;
  background: var(--border-primary);
  margin-left: 8px;
}
</style>

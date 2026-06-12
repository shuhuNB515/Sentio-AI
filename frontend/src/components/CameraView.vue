<template>
  <div class="camera-view">
    <div class="video-container" :class="{ active: cameraActive }">
      <video ref="videoEl" autoplay playsinline muted class="camera-video" :style="{ filter: props.filter }"></video>

      <!-- 扫描线 -->
      <div v-if="cameraActive" class="scan-line"></div>

      <!-- 四角装饰 -->
      <template v-if="cameraActive">
        <div class="corner tl"></div>
        <div class="corner tr"></div>
        <div class="corner bl"></div>
        <div class="corner br"></div>
      </template>

      <!-- 截图闪光效果 -->
      <div v-if="justCaptured" class="capture-flash"></div>

      <!-- 未开启占位 -->
      <div v-if="!cameraActive" class="camera-placeholder">
        <div class="placeholder-icon">
          <svg viewBox="0 0 80 80" width="80" height="80">
            <circle cx="40" cy="40" r="36" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="6 4" class="ring-anim"/>
            <circle cx="40" cy="40" r="24" fill="none" stroke="currentColor" stroke-width="1" opacity="0.5"/>
            <path d="M30 40 L36 46 L50 32" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <p class="placeholder-text">点击下方按钮开启摄像头</p>
        <div v-if="cameraError" class="camera-error">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          {{ cameraError }}
        </div>
      </div>

      <!-- 顶部状态 -->
      <div v-if="cameraActive" class="overlay-top">
        <div class="status-chip live">
          <span class="rec-dot"></span>
          直播
        </div>
        <div class="overlay-info-right">
          <span>640x480</span>
        </div>
      </div>

      <!-- 底部时间戳 -->
      <div v-if="cameraActive" class="overlay-bottom">
        <span class="timestamp">{{ currentTime }}</span>
      </div>
    </div>

    <!-- 控制按钮 -->
    <div class="camera-controls">
      <button @click="toggleCamera" :class="['ctrl-btn', cameraActive ? 'active' : '']">
        <svg v-if="!cameraActive" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
        </svg>
        <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18.36 6.64a9 9 0 1 1-12.73 0"/><line x1="12" y1="2" x2="12" y2="12"/>
        </svg>
        {{ cameraActive ? '停止' : '开启摄像头' }}
      </button>
      <button v-if="cameraActive" @click="captureAndSend(true)" class="ctrl-btn capture">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
          <circle cx="12" cy="13" r="4"/>
        </svg>
        截图
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, onMounted } from 'vue'

const props = defineProps({
  filter: { type: String, default: '' }
})
const emit = defineEmits(['frame-captured', 'camera-status', 'screenshot-taken'])

const videoEl = ref(null)
const cameraActive = ref(false)
const currentTime = ref('')
const justCaptured = ref(false)
const cameraError = ref('')
let stream = null
let frameInterval = null
let timeInterval = null

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', { hour12: false })
}

const toggleCamera = async () => {
  cameraError.value = ''
  if (cameraActive.value) {
    stopCamera()
  } else {
    await startCamera()
  }
}

const startCamera = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: 'user' }
    })
    if (videoEl.value) {
      videoEl.value.srcObject = stream
      // 等待视频就绪后立即抓取第一帧
      await new Promise(r => { videoEl.value.onloadedmetadata = r })
      await new Promise(r => setTimeout(r, 500))  // 等画面稳定
    }
    cameraActive.value = true
    emit('camera-status', true)
    captureAndSend()  // 立即抓取第一帧

    frameInterval = setInterval(() => captureAndSend(), 5000)
    timeInterval = setInterval(updateTime, 1000)
    updateTime()
  } catch (err) {
    console.error('Camera error:', err)
    cameraActive.value = false
    if (err.name === 'NotAllowedError') {
      cameraError.value = '摄像头权限被拒绝，请在浏览器设置中允许摄像头访问。如果是HTTP连接，请使用HTTPS访问（如 https://shuhuNB515.github.io/Sentio-AI/ ）'
    } else if (err.name === 'NotFoundError') {
      cameraError.value = '未检测到摄像头设备'
    } else {
      cameraError.value = '摄像头开启失败：' + (err.message || '未知错误') + '。请确保使用HTTPS连接。'
    }
  }
}

const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(t => t.stop())
    stream = null
  }
  cameraActive.value = false
  emit('camera-status', false)
  clearInterval(frameInterval)
  clearInterval(timeInterval)
}

const captureAndSend = (isManual = false) => {
  if (!videoEl.value || !cameraActive.value) return null
  const base64 = getCurrentFrame()
  if (!base64) return null
  emit('frame-captured', base64)

  // 手动截图时添加闪光效果和通知
  if (isManual) {
    justCaptured.value = true
    emit('screenshot-taken', base64)
    setTimeout(() => { justCaptured.value = false }, 500)
  }
  return base64
}

// 获取当前摄像头画面的base64（不触发emit）
const getCurrentFrame = () => {
  if (!videoEl.value || !cameraActive.value) return null
  const canvas = document.createElement('canvas')
  canvas.width = 640
  canvas.height = 480
  const ctx = canvas.getContext('2d')
  ctx.drawImage(videoEl.value, 0, 0, 640, 480)
  const dataUrl = canvas.toDataURL('image/jpeg', 0.7)
  return dataUrl.split(',')[1]
}

// 暴露给父组件
defineExpose({ getCurrentFrame, captureAndSend })

onUnmounted(() => {
  stopCamera()
})
</script>

<style scoped>
.camera-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.video-container {
  position: relative;
  flex: 1;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  overflow: hidden;
  margin: 12px;
  min-height: 0;
}

.video-container.active {
  border: 1px solid rgba(99,102,241,0.3);
}

.camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* 扫描线 */
.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(99,102,241,0.4), transparent);
  animation: scan 3s linear infinite;
  pointer-events: none;
}

@keyframes scan {
  0% { top: 0; }
  100% { top: 100%; }
}

/* 四角装饰 */
.corner {
  position: absolute;
  width: 20px;
  height: 20px;
  pointer-events: none;
}
.corner.tl { top: 8px; left: 8px; border-top: 2px solid var(--accent-primary); border-left: 2px solid var(--accent-primary); }
.corner.tr { top: 8px; right: 8px; border-top: 2px solid var(--accent-primary); border-right: 2px solid var(--accent-primary); }
.corner.bl { bottom: 8px; left: 8px; border-bottom: 2px solid var(--accent-primary); border-left: 2px solid var(--accent-primary); }
.corner.br { bottom: 8px; right: 8px; border-bottom: 2px solid var(--accent-primary); border-right: 2px solid var(--accent-primary); }

/* 占位 */
.camera-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--text-muted);
}

.placeholder-icon {
  opacity: 0.5;
}

.ring-anim {
  animation: rotate 20s linear infinite;
  transform-origin: center;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.placeholder-text {
  font-size: 13px;
  color: var(--text-muted);
}

.camera-error {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 8px;
  font-size: 11px;
  color: #fca5a5;
  text-align: left;
  line-height: 1.5;
}

/* 覆盖层 */
.overlay-top {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  pointer-events: none;
}

.status-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(239,68,68,0.9);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  color: white;
  letter-spacing: 1px;
}

.rec-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: white;
  animation: blink 1s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.overlay-info-right {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-family: 'JetBrains Mono', monospace;
}

.overlay-bottom {
  position: absolute;
  bottom: 12px;
  left: 12px;
  pointer-events: none;
}

.timestamp {
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  color: rgba(255,255,255,0.6);
  background: rgba(0,0,0,0.4);
  padding: 2px 6px;
  border-radius: 3px;
}

/* 截图闪光效果 */
.capture-flash {
  position: absolute;
  inset: 0;
  background: white;
  opacity: 0.8;
  animation: flash-out 0.5s ease-out forwards;
  pointer-events: none;
  z-index: 10;
}

@keyframes flash-out {
  from { opacity: 0.8; }
  to { opacity: 0; }
}

/* 控制按钮 */
.camera-controls {
  display: flex;
  gap: 8px;
  padding: 0 12px 12px;
}

.ctrl-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.ctrl-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--accent-primary);
}

.ctrl-btn.active {
  border-color: var(--danger);
  color: var(--danger);
}

.ctrl-btn.capture {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.ctrl-btn.capture:hover {
  background: rgba(99,102,241,0.1);
}

/* ====== 响应式 ====== */
@media (max-width: 768px) {
  .camera-view { height: auto; }
  .video-container { margin: 8px; border-radius: var(--radius-sm); }
  .camera-controls { padding: 0 8px 8px; gap: 6px; }
  .ctrl-btn { padding: 8px; font-size: 12px; }
  .overlay-top { top: 6px; left: 6px; right: 6px; }
  .overlay-bottom { bottom: 6px; left: 6px; }
  .status-chip { font-size: 10px; padding: 2px 8px; }
  .corner { width: 14px; height: 14px; }
}
</style>

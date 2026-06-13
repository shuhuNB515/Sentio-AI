<template>
  <div class="main-page">
    <!-- 背景图 + 雨滴效果 -->
    <div class="bg-layer">
      <img src="/bg.png" class="bg-image" alt="" />
      <div class="bg-overlay"></div>
      <RainEffect />
    </div>

    <!-- 侧边栏 -->
    <aside :class="['sidebar', { collapsed: sidebarCollapsed }]">
      <div class="sidebar-header">
        <div class="sidebar-logo" v-if="!sidebarCollapsed">
          <div class="logo-dot"></div>
          <span class="logo-name">Sentio-AI</span>
        </div>
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- 新建对话 -->
      <button class="new-chat-btn" @click="handleNewConversation">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        <span v-if="!sidebarCollapsed">新建对话</span>
      </button>

      <!-- 对话列表 -->
      <div class="conversation-list" v-if="!sidebarCollapsed">
        <div class="list-label">对话列表</div>
        <div
          v-for="conv in conversations"
          :key="conv.id"
          :class="['conv-item', { active: currentConvId === conv.id }]"
          @click="switchConversation(conv.id)"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <span class="conv-title">{{ conv.title }}</span>
          <button class="conv-delete" @click.stop="handleDeleteConv(conv.id)" title="删除">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div v-if="conversations.length === 0" class="empty-list">
          暂无对话
        </div>
      </div>

      <!-- 底部用户区 -->
      <div class="sidebar-footer">
        <div class="user-info" v-if="!sidebarCollapsed">
          <img class="user-avatar" src="/avatar.png" alt="头像" />
          <div class="user-detail">
            <span class="user-name">{{ user?.username }}</span>
          </div>
        </div>
        <button class="logout-btn" @click="handleLogout" :title="sidebarCollapsed ? '退出登录' : ''">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          <span v-if="!sidebarCollapsed">退出登录</span>
        </button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶栏 -->
      <header class="top-bar">
        <div class="top-bar-left">
          <h2 class="page-title">
            <span class="title-dot" :style="{ background: currentConvId ? 'var(--success)' : 'var(--text-muted)' }"></span>
            {{ currentConvTitle }}
          </h2>
        </div>
        <div class="top-bar-right">
          <div class="connection-status" :class="{ connected: backendConnected }">
            <span class="status-dot"></span>
            {{ backendConnected ? '已连接' : '离线' }}
          </div>
          <button class="icon-btn" @click="showSettings = true" title="设置">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
          </button>
        </div>
      </header>

      <!-- 创意工具栏 -->
      <CreativeToolbar
        ref="toolbarRef"
        :camera-active="cameraActive"
        @filter-change="onFilterChange"
        @voice-command="onVoiceCommand"
        @compare="onCompare"
        @capture-frame="onCaptureForToolbar"
      />

      <!-- 内容区 -->
      <div class="content-area">
        <!-- 左侧：视觉区 -->
        <section class="vision-section" :style="{ width: visionWidth + 'px' }">
          <CameraView
            ref="cameraRef"
            :filter="cameraVideoFilter"
            @frame-captured="onFrameCaptured"
            @camera-status="onCameraStatus"
            @screenshot-taken="onScreenshotTaken"
          />
          <!-- 快捷操作 -->
          <QuickActions
            :camera-active="cameraActive"
            :current-frame="currentFrame"
            :session-id="currentConvId"
            @action-result="onActionResult"
          />
        </section>

        <!-- 拖拽分隔条 -->
        <div
          class="resize-handle"
          @mousedown="startResize"
        >
          <div class="resize-line"></div>
        </div>

        <!-- 右侧：对话区 + 识别记录 -->
        <section class="chat-section">
          <!-- 标签切换 -->
          <div class="right-tabs">
            <button :class="['tab-btn', { active: rightTab === 'chat' }]" @click="rightTab = 'chat'">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              对话
            </button>
            <button :class="['tab-btn', { active: rightTab === 'recognition' }]" @click="rightTab = 'recognition'">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              识别记录
              <span v-if="recognitionCount > 0" class="tab-badge">{{ recognitionCount }}</span>
            </button>
          </div>

          <!-- 对话面板 -->
          <ChatPanel
            v-show="rightTab === 'chat'"
            ref="chatRef"
            :session-id="currentConvId"
            :current-frame="currentFrame"
            :enable-t-t-s="enableTTS"
            @toggle-tts="enableTTS = !enableTTS"
            @transcript="onVoiceTranscript"
          />

          <!-- 跨模态识别记录 -->
          <RecognitionPanel
            v-show="rightTab === 'recognition'"
            ref="recognitionRef"
            @send-to-chat="onSendToChat"
          />
        </section>
      </div>
    </div>

    <!-- 设置弹窗 -->
    <SettingsModal v-if="showSettings" @close="showSettings = false" @saved="onSettingsSaved" />

    <!-- Toast通知 -->
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div v-for="toast in toasts" :key="toast.id" :class="['toast', toast.type]">
          {{ toast.message }}
        </div>
      </TransitionGroup>
    </div>

    <!-- 确认弹窗 -->
    <ConfirmModal
      v-if="confirmInfo.show"
      :message="confirmInfo.message"
      @confirm="confirmInfo.onConfirm()"
      @cancel="confirmInfo.show = false"
    />

    <!-- 退出确认弹窗 -->
    <ConfirmModal
      v-if="logoutConfirm.show"
      :message="logoutConfirm.message"
      :image="logoutConfirm.image"
      @confirm="doLogout()"
      @cancel="logoutConfirm.show = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { conversationAPI, visionAPI } from '../api'
import CameraView from '../components/CameraView.vue'
import ChatPanel from '../components/ChatPanel.vue'
import QuickActions from '../components/QuickActions.vue'
import RecognitionPanel from '../components/RecognitionPanel.vue'
import SettingsModal from '../components/SettingsModal.vue'
import RainEffect from '../components/RainEffect.vue'
import CreativeToolbar from '../components/CreativeToolbar.vue'
import ConfirmModal from '../components/ConfirmModal.vue'

const router = useRouter()
const { state, logout, loadConversations, createConversation, deleteConversation, setCurrentConversation } = useAuth()

const sidebarCollapsed = ref(false)
const showSettings = ref(false)
const cameraActive = ref(false)
const currentFrame = ref(null)
const enableTTS = ref(true)
const backendConnected = ref(false)
const toasts = ref([])
const rightTab = ref('chat')  // 'chat' | 'recognition'
const cameraVideoFilter = ref('')  // 摄像头滤镜
const toolbarRef = ref(null)
const appSettings = ref({})  // 应用设置缓存

// ====== 设置回调 ======
const onSettingsSaved = (settings) => {
  appSettings.value = settings
  enableTTS.value = settings.ttsEnabled !== false
}

// ====== 拖拽调整大小 ======
const visionWidth = ref(0)  // 0 = 使用CSS默认
const isResizing = ref(false)

const startResize = (e) => {
  e.preventDefault()
  isResizing.value = true
  const startX = e.clientX
  const startWidth = e.target.closest('.content-area').querySelector('.vision-section').offsetWidth

  const onMouseMove = (ev) => {
    const delta = ev.clientX - startX
    const newWidth = Math.max(250, Math.min(startWidth + delta, window.innerWidth - 350))
    visionWidth.value = newWidth
  }

  const onMouseUp = () => {
    isResizing.value = false
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }

  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

const cameraRef = ref(null)
const chatRef = ref(null)
const recognitionRef = ref(null)

const user = computed(() => state.user)
const conversations = computed(() => state.conversations)
const currentConvId = computed(() => state.currentConversationId)
const currentConvTitle = computed(() => {
  const conv = conversations.value.find(c => c.id === currentConvId.value)
  return conv?.title || '选择或新建一个对话'
})

// 识别记录数量（用于标签角标）
const recognitionCount = computed(() => {
  return recognitionRef.value?.records?.length || 0
})

const addToast = (message, type = 'info') => {
  const id = Date.now()
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 3000)
}

const handleNewConversation = async () => {
  try {
    const id = await createConversation()
    addToast('新对话已创建', 'success')
  } catch (e) {
    addToast('创建对话失败', 'error')
  }
}

const switchConversation = (id) => {
  setCurrentConversation(id)
}

const confirmInfo = reactive({
  show: false,
  message: '',
  onConfirm: null,
})

const showConfirm = (message, onConfirm) => {
  confirmInfo.message = message
  confirmInfo.onConfirm = () => {
    onConfirm()
    confirmInfo.show = false
  }
  confirmInfo.show = true
}

const handleDeleteConv = async (id) => {
  showConfirm('确定要删除这个对话吗？此操作不可撤销。', async () => {
    try {
      await deleteConversation(id)
      addToast('对话已删除', 'success')
    } catch (e) {
      addToast('删除失败', 'error')
    }
  })
}

const handleLogout = () => {
  logoutConfirm.show = true
}

const logoutConfirm = reactive({
  show: false,
  message: '确定要退出登录吗？记得打钱！',
  image: '/pay.png',
})

const doLogout = () => {
  logoutConfirm.show = false
  logout()
  router.push('/login')
}

const onFrameCaptured = (frame) => {
  currentFrame.value = frame
}

const onCameraStatus = (active) => {
  cameraActive.value = active
}

const onActionResult = async (result) => {
  const isError = result.includes('错误')
  const actionType = isError ? null : result.split(':')[0]
  const content = result

  // 识别记录（保留一份）
  if (recognitionRef.value && !isError) {
    const typeMap = { '场景描述': 'describe', '文字识别': 'ocr', '物体识别': 'objects', '翻译': 'translate', '情绪分析': 'emotion' }
    recognitionRef.value.addRecord(typeMap[actionType] || 'vision', result, currentFrame.value ? `data:image/jpeg;base64,${currentFrame.value}` : null)
  }

  // 直接发送到AI对话，不再需要手动跳转
  if (!isError && chatRef.value && currentConvId.value) {
    const prefixMap = { '场景描述': '描述画面内容', '文字识别': '识别画面中的文字', '物体识别': '识别画面中的物体', '翻译': '翻译画面中的文字', '情绪分析': '分析画面情绪' }
    const prompt = prefixMap[actionType] || '分析画面内容'
    await chatRef.value.sendMessage(prompt)
    rightTab.value = 'chat'
  } else {
    rightTab.value = 'recognition'
  }

  addToast(result, isError ? 'error' : 'success')
}

// 截图后自动分析，结果发到对话框+识别记录
const onScreenshotTaken = async (frame) => {
  if (!currentConvId.value) return
  addToast('截图成功，正在分析...', 'info')
  try {
    const res = await visionAPI.quick(frame, 'describe', currentConvId.value)
    const text = res.data.result

    // 1. 发送到对话框（显示图片+AI分析）
    if (chatRef.value) {
      chatRef.value.sendImageMessage(frame, text)
      rightTab.value = 'chat'  // 切到对话标签
    }

    // 2. 同时添加到识别记录
    if (recognitionRef.value) {
      recognitionRef.value.addRecord('vision', text, `data:image/jpeg;base64,${frame}`)
    }
  } catch (e) {
    addToast('分析失败: ' + (e.response?.data?.error || e.message), 'error')
  }
}

// 语音识别回调
const onVoiceTranscript = (text) => {
  // 摄像头开启时，抓取最新画面用于语音识别
  if (cameraActive.value && cameraRef.value) {
    const latestFrame = cameraRef.value.getCurrentFrame()
    if (latestFrame) {
      currentFrame.value = latestFrame
    }
  }

  // 识别记录（保留一份）
  if (recognitionRef.value) {
    recognitionRef.value.addRecord('speech', text, currentFrame.value ? `data:image/jpeg;base64,${currentFrame.value}` : null)
  }

  // 直接发送到AI对话
  if (chatRef.value && currentConvId.value && text) {
    chatRef.value.sendMessage(text)
    rightTab.value = 'chat'
  }
}

// ====== 创意工具栏事件 ======
// 滤镜切换
const onFilterChange = (filter) => {
  cameraVideoFilter.value = filter
  console.log('[Filter] 切换滤镜:', filter)
}

// 语音命令
const onVoiceCommand = async (action) => {
  console.log('[VoiceCmd] 执行命令:', action)
  if (!cameraActive.value) {
    addToast('请先开启摄像头', 'error')
    return
  }

  // 没有对话时自动创建
  if (!currentConvId.value) {
    await handleNewConversation()
    if (!currentConvId.value) {
      addToast('请先新建对话', 'error')
      return
    }
  }

  // 抓取当前画面
  if (cameraRef.value) {
    const frame = cameraRef.value.getCurrentFrame()
    if (frame) currentFrame.value = frame
  }

  if (action === 'capture') {
    if (cameraRef.value) {
      cameraRef.value.captureAndSend(true)
    }
  } else {
    const actionMap = {
      'describe': '描述画面内容',
      'ocr': '识别画面中的文字',
      'translate': '翻译画面中的文字',
      'objects': '识别画面中的物体',
    }
    const prompt = actionMap[action] || action
    if (chatRef.value && currentConvId.value) {
      chatRef.value.sendMessage(prompt)
      rightTab.value = 'chat'
    }
  }
}

// 工具栏抓取画面
const onCaptureForToolbar = (mode) => {
  const frame = cameraRef.value?.getCurrentFrame()
  if (!frame || !toolbarRef.value) return

  if (mode === 'before') {
    toolbarRef.value.setBeforeImage(frame)
    addToast('已拍第一张照片', 'info')
  } else {
    toolbarRef.value.setAfterImage(frame)
    addToast('已拍第二张照片', 'info')
  }
}

// 前后对比
const onCompare = async ({ before, after }) => {
  if (!currentConvId.value) return
  addToast('正在分析两张图片的差异...', 'info')

  try {
    const res = await visionAPI.quick(before, 'describe', currentConvId.value)
    const res2 = await visionAPI.quick(after, 'describe', currentConvId.value)

    const comparePrompt = `请对比这两张图片的变化。第一张的描述：${res.data.result}；第二张的描述：${res2.data.result}。请分析两张图之间有什么不同和变化。`

    if (chatRef.value) {
      chatRef.value.sendImageMessage(after, comparePrompt)
      rightTab.value = 'chat'
    }

    // 同时添加到识别记录
    if (recognitionRef.value) {
      recognitionRef.value.addRecord('vision', `[前后对比]\n前：${res.data.result}\n后：${res2.data.result}`, `data:image/jpeg;base64,${after}`)
    }

    if (toolbarRef.value) {
      toolbarRef.value.setCompareLoading(false)
      toolbarRef.value.resetCompare()
    }
    addToast('对比分析完成', 'success')
  } catch (e) {
    addToast('对比分析失败', 'error')
    if (toolbarRef.value) {
      toolbarRef.value.setCompareLoading(false)
    }
  }
}

// 从识别记录发送到对话
const onSendToChat = (prefix, content, imageDataUrl) => {
  rightTab.value = 'chat'
  // 通过chatRef发送消息
  if (chatRef.value) {
    chatRef.value.sendMessage(prefix + content)
  }
}

// 检查后端连接
const checkBackend = async () => {
  try {
    const res = await fetch('http://localhost:5000/api/health')
    backendConnected.value = res.ok
  } catch {
    backendConnected.value = false
  }
}

onMounted(async () => {
  // 恢复本地设置缓存
  const saved = localStorage.getItem('app_settings')
  if (saved) {
    try { appSettings.value = JSON.parse(saved) } catch (_) {}
  }

  await loadConversations()
  checkBackend()
  setInterval(checkBackend, 15000)

  // 如果没有当前对话且列表有对话，自动选中第一个
  if (!currentConvId.value && conversations.value.length > 0) {
    setCurrentConversation(conversations.value[0].id)
  }
})
</script>

<style scoped>
.main-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  overflow: hidden;
  position: relative;
  background: transparent;
}

/* 背景层 */
.bg-layer {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.bg-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0.3) saturate(1.2);
}

.bg-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(20, 5, 40, 0.5) 0%, rgba(35, 12, 55, 0.45) 100%);
}

/* 侧边栏 */
.sidebar {
  width: 260px;
  background: rgba(15, 15, 25, 0.85);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--border-primary);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  flex-shrink: 0;
  position: relative;
  z-index: 2;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-primary);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--accent-primary);
  box-shadow: 0 0 8px var(--accent-glow);
}

.logo-name {
  font-size: 16px;
  font-weight: 700;
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.collapse-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px;
  border-radius: var(--radius-sm);
  transition: var(--transition);
}

.collapse-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.new-chat-btn {
  margin: 12px;
  padding: 10px 16px;
  background: var(--accent-primary);
  border: none;
  border-radius: var(--radius-md);
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  transition: var(--transition);
}

.new-chat-btn:hover {
  background: #5558e6;
  transform: translateY(-1px);
}

.sidebar.collapsed .new-chat-btn {
  padding: 10px;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.list-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 8px 8px 4px;
}

.conv-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-secondary);
  position: relative;
}

.conv-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.conv-item.active {
  background: rgba(99,102,241,0.15);
  color: var(--accent-primary);
}

.conv-title {
  flex: 1;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conv-delete {
  opacity: 0;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  transition: var(--transition);
}

.conv-item:hover .conv-delete {
  opacity: 1;
}

.conv-delete:hover {
  color: var(--danger);
  background: rgba(239,68,68,0.1);
}

.empty-list {
  padding: 20px;
  text-align: center;
  color: var(--text-muted);
  font-size: 12px;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--border-primary);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: var(--radius-sm);
}

.user-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border-primary);
  flex-shrink: 0;
}

.user-detail {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.user-plan {
  font-size: 11px;
  color: var(--text-muted);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: none;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: var(--transition);
  justify-content: center;
}

.logout-btn:hover {
  border-color: var(--danger);
  color: var(--danger);
  background: rgba(239,68,68,0.05);
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  z-index: 2;
}

.top-bar {
  height: 52px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-primary);
  background: rgba(15, 15, 25, 0.8);
  backdrop-filter: blur(12px);
  flex-shrink: 0;
}

.page-title {
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border-radius: 20px;
}

.connection-status.connected {
  color: var(--success);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
}

.connection-status.connected .status-dot {
  background: var(--success);
  box-shadow: 0 0 6px rgba(16,185,129,0.5);
}

.icon-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: var(--radius-sm);
  transition: var(--transition);
}

.icon-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* 内容区 */
.content-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.vision-section {
  min-width: 250px;
  display: flex;
  flex-direction: column;
  border-right: none;
  overflow-y: auto;
  flex-shrink: 0;
}

/* 拖拽分隔条 */
.resize-handle {
  width: 8px;
  cursor: col-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  z-index: 10;
}
.resize-handle:hover .resize-line,
.resize-handle:active .resize-line {
  background: var(--accent-primary);
  box-shadow: 0 0 8px var(--accent-glow);
}
.resize-line {
  width: 3px;
  height: 40px;
  background: var(--border-primary);
  border-radius: 2px;
  transition: all 0.2s ease;
}

.chat-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 300px;
}

/* 右侧标签切换 */
.right-tabs {
  display: flex;
  gap: 2px;
  padding: 8px 12px 0;
  background: var(--bg-secondary);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: var(--transition);
  position: relative;
}
.tab-btn:hover {
  color: var(--text-primary);
}
.tab-btn.active {
  color: var(--accent-primary);
  border-bottom-color: var(--accent-primary);
}
.tab-badge {
  padding: 1px 6px;
  background: var(--accent-primary);
  color: white;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 700;
}

/* Toast */
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toast {
  padding: 10px 18px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 500;
  animation: slideIn 0.3s ease;
  box-shadow: var(--shadow-md);
}

.toast.info { background: var(--info); color: white; }
.toast.success { background: var(--success); color: white; }
.toast.error { background: var(--danger); color: white; }

.toast-enter-active, .toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from { opacity: 0; transform: translateX(30px); }
.toast-leave-to { opacity: 0; transform: translateX(30px); }

@keyframes slideIn {
  from { opacity: 0; transform: translateX(30px); }
  to { opacity: 1; transform: translateX(0); }
}

/* ====== 平板 (768~1024px) ====== */
@media (min-width: 769px) and (max-width: 1024px) {
  .sidebar { width: 200px; }
  .sidebar.collapsed { width: 56px; }
  .vision-section { min-width: 220px; }
  .top-bar { padding: 0 16px; }
  .creative-toolbar { gap: 8px; padding: 6px 12px; }
  .creative-toolbar .filter-list { gap: 2px; }
  .creative-toolbar .filter-btn { padding: 4px 6px; font-size: 10px; }
}

/* ====== 手机 (< 768px) ====== */
@media (max-width: 768px) {
  .main-page {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
    height: auto;
    flex-direction: row;
    align-items: center;
    padding: 8px 12px;
    border-right: none;
    border-bottom: 1px solid var(--border-primary);
    gap: 8px;
    overflow-x: auto;
  }
  .sidebar-header { border-bottom: none; padding: 0; }
  .sidebar-logo { display: none; }
  .collapse-btn { display: none; }
  .sidebar .new-chat-btn { padding: 6px 10px; font-size: 11px; flex-shrink: 0; }
  .conversation-list { display: flex; gap: 6px; overflow-x: auto; padding: 0; }
  .conversation-list .list-label { display: none; }
  .conv-item { padding: 4px 10px; font-size: 11px; white-space: nowrap; flex-shrink: 0; border-radius: 20px; }
  .conv-item .conv-delete { display: none; }
  .sidebar-footer { flex-direction: row; gap: 8px; padding: 0; }
  .sidebar-footer .user-info { display: none; }
  .sidebar-footer .logout-btn { padding: 4px 8px; font-size: 11px; }

  .content-area { flex-direction: column; }
  .vision-section { width: 100% !important; height: 200px; min-width: 0; }
  .resize-handle { display: none; }
  .chat-section { min-width: 0; }

  .top-bar { padding: 0 10px; height: 44px; }
  .page-title { font-size: 12px; }
  .connection-status { display: none; }
  .top-bar-right .icon-btn { padding: 4px; }

  .creative-toolbar {
    flex-wrap: wrap;
    gap: 6px;
    padding: 6px 8px;
  }
  .creative-toolbar .tool-group::after { display: none; }
  .creative-toolbar .filter-btn { padding: 3px 5px; font-size: 10px; }
  .creative-toolbar .voice-cmd-btn { padding: 4px 8px; font-size: 10px; }
  .creative-toolbar .compare-btn { padding: 4px 8px; font-size: 10px; }

  .right-tabs { padding: 4px 8px; }
  .right-tabs .tab-btn { font-size: 11px; padding: 6px 10px; }
}

/* ====== 超小手机 (< 400px) ====== */
@media (max-width: 400px) {
  .vision-section { height: 160px; }
  .creative-toolbar .filter-list { flex-wrap: wrap; }
  .creative-toolbar { flex-wrap: wrap; }
  .chat-input-area { gap: 6px; padding: 8px 10px; }
  .text-input-row { gap: 4px; padding: 2px 2px 2px 8px; }
  .text-input { font-size: 13px; }
  .send-btn { padding: 8px; }
}
</style>

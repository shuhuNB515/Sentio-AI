<template>
  <div class="recognition-panel">
    <!-- 头部 -->
    <div class="panel-header">
      <div class="header-left">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2a10 10 0 1 0 10 10H12V2z"/>
          <path d="M12 2a10 10 0 0 1 10 10"/>
          <circle cx="12" cy="12" r="4"/>
        </svg>
        <span>跨模态识别</span>
        <span v-if="records.length" class="record-count">{{ records.length }}</span>
      </div>
      <button v-if="records.length" @click="clearAll" class="clear-btn" title="清空记录">清空</button>
    </div>

    <!-- 空状态 -->
    <div v-if="records.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <path d="M9 9h6v6H9z"/>
          <path d="M9 3v6M15 3v6M9 15v6M15 15v6M3 9h6M3 15h6M15 9h6M15 15h6"/>
        </svg>
      </div>
      <p>暂无识别记录</p>
      <p class="empty-hint">截图、语音或使用快捷操作后<br/>结果将显示在这里</p>
    </div>

    <!-- 记录列表 -->
    <TransitionGroup name="record" tag="div" class="records-list">
      <div
        v-for="(record, idx) in records"
        :key="record.id"
        :class="['record-item', record.type]"
      >
        <!-- 左侧：类型图标 + 时间 -->
        <div class="record-meta">
          <span class="type-icon">{{ getTypeIcon(record.type) }}</span>
          <span class="record-time">{{ formatTime(record.time) }}</span>
          <span class="type-label">{{ getTypeLabel(record.type) }}</span>
        </div>

        <!-- 中间：内容 -->
        <div class="record-content">
          <!-- 图片预览（如果有） -->
          <img v-if="record.image" :src="record.imageDataUrl" class="record-thumb" />
          <p class="record-text">{{ record.content }}</p>
        </div>

        <!-- 右侧：操作按钮 -->
        <div class="record-actions">
          <button
            @click="sendToChat(record)"
            class="action-btn send-to-chat"
            title="发送到对话"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
            发送
          </button>
          <button
            @click="removeRecord(idx)"
            class="action-btn delete-record"
            title="删除"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>
    </TransitionGroup>

    <!-- 确认弹窗 -->
    <ConfirmModal
      v-if="confirmShow"
      message="确定清空所有识别记录？"
      @confirm="doClear()"
      @cancel="confirmShow = false"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ConfirmModal from './ConfirmModal.vue'

const emit = defineEmits(['send-to-chat'])

// 识别记录
const records = ref([])

let idCounter = 0

const addRecord = (type, content, imageDataUrl = null) => {
  const record = {
    id: ++idCounter,
    type, // 'voice' | 'vision' | 'ocr' | 'objects' | 'translate' | 'emotion' | 'describe'
    content,
    image: !!imageDataUrl,
    imageDataUrl: imageDataUrl || null,
    time: Date.now(),
  }
  records.value.unshift(record)

  // 最多保存50条
  if (records.value.length > 50) {
    records.value.pop()
  }

  return record
}

const confirmShow = ref(false)

const removeRecord = (idx) => {
  records.value.splice(idx, 1)
}

const clearAll = () => {
  confirmShow.value = true
}

const doClear = () => {
  records.value = []
  confirmShow.value = false
}

const sendToChat = (record) => {
  const prefixMap = {
    voice: '[语音识别] ',
    vision: '[视觉分析] ',
    describe: '[场景描述] ',
    ocr: '[文字识别] ',
    objects: '[物体识别] ',
    translate: '[翻译] ',
    emotion: '[情绪分析] ',
  }
  emit('send-to-chat', prefixMap[record.type] || '', record.content, record.imageDataUrl)
}

const getTypeIcon = (type) => {
  const icons = { voice: '🎤', vision: '👁', describe: '👁', ocr: '📝', objects: '🔍', translate: '🌐', emotion: '😊' }
  return icons[type] || '📋'
}

const getTypeLabel = (type) => {
  const labels = { voice: '语音', vision: '视觉', describe: '描述', ocr: '文字', objects: '物体', translate: '翻译', emotion: '情绪' }
  return labels[type] || '识别'
}

const formatTime = (ts) => {
  const d = new Date(ts)
  return `${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}:${d.getSeconds().toString().padStart(2,'0')}`
}

// 暴露给父组件的方法
defineExpose({ addRecord })
</script>

<style scoped>
.recognition-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-primary);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-primary);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.record-count {
  padding: 1px 7px;
  background: var(--accent-primary);
  color: white;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
}

.clear-btn {
  padding: 3px 10px;
  font-size: 11px;
  color: var(--text-muted);
  background: transparent;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition);
}
.clear-btn:hover {
  color: var(--danger);
  border-color: var(--danger);
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  text-align: center;
  color: var(--text-muted);
}
.empty-icon {
  opacity: 0.3;
  margin-bottom: 12px;
}
.empty-state p {
  font-size: 13px;
  margin: 0;
}
.empty-hint {
  font-size: 11px !important;
  opacity: 0.6;
  margin-top: 6px !important;
  line-height: 1.5;
}

/* 记录列表 */
.records-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.record-item {
  display: flex;
  gap: 10px;
  padding: 10px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  margin-bottom: 6px;
  transition: var(--transition);
  animation: slideIn 0.25s ease-out;
}
.record-item:hover {
  border-color: var(--accent-primary);
  box-shadow: 0 2px 8px rgba(99,102,241,0.08);
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 元信息 */
.record-meta {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 50px;
}
.type-icon {
  font-size: 20px;
}
.record-time {
  font-size: 10px;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-muted);
}
.type-label {
  font-size: 10px;
  color: var(--text-muted);
  padding: 1px 5px;
  background: var(--bg-tertiary);
  border-radius: 3px;
}

/* 内容区 */
.record-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.record-thumb {
  max-width: 120px;
  max-height: 80px;
  border-radius: var(--radius-sm);
  object-fit: cover;
  border: 1px solid var(--border-primary);
}
.record-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 操作按钮 */
.record-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  justify-content: center;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  font-size: 11px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition);
  border: 1px solid transparent;
  white-space: nowrap;
}
.send-to-chat {
  color: var(--accent-primary);
  background: rgba(99,102,241,0.08);
  border-color: rgba(99,102,241,0.2);
}
.send-to-chat:hover {
  background: rgba(99,102,241,0.15);
}
.delete-record {
  color: var(--text-muted);
  background: transparent;
  border-color: var(--border-primary);
  padding: 4px 6px;
}
.delete-record:hover {
  color: var(--danger);
  border-color: var(--danger);
  background: rgba(239,68,68,0.06);
}

/* 动画 */
.record-enter-active { transition: all 0.3s ease; }
.record-leave-active { transition: all 0.2s ease; position: absolute; }
.record-enter-from { opacity: 0; transform: translateY(-10px); }
.record-leave-to { opacity: 0; transform: translateX(20px); }
.record-move { transition: transform 0.3s ease; }
</style>

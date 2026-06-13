<template>
  <div class="quick-actions">
    <div class="actions-label">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
      </svg>
      快捷视觉操作
    </div>
    <div class="actions-grid">
      <button
        v-for="action in actions"
        :key="action.id"
        :class="['action-btn', { loading: loadingAction === action.id, disabled: !cameraActive }]"
        :disabled="!cameraActive || !!loadingAction"
        @click="executeAction(action)"
      >
        <span class="action-icon">{{ action.icon }}</span>
        <span class="action-name">{{ action.name }}</span>
        <span v-if="loadingAction === action.id" class="action-spinner"></span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { visionAPI } from '../api'
import { isDirectApiEnabled, quickVision } from '../services/directApi'

const props = defineProps({
  cameraActive: Boolean,
  currentFrame: String,
  sessionId: String,
})

const emit = defineEmits(['action-result'])

const loadingAction = ref(null)

const actions = [
  { id: 'describe', name: '场景描述', icon: '👁', action: 'describe' },
  { id: 'ocr', name: '文字识别', icon: '📝', action: 'ocr' },
  { id: 'objects', name: '物体识别', icon: '🔍', action: 'objects' },
  { id: 'translate', name: '翻译', icon: '🌐', action: 'translate' },
  { id: 'emotion', name: '情绪分析', icon: '😊', action: 'emotion' },
]

const executeAction = async (action) => {
  if (!props.currentFrame || !props.cameraActive) return
  loadingAction.value = action.id
  try {
    let result
    if (isDirectApiEnabled()) {
      result = await quickVision(props.currentFrame, action.action)
    } else {
      const res = await visionAPI.quick(props.currentFrame, action.action, props.sessionId)
      result = res.data.result
    }
    emit('action-result', `${action.name}: ${result}`)
  } catch (e) {
    emit('action-result', `错误: ${e.message}`)
  } finally {
    loadingAction.value = null
  }
}
</script>

<style scoped>
.quick-actions {
  padding: 0 12px 12px;
}

.actions-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
  padding-left: 4px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 4px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition);
  position: relative;
}

.action-btn:hover:not(.disabled) {
  background: var(--bg-hover);
  border-color: var(--accent-primary);
  color: var(--text-primary);
  transform: translateY(-1px);
}

.action-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.action-btn.loading {
  border-color: var(--accent-primary);
  background: rgba(99,102,241,0.1);
}

.action-icon {
  font-size: 18px;
}

.action-name {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.action-spinner {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 10px;
  height: 10px;
  border: 1.5px solid rgba(99,102,241,0.3);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .actions-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>

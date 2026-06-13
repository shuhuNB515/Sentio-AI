<template>
  <div class="status-bar">
    <div class="status-group">
      <div class="status-item">
        <span :class="['status-led', connected ? 'on' : 'off']"></span>
        <span class="status-label">{{ connected ? 'Connected' : 'Offline' }}</span>
      </div>
      <div class="status-divider"></div>
      <div class="status-item" v-if="sessionId">
        <span class="status-label mono">SID:{{ sessionId.substring(0, 6) }}</span>
      </div>
      <div class="status-divider"></div>
      <div class="status-item">
        <span class="status-label">Frame: {{ frameInterval }}s</span>
      </div>
      <div class="status-divider"></div>
      <div class="status-item">
        <span class="status-label">Calls: {{ totalCalls }}</span>
        <span v-if="stats.cache_hits > 0" class="cache-badge">{{ stats.cache_hits }} cached</span>
      </div>
    </div>

    <div class="status-actions">
      <button @click="$emit('toggle-tts')" :class="['action-btn', ttsEnabled ? 'active' : '']">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
          <path v-if="ttsEnabled" d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
          <path v-if="ttsEnabled" d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
        </svg>
        <span>{{ ttsEnabled ? 'ON' : 'OFF' }}</span>
      </button>
      <button @click="$emit('new-session')" class="action-btn">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 2v6h-6"/>
          <path d="M3 12a9 9 0 0 1 15-6.7L21 8"/>
          <path d="M3 22v-6h6"/>
          <path d="M21 12a9 9 0 0 1-15 6.7L3 16"/>
        </svg>
        <span>New</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getStats } from '../services/api'

defineProps({
  connected: { type: Boolean, default: false },
  sessionId: { type: String, default: '' },
  frameInterval: { type: Number, default: 5 },
  ttsEnabled: { type: Boolean, default: true },
})

defineEmits(['toggle-tts', 'new-session'])

const stats = ref({
  vision_calls: 0,
  chat_calls: 0,
  stt_calls: 0,
  tts_calls: 0,
  cache_hits: 0,
})

const totalCalls = computed(() =>
  stats.value.vision_calls + stats.value.chat_calls + stats.value.stt_calls + stats.value.tts_calls
)

async function refreshStats() {
  try {
    const response = await getStats()
    stats.value = response.data
  } catch {}
}

onMounted(() => {
  refreshStats()
  setInterval(refreshStats, 10000)
})
</script>

<style scoped>
.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: var(--bg-card, rgba(17, 24, 39, 0.7));
  border: 1px solid var(--border-color, rgba(99, 102, 241, 0.2));
  border-radius: 10px;
  backdrop-filter: blur(10px);
  gap: 12px;
  flex-wrap: wrap;
}

.status-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-led {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  transition: all 0.3s;
}

.status-led.on {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
}

.status-led.off {
  background: #64748b;
}

.status-label {
  font-size: 11px;
  color: var(--text-secondary, #94a3b8);
  letter-spacing: 0.3px;
}

.status-label.mono {
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-muted, #64748b);
}

.status-divider {
  width: 1px;
  height: 14px;
  background: var(--border-color, rgba(99, 102, 241, 0.2));
}

.cache-badge {
  padding: 1px 8px;
  border-radius: 8px;
  font-size: 10px;
  background: rgba(99, 102, 241, 0.1);
  color: var(--accent-light, #818cf8);
  border: 1px solid rgba(99, 102, 241, 0.15);
}

.status-actions {
  display: flex;
  gap: 6px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border: 1px solid var(--border-color, rgba(99, 102, 241, 0.2));
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary, #94a3b8);
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 0.5px;
}

.action-btn:hover {
  border-color: var(--accent, #6366f1);
  color: var(--text-primary, #f1f5f9);
}

.action-btn.active {
  background: rgba(99, 102, 241, 0.15);
  border-color: var(--accent, #6366f1);
  color: var(--accent-light, #818cf8);
}
</style>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>设置</h2>
        <button class="close-btn" @click="$emit('close')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <!-- 视觉设置 -->
        <div class="settings-section">
          <h3 class="section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            视觉
          </h3>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">帧采样间隔</span>
              <span class="setting-desc">多久捕获一帧（秒）</span>
            </div>
            <div class="setting-control">
              <input type="range" v-model.number="settings.frameInterval" min="2" max="30" step="1" class="slider" />
              <span class="slider-value">{{ settings.frameInterval }}秒</span>
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">图像质量</span>
              <span class="setting-desc">摄像头帧的压缩质量</span>
            </div>
            <div class="setting-control">
              <input type="range" v-model.number="settings.imageQuality" min="30" max="100" step="10" class="slider" />
              <span class="slider-value">{{ settings.imageQuality }}%</span>
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">摄像头分辨率</span>
            </div>
            <select v-model="settings.cameraResolution" class="select-input">
              <option value="640x480">640×480</option>
              <option value="1280x720">1280×720 (HD)</option>
              <option value="1920x1080">1920×1080 (Full HD)</option>
            </select>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">低细节模式</span>
              <span class="setting-desc">视觉API调用使用低细节，节省成本</span>
            </div>
            <label class="toggle">
              <input type="checkbox" v-model="settings.lowDetail" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <!-- 语音设置 -->
        <div class="settings-section">
          <h3 class="section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
              <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
            </svg>
            语音
          </h3>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">语音合成（TTS）</span>
              <span class="setting-desc">AI朗读回复内容</span>
            </div>
            <label class="toggle">
              <input type="checkbox" v-model="settings.ttsEnabled" />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">TTS语音风格</span>
              <span class="setting-desc">语音合成的声音</span>
            </div>
            <select v-model="settings.ttsVoice" class="select-input">
              <option value="alloy">Alloy (中性)</option>
              <option value="echo">Echo (男声)</option>
              <option value="fable">Fable (英音)</option>
              <option value="onyx">Onyx (深沉)</option>
              <option value="nova">Nova (女声)</option>
              <option value="shimmer">Shimmer (柔和)</option>
              <option value="mimo_default">MiMo默认</option>
            </select>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">静音自动停止</span>
              <span class="setting-desc">静音多少秒后自动停止录音</span>
            </div>
            <div class="setting-control">
              <input type="range" v-model.number="settings.silenceDuration" min="5" max="30" step="5" class="slider" />
              <span class="slider-value">{{ settings.silenceDuration }}秒</span>
            </div>
          </div>
        </div>

        <!-- 对话设置 -->
        <div class="settings-section">
          <h3 class="section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            对话
          </h3>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">AI模型</span>
              <span class="setting-desc">选择对话使用的模型</span>
            </div>
            <select v-model="settings.chatModel" class="select-input">
              <option value="mimo-v2-flash">MiMo Flash (快速)</option>
              <option value="mimo-v2-omni">MiMo Omni (全能)</option>
            </select>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">最大历史条数</span>
              <span class="setting-desc">每次发送给AI的上下文消息数</span>
            </div>
            <div class="setting-control">
              <input type="range" v-model.number="settings.maxHistory" min="2" max="20" step="2" class="slider" />
              <span class="slider-value">{{ settings.maxHistory }}</span>
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">缓存结果</span>
              <span class="setting-desc">缓存相似帧的分析结果</span>
            </div>
            <label class="toggle">
              <input type="checkbox" v-model="settings.cacheEnabled" />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">持续对话模式</span>
              <span class="setting-desc">语音识别后自动开始下一轮</span>
            </div>
            <label class="toggle">
              <input type="checkbox" v-model="settings.continuousMode" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <!-- 快捷键提示 -->
        <div class="settings-section">
          <h3 class="section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 10 4 15 9 20"/><path d="M20 4v7a4 4 0 0 1-4 4H4"/>
            </svg>
            快捷操作
          </h3>
          <div class="shortcut-list">
            <div class="shortcut-item"><kbd>Enter</kbd><span>发送消息</span></div>
            <div class="shortcut-item"><kbd>语音命令</kbd><span>说"截图/描述/翻译/识别"自动执行</span></div>
            <div class="shortcut-item"><kbd>滤镜</kbd><span>实时叠加赛博/复古/素描等效果</span></div>
            <div class="shortcut-item"><kbd>前后对比</kbd><span>拍两张照片 → AI分析变化</span></div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="$emit('close')">取消</button>
        <button class="btn-primary" @click="saveSettings">保存设置</button>
      </div>

      <!-- 保存成功提示 -->
      <Transition name="fade">
        <div v-if="saved" class="save-toast">设置已保存</div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { authAPI } from '../api'

const emit = defineEmits(['close', 'saved'])

const saved = ref(false)

const defaultSettings = {
  frameInterval: 5,
  imageQuality: 70,
  cameraResolution: '640x480',
  ttsEnabled: true,
  ttsVoice: 'alloy',
  lowDetail: true,
  cacheEnabled: true,
  maxHistory: 10,
  silenceDuration: 20,
  continuousMode: false,
  chatModel: 'mimo-v2-flash',
}

const settings = reactive({ ...defaultSettings })

// 从后端加载已保存的设置
onMounted(async () => {
  try {
    const res = await authAPI.getMe()
    if (res.data?.settings) {
      let saved = typeof res.data.settings === 'string'
        ? JSON.parse(res.data.settings)
        : res.data.settings
      // 兼容旧格式：如果多了层settings嵌套，解出来
      if (saved.settings && typeof saved.settings === 'object') {
        saved = saved.settings
      }
      // 合并，用后端值覆盖默认值
      Object.keys(defaultSettings).forEach(key => {
        if (saved[key] !== undefined) {
          settings[key] = saved[key]
        }
      })
    }
  } catch (e) {
    console.warn('加载设置失败，使用默认值', e)
  }
})

const saveSettings = async () => {
  try {
    await authAPI.updateSettings({ settings: { ...settings } })
    // 保存到localStorage供其他组件读取
    localStorage.setItem('app_settings', JSON.stringify({ ...settings }))
    saved.value = true
    emit('saved', { ...settings })
    setTimeout(() => {
      saved.value = false
      emit('close')
    }, 800)
  } catch (e) {
    console.error('保存设置失败', e)
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 540px;
  max-width: 95vw;
  max-height: 85vh;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-lg);
  position: relative;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-primary);
}

.modal-header h2 {
  font-size: 16px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  transition: var(--transition);
}

.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 2px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 6px 0;
}

.setting-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.setting-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.setting-desc {
  font-size: 11px;
  color: var(--text-muted);
}

.setting-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.slider {
  width: 100px;
  accent-color: var(--accent-primary);
}

.slider-value {
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-secondary);
  min-width: 30px;
  text-align: right;
}

/* Toggle */
.toggle {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 22px;
  flex-shrink: 0;
}

.toggle input { opacity: 0; width: 0; height: 0; }

.toggle-slider {
  position: absolute;
  inset: 0;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 11px;
  cursor: pointer;
  transition: var(--transition);
}

.toggle-slider::before {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  left: 2px;
  top: 2px;
  background: var(--text-secondary);
  border-radius: 50%;
  transition: var(--transition);
}

.toggle input:checked + .toggle-slider {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
}

.toggle input:checked + .toggle-slider::before {
  transform: translateX(18px);
  background: white;
}

/* Select */
.select-input {
  padding: 6px 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  cursor: pointer;
}

.select-input:focus {
  border-color: var(--accent-primary);
}

/* 快捷键 */
.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: var(--text-secondary);
}

.shortcut-item kbd {
  padding: 2px 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--accent-primary);
  min-width: 60px;
  text-align: center;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-primary);
}

.btn-secondary {
  padding: 8px 18px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.btn-secondary:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-primary {
  padding: 8px 18px;
  background: var(--accent-primary);
  border: none;
  border-radius: var(--radius-sm);
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.btn-primary:hover {
  background: #5558e6;
}

/* 保存成功提示 */
.save-toast {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 12px 28px;
  background: var(--success);
  color: white;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 4px 20px rgba(16,185,129,0.4);
  z-index: 10;
}

.fade-enter-active, .fade-leave-active { transition: all 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }

/* ====== 响应式 ====== */
@media (max-width: 600px) {
  .modal-content { width: 95vw; max-height: 90vh; }
  .modal-header { padding: 14px 16px; }
  .modal-body { padding: 16px; gap: 14px; }
  .modal-footer { padding: 12px 16px; }
  .setting-item { flex-direction: column; align-items: flex-start; gap: 8px; }
  .setting-control { width: 100%; }
  .slider { width: 100%; }
}
</style>

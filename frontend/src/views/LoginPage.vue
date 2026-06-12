<template>
  <div class="login-page">
    <!-- 背景图 + 雨滴效果 -->
    <div class="bg-canvas">
      <img :src="baseUrl + 'bg.png'" class="bg-image" alt="" />
      <div class="bg-overlay"></div>
      <RainEffect />
    </div>

    <div class="login-container">
      <!-- 左侧品牌区 -->
      <div class="brand-side">
        <div class="brand-content">
          <div class="logo-mark">
            <div class="logo-ring">
              <svg viewBox="0 0 120 120" class="logo-svg">
                <defs>
                  <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#a78bfa;stop-opacity:1" />
                  </linearGradient>
                </defs>
                <circle cx="60" cy="60" r="54" fill="none" stroke="url(#grad1)" stroke-width="2" stroke-dasharray="8 4" class="ring-rotate"/>
                <circle cx="60" cy="60" r="40" fill="none" stroke="url(#grad1)" stroke-width="1.5" opacity="0.6"/>
                <circle cx="60" cy="60" r="20" fill="url(#grad1)" opacity="0.15"/>
                <!-- Eye icon -->
                <ellipse cx="60" cy="60" rx="18" ry="12" fill="none" stroke="url(#grad1)" stroke-width="2"/>
                <circle cx="60" cy="60" r="6" fill="url(#grad1)"/>
              </svg>
            </div>
          </div>
          <h1 class="brand-title">Sentio-AI</h1>
          <p class="brand-subtitle">看见 &middot; 听见 &middot; 理解</p>
          <div class="brand-features">
            <div class="feature-item">
              <div class="feature-icon">&#128065;</div>
              <div class="feature-text">
                <strong>视觉理解</strong>
                <span>AI实时看到你所看到的</span>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">&#127908;</div>
              <div class="feature-text">
                <strong>语音交互</strong>
                <span>自然对话，AI即时回应</span>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">&#129504;</div>
              <div class="feature-text">
                <strong>智能分析</strong>
                <span>OCR文字识别、物体检测、情绪分析等</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区 -->
      <div class="form-side">
        <div class="form-wrapper">
          <!-- Tab切换 -->
          <div class="auth-tabs">
            <button
              :class="['tab-btn', { active: mode === 'login' }]"
              @click="mode = 'login'"
            >登录</button>
            <button
              :class="['tab-btn', { active: mode === 'register' }]"
              @click="mode = 'register'"
            >注册</button>
            <div class="tab-indicator" :class="{ right: mode === 'register' }"></div>
          </div>

          <!-- 表单 -->
          <form @submit.prevent="handleSubmit" class="auth-form">
            <div class="form-group">
              <label class="form-label">用户名</label>
              <div class="input-wrapper">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                <input
                  v-model="username"
                  type="text"
                  class="form-input"
                  placeholder="请输入用户名"
                  autocomplete="username"
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">密码</label>
              <div class="input-wrapper">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                <input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  class="form-input"
                  placeholder="请输入密码"
                  autocomplete="current-password"
                  required
                />
                <button type="button" class="toggle-pwd" @click="showPassword = !showPassword">
                  {{ showPassword ? '&#128064;' : '&#128065;' }}
                </button>
              </div>
            </div>

            <div v-if="mode === 'register'" class="form-group">
              <label class="form-label">确认密码</label>
              <div class="input-wrapper">
                <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
                <input
                  v-model="confirmPassword"
                  type="password"
                  class="form-input"
                  placeholder="请再次输入密码"
                  required
                />
              </div>
            </div>

            <div v-if="error" class="error-msg">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
              {{ error }}
            </div>

            <button type="submit" class="submit-btn" :disabled="loading">
              <span v-if="loading" class="btn-loader"></span>
              <span v-else>{{ mode === 'login' ? '登录' : '注册' }}</span>
            </button>
          </form>

          <div class="form-footer">
            <p v-if="mode === 'login'">
              还没有账号？
              <a href="#" @click.prevent="mode = 'register'">去注册</a>
            </p>
            <p v-else>
              已有账号？
              <a href="#" @click.prevent="mode = 'login'">去登录</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const baseUrl = import.meta.env.BASE_URL
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import RainEffect from '../components/RainEffect.vue'

const router = useRouter()
const { login, register } = useAuth()

const mode = ref('login')
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

const handleSubmit = async () => {
  error.value = ''

  if (username.value.length < 3) {
    error.value = '用户名至少3个字符'
    return
  }
  if (password.value.length < 6) {
    error.value = '密码至少6位'
    return
  }
  if (mode.value === 'register' && password.value !== confirmPassword.value) {
    error.value = '两次密码不一致'
    return
  }

  loading.value = true
  try {
    if (mode.value === 'login') {
      await login(username.value, password.value)
    } else {
      await register(username.value, password.value)
    }
    router.push('/')
  } catch (e) {
    if (e.code === 'ERR_NETWORK' || e.message?.includes('Network Error')) {
      error.value = '无法连接后端服务器，请确保后端已部署在 PythonAnywhere'
    } else {
      error.value = e.response?.data?.error || e.message || '操作失败，请重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* 背景动画 */
.bg-canvas {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.bg-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0.8) saturate(1.1);
}

.bg-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(10,10,20,0.05) 0%, rgba(10,10,20,0.15) 100%);
}

/* 主容器 */
.login-container {
  position: relative;
  display: flex;
  width: 900px;
  max-width: 95vw;
  min-height: 560px;
  background: rgba(30, 20, 60, 0.08);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(139, 92, 246, 0.15);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: 0 8px 40px rgba(88, 28, 135, 0.15);
}

/* 左侧品牌 */
.brand-side {
  flex: 1;
  padding: 48px 40px;
  display: flex;
  align-items: center;
  background: rgba(99, 102, 241, 0.04);
  border-right: 1px solid rgba(139, 92, 246, 0.1);
}

.brand-content {
  width: 100%;
}

.logo-mark {
  margin-bottom: 24px;
}

.logo-svg {
  width: 80px;
  height: 80px;
}

.ring-rotate {
  animation: rotate 30s linear infinite;
  transform-origin: center;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.brand-title {
  font-size: 32px;
  font-weight: 800;
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.brand-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.brand-features {
  margin-top: 36px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.feature-icon {
  font-size: 22px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(99,102,241,0.1);
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.feature-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.feature-text strong {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.feature-text span {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 右侧表单 */
.form-side {
  flex: 1;
  padding: 48px 40px;
  display: flex;
  align-items: center;
}

.form-wrapper {
  width: 100%;
}

/* Tab */
.auth-tabs {
  display: flex;
  position: relative;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  padding: 4px;
  margin-bottom: 32px;
}

.tab-btn {
  flex: 1;
  padding: 10px;
  border: none;
  background: none;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  position: relative;
  z-index: 1;
  border-radius: var(--radius-sm);
}

.tab-btn.active {
  color: var(--text-primary);
}

.tab-indicator {
  position: absolute;
  top: 4px;
  left: 4px;
  width: calc(50% - 4px);
  height: calc(100% - 8px);
  background: var(--accent-primary);
  border-radius: var(--radius-sm);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(99,102,241,0.3);
}

.tab-indicator.right {
  transform: translateX(100%);
}

/* 表单 */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: var(--text-muted);
  pointer-events: none;
}

.form-input {
  width: 100%;
  padding: 12px 14px 12px 42px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  transition: var(--transition);
}

.form-input:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.form-input::placeholder {
  color: var(--text-muted);
}

.toggle-pwd {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  opacity: 0.6;
  transition: var(--transition);
}

.toggle-pwd:hover {
  opacity: 1;
}

.error-msg {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.2);
  border-radius: var(--radius-sm);
  color: #fca5a5;
  font-size: 13px;
}

.submit-btn {
  width: 100%;
  padding: 13px;
  background: var(--accent-gradient);
  border: none;
  border-radius: var(--radius-md);
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  margin-top: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(99,102,241,0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-loader {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.form-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 13px;
  color: var(--text-secondary);
}

.form-footer a {
  color: var(--accent-primary);
  font-weight: 500;
}

.form-footer a:hover {
  text-decoration: underline;
}

/* 响应式 - 平板 */
@media (min-width: 769px) and (max-width: 1024px) {
  .login-container { width: 700px; }
  .brand-side { padding: 36px 28px; }
  .form-side { padding: 36px 28px; }
  .brand-title { font-size: 26px; }
}

/* 响应式 - 手机 */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    min-height: auto;
    width: 92vw;
    border-radius: var(--radius-lg);
  }
  .brand-side {
    padding: 28px 20px;
    border-right: none;
    border-bottom: 1px solid var(--border-primary);
  }
  .brand-features { display: none; }
  .brand-title { font-size: 24px; }
  .brand-subtitle { font-size: 11px; }
  .logo-svg { width: 60px; height: 60px; }
  .form-side { padding: 28px 20px; }
  .form-label { font-size: 11px; }
  .form-input { padding: 10px 12px; font-size: 13px; }
  .login-btn { padding: 12px; font-size: 13px; }
}

/* 响应式 - 超小屏 */
@media (max-width: 400px) {
  .brand-side { padding: 20px 14px; }
  .brand-title { font-size: 20px; }
  .form-side { padding: 20px 14px; }
}
</style>

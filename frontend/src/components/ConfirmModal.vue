<template>
  <Transition name="modal">
    <div class="confirm-overlay" @click.self="$emit('cancel')">
      <div class="confirm-box">
        <!-- 图片 -->
        <img :src="image || '/alert.png'" class="confirm-img" alt="" />
        <!-- 文字 -->
        <p class="confirm-text">{{ message }}</p>
        <!-- 按钮 -->
        <div class="confirm-actions">
          <button class="confirm-btn cancel" @click="$emit('cancel')">取消</button>
          <button class="confirm-btn ok" @click="$emit('confirm')">确定</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({ message: String, image: String })
defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.confirm-box {
  width: 320px;
  height: 320px;
  max-width: 90vw;
  max-height: 90vw;
  padding: 24px;
  background: rgba(30, 20, 60, 0.92);
  border: 1px solid rgba(139, 92, 246, 0.25);
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 8px 40px rgba(88, 28, 135, 0.3);
  backdrop-filter: blur(12px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.confirm-img {
  width: 120px;
  height: 120px;
  object-fit: contain;
  border-radius: 12px;
}

.confirm-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}

.confirm-actions {
  display: flex;
  gap: 10px;
  width: 100%;
}

.confirm-btn {
  flex: 1;
  padding: 10px 0;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.confirm-btn.cancel {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-muted);
  border: 1px solid var(--border-primary);
}
.confirm-btn.cancel:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.confirm-btn.ok {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}
.confirm-btn.ok:hover {
  background: linear-gradient(135deg, #f87171, #ef4444);
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.3);
}

.modal-enter-active, .modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .confirm-box { transform: scale(0.9); }
</style>

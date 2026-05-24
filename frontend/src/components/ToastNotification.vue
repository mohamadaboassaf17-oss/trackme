<template>
  <Transition name="toast">
    <div v-if="visible" :class="['toast-notification', 'toast-' + type]">
      <span class="toast-icon">{{ icons[type] }}</span>
      <span class="toast-text">{{ message }}</span>
    </div>
  </Transition>
</template>

<script>
export default {
  name: 'ToastNotification',
  data() {
    return {
      visible: false,
      message: '',
      type: 'success',
      icons: { success: '✓', error: '✕', warning: '⚠️', info: 'ℹ️' },
      timer: null
    }
  },
  methods: {
    show(message, type = 'success', duration = 3000) {
      if (this.timer) clearTimeout(this.timer)
      this.message = message
      this.type = type
      this.visible = true
      this.timer = setTimeout(() => { this.visible = false }, duration)
    }
  }
}
</script>

<style scoped>
.toast-notification {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 14px 28px;
  border-radius: 14px;
  font-weight: 600;
  font-size: 0.95rem;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.24);
  min-width: 250px;
  justify-content: center;
  backdrop-filter: blur(8px);
}
.toast-success { background: var(--success); color: white; }
.toast-error   { background: var(--danger);  color: white; }
.toast-warning { background: var(--warning); color: white; }
.toast-info    { background: var(--accent);  color: white; }
.toast-enter-active, .toast-leave-active { transition: all 0.35s cubic-bezier(0.4,0,0.2,1); }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(16px); }
</style>

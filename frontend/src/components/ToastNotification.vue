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
      icons: { success: '\u2713', error: '\u2717', warning: '\u26A0', info: '\u2139' },
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
  padding: 16px 32px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.95rem;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.25), 0 0 0 1px rgba(255,255,255,0.06);
  min-width: 200px;
  justify-content: center;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.1);
}
.toast-success {
  background: color-mix(in srgb, var(--success) 85%, transparent);
  color: white;
}
.toast-error {
  background: color-mix(in srgb, var(--danger) 85%, transparent);
  color: white;
}
.toast-warning {
  background: color-mix(in srgb, var(--warning) 85%, transparent);
  color: white;
}
.toast-info {
  background: color-mix(in srgb, var(--accent) 85%, transparent);
  color: white;
}
.toast-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  font-size: 0.8rem;
  flex-shrink: 0;
}
.toast-enter-active, .toast-leave-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(24px) scale(0.9);
}
</style>

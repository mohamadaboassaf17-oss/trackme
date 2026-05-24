<template>
  <div id="app-root">
    <Navbar v-if="authStore.isAuthenticated" />
    <main class="main-content" :class="{ 'with-navbar': authStore.isAuthenticated }">
      <router-view />
      <ToastNotification ref="toast" />
    </main>
    <button
      class="theme-toggle-global"
      @click="toggleTheme"
      :aria-label="theme === 'dark' ? 'تفعيل الوضع الفاتح' : 'تفعيل الوضع الداكن'"
      :title="theme === 'dark' ? 'تفعيل الوضع الفاتح' : 'تفعيل الوضع الداكن'"
    >
      {{ theme === 'dark' ? '☀️' : '🌙' }}
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, provide, getCurrentInstance } from "vue";
import { useAuthStore } from "./stores/auth";
import Navbar from "./components/Navbar.vue";
import ToastNotification from "./components/ToastNotification.vue";

const authStore = useAuthStore();
const theme = ref("dark");
const toastRef = ref(null);

const toast = {
  show: (message, type = "success", duration = 3000) => {
    toastRef.value?.show(message, type, duration);
  },
};

provide("$toast", toast);

const instance = getCurrentInstance();
if (instance?.appContext) {
  instance.appContext.config.globalProperties.$toast = toast;
}

function applyTheme(t) {
  document.documentElement.setAttribute("data-theme", t);
}

function toggleTheme() {
  theme.value = theme.value === "dark" ? "light" : "dark";
  applyTheme(theme.value);
  localStorage.setItem("theme", theme.value);
}

onMounted(() => {
  const saved = localStorage.getItem("theme") || "dark";
  theme.value = saved;
  applyTheme(saved);
});
</script>

<style>
.main-content.with-navbar {
  padding-top: 60px;
}

.theme-toggle-global {
  position: fixed;
  top: 12px;
  right: 12px;
  z-index: 200;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--bg-card);
  font-size: 1.3rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
  box-shadow: var(--shadow);
}

.theme-toggle-global:hover {
  transform: rotate(15deg) scale(1.1);
  box-shadow: var(--shadow-md);
}

@media (min-width: 769px) {
  .main-content.with-navbar ~ .theme-toggle-global {
    display: none;
  }
}

@media (max-width: 768px) {
  .main-content.with-navbar {
    padding-top: 0;
  }
}
</style>

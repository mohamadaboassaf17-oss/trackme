<template>
  <div id="app-root">
    <div class="app-atmosphere" aria-hidden="true">
      <div class="atmosphere-gradient"></div>
      <div class="atmosphere-pattern"></div>
      <div class="atmosphere-particles">
        <span class="particle" v-for="n in 6" :key="'p'+n" :style="{ '--i': n }"></span>
      </div>
    </div>
    <Navbar v-if="authStore.isAuthenticated" />
    <main class="main-content" :class="{ 'with-navbar': authStore.isAuthenticated }">
      <router-view v-slot="{ Component }">
        <keep-alive :include="keepAliveViews">
          <component :is="Component" />
        </keep-alive>
      </router-view>
      <ToastNotification ref="toast" />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, provide, getCurrentInstance } from "vue";
import { useAuthStore } from "./stores/auth";
import Navbar from "./components/Navbar.vue";
import ToastNotification from "./components/ToastNotification.vue";

const authStore = useAuthStore();
const theme = ref("dark");
const keepAliveViews = ['Dashboard', 'Attendance', 'Expenses', 'Goals', 'Reports', 'Settings'];
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

onMounted(() => {
  const saved = localStorage.getItem("theme") || "dark";
  theme.value = saved;
  applyTheme(saved);
  authStore.initFromStorage();
});
</script>

<style>
.main-content.with-navbar {
  padding-top: 60px;
}

@media (max-width: 768px) {
  .main-content.with-navbar {
    padding-top: 0;
  }
}

/* === Atmospheric Background === */
.app-atmosphere {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.atmosphere-gradient {
  position: absolute;
  top: -20%;
  left: 50%;
  transform: translateX(-50%);
  width: 80vw;
  height: 60vh;
  background: radial-gradient(ellipse at 50% 0%, color-mix(in srgb, var(--accent) 8%, transparent) 0%, transparent 70%);
  opacity: 0.7;
}

[data-theme="dark"] .atmosphere-gradient {
  background: radial-gradient(ellipse at 50% 0%, color-mix(in srgb, var(--accent) 12%, transparent) 0%, transparent 70%);
  opacity: 0.9;
}

.atmosphere-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.012;
  background-image:
    repeating-linear-gradient(45deg, var(--accent) 0, var(--accent) 1px, transparent 0, transparent 30px),
    repeating-linear-gradient(-45deg, var(--accent) 0, var(--accent) 1px, transparent 0, transparent 30px);
  mask-image: radial-gradient(ellipse at 50% 35%, black 30%, transparent 65%);
  -webkit-mask-image: radial-gradient(ellipse at 50% 35%, black 30%, transparent 65%);
}

[data-theme="dark"] .atmosphere-pattern {
  opacity: 0.02;
}

.atmosphere-particles {
  position: absolute;
  inset: 0;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: var(--accent);
  border-radius: 50%;
  opacity: 0.15;
  animation: particleFloat calc(8s + var(--i) * 3s) ease-in-out infinite;
  animation-delay: calc(var(--i) * 1.5s);
  left: calc(10% + var(--i) * 15%);
  top: calc(20% + var(--i) * 8%);
}

[data-theme="dark"] .particle {
  opacity: 0.25;
}

@keyframes particleFloat {
  0%, 100% {
    transform: translateY(0) translateX(0);
    opacity: 0.1;
  }
  25% {
    transform: translateY(-30px) translateX(10px);
    opacity: 0.25;
  }
  50% {
    transform: translateY(-60px) translateX(-5px);
    opacity: 0.15;
  }
  75% {
    transform: translateY(-30px) translateX(-15px);
    opacity: 0.2;
  }
}

.main-content {
  position: relative;
  z-index: 1;
}

</style>

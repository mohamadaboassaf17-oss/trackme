<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <div class="navbar-brand">
        <router-link to="/dashboard">
          <span class="brand-icon" aria-hidden="true"></span>
          TrackMe | تتبع
        </router-link>
      </div>
      <div class="navbar-links">
        <router-link to="/dashboard">لوحة التحكم</router-link>
        <router-link to="/attendance">الدوام</router-link>
        <router-link to="/expenses">المصاريف</router-link>
        <router-link to="/goals">الأهداف</router-link>
        <router-link to="/reports">التقارير</router-link>
        <router-link to="/settings">الإعدادات</router-link>
      </div>
      <div class="navbar-actions">
        <button
          class="theme-toggle-btn"
          @click="toggleTheme"
          :aria-label="theme === 'dark' ? 'تفعيل الوضع الفاتح' : 'تفعيل الوضع الداكن'"
          :title="theme === 'dark' ? 'تفعيل الوضع الفاتح' : 'تفعيل الوضع الداكن'"
        >
          <span v-if="theme === 'dark'" class="theme-icon-sun" aria-hidden="true"></span>
          <span v-else class="theme-icon-moon" aria-hidden="true"></span>
        </button>
        <span class="navbar-user">{{ authStore.user?.username }}</span>
        <button class="btn btn-logout" @click="handleLogout">تسجيل الخروج</button>
      </div>
    </div>
  </nav>

    <nav class="bottom-nav">
      <router-link to="/dashboard" class="bottom-nav-item">
        <span class="bottom-nav-icon nav-icon-dashboard" aria-hidden="true"></span>
        <span class="bottom-nav-label">الرئيسية</span>
      </router-link>
      <router-link to="/attendance" class="bottom-nav-item">
        <span class="bottom-nav-icon nav-icon-clock" aria-hidden="true"></span>
        <span class="bottom-nav-label">الدوام</span>
      </router-link>
      <router-link to="/expenses" class="bottom-nav-item">
        <span class="bottom-nav-icon nav-icon-money" aria-hidden="true"></span>
        <span class="bottom-nav-label">مصاريف</span>
      </router-link>
      <router-link to="/goals" class="bottom-nav-item">
        <span class="bottom-nav-icon nav-icon-target" aria-hidden="true"></span>
        <span class="bottom-nav-label">أهداف</span>
      </router-link>
      <router-link to="/settings" class="bottom-nav-item">
        <span class="bottom-nav-icon nav-icon-settings" aria-hidden="true"></span>
        <span class="bottom-nav-label">إعدادات</span>
      </router-link>
      <button class="bottom-nav-item bottom-nav-theme" @click="toggleTheme" :aria-label="theme === 'dark' ? 'الوضع النهاري' : 'الوضع الليلي'">
        <span v-if="theme === 'dark'" class="bottom-nav-icon theme-icon-sun" aria-hidden="true"></span>
        <span v-else class="bottom-nav-icon theme-icon-moon" aria-hidden="true"></span>
        <span class="bottom-nav-label">مظهر</span>
      </button>
    </nav>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const theme = ref("dark");

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

function handleLogout() {
  authStore.logout();
  router.push("/login");
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: color-mix(in srgb, var(--bg-card) 75%, transparent);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid transparent;
  position: relative;
  z-index: 100;
  display: flex;
  align-items: center;
}

.navbar::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(to left, transparent, var(--gold), var(--accent), var(--gold), transparent);
  opacity: 0.6;
}

.navbar-inner {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-brand a {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.2rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--accent), var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-decoration: none;
  transition: opacity var(--transition);
}

.navbar-brand a:hover {
  opacity: 0.85;
}

.brand-icon {
  font-size: 1.4rem;
}

.navbar-links {
  display: flex;
  gap: 4px;
}

.navbar-links a {
  padding: 7px 14px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all var(--transition);
}

.navbar-links a:hover {
  color: var(--text-primary);
  background: var(--accent-light);
}

.navbar-links a.router-link-active {
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  color: var(--accent);
  font-weight: 700;
  box-shadow: none;
  border-bottom: none;
  position: relative;
}

.navbar-links a.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 10%;
  width: 80%;
  height: 2.5px;
  background: linear-gradient(to left, var(--accent), var(--gold));
  border-radius: 2px;
  box-shadow: 0 0 8px color-mix(in srgb, var(--accent) 40%, transparent);
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.theme-toggle-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: transparent;
  font-size: 1.15rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
  padding: 0;
}

.theme-toggle-btn:hover {
  transform: rotate(15deg) scale(1.15);
  border-color: var(--accent);
}

.navbar-user {
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* Bottom Navigation (mobile only) */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--bg-card);
  border-top: 1px solid var(--border);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  display: none;
  justify-content: space-around;
  align-items: center;
  z-index: 1000;
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 0.7rem;
  padding: 6px 12px;
  border-radius: 8px;
  transition: all var(--transition);
  min-width: 56px;
  min-height: 44px;
}

.bottom-nav-item:hover {
  color: var(--accent);
  background: var(--accent-light);
}

.bottom-nav-item.router-link-active {
  color: var(--accent);
  background: color-mix(in srgb, var(--accent) 8%, transparent);
  border-radius: 16px;
  box-shadow: var(--shadow);
}

.bottom-nav-item.router-link-active .bottom-nav-label {
  text-shadow: 0 0 8px color-mix(in srgb, var(--accent) 30%, transparent);
}

.bottom-nav-item.router-link-active::after {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background: var(--accent);
  border-radius: 0 0 2px 2px;
}

.bottom-nav-icon {
}

.bottom-nav-label {
  font-weight: 600;
}

.bottom-nav-theme {
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
}
.bottom-nav-theme:hover .bottom-nav-icon,
.bottom-nav-theme:focus-visible .bottom-nav-icon {
  color: var(--gold);
}

@media (max-width: 768px) {
  .navbar {
    display: none !important;
  }

  .bottom-nav {
    display: flex;
  }
}

@media (min-width: 769px) {
  .bottom-nav {
    display: none;
  }

  .navbar {
    display: flex;
  }
}
</style>

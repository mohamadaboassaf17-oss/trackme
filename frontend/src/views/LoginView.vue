<template>
  <div class="login-view">
    <div class="login-card">
      <div class="login-brand">
        <span class="brand-icon">◈</span>
        <h1>TrackMe | تتبع</h1>
        <p class="subtitle">نظام تتبع الحضور والمصاريف</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">اسم المستخدم</label>
          <input id="username" v-model="username" type="text" required placeholder="أدخل اسم المستخدم" />
        </div>
        <div class="form-group">
          <label for="password">كلمة المرور</label>
          <input id="password" v-model="password" type="password" required placeholder="أدخل كلمة المرور" />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="btn btn-primary btn-login" :disabled="loading">
          {{ loading ? "جاري الدخول..." : "دخول" }}
        </button>
      </form>

      <p class="switch-mode">
        ليس لديك حساب؟
        <button class="btn-link" @click="showRegister = true">إنشاء حساب جديد</button>
      </p>
    </div>

    <div v-if="showRegister" class="modal-overlay" @click.self="showRegister = false">
      <div class="login-card modal-card-scroll">
        <div class="login-brand">
          <h1>إنشاء حساب</h1>
        </div>
        <form @submit.prevent="handleRegister" class="login-form">
          <div class="form-group">
            <label for="reg-username">اسم المستخدم</label>
            <input id="reg-username" v-model="regUsername" type="text" required placeholder="اختر اسم مستخدم" />
          </div>
          <div class="form-group">
            <label for="reg-password">كلمة المرور</label>
            <input id="reg-password" v-model="regPassword" type="password" required placeholder="اختر كلمة مرور" />
          </div>
          <div class="form-group">
            <label for="salary-type">نوع الراتب</label>
            <select id="salary-type" v-model="regSalaryType">
              <option value="monthly">شهري</option>
              <option value="weekly">أسبوعي</option>
            </select>
          </div>
          <div class="form-group">
            <label for="salary-amount">مبلغ الراتب ($)</label>
            <input id="salary-amount" v-model.number="regSalaryAmount" type="number" step="0.01" min="0" placeholder="0.00" />
          </div>
          <p v-if="regError" class="error-msg">{{ regError }}</p>
          <button type="submit" class="btn btn-primary" :disabled="regLoading">
            {{ regLoading ? "جاري الإنشاء..." : "إنشاء حساب" }}
          </button>
        </form>
        <button class="btn-link btn-back" @click="showRegister = false">العودة لتسجيل الدخول</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const username = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

const showRegister = ref(false);
const regUsername = ref("");
const regPassword = ref("");
const regSalaryType = ref("monthly");
const regSalaryAmount = ref(0);
const regError = ref("");
const regLoading = ref(false);

async function handleLogin() {
  error.value = "";
  loading.value = true;
  try {
    await authStore.login(username.value, password.value);
    router.push("/dashboard");
  } catch (err) {
    error.value = err.response?.data?.detail || "حدث خطأ أثناء تسجيل الدخول";
  } finally {
    loading.value = false;
  }
}

async function handleRegister() {
  regError.value = "";
  regLoading.value = true;
  try {
    await authStore.register(
      regUsername.value,
      regPassword.value,
      regSalaryType.value,
      regSalaryAmount.value
    );
    await authStore.login(regUsername.value, regPassword.value);
    router.push("/dashboard");
  } catch (err) {
    regError.value = err.response?.data?.detail || "حدث خطأ أثناء إنشاء الحساب";
  } finally {
    regLoading.value = false;
  }
}
</script>

<style scoped>
.login-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 24px;
  animation: loginFadeIn 0.5s ease-out;
}

@keyframes loginFadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

.login-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 40px 36px;
  width: 100%;
  max-width: 420px;
  box-shadow: var(--shadow-lg);
  animation: cardSlideUp 0.5s ease-out;
}

@keyframes cardSlideUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

.login-brand {
  text-align: center;
  margin-bottom: 32px;
}

.brand-icon {
  font-size: 2.5rem;
  color: var(--accent);
  display: block;
  margin-bottom: 8px;
}

.login-brand h1 {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-top: 6px;
}

.login-form {
  margin-bottom: 20px;
}

.btn-login {
  margin-top: 8px;
}

.switch-mode {
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  animation: fadeOverlayIn 0.2s ease-out;
}

@keyframes fadeOverlayIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

.modal-card-scroll {
  max-height: 90vh;
  overflow-y: auto;
}

.btn-back {
  display: block;
  margin: 16px auto 0;
  text-align: center;
  font-size: 0.9rem;
}

.error-msg {
  background: rgba(239,68,68,0.1);
  color: var(--danger);
  border: 1px solid var(--danger);
  padding: 12px 16px;
  border-radius: 10px;
  margin-bottom: 16px;
  font-weight: 500;
}
.success-msg {
  background: rgba(16,185,129,0.1);
  color: var(--success);
  border: 1px solid var(--success);
  padding: 12px 16px;
  border-radius: 10px;
  margin-bottom: 16px;
  font-weight: 500;
}
</style>

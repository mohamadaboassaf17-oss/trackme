<template>
  <div class="login-view">
    <!-- Atmospheric background layers -->
    <div class="login-atmosphere" aria-hidden="true">
      <div class="login-glow"></div>
      <div class="login-particles">
        <span class="login-particle" v-for="n in 8" :key="'lp'+n" :style="{ '--lp': n }"></span>
      </div>
    </div>

    <!-- Main card -->
    <div class="login-card">
      <div class="login-brand">
        <div class="brand-icon-wrapper">
          <span class="brand-icon" aria-hidden="true"></span>
        </div>
        <h1 class="heading-gold">TrackMe | تتبع</h1>
        <p class="subtitle">نظام تتبع الحضور والمصاريف</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <p class="login-subtitle">مرحباً بعودتك! سجل دخولك للمتابعة</p>
        <div class="form-group">
          <label for="username">اسم المستخدم</label>
          <input id="username" v-model="username" type="text" required placeholder="أدخل اسم المستخدم" />
        </div>
        <div class="form-group">
          <label for="password">كلمة المرور</label>
          <div class="input-wrapper">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              required
              placeholder="أدخل كلمة المرور"
              @input="validatePassword"
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="toggle-password-btn"
              :title="showPassword ? 'إخفاء' : 'إظهار'"
            >
              <span v-if="showPassword" class="password-eye-off" aria-hidden="true"></span>
              <span v-else class="password-eye" aria-hidden="true"></span>
            </button>
          </div>
          <small v-if="passwordError" class="field-error">{{ passwordError }}</small>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="btn btn-primary btn-login btn-full" :disabled="loading || !!passwordError">
          <span v-if="loading" class="btn-spinner"></span>
          <span>{{ loading ? "جاري الدخول..." : "دخول" }}</span>
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
            <div class="input-wrapper">
              <input
                id="reg-password"
                v-model="regPassword"
                :type="showRegPassword ? 'text' : 'password'"
                required
                placeholder="اختر كلمة مرور"
              />
              <button
                type="button"
                @click="showRegPassword = !showRegPassword"
                class="toggle-password-btn"
              >
                <span v-if="showRegPassword" class="password-eye-off" aria-hidden="true"></span>
                <span v-else class="password-eye" aria-hidden="true"></span>
              </button>
            </div>
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
        <button class="btn-link btn-back" @click="showRegister = false">العودة للدخول</button>
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

const showPassword = ref(false);
const showRegPassword = ref(false);
const passwordError = ref("");

function validatePassword() {
  if (password.value.length > 0 && password.value.length < 8) {
    passwordError.value = 'كلمة المرور يجب أن تكون 8 أحرف على الأقل';
  } else {
    passwordError.value = '';
  }
}

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
/* === Login View — Premium Immersive Experience === */

.login-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 24px;
  position: relative;
  overflow: hidden;
}

/* Atmospheric layers */
.login-atmosphere {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.login-glow {
  position: absolute;
  top: -15%;
  left: 50%;
  transform: translateX(-50%);
  width: 70vw;
  height: 50vh;
  background: radial-gradient(ellipse at 50% 0%, color-mix(in srgb, var(--accent) 10%, transparent) 0%, transparent 70%);
  animation: loginGlowPulse 6s ease-in-out infinite;
}

[data-theme="dark"] .login-glow {
  background: radial-gradient(ellipse at 50% 0%, color-mix(in srgb, var(--accent) 18%, transparent) 0%, transparent 70%);
}

@keyframes loginGlowPulse {
  0%, 100% { opacity: 0.6; transform: translateX(-50%) scale(1); }
  50%      { opacity: 1; transform: translateX(-50%) scale(1.05); }
}

/* Floating particles */
.login-particles {
  position: absolute;
  inset: 0;
}

.login-particle {
  position: absolute;
  width: 3px;
  height: 3px;
  background: var(--accent);
  border-radius: 50%;
  opacity: 0;
  animation: loginParticleFloat calc(7s + var(--lp) * 2s) ease-in-out infinite;
  animation-delay: calc(var(--lp) * 0.8s);
  left: calc(5% + var(--lp) * 12%);
  top: calc(10% + var(--lp) * 8%);
}

[data-theme="dark"] .login-particle {
  background: var(--accent);
  box-shadow: 0 0 6px var(--accent);
}

@keyframes loginParticleFloat {
  0%   { opacity: 0; transform: translateY(0) translateX(0); }
  20%  { opacity: 0.5; }
  50%  { opacity: 0.3; transform: translateY(-40px) translateX(15px); }
  80%  { opacity: 0.1; }
  100% { opacity: 0; transform: translateY(-80px) translateX(-5px); }
}

/* Login Card */
.login-card {
  position: relative;
  z-index: 1;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 44px 40px;
  width: 100%;
  max-width: 440px;
  box-shadow: var(--shadow-lg), 0 0 0 1px color-mix(in srgb, var(--accent) 6%, transparent);
  animation: cardSlideUp 0.6s cubic-bezier(0.22, 1, 0.36, 1);
  backdrop-filter: blur(2px);
}

[data-theme="dark"] .login-card {
  box-shadow: var(--shadow-lg), 0 0 40px color-mix(in srgb, var(--accent) 10%, transparent);
}

/* Top gradient accent bar */
.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(to left, var(--accent), #E6A817, var(--accent));
  border-radius: 3px 0 3px 0;
}

@keyframes cardSlideUp {
  from { opacity: 0; transform: translateY(30px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* Brand Section */
.login-brand {
  text-align: center;
  margin-bottom: 32px;
}

.brand-icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: 20px;
  background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 10%, transparent), color-mix(in srgb, var(--accent) 5%, transparent));
  border: 1px solid color-mix(in srgb, var(--accent) 15%, transparent);
  margin-bottom: 16px;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50%      { transform: translateY(-6px); }
}

.brand-icon {
  font-size: 2rem;
  color: var(--accent);
  display: block;
  filter: drop-shadow(0 2px 8px color-mix(in srgb, var(--accent) 25%, transparent));
}

.login-brand h1 {
  font-size: 1.6rem;
  font-weight: 800;
  margin-bottom: 6px;
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-top: 6px;
}

.login-subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
  text-align: center;
  margin-bottom: 24px;
  font-weight: 500;
}

.login-form {
  margin-bottom: 20px;
}

/* Button */
.btn-login {
  margin-top: 8px;
}

/* Switch mode */
.switch-mode {
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.9rem;
  padding-top: 8px;
  border-top: 1px solid var(--border);
}

/* Registration Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  animation: modalFadeIn 0.25s ease-out;
}

@keyframes modalFadeIn {
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

/* Form helpers - keep existing */
.input-wrapper { position: relative; }
.toggle-password-btn {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 4px;
}
.field-error {
  color: var(--danger);
  font-size: 0.8rem;
  margin-top: 4px;
  display: block;
}
.btn-full { width: 100%; }

/* Spinner */
.btn-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid color-mix(in srgb, white 40%, transparent);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  margin-left: 8px;
  vertical-align: middle;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>

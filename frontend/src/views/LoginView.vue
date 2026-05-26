<template>
  <div class="login-view">
    <div class="login-card">
      <div class="login-brand">
        <span class="brand-icon" aria-hidden="true"></span>
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
.login-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 24px;
  animation: loginFadeIn 0.5s ease-out;
  position: relative;
}

.login-view::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  opacity: 0.02;
  background-image: 
    repeating-linear-gradient(45deg, var(--accent) 0, var(--accent) 1px, transparent 0, transparent 20px),
    repeating-linear-gradient(-45deg, var(--gold) 0, var(--gold) 1px, transparent 0, transparent 20px);
  mask-image: radial-gradient(ellipse at 50% 30%, black 35%, transparent 60%);
  -webkit-mask-image: radial-gradient(ellipse at 50% 30%, black 35%, transparent 60%);
  animation: arabesqueRotate 90s linear infinite;
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
  position: relative;
  overflow: hidden;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(to left, var(--accent), var(--gold), var(--accent));
  border-radius: 3px 0 3px 0;
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
.btn-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  margin-left: 8px;
  vertical-align: middle;
}
@keyframes spin { to { transform: rotate(360deg); } }

.error-msg {
  background: var(--danger-light);
  color: var(--danger);
  border: 1px solid var(--danger);
  padding: 12px 16px;
  border-radius: 10px;
  margin-bottom: 16px;
  font-weight: 500;
}
.success-msg {
  background: var(--success-light);
  color: var(--success);
  border: 1px solid var(--success);
  padding: 12px 16px;
  border-radius: 10px;
  margin-bottom: 16px;
  font-weight: 500;
}
</style>

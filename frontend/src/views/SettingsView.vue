<template>
  <div class="view">
    <div class="page-header">
      <h1>الإعدادات</h1>
      <p>إعدادات الحساب والراتب</p>
    </div>

    <div class="settings-grid">
      <div class="card">
        <h2>إعدادات الراتب</h2>
        <form @submit.prevent="saveSalary" class="settings-form">
          <div class="form-group">
            <label for="salary-type">نوع الراتب</label>
            <select id="salary-type" v-model="salaryType">
              <option value="monthly">شهري</option>
              <option value="weekly">أسبوعي</option>
            </select>
          </div>
          <div class="form-group">
            <label for="salary-amount">مبلغ الراتب ($)</label>
            <input
              id="salary-amount"
              v-model.number="salaryAmount"
              type="number"
              min="0"
              step="0.01"
              placeholder="0.00"
            />
          </div>
          <div v-if="saveError" class="error-msg">{{ saveError }}</div>
          <div v-if="saveSuccess" class="success-msg">{{ saveSuccess }}</div>
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? "جارٍ الحفظ..." : "حفظ الإعدادات" }}
          </button>
        </form>
      </div>

      <div class="card">
        <h2>وقت الدوام الافتراضي</h2>
        <form @submit.prevent="saveShiftDefaults" class="settings-form">
          <div class="form-group">
            <label for="shift-start">وقت البداية الافتراضي</label>
            <input id="shift-start" v-model="defaultStartTime" type="time" />
          </div>
          <div class="form-group">
            <label for="shift-end">وقت النهاية الافتراضي</label>
            <input id="shift-end" v-model="defaultEndTime" type="time" />
          </div>
          <div v-if="shiftSaveError" class="error-msg">{{ shiftSaveError }}</div>
          <div v-if="shiftSaveSuccess" class="success-msg">{{ shiftSaveSuccess }}</div>
          <button type="submit" class="btn btn-primary" :disabled="shiftSaving">
            {{ shiftSaving ? "جارٍ الحفظ..." : "حفظ" }}
          </button>
        </form>
      </div>

      <div class="card">
        <h2>ملخص الراتب</h2>
        <div v-if="salaryLoading" class="loading">جارٍ التحميل...</div>
        <div v-else-if="salaryError" class="error-msg">{{ salaryError }}</div>
        <div v-else-if="salaryData" class="salary-summary">
          <div class="summary-row">
            <span class="summary-label">نوع الراتب</span>
            <span class="summary-value">{{ salaryData.salary_type === "monthly" ? "شهري" : "أسبوعي" }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">الفترة</span>
            <span class="summary-value">من {{ salaryData.period_start }} إلى {{ salaryData.period_end }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">أيام العمل المتوقعة</span>
            <span class="summary-value">{{ salaryData.expected_work_days }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">أيام الحضور الفعلية</span>
            <span class="summary-value present">{{ salaryData.actual_present_days }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">أيام الغياب</span>
            <span class="summary-value absent">{{ salaryData.absent_days }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">أيام الإجازة</span>
            <span class="summary-value holiday">{{ salaryData.holiday_days }}</span>
          </div>
          <div class="summary-divider"></div>
          <div class="summary-row">
            <span class="summary-label">الراتب اليومي</span>
            <span class="summary-value">${{ (salaryData.daily_rate ?? 0).toFixed(2) }}</span>
          </div>
          <div class="summary-row earned-row">
            <span class="summary-label">الراتب المستحق</span>
            <span class="summary-value earned">${{ (salaryData.earned_salary ?? 0).toFixed(2) }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">الفرق</span>
            <span class="summary-value" :class="{ negative: salaryData.difference > 0 }">
              ${{ (salaryData.difference ?? 0).toFixed(2) }}
            </span>
          </div>
        </div>
        <div v-else class="loading">لا توجد بيانات متاحة</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import api from "@/utils/api";

const authStore = useAuthStore();

const salaryType = ref("monthly");
const salaryAmount = ref(0);
const saving = ref(false);
const saveError = ref("");
const saveSuccess = ref("");

const salaryData = ref(null);
const salaryLoading = ref(true);
const salaryError = ref("");

const defaultStartTime = ref("");
const defaultEndTime = ref("");
const shiftSaving = ref(false);
const shiftSaveError = ref("");
const shiftSaveSuccess = ref("");

onMounted(() => {
  if (authStore.user) {
    salaryType.value = authStore.user.salary_type || "monthly";
    salaryAmount.value = authStore.user.salary_amount || 0;
  }
  fetchSalary();
  fetchShiftDefaults();
});

async function saveSalary() {
  saveError.value = "";
  saveSuccess.value = "";
  saving.value = true;
  try {
    const response = await api.put("/users/me", {
      salary_type: salaryType.value,
      salary_amount: salaryAmount.value,
    });
    authStore.user = response.data;
    localStorage.setItem("user", JSON.stringify(authStore.user));
    saveSuccess.value = "تم حفظ الإعدادات بنجاح";
    await fetchSalary();
  } catch (err) {
    saveError.value =
      err.response?.data?.detail || "حدث خطأ أثناء حفظ الإعدادات";
  } finally {
    saving.value = false;
  }
}

async function fetchSalary() {
  salaryLoading.value = true;
  salaryError.value = "";
  try {
    const response = await api.get("/salary");
    salaryData.value = response.data;
  } catch (err) {
    salaryError.value =
      err.response?.data?.detail || "تعذر تحميل ملخص الراتب";
  } finally {
    salaryLoading.value = false;
  }
}

async function fetchShiftDefaults() {
  try {
    const response = await api.get("/settings/shift-defaults");
    defaultStartTime.value = response.data.default_start_time || "";
    defaultEndTime.value = response.data.default_end_time || "";
  } catch (err) {
    // silent fail - user can still set defaults
  }
}

async function saveShiftDefaults() {
  shiftSaveError.value = "";
  shiftSaveSuccess.value = "";
  shiftSaving.value = true;
  try {
    const response = await api.put("/settings/shift-defaults", {
      default_start_time: defaultStartTime.value || null,
      default_end_time: defaultEndTime.value || null,
    });
    defaultStartTime.value = response.data.default_start_time || "";
    defaultEndTime.value = response.data.default_end_time || "";
    shiftSaveSuccess.value = "تم الحفظ ✓";
  } catch (err) {
    shiftSaveError.value =
      err.response?.data?.detail || "حدث خطأ أثناء حفظ إعدادات وقت الدوام";
  } finally {
    shiftSaving.value = false;
  }
}
</script>

<style scoped>
.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}

h2 {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.settings-form {
  max-width: 400px;
}

.salary-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  transition: background var(--transition);
}

.summary-row:hover {
  background: rgba(99, 102, 241, 0.03);
  margin: 0 -8px;
  padding-left: 8px;
  padding-right: 8px;
  border-radius: var(--radius-sm);
}

.summary-label {
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.summary-value {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.summary-value.present {
  color: var(--success);
}

.summary-value.absent {
  color: var(--danger);
}

.summary-value.holiday {
  color: var(--warning);
}

.earned-row {
  padding: 12px 0;
}

.summary-value.earned {
  color: var(--accent);
  font-size: 1.2rem;
  font-weight: 800;
}

.summary-value.negative {
  color: var(--danger);
}

.summary-divider {
  height: 1px;
  background-color: var(--border);
  margin: 8px 0;
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

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
        <h2>أيام العمل في الأسبوع</h2>
        <p class="card-desc">اختر عدد أيام العمل لحساب الراتب اليومي</p>
        <div class="work-days-options">
          <label class="work-day-option" :class="{ active: workDays === 5 }">
            <input type="radio" v-model="workDays" :value="5" />
            <span class="work-day-badge">5</span>
            <span class="work-day-label">أيام</span>
            <span class="work-day-detail">الإثنين - الجمعة</span>
          </label>
          <label class="work-day-option" :class="{ active: workDays === 6 }">
            <input type="radio" v-model="workDays" :value="6" />
            <span class="work-day-badge">6</span>
            <span class="work-day-label">أيام</span>
            <span class="work-day-detail">الإثنين - السبت</span>
          </label>
        </div>
        <div v-if="workDaysError" class="error-msg">{{ workDaysError }}</div>
        <div v-if="workDaysSaved" class="success-msg">{{ workDaysSaved }}</div>
        <button class="btn btn-primary" @click="saveWorkDays" :disabled="workDaysSaving" style="margin-top:12px">
          {{ workDaysSaving ? 'جارٍ الحفظ...' : 'حفظ' }}
        </button>
      </div>

      <!-- Expected Work Days Per Month -->
      <div class="card card-settings">
        <div class="card-header">
          <h3>أيام العمل المتوقعة شهرياً</h3>
          <p class="card-desc">الحد الأدنى لأيام العمل المتوقعة لحساب الراتب الشهري</p>
        </div>
        <div class="expected-days-input">
          <input
            id="expectedDays"
            v-model.number="expectedDays"
            type="number"
            min="26"
            max="31"
            class="input-number"
            placeholder="26"
          />
          <span class="expected-days-unit">يوم في الشهر</span>
        </div>
        <button
          class="btn btn-save"
          :disabled="savingExpectedDays"
          @click="saveExpectedDays"
        >
          {{ savingExpectedDays ? 'جاري الحفظ...' : 'حفظ' }}
        </button>
        <p v-if="expectedDaysError" class="error-msg">{{ expectedDaysError }}</p>
        <p v-if="expectedDaysSuccess" class="success-msg">{{ expectedDaysSuccess }}</p>
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
import { safeArray } from "@/utils/helpers";

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

const workDays = ref(6)
const workDaysSaving = ref(false)
const workDaysError = ref('')
const workDaysSaved = ref('')

const expectedDays = ref(26);
const savingExpectedDays = ref(false);
const expectedDaysError = ref("");
const expectedDaysSuccess = ref("");

onMounted(() => {
  if (authStore.user) {
    salaryType.value = authStore.user.salary_type || "monthly";
    salaryAmount.value = authStore.user.salary_amount || 0;
  }
  fetchSalary();
  fetchShiftDefaults();
  fetchWorkDays();
  fetchExpectedDays();
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
    salaryData.value = response.data || null;
    if (salaryData.value) {
      salaryData.value.expected_work_days = salaryData.value.expected_work_days ?? 0;
      salaryData.value.actual_present_days = salaryData.value.actual_present_days ?? 0;
      salaryData.value.absent_days = salaryData.value.absent_days ?? 0;
      salaryData.value.holiday_days = salaryData.value.holiday_days ?? 0;
      salaryData.value.daily_rate = salaryData.value.daily_rate ?? 0;
      salaryData.value.earned_salary = salaryData.value.earned_salary ?? 0;
      salaryData.value.difference = salaryData.value.difference ?? 0;
    }
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
    shiftSaveSuccess.value = "تم الحفظ";
  } catch (err) {
    shiftSaveError.value =
      err.response?.data?.detail || "حدث خطأ أثناء حفظ إعدادات وقت الدوام";
  } finally {
    shiftSaving.value = false;
  }
}

async function fetchWorkDays() {
  try {
    const res = await api.get('/settings/work-days')
    workDays.value = res.data.work_days_per_week || 6
  } catch (e) { /* silent */ }
}

async function saveWorkDays() {
  workDaysError.value = ''
  workDaysSaved.value = ''
  workDaysSaving.value = true
  try {
    await api.put('/settings/work-days', { work_days_per_week: workDays.value })
    workDaysSaved.value = 'تم حفظ إعدادات أيام العمل'
  } catch (e) {
    workDaysError.value = e.response?.data?.detail || 'حدث خطأ'
  } finally {
    workDaysSaving.value = false
  }
}

async function fetchExpectedDays() {
  try {
    const res = await api.get("/settings/expected-days");
    expectedDays.value = res.data.expected_days_per_month || 26;
  } catch {
    expectedDays.value = 26;
  }
}

async function saveExpectedDays() {
  expectedDaysError.value = "";
  expectedDaysSuccess.value = "";
  savingExpectedDays.value = true;
  try {
    await api.put("/settings/expected-days", {
      expected_days_per_month: expectedDays.value
    });
    expectedDaysSuccess.value = "تم حفظ الإعدادات بنجاح";
  } catch (err) {
    expectedDaysError.value = err.response?.data?.detail || "حدث خطأ أثناء الحفظ";
  } finally {
    savingExpectedDays.value = false;
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
  background: color-mix(in srgb, var(--accent) 3%, transparent);
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
  color: var(--info);
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

.work-days-options {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}
.work-day-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 12px;
  border: 2px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition);
  text-align: center;
}
.work-day-option.active {
  border-color: var(--accent);
  background: var(--accent-light);
}
.work-day-option input { display: none; }
.work-day-badge {
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--accent);
}
.work-day-label { font-size: var(--text-sm); font-weight: 600; color: var(--text-primary); }
.work-day-detail { font-size: var(--text-xs); color: var(--text-secondary); }
.card-desc { font-size: var(--text-sm); color: var(--text-secondary); margin-bottom: 16px; }

.expected-days-input {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 12px 0 16px;
}
.input-number {
  width: 90px;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-family);
  font-size: 1.1rem;
  font-weight: 600;
  text-align: center;
  transition: var(--transition);
}
.input-number:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 15%, transparent);
}
.expected-days-unit {
  color: var(--text-muted);
  font-size: 0.9rem;
}
.btn-save {
  background: var(--accent);
  color: white;
  border: none;
  padding: 10px 32px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: var(--font-family);
  font-size: 0.95rem;
  font-weight: 600;
  transition: var(--transition);
}
.btn-save:hover {
  background: var(--accent-hover);
}
.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.success-msg {
  color: var(--success);
  font-size: 0.85rem;
  margin-top: 8px;
}
</style>

<template>
  <div class="view">
    <div class="page-header">
      <h1>لوحة التحكم</h1>
      <p>مرحباً، {{ authStore.user?.username }}</p>
    </div>

    <div class="period-toggle">
      <button
        class="toggle-btn"
        :class="{ active: period === 'weekly' }"
        @click="period = 'weekly'"
      >
        أسبوعي
      </button>
      <button
        class="toggle-btn"
        :class="{ active: period === 'monthly' }"
        @click="period = 'monthly'"
      >
        شهري
      </button>
    </div>

    <div v-if="loading" class="loading">جاري التحميل...</div>
    <div v-if="error" class="error-msg">{{ error }}</div>

    <div class="summary-cards summary-grid">
      <div class="card summary-card">
        <div class="card-label">⏰ ساعات العمل</div>
        <div class="card-value number-fade-in">{{ totalHours }}</div>
        <div class="card-meta">من {{ presentDays }} يوم عمل</div>
      </div>
      <div class="card summary-card">
        <div class="card-label">💰 الراتب المستحق</div>
        <div class="card-value number-fade-in">${{ earnedSalary }}</div>
        <div class="card-meta">
          {{ salaryData?.actual_present_days || 0 }} أيام حضور
        </div>
      </div>
      <div class="card summary-card">
        <div class="card-label">💸 المصاريف</div>
        <div class="card-value number-fade-in">${{ totalExpenses }}</div>
        <div class="card-meta">
          {{ expensesData?.count || 0 }} معاملة
        </div>
      </div>
      <div class="card summary-card" :class="netSummaryClass">
        <div class="card-label">🏦 الصافي</div>
        <div class="card-value number-fade-in" :class="netValueClass">${{ netAmount }}</div>
        <div class="card-meta">{{ netLabel }}</div>
      </div>
    </div>

    <div v-if="lastUpdated" class="dashboard-timestamp">
      آخر تحديث: {{ lastUpdated }}
    </div>

    <div class="dashboard-grid">
      <div class="card">
        <h3>الأهداف النشطة</h3>
        <div v-if="!goals.length" class="empty-state">🎯 لا توجد أهداف</div>
        <div v-for="goal in topGoals" :key="goal.id" class="goal-item">
          <div class="goal-header">
            <span>{{ goal.name }}</span>
            <span class="goal-pct">{{ goalPercentage(goal) }}%</span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: goalPercentage(goal) + '%' }"
            ></div>
          </div>
          <div class="goal-amounts">
            ${{ goal.saved_amount.toFixed(2) }} /
            ${{ goal.target_amount.toFixed(2) }}
          </div>
        </div>
        <router-link to="/goals" class="card-link">عرض كل الأهداف &larr;</router-link>
      </div>

      <div class="card">
        <h3>آخر سجلات الدوام</h3>
        <div v-if="!allAttendance.length" class="empty-state">📋 لا توجد سجلات دوام</div>
        <div
          v-for="record in lastFiveAttendance"
          :key="record.id"
          class="attendance-item"
        >
          <div class="attendance-left">
            <div class="attendance-date">{{ formatDate(record.date) }}</div>
            <span class="status-badge" :class="'status-' + record.status">
              {{ statusLabel(record.status) }}
            </span>
          </div>
          <div class="attendance-hours">{{ record.hours_worked }} ساعة</div>
        </div>
        <router-link to="/attendance" class="card-link">عرض كل السجلات &larr;</router-link>
      </div>
    </div>

    <div class="dashboard-footer">
      <router-link to="/reports" class="btn btn-primary">
        عرض التقارير الكاملة
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import { useAuthStore } from "@/stores/auth"
import api from "@/utils/api"

const authStore = useAuthStore()
const period = ref("monthly")
const loading = ref(true)
const error = ref("")
const lastUpdated = ref("")

const salaryData = ref(null)
const expensesData = ref(null)
const goals = ref([])
const allAttendance = ref([])

function getPeriodStart() {
  const today = new Date()
  const yyyy = today.getFullYear()
  if (period.value === "weekly") {
    const day = today.getDay()
    const diff = day === 0 ? 6 : day - 1
    const monday = new Date(today)
    monday.setDate(today.getDate() - diff)
    const my = monday.getFullYear()
    const mmd = String(monday.getMonth() + 1).padStart(2, "0")
    const md = String(monday.getDate()).padStart(2, "0")
    return `${my}-${mmd}-${md}`
  }
  const mm = String(today.getMonth() + 1).padStart(2, "0")
  return `${yyyy}-${mm}-01`
}

const periodAttendance = computed(() => {
  const start = getPeriodStart()
  return allAttendance.value.filter(
    (r) => r.date >= start && r.status === "present"
  )
})

const totalHours = computed(() => {
  const sum = periodAttendance.value.reduce(
    (s, r) => s + (r.hours_worked || 0),
    0
  )
  return sum.toFixed(1)
})

const presentDays = computed(() => periodAttendance.value.length)

const earnedSalary = computed(() => {
  return salaryData.value?.earned_salary?.toFixed(2) || "0.00"
})

const totalExpenses = computed(() => {
  return expensesData.value?.total_amount?.toFixed(2) || "0.00"
})

const netAmount = computed(() => {
  const salary = salaryData.value?.earned_salary || 0
  const expenses = expensesData.value?.total_amount || 0
  return (salary - expenses).toFixed(2)
})

const netValueClass = computed(() => {
  const net = parseFloat(netAmount.value)
  return net >= 0 ? "text-success" : "text-danger"
})

const netSummaryClass = computed(() => {
  const net = parseFloat(netAmount.value)
  return net >= 0 ? "net-positive" : "net-negative"
})

const netLabel = computed(() => {
  const net = parseFloat(netAmount.value)
  return net >= 0 ? "فائض" : "عجز"
})

const topGoals = computed(() => goals.value.slice(0, 3))

function goalPercentage(goal) {
  if (!goal.target_amount) return 0
  return Math.min(
    Math.round((goal.saved_amount / goal.target_amount) * 100),
    100
  )
}

const lastFiveAttendance = computed(() => allAttendance.value.slice(0, 5))

function formatDate(dateStr) {
  if (!dateStr) return ""
  const d = new Date(dateStr)
  return d.toLocaleDateString("ar-EG", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

function statusLabel(status) {
  const labels = {
    present: "حاضر",
    absent: "غائب",
    holiday: "إجازة",
    late: "متأخر",
  }
  return labels[status] || status
}

async function fetchData() {
  loading.value = true
  error.value = ""
  try {
    const [salaryRes, expensesRes, goalsRes, attendanceRes] = await Promise.all([
      api.get("/salary"),
      api.get("/expenses/summary", { params: { period: period.value } }),
      api.get("/goals/"),
      api.get("/attendance/"),
    ])
    salaryData.value = salaryRes.data
    expensesData.value = expensesRes.data
    goals.value = goalsRes.data
    allAttendance.value = attendanceRes.data
    lastUpdated.value = new Date().toLocaleTimeString("ar-EG", {
      hour: "2-digit",
      minute: "2-digit",
    })
  } catch (e) {
    error.value = "حدث خطأ أثناء تحميل البيانات. يرجى المحاولة مرة أخرى."
  } finally {
    loading.value = false
  }
}

watch(period, () => {
  fetchData()
})

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.period-toggle {
  display: flex;
  gap: 8px;
  margin-bottom: 28px;
}

.toggle-btn {
  padding: 8px 22px;
  border: 1px solid var(--border);
  border-radius: 24px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition);
}

.toggle-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.toggle-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}

.net-positive {
  border-left-color: var(--success) !important;
}

.net-negative {
  border-left-color: var(--danger) !important;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 28px;
}

.empty-state {
  color: var(--text-secondary);
  padding: 24px 0;
  text-align: center;
  font-size: 0.9rem;
}

.goal-item {
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
  transition: background var(--transition);
}

.goal-item:last-of-type {
  border-bottom: none;
}

.goal-item:hover {
  background: rgba(99, 102, 241, 0.03);
  margin: 0 -8px;
  padding-left: 8px;
  padding-right: 8px;
  border-radius: var(--radius-sm);
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 6px;
}

.goal-pct {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 500;
}

.goal-amounts {
  font-size: 0.78rem;
  color: var(--text-secondary);
  margin-top: 6px;
}

.attendance-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
  transition: background var(--transition);
}

.attendance-item:last-of-type {
  border-bottom: none;
}

.attendance-item:hover {
  background: rgba(99, 102, 241, 0.03);
  margin: 0 -8px;
  padding-left: 8px;
  padding-right: 8px;
  border-radius: var(--radius-sm);
}

.attendance-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.attendance-date {
  font-size: 0.875rem;
  font-weight: 600;
}

.attendance-hours {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.card-link {
  display: inline-block;
  margin-top: 14px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent);
  transition: color var(--transition);
}

.card-link:hover {
  color: var(--accent-hover);
}

.dashboard-footer {
  text-align: center;
  max-width: 320px;
  margin: 0 auto;
}

.dashboard-footer .btn {
  text-decoration: none;
}

.dashboard-timestamp {
  text-align: center;
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .toggle-btn {
    min-height: 44px;
    padding: 8px 18px;
    font-size: 0.8rem;
  }
  .dashboard-footer {
    max-width: 100%;
  }
}
</style>

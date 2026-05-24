<template>
  <div class="view">
    <div class="page-header">
      <h1>التقارير</h1>
    </div>

    <div class="report-controls">
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
    </div>

    <div v-if="loading" class="loading">جاري تحميل البيانات...</div>
    <div v-if="error" class="error-msg">{{ error }}</div>

    <template v-if="!loading && !error">
      <div class="card chart-card">
        <h3>📊 الدخل مقابل المصاريف</h3>
        <div class="bar-chart">
          <div class="bar-row">
            <span class="bar-label">الدخل</span>
            <div class="bar-track">
              <div
                class="bar-fill bar-income"
                :style="{ width: incomeBarWidth + '%' }"
              ></div>
            </div>
            <span class="bar-value">${{ earnedSalary }}</span>
          </div>
          <div class="bar-row">
            <span class="bar-label">المصاريف</span>
            <div class="bar-track">
              <div
                class="bar-fill bar-expense"
                :style="{ width: expenseBarWidth + '%' }"
              ></div>
            </div>
            <span class="bar-value">${{ totalExpenses }}</span>
          </div>
        </div>
      </div>

      <div class="charts-grid">
        <div class="card chart-card">
          <h3>🍩 المصاريف حسب الفئة</h3>
          <div v-if="!categoryEntries.length" class="empty-state">
            لا توجد مصاريف في هذه الفترة
          </div>
          <template v-else>
            <div class="donut-wrapper">
              <div
                class="donut-chart"
                :style="{ background: conicGradient }"
              ></div>
              <div class="donut-hole">
                <span class="donut-total">${{ totalExpenses }}</span>
              </div>
            </div>
            <div class="chart-legend">
              <div
                v-for="entry in categoryEntries"
                :key="entry.name"
                class="legend-item"
              >
                <span
                  class="legend-color"
                  :style="{ backgroundColor: entry.color }"
                ></span>
                <span class="legend-name">{{ entry.name }}</span>
                <span class="legend-value">
                  ${{ (entry.amount ?? 0).toFixed(2) }} ({{ entry.percent }}%)
                </span>
              </div>
            </div>
          </template>
        </div>

        <div class="card chart-card">
          <h3>🎯 تقدم الأهداف</h3>
          <div v-if="!goals.length" class="empty-state">لا توجد أهداف</div>
          <div v-for="goal in goals" :key="goal.id" class="goal-row">
            <div class="goal-info">
              <span class="goal-name">{{ goal.name }}</span>
              <span class="goal-amounts">
                ${{ (goal.saved_amount ?? 0).toFixed(2) }} /
                ${{ (goal.target_amount ?? 0).toFixed(2) }}
              </span>
            </div>
            <div class="goal-bar-row">
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :class="goalColorClass(goal)"
                  :style="{ width: goalPercent(goal) + '%' }"
                ></div>
              </div>
              <span class="goal-percent">{{ goalPercent(goal) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import api from "@/utils/api"

const period = ref("monthly")
const loading = ref(true)
const error = ref("")

const salaryData = ref(null)
const expensesData = ref(null)
const goals = ref([])

const categoryColors = {
  طعام: "#FF6384",
  إيجار: "#36A2EB",
  مواصلات: "#FFCE56",
  ترفيه: "#4BC0C0",
  صحة: "#9966FF",
  أخرى: "#C9CBCF",
}

const extraColors = [
  "#FF9F40",
  "#8B5CF6",
  "#EC4899",
  "#10B981",
  "#F59E0B",
  "#3B82F6",
  "#EF4444",
  "#14B8A6",
  "#F97316",
  "#6366F1",
]

function getCategoryColor(category, index) {
  if (categoryColors[category]) return categoryColors[category]
  return extraColors[(index - Object.keys(categoryColors).length) % extraColors.length]
}

const earnedSalary = computed(() => {
  return salaryData.value?.earned_salary?.toFixed(2) || "0.00"
})

const totalExpenses = computed(() => {
  return expensesData.value?.total_amount?.toFixed(2) || "0.00"
})

const maxBarValue = computed(() => {
  return Math.max(
    salaryData.value?.earned_salary || 0,
    expensesData.value?.total_amount || 0,
    1
  )
})

const incomeBarWidth = computed(() => {
  return ((salaryData.value?.earned_salary || 0) / maxBarValue.value) * 100
})

const expenseBarWidth = computed(() => {
  return ((expensesData.value?.total_amount || 0) / maxBarValue.value) * 100
})

const categoryEntries = computed(() => {
  if (!expensesData.value?.by_category) return []
  const byCategory = expensesData.value.by_category
  const total = expensesData.value.total_amount || 1
  return Object.entries(byCategory)
    .map(([name, amount], idx) => ({
      name,
      amount,
      percent: Math.round((amount / total) * 100),
      color: getCategoryColor(name, idx),
    }))
    .sort((a, b) => b.amount - a.amount)
})

const conicGradient = computed(() => {
  const entries = categoryEntries.value
  if (!entries.length) return "conic-gradient(#e2e8f0 0deg 360deg)"

  let currentDeg = 0
  const total = expensesData.value?.total_amount || 1
  const segments = entries.map((entry) => {
    const deg = (entry.amount / total) * 360
    const segment = `${entry.color} ${currentDeg}deg ${currentDeg + deg}deg`
    currentDeg += deg
    return segment
  })
  return `conic-gradient(${segments.join(", ")})`
})

function goalPercent(goal) {
  if (!goal.target_amount) return 0
  return Math.min(
    Math.round((goal.saved_amount / goal.target_amount) * 100),
    100
  )
}

function goalColorClass(goal) {
  const pct = goalPercent(goal)
  if (pct >= 80) return "progress-high"
  if (pct >= 50) return "progress-mid"
  return "progress-low"
}

async function fetchData() {
  loading.value = true
  error.value = ""
  try {
    const [salaryRes, expensesRes, goalsRes] = await Promise.all([
      api.get("/salary"),
      api.get("/expenses/summary", { params: { period: period.value } }),
      api.get("/goals/"),
    ])
    salaryData.value = salaryRes.data
    expensesData.value = expensesRes.data
    goals.value = goalsRes.data
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
.report-controls {
  margin-bottom: 28px;
}

.period-toggle {
  display: flex;
  gap: 8px;
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

.chart-card {
  margin-bottom: 20px;
}

.chart-card h3 {
  margin-bottom: 20px;
  font-size: 1.05rem;
  color: var(--text-primary);
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.bar-label {
  min-width: 70px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.bar-track {
  flex: 1;
  height: 32px;
  background: var(--bg-primary);
  border-radius: 8px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 8px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 0;
}

.bar-income {
  background: linear-gradient(135deg, var(--success), #34D399);
}

.bar-expense {
  background: linear-gradient(135deg, var(--danger), #F87171);
}

.bar-value {
  min-width: 90px;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-primary);
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 28px;
}

.donut-wrapper {
  position: relative;
  width: 180px;
  height: 180px;
  margin: 0 auto 20px;
}

.donut-chart {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.donut-hole {
  position: absolute;
  width: 100px;
  height: 100px;
  background: var(--bg-card);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.donut-total {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--text-primary);
}

.chart-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
}

.legend-name {
  min-width: 60px;
  color: var(--text-primary);
  font-weight: 500;
}

.legend-value {
  color: var(--text-secondary);
}

.empty-state {
  color: var(--text-secondary);
  padding: 32px 0;
  text-align: center;
  font-size: 0.9rem;
}

.goal-row {
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
  transition: background var(--transition);
}

.goal-row:last-of-type {
  border-bottom: none;
}

.goal-row:hover {
  background: rgba(99, 102, 241, 0.03);
  margin: 0 -8px;
  padding-left: 8px;
  padding-right: 8px;
  border-radius: var(--radius-sm);
}

.goal-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.goal-name {
  font-size: 0.9rem;
  font-weight: 600;
}

.goal-amounts {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.goal-bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 10px;
}

.progress-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-high {
  background: var(--success);
}

.progress-mid {
  background: var(--warning);
}

.progress-low {
  background: var(--danger);
}

.goal-percent {
  min-width: 40px;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  .bar-label {
    min-width: 55px;
    font-size: 0.8rem;
  }
  .bar-value {
    min-width: 70px;
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .toggle-btn {
    min-height: 44px;
    padding: 8px 16px;
    font-size: 0.8rem;
  }
  .donut-wrapper {
    width: 140px;
    height: 140px;
  }
  .donut-hole {
    width: 80px;
    height: 80px;
  }
  .donut-total {
    font-size: 0.85rem;
  }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  gap: 12px;
}

.spinner {
  width: 40px; height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

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

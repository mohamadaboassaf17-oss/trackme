<template>
  <div class="view">
    <div class="page-header">
      <h1>الدوام</h1>
      <p>تتبع ساعات العمل والحضور</p>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="success" class="record-success">{{ success }}</div>

    <div class="attendance-grid">
      <div class="card">
        <h2>{{ editingId ? 'تعديل سجل الدوام' : 'تسجيل الدوام' }}</h2>

        <div class="quick-log-section">
          <button class="quick-log-btn" @click="quickLog" :disabled="quickLogLoading">
            {{ quickLogLoading ? 'جاري التسجيل...' : 'تسجيل يوم بالوقت الافتراضي' }}
          </button>
          <transition name="quick-msg-fade">
            <div v-if="quickLogMessage" :class="['quick-log-msg', 'quick-log-msg--' + quickLogMessage.type]">
              {{ quickLogMessage.text }}
            </div>
          </transition>
        </div>

        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="date">التاريخ</label>
            <input id="date" v-model="form.date" type="date" required />
          </div>

          <div class="form-group">
            <label for="status">الحالة</label>
            <select id="status" v-model="form.status" required>
              <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>

          <template v-if="form.status === 'present'">
            <div class="form-group">
              <label for="start_time">وقت البداية</label>
              <input id="start_time" v-model="form.start_time" type="time" />
            </div>

            <div class="form-group">
              <label for="end_time">وقت النهاية</label>
              <input id="end_time" v-model="form.end_time" type="time" />
            </div>

            <div v-if="computedHours !== null" class="hours-display">
              ساعات العمل: {{ computedHours }}
            </div>
          </template>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? 'جاري الحفظ...' : editingId ? 'تحديث' : 'حفظ' }}
            </button>
            <button v-if="editingId" type="button" class="btn btn-cancel" @click="resetForm">
              إلغاء
            </button>
          </div>
        </form>
      </div>

      <div class="card">
        <h2>سجلات الدوام</h2>

        <div v-if="recordsLoading" class="loading">جاري التحميل...</div>

        <div v-else-if="records.length === 0" class="empty-state">
          لا توجد سجلات دوام بعد
        </div>

        <div v-else class="records-list">
          <div v-for="record in records" :key="record.id" class="record-item">
            <div class="record-body">
              <div class="record-date">{{ formatDate(record.date) }}</div>
              <div class="record-times" v-if="record.start_time">
                {{ fmtTime(record.start_time) }} - {{ fmtTime(record.end_time) }}
              </div>
              <div class="record-hours">{{ fmtHours(record.hours_worked) }} ساعة</div>
            </div>
            <div class="record-meta">
              <span class="status-badge" :class="'status-' + record.status">
                {{ statusLabels[record.status] || record.status }}
              </span>
            </div>
            <div class="record-actions">
              <button class="btn-link" @click="editRecord(record)">تعديل</button>
              <button class="btn-link btn-link-delete" @click="confirmDelete(record)">حذف</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal-card">
        <p>هل أنت متأكد من حذف هذا السجل؟</p>
        <div class="modal-actions">
          <button class="btn btn-danger" @click="handleDelete">نعم، احذف</button>
          <button class="btn btn-cancel" @click="deleteTarget = null">إلغاء</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/utils/api'
import { safeArray } from '@/utils/helpers'

const statusOptions = [
  { value: 'present', label: 'حضر' },
  { value: 'absent', label: 'غائب' },
  { value: 'holiday', label: 'إجازة' },
]

const statusLabels = {
  present: 'حضر',
  absent: 'غائب',
  holiday: 'إجازة',
}

const defaultForm = () => ({
  date: todayString(),
  status: 'present',
  start_time: '',
  end_time: '',
})

const form = ref(defaultForm())
const records = ref([])
const recordsLoading = ref(false)
const error = ref('')
const success = ref('')
const submitting = ref(false)
const editingId = ref(null)
const deleteTarget = ref(null)
const quickLogMessage = ref(null)
const quickLogLoading = ref(false)

let quickLogTimer = null

const computedHours = computed(() => {
  if (!form.value.start_time || !form.value.end_time) return null
  const [sh, sm] = form.value.start_time.split(':').map(Number)
  const [eh, em] = form.value.end_time.split(':').map(Number)
  let diff = (eh * 60 + em) - (sh * 60 + sm)
  if (diff < 0) diff += 24 * 60
  return ((diff / 60) ?? 0).toFixed(1)
})

function todayString() {
  return new Date().toISOString().slice(0, 10)
}

function calcHours(start, end) {
  const [sh, sm] = start.split(':').map(Number)
  const [eh, em] = end.split(':').map(Number)
  let diff = (eh * 60 + em) - (sh * 60 + sm)
  if (diff < 0) diff += 24 * 60
  return parseFloat(((diff / 60) ?? 0).toFixed(1))
}

async function fetchRecords() {
  recordsLoading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/attendance/')
    records.value = safeArray(data)
  } catch (e) {
    error.value = e.response?.data?.detail || 'حدث خطأ أثناء جلب السجلات'
  } finally {
    recordsLoading.value = false
  }
}

async function fetchShiftDefaults() {
  try {
    const { data } = await api.get('/settings/shift-defaults')
    return data
  } catch {
    return null
  }
}

async function quickLog() {
  quickLogMessage.value = null
  quickLogLoading.value = true
  try {
    const defaults = await fetchShiftDefaults()
    const start = defaults?.default_start_time?.slice(0, 5)
    const end = defaults?.default_end_time?.slice(0, 5)

    if (!start || !end) {
      quickLogMessage.value = {
        type: 'warning',
        text: 'يرجى تحديد وقت الدوام الافتراضي في الإعدادات أولاً'
      }
      return
    }

    await api.post('/attendance/', {
      date: todayString(),
      status: 'present',
      start_time: start,
      end_time: end,
      hours_worked: calcHours(start, end),
    })

    quickLogMessage.value = {
      type: 'success',
          text: 'تم تسجيل يوم عمل بنجاح'
    }

    if (quickLogTimer) clearTimeout(quickLogTimer)
    quickLogTimer = setTimeout(() => {
      if (quickLogMessage.value?.type === 'success') {
        quickLogMessage.value = null
      }
    }, 3000)

    await fetchRecords()
  } catch (e) {
    error.value = e.response?.data?.detail || 'حدث خطأ أثناء تسجيل الدوام السريع'
  } finally {
    quickLogLoading.value = false
  }
}

async function handleSubmit() {
  error.value = ''
  submitting.value = true
  try {
    const payload = {
      date: form.value.date,
      status: form.value.status,
      hours_worked: 0,
      start_time: null,
      end_time: null,
    }

    if (form.value.status === 'present') {
      if (form.value.start_time) payload.start_time = form.value.start_time
      if (form.value.end_time) payload.end_time = form.value.end_time
      if (form.value.start_time && form.value.end_time) {
        payload.hours_worked = parseFloat(computedHours.value)
      }
    }

    if (editingId.value) {
      await api.put(`/attendance/${editingId.value}`, payload)
    } else {
      await api.post('/attendance/', payload)
    }

    resetForm()
    await fetchRecords()
  } catch (e) {
    error.value = e.response?.data?.detail || 'حدث خطأ أثناء حفظ السجل'
  } finally {
    submitting.value = false
  }
}

function editRecord(record) {
  editingId.value = record.id
  form.value = {
    date: record.date,
    status: record.status,
    start_time: record.start_time ? record.start_time.slice(0, 5) : '',
    end_time: record.end_time ? record.end_time.slice(0, 5) : '',
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function confirmDelete(record) {
  deleteTarget.value = record
}

async function handleDelete() {
  if (!deleteTarget.value) return
  error.value = ''
  try {
    await api.delete(`/attendance/${deleteTarget.value.id}`)
    if (editingId.value === deleteTarget.value.id) resetForm()
    deleteTarget.value = null
    await fetchRecords()
  } catch (e) {
    error.value = e.response?.data?.detail || 'حدث خطأ أثناء حذف السجل'
    deleteTarget.value = null
  }
}

function resetForm() {
  form.value = defaultForm()
  editingId.value = null
  error.value = ''
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  return `${parts[2]}/${parts[1]}/${parts[0]}`
}

function fmtTime(timeStr) {
  if (!timeStr) return '--:--'
  return timeStr.slice(0, 5)
}

function fmtHours(hours) {
  if (hours == null) return '0.0'
  return (Number(hours) ?? 0).toFixed(1)
}

onMounted(async () => {
  await fetchRecords()
  const defaults = await fetchShiftDefaults()
  if (defaults?.default_start_time && defaults?.default_end_time) {
    form.value.start_time = defaults.default_start_time.slice(0, 5)
    form.value.end_time = defaults.default_end_time.slice(0, 5)
  }
})
</script>

<style scoped>
.attendance-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}

.card h2 {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.quick-log-section {
  margin-bottom: 20px;
  text-align: center;
}

.quick-log-btn {
  width: 100%;
  padding: 14px 24px;
  font-size: 1.05rem;
  font-weight: 700;
  color: white;
  background: var(--accent);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition);
  box-shadow: 0 2px 8px color-mix(in srgb, var(--accent) 30%, transparent);
}

.quick-log-btn:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px color-mix(in srgb, var(--accent) 45%, transparent);
}

.quick-log-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

.quick-log-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.quick-log-msg {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.9rem;
}

.quick-log-msg--success {
  background-color: var(--success-light);
  color: var(--success);
  border: 1px solid color-mix(in srgb, var(--success) 20%, transparent);
}

.quick-log-msg--warning {
  background-color: var(--warning-light);
  color: var(--warning);
  border: 1px solid color-mix(in srgb, var(--warning) 20%, transparent);
}

.quick-msg-fade-enter-active {
  animation: quickMsgIn 0.3s ease-out;
}

.quick-msg-fade-leave-active {
  animation: quickMsgIn 0.2s ease-in reverse;
}

@keyframes quickMsgIn {
  from { opacity: 0; transform: translateY(-8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.hours-display {
  background: var(--accent-light);
  color: var(--accent);
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-weight: 700;
  font-size: 0.95rem;
  margin-bottom: 16px;
  text-align: center;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.form-actions .btn {
  flex: 1;
}

.btn-cancel {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 10px 24px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
}

.btn-cancel:hover {
  background-color: var(--border);
}

.empty-state {
  text-align: center;
  padding: 48px 16px;
  color: var(--text-secondary);
  font-size: 1rem;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
  transition: all var(--transition);
}

.record-item:hover {
  background: color-mix(in srgb, var(--accent) 3%, transparent);
  border-color: var(--accent);
}

.record-body {
  flex: 1;
  min-width: 0;
}

.record-date {
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--text-primary);
}

.record-times {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 3px;
}

.record-hours {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 2px;
}

.record-meta {
  flex-shrink: 0;
}

.record-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn-link-delete {
  color: var(--danger) !important;
}

.btn-link-delete:hover {
  opacity: 0.8;
}

.records-list {
  max-height: 520px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .attendance-grid {
    grid-template-columns: 1fr;
  }
  .record-item {
    flex-wrap: wrap;
  }
  .record-actions {
    width: 100%;
    justify-content: flex-start;
    margin-top: 8px;
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

.record-success {
  animation: pulseSuccess 0.4s ease-out;
  background: var(--success-light);
  color: var(--success);
  border: 1px solid var(--success);
  padding: 12px 16px;
  border-radius: 10px;
  margin-bottom: 16px;
  font-weight: 500;
}
@keyframes pulseSuccess {
  0% { transform: scale(0.95); opacity: 0.6; }
  50% { transform: scale(1.03); }
  100% { transform: scale(1); opacity: 1; }
}

/* === Phase 4 — Attendance Improvements === */

/* Record items: gold accent border on hover */
.record-item {
  border-right: 3px solid transparent;
  transition: all var(--transition);
}
.record-item:hover {
  border-right-color: var(--accent);
}

/* Quick log button: gold gradient variant */
.quick-log-btn {
  background: linear-gradient(135deg, var(--accent), var(--gold));
  box-shadow: 0 4px 16px color-mix(in srgb, var(--accent) 30%, transparent);
}
.quick-log-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--accent-hover), var(--gold-dark));
  box-shadow: 0 6px 24px color-mix(in srgb, var(--accent) 45%, transparent);
}

/* Hours display: warmer style */
.hours-display {
  background: color-mix(in srgb, var(--gold) 12%, transparent);
  color: var(--gold-dark);
  border: 1px solid color-mix(in srgb, var(--gold) 20%, transparent);
}

/* Card headers with gold underline accent */
.card h2 {
  border-bottom: 2px solid;
  border-image: linear-gradient(to left, var(--accent), var(--gold), transparent) 1;
}
</style>

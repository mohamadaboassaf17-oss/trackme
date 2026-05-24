<template>
  <div class="view">
    <div class="page-header">
      <h1>الأهداف</h1>
      <p>تتبع أهداف الادخار</p>
    </div>

    <div class="summary-cards">
      <div class="card summary-card">
        <div class="card-label">الراتب المكتسب</div>
        <div class="card-value number-fade-in">${{ (earnedSalary ?? 0).toFixed(2) }}</div>
      </div>
      <div class="card summary-card">
        <div class="card-label">إجمالي المصاريف</div>
        <div class="card-value number-fade-in">${{ (totalExpenses ?? 0).toFixed(2) }}</div>
      </div>
      <div class="card summary-card" :class="{ 'net-negative': availableForSaving < 0 }">
        <div class="card-label">المتاح للادخار</div>
        <div class="card-value number-fade-in" :class="availableForSaving >= 0 ? 'text-success' : 'text-danger'">
          ${{ (availableForSaving ?? 0).toFixed(2) }}
        </div>
        <div v-if="availableForSaving < 0" class="card-meta" style="color: var(--danger);">تجاوزت الميزانية</div>
      </div>
    </div>

    <div class="card form-card">
      <h2>{{ editingGoal ? 'تعديل الهدف' : 'إضافة هدف جديد' }}</h2>
      <form @submit.prevent="handleSubmit" class="goal-form">
        <div class="form-group">
          <label for="goalName">اسم الهدف</label>
          <input
            id="goalName"
            v-model="form.name"
            type="text"
            required
            placeholder="مثال: شراء سيارة"
          />
        </div>
        <div class="form-group">
          <label for="goalTarget">المبلغ المستهدف ($)</label>
          <input
            id="goalTarget"
            v-model.number="form.target_amount"
            type="number"
            step="0.01"
            min="0.01"
            required
          />
        </div>
        <div class="form-group">
          <label for="goalDue">تاريخ الاستحقاق</label>
          <input id="goalDue" v-model="form.due_date" type="date" required />
        </div>
        <div class="form-group">
          <label for="goalSaved">المبلغ المدخر حالياً ($)</label>
          <input
            id="goalSaved"
            v-model.number="form.saved_amount"
            type="number"
            step="0.01"
            min="0"
          />
        </div>
        <div v-if="formError" class="error-msg">{{ formError }}</div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ editingGoal ? 'تحديث' : 'حفظ' }}
          </button>
          <button
            v-if="editingGoal"
            type="button"
            class="btn btn-cancel"
            @click="cancelEdit"
          >
            إلغاء
          </button>
        </div>
      </form>
    </div>

    <div v-if="loading" class="loading">جاري التحميل...</div>

    <div v-else-if="goals.length === 0" class="card">
      <p class="text-center" style="color: var(--text-secondary); padding: 24px;">لا توجد أهداف حالياً</p>
    </div>

    <div v-else class="goals-grid">
      <div v-for="goal in goals" :key="goal.id" class="card goal-card">
        <div class="goal-header">
          <h3>{{ goal.name }}</h3>
          <div class="goal-badges">
            <span
              v-if="goal.saved_amount > goal.target_amount"
              class="badge badge-gold"
            >
              تم تحقيق الهدف!
            </span>
            <span
              v-else-if="goalProgress(goal) > 90"
              class="badge badge-success"
            >
              شارف على الاكتمال!
            </span>
          </div>
        </div>

        <div class="goal-details">
          <div class="goal-detail">
            <span class="label">المبلغ المستهدف:</span>
            <span class="value">${{ (goal.target_amount ?? 0).toFixed(2) }}</span>
          </div>
          <div class="goal-detail">
            <span class="label">المبلغ المدخر:</span>
            <span class="value">${{ (goal.saved_amount ?? 0).toFixed(2) }}</span>
          </div>
          <div class="goal-detail">
            <span class="label">تاريخ الاستحقاق:</span>
            <span class="value">{{ formatDate(goal.due_date) }}</span>
          </div>
        </div>

        <div class="progress-container">
          <div class="progress-label">
            <span>{{ goalProgress(goal) }}% مكتمل</span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :class="progressColorClass(goal)"
              :style="{ width: Math.min(goalProgress(goal), 100) + '%' }"
            ></div>
          </div>
        </div>

        <div class="goal-actions">
          <button class="btn btn-primary btn-sm" @click="editGoal(goal)">
            تعديل
          </button>
          <button class="btn btn-danger btn-sm" @click="confirmDelete(goal)">
            حذف
          </button>
        </div>
      </div>
    </div>

    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="showDeleteConfirm = false">
      <div class="modal-card">
        <h3>تأكيد الحذف</h3>
        <p>هل أنت متأكد من حذف هذا الهدف؟</p>
        <div class="modal-actions">
          <button class="btn btn-danger" @click="deleteGoal">
            حذف
          </button>
          <button class="btn btn-cancel" @click="showDeleteConfirm = false">
            إلغاء
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/utils/api";

export default {
  name: "GoalsView",
  data() {
    return {
      goals: [],
      earnedSalary: 0,
      totalExpenses: 0,
      loading: false,
      saving: false,
      formError: "",
      editingGoal: null,
      showDeleteConfirm: false,
      deleteTarget: null,
      form: {
        name: "",
        target_amount: 0,
        due_date: "",
        saved_amount: 0,
      },
    };
  },
  computed: {
    availableForSaving() {
      return this.earnedSalary - this.totalExpenses;
    },
  },
  created() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      this.loading = true;
      try {
        const [goalsRes, salaryRes, expensesRes] = await Promise.all([
          api.get("/goals/"),
          api.get("/salary"),
          api.get("/expenses/summary", { params: { period: "monthly" } }),
        ]);
        this.goals = goalsRes.data;
        this.earnedSalary = salaryRes.data.earned_salary || 0;
        this.totalExpenses = expensesRes.data.total_amount || 0;
      } catch (err) {
        console.error("فشل في تحميل البيانات", err);
      } finally {
        this.loading = false;
      }
    },
    async handleSubmit() {
      this.saving = true;
      this.formError = "";
      try {
        if (this.editingGoal) {
          await api.put(`/goals/${this.editingGoal.id}`, this.form);
        } else {
          await api.post("/goals/", this.form);
        }
        this.resetForm();
        await this.fetchData();
      } catch (err) {
        this.formError =
          err.response?.data?.detail || "فشل في حفظ الهدف";
      } finally {
        this.saving = false;
      }
    },
    editGoal(goal) {
      this.editingGoal = goal;
      this.form = {
        name: goal.name,
        target_amount: goal.target_amount,
        due_date: goal.due_date,
        saved_amount: goal.saved_amount,
      };
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
    cancelEdit() {
      this.resetForm();
    },
    resetForm() {
      this.editingGoal = null;
      this.form = {
        name: "",
        target_amount: 0,
        due_date: "",
        saved_amount: 0,
      };
      this.formError = "";
    },
    confirmDelete(goal) {
      this.deleteTarget = goal;
      this.showDeleteConfirm = true;
    },
    async deleteGoal() {
      if (!this.deleteTarget) return;
      try {
        await api.delete(`/goals/${this.deleteTarget.id}`);
        this.showDeleteConfirm = false;
        this.deleteTarget = null;
        if (this.editingGoal?.id === this.deleteTarget?.id) {
          this.resetForm();
        }
        await this.fetchData();
      } catch (err) {
        console.error("فشل في حذف الهدف", err);
      }
    },
    goalProgress(goal) {
      if (goal.target_amount <= 0) return 0;
      return Math.round((goal.saved_amount / goal.target_amount) * 100);
    },
    progressColorClass(goal) {
      const pct = this.goalProgress(goal);
      if (pct > 50) return "progress-green";
      if (pct > 25) return "progress-orange";
      return "progress-red";
    },
    formatDate(dateStr) {
      if (!dateStr) return "";
      const d = new Date(dateStr);
      return d.toLocaleDateString("ar-EG", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    },
  },
};
</script>

<style scoped>
.form-card {
  margin-bottom: 28px;
}

.form-card h2 {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.goal-form {
  max-width: 480px;
}

.form-actions {
  display: flex;
  gap: 12px;
  align-items: center;
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

.btn-sm {
  padding: 8px 16px;
  font-size: 0.85rem;
  width: auto;
}

.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-success {
  background-color: var(--success-light);
  color: var(--success);
}

.badge-gold {
  background-color: var(--warning-light);
  color: #a16207;
}

[data-theme="dark"] .badge-gold {
  color: #FBBF24;
}

.goals-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 28px;
}

@media (max-width: 768px) {
  .goals-grid {
    grid-template-columns: 1fr;
  }
}

.goal-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.goal-card h3 {
  font-size: 1.1rem;
  font-weight: 700;
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.goal-badges {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

.goal-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.goal-detail {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.goal-detail .label {
  color: var(--text-secondary);
}

.goal-detail .value {
  font-weight: 600;
}

.progress-container {
  margin-top: 4px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 6px;
  font-weight: 500;
}

.progress-bar {
  height: 10px;
}

.progress-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-green {
  background-color: var(--success);
}

.progress-orange {
  background-color: var(--warning);
}

.progress-red {
  background-color: var(--danger);
}

.goal-actions {
  display: flex;
  gap: 8px;
  margin-top: 6px;
}

.net-negative {
  border-left-color: var(--danger) !important;
}

.modal-card h3 {
  border-bottom: none;
  margin-bottom: 8px;
  padding-bottom: 0;
}

.loading-state, .empty-state {
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
</style>

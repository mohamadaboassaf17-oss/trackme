<template>
  <div class="view">
    <div class="page-header">
      <h1>المصاريف</h1>
      <p>إدارة المصاريف الشخصية</p>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <div class="expenses-grid">
      <div class="card">
        <h2>{{ isEditing ? "تعديل مصروف" : "إضافة مصروف جديد" }}</h2>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>التاريخ</label>
            <input type="date" v-model="form.date" required />
          </div>
          <div class="form-group">
            <label>المبلغ ($)</label>
            <input type="number" v-model="form.amount" step="0.01" min="0" required />
          </div>
          <div class="form-group">
            <label>الفئة</label>
            <select v-model="form.category" @change="onCategoryChange" required>
              <option v-for="cat in defaultCategories" :key="cat" :value="cat">{{ cat }}</option>
              <option value="__custom__">+ إضافة فئة جديدة...</option>
            </select>
            <input
              v-if="showCustomCategory"
              type="text"
              v-model="customCategoryName"
              placeholder="اسم الفئة الجديدة..."
              class="custom-category-input"
            />
          </div>
          <div class="form-group">
            <label>ملاحظة</label>
            <textarea v-model="form.note" rows="2" placeholder="ملاحظة اختيارية..."></textarea>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? "جاري الحفظ..." : isEditing ? "تحديث" : "حفظ" }}
            </button>
            <button
              v-if="isEditing"
              type="button"
              class="btn btn-cancel"
              @click="resetForm"
            >
              إلغاء
            </button>
          </div>
        </form>
      </div>

      <div class="expenses-list-section">
        <div class="card summary-card-compact">
          <div class="summary-header">
            <h3>ملخص المصاريف</h3>
            <select v-model="summaryPeriod" @change="loadSummary" class="period-select">
              <option value="weekly">هذا الأسبوع</option>
              <option value="monthly">هذا الشهر</option>
            </select>
          </div>
          <div v-if="summary" class="summary-body">
            <div class="summary-total">
              <span>إجمالي المصاريف:</span>
              <span class="amount-danger">${{ (summary.total_amount ?? 0).toFixed(2) }}</span>
            </div>
            <div class="summary-breakdown" v-if="summary.by_category && Object.keys(summary.by_category).length">
              <div
                v-for="(amount, cat) in summary.by_category"
                :key="cat"
                class="breakdown-item"
              >
                <span class="badge" :style="{ backgroundColor: categoryColor(cat) }">{{ cat }}</span>
                <span class="amount-danger">${{ (amount ?? 0).toFixed(2) }}</span>
              </div>
            </div>
            <div v-else class="no-data">لا توجد مصاريف في هذه الفترة</div>
          </div>
        </div>

        <div class="card">
          <h3>قائمة المصاريف</h3>
          <div v-if="loading" class="loading">جاري التحميل...</div>
          <div v-else-if="expenses.length === 0" class="no-data">لا توجد مصاريف مسجلة</div>
          <div v-else class="expense-list">
            <div v-for="expense in expenses" :key="expense.id" class="expense-item">
              <div class="expense-info">
                <div class="expense-header">
                  <span class="expense-date">{{ formatDate(expense.date) }}</span>
                  <span class="badge" :style="{ backgroundColor: categoryColor(expense.category) }">
                    {{ expense.category }}
                  </span>
                </div>
                <p v-if="expense.note" class="expense-note">{{ expense.note }}</p>
              </div>
              <div class="expense-actions">
                <span class="amount-danger">${{ (expense.amount ?? 0).toFixed(2) }}</span>
                <button class="btn-link" @click="editExpense(expense)">تعديل</button>
                <button class="btn-link btn-delete" @click="confirmDelete(expense)">حذف</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="showDeleteConfirm = false">
      <div class="modal-card">
        <p>هل أنت متأكد من حذف هذا المصروف؟</p>
        <div class="modal-actions">
          <button class="btn btn-danger" @click="handleDelete" :disabled="deleting">
            {{ deleting ? "جاري الحذف..." : "حذف" }}
          </button>
          <button class="btn btn-cancel" @click="showDeleteConfirm = false">إلغاء</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/utils/api";

const DEFAULT_CATEGORIES = ["طعام", "إيجار", "مواصلات", "ترفيه", "صحة", "أخرى"];

const CATEGORY_COLORS = {
  طعام: "#f59e0b",
  إيجار: "#6366f1",
  مواصلات: "#06b6d4",
  ترفيه: "#8b5cf6",
  صحة: "#10b981",
  أخرى: "#6b7280",
};

export default {
  name: "ExpensesView",
  data() {
    return {
      expenses: [],
      summary: null,
      summaryPeriod: "monthly",
      form: {
        date: new Date().toISOString().slice(0, 10),
        amount: "",
        category: "",
        note: "",
      },
      defaultCategories: DEFAULT_CATEGORIES,
      showCustomCategory: false,
      customCategoryName: "",
      isEditing: false,
      editingId: null,
      loading: false,
      saving: false,
      error: "",
      showDeleteConfirm: false,
      deleteTarget: null,
      deleting: false,
    };
  },
  mounted() {
    this.loadExpenses();
    this.loadSummary();
  },
  methods: {
    formatDate(dateStr) {
      const d = new Date(dateStr);
      return d.toLocaleDateString("ar-SA", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    },
    categoryColor(cat) {
      return CATEGORY_COLORS[cat] || this.hashColor(cat);
    },
    hashColor(str) {
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
      }
      const h = Math.abs(hash) % 360;
      return `hsl(${h}, 55%, 50%)`;
    },
    onCategoryChange() {
      this.showCustomCategory = this.form.category === "__custom__";
    },
    resetForm() {
      this.form = {
        date: new Date().toISOString().slice(0, 10),
        amount: "",
        category: "",
        note: "",
      };
      this.showCustomCategory = false;
      this.customCategoryName = "";
      this.isEditing = false;
      this.editingId = null;
      this.error = "";
    },
    async loadExpenses() {
      this.loading = true;
      try {
        const res = await api.get("/expenses/");
        this.expenses = res.data;
      } catch (err) {
        this.error = err.response?.data?.detail || "حدث خطأ أثناء تحميل المصاريف";
      } finally {
        this.loading = false;
      }
    },
    async loadSummary() {
      try {
        const res = await api.get("/expenses/summary", {
          params: { period: this.summaryPeriod },
        });
        this.summary = res.data;
      } catch {
        this.summary = null;
      }
    },
    async handleSubmit() {
      this.error = "";

      let category = this.form.category;
      if (category === "__custom__") {
        category = this.customCategoryName.trim();
        if (!category) {
          this.error = "الرجاء إدخال اسم الفئة الجديدة";
          return;
        }
      }
      if (!category) {
        this.error = "الرجاء اختيار الفئة";
        return;
      }

      const payload = {
        date: this.form.date,
        amount: parseFloat(this.form.amount),
        category,
        note: this.form.note || null,
      };

      this.saving = true;
      try {
        if (this.isEditing) {
          await api.put(`/expenses/${this.editingId}`, payload);
        } else {
          await api.post("/expenses/", payload);
        }

        if (category !== "__custom__" && !this.defaultCategories.includes(category)) {
          this.defaultCategories.push(category);
        }

        this.resetForm();
        await this.loadExpenses();
        await this.loadSummary();
      } catch (err) {
        this.error = err.response?.data?.detail || "حدث خطأ أثناء حفظ المصروف";
      } finally {
        this.saving = false;
      }
    },
    editExpense(expense) {
      this.isEditing = true;
      this.editingId = expense.id;
      this.form.date = expense.date;
      this.form.amount = expense.amount.toString();
      this.form.category = expense.category;
      this.form.note = expense.note || "";
      this.showCustomCategory = false;
      this.error = "";
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
    confirmDelete(expense) {
      this.deleteTarget = expense;
      this.showDeleteConfirm = true;
    },
    async handleDelete() {
      if (!this.deleteTarget) return;
      this.deleting = true;
      try {
        await api.delete(`/expenses/${this.deleteTarget.id}`);
        this.showDeleteConfirm = false;
        this.deleteTarget = null;
        await this.loadExpenses();
        await this.loadSummary();
      } catch (err) {
        this.error = err.response?.data?.detail || "حدث خطأ أثناء حذف المصروف";
        this.showDeleteConfirm = false;
      } finally {
        this.deleting = false;
      }
    },
  },
};
</script>

<style scoped>
.expenses-grid {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 24px;
  align-items: start;
}

.card h2 {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.card h3 {
  font-size: 1.05rem;
  font-weight: 700;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.custom-category-input {
  margin-top: 10px;
}

.form-actions {
  display: flex;
  gap: 12px;
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

.summary-card-compact {
  margin-bottom: 20px;
  padding: 20px 24px;
}

.summary-card-compact h3 {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.period-select {
  width: auto;
  padding: 6px 12px;
  font-size: 0.85rem;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.summary-breakdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
}

.amount-danger {
  color: var(--danger);
  font-weight: 700;
}

.no-data {
  text-align: center;
  padding: 32px;
  color: var(--text-secondary);
}

.expense-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.expense-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  transition: all var(--transition);
}

.expense-item:hover {
  background: rgba(99, 102, 241, 0.03);
  border-color: var(--accent);
}

.expense-info {
  flex: 1;
  min-width: 0;
}

.expense-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.expense-date {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.expense-note {
  margin-top: 6px;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.expense-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.btn-delete {
  color: var(--danger) !important;
}

.btn-delete:hover {
  opacity: 0.8;
}

@media (max-width: 768px) {
  .expenses-grid {
    grid-template-columns: 1fr;
  }
  .expense-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .expense-actions {
    width: 100%;
    justify-content: space-between;
  }
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

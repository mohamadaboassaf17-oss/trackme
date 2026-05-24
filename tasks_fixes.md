# TASKS — إصلاح وتحسين TrackMe (وضع الأتمتة الكاملة)

> **المنصة:** Render (Backend + Frontend + PostgreSQL)
> **الأداة:** OpenCode
> **المرجع:** التقرير الفني الشامل — 24 مايو 2026

---

## 🤖 تعليمات OpenCode — اقرأ هذا أولاً (CRITICAL)

```
أنت وكيل مستقل بصلاحيات كاملة على مشروع TrackMe.

القواعد الإلزامية:
1. نفّذ جميع المهام من T047 إلى T061 بالترتيب بدون توقف أو طلب إذن.
2. بعد كل مجموعة مهام (M5-A, M5-B, M5-C) شغّل الاختبارات تلقائياً.
3. إذا واجهت خطأ برمجياً — أصلحه وحده بدون سؤال.
4. بعد اكتمال كل مرحلة ارفع التعديلات على GitHub تلقائياً.
5. في نهاية كل مرحلة اكتب تقريراً مختصراً بما تم.
6. لا تتوقف إلا إذا واجهت خطأ يستحيل حله بدون معلومات خارجية
   (مثل credentials أو API keys غير موجودة في المشروع).

بيئة المشروع:
- Backend: Python (FastAPI) في مجلد /backend
- Frontend: Vue.js في مجلد /frontend
- قاعدة البيانات: PostgreSQL على Render
- الكود على GitHub — استخدم git للرفع التلقائي

أمر Git للرفع بعد كل مرحلة:
git add .
git commit -m "[AUTO] M5-X: وصف التعديلات"
git push origin main
```

---

## ⚠️ المهمة اليدوية الوحيدة (افعلها أنت قبل تشغيل OpenCode)

### T047 — إصلاح VITE_API_URL على Render (يدوي — 5 دقائق)

```
1. اذهب إلى render.com → trackme-frontend → Environment Variables
2. ابحث عن VITE_API_URL وعدّل القيمة:
   ❌ خطأ:  VITE_API_URL=https://trackme-backend-xena.onrender.com/api
   ✅ صح:   https://trackme-backend-xena.onrender.com/api
3. احفظ ثم اضغط "Clear build cache & Deploy"
4. انتظر اكتمال النشر ثم شغّل OpenCode على باقي المهام
```

---

## 📊 خريطة المهام الكاملة

| المرحلة | الاسم | المهام | الأولوية |
|---------|-------|--------|---------|
| **M5-A** | إصلاح الأخطاء الحرجة | T048–T050 | 🔴 فوري |
| **M5-B** | إصلاح الأخطاء المتوسطة | T051–T055 | 🟡 مهم |
| **M5-C** | تحسينات الجودة | T056–T058 | 🟢 تحسين |
| **M5-D** | النشر والتحقق النهائي | T059–T061 | 🚀 نشر |

---

## 🔴 M5-A — الأخطاء الحرجة

> بعد اكتمال M5-A نفّذ تلقائياً:
> `git add . && git commit -m "[AUTO] M5-A: Security fixes and UI hardening" && git push origin main`

---

### T048 — تحصين الواجهة ضد خطأ toFixed والبيانات الفارغة

**الملفات المستهدفة:**
- `frontend/src/views/AttendanceView.vue`
- `frontend/src/views/DashboardView.vue`
- `frontend/src/views/ReportsView.vue`
- `frontend/src/views/GoalsView.vue`

**التنفيذ:**
```
في كل صفحة تعرض بيانات من API طبّق التالي:

1. أضف حالات v-if للتحميل والفراغ:
<div v-if="loading" class="loading-state">
  <div class="spinner"></div>
  <p>جاري تحميل البيانات...</p>
</div>
<div v-else-if="!records || records.length === 0" class="empty-state">
  <span>📭</span>
  <p>لا توجد سجلات لعرضها</p>
</div>
<div v-else> <!-- البيانات الفعلية --> </div>

2. استبدل كل .toFixed() بـ Optional Chaining:
(record.hours_worked ?? 0).toFixed(1)
(item.amount ?? 0).toFixed(2)
(summary.total ?? 0).toFixed(2)

3. في data() أضف قيم افتراضية:
data() {
  return {
    records: [],
    loading: false,
    error: null
  }
}

4. في كل طلب API استخدم try/catch/finally:
async fetchData() {
  try {
    this.loading = true
    this.error = null
    const res = await api.get('/endpoint')
    this.records = res.data ?? []
  } catch (err) {
    this.error = 'حدث خطأ في تحميل البيانات'
    this.records = []
  } finally {
    this.loading = false
  }
}

5. أضف CSS للحالات الجديدة في style.css:
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
```

**تحقق تلقائي:** افتح كل صفحة وتأكد أنه لا يوجد خطأ في Console.

---

### T049 — سد ثغرة XSS وتقوية التحقق من المدخلات

**الملفات المستهدفة:**
- `backend/app/schemas.py`
- `backend/app/routers/auth.py`
- `backend/requirements.txt`

**التنفيذ:**
```
1. في requirements.txt أضف:
email-validator==2.1.0

2. في schemas.py استبدل RegisterRequest بالكامل:

from pydantic import BaseModel, Field, field_validator
import re

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3 or len(v) > 50:
            raise ValueError('اسم المستخدم يجب أن يكون بين 3 و 50 حرفاً')
        if not re.match(r'^[a-zA-Z0-9_\u0600-\u06FF]+$', v):
            raise ValueError('اسم المستخدم يحتوي على رموز غير مسموح بها')
        if re.search(r'[<>&"\']', v):
            raise ValueError('اسم المستخدم يحتوي على رموز غير مسموح بها')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('البريد الإلكتروني غير صالح')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        if not any(c.isupper() for c in v):
            raise ValueError('يجب أن تحتوي على حرف كبير واحد على الأقل')
        if not any(c.isdigit() for c in v):
            raise ValueError('يجب أن تحتوي على رقم واحد على الأقل')
        return v

3. في schemas.py عدّل ExpenseCreate:

class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0, description="يجب أن يكون أكبر من صفر")
    category: str = Field(min_length=1, max_length=50)
    note: str = Field(default="", max_length=500)
    date: date

    @field_validator('note', 'category')
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        v = re.sub(r'<[^>]+>', '', v)
        return v.strip()

4. في auth.py داخل دالة register أضف:

existing_email = db.query(User).filter(User.email == user_data.email).first()
if existing_email:
    raise HTTPException(status_code=400, detail="البريد الإلكتروني مستخدم مسبقاً")

existing_username = db.query(User).filter(User.username == user_data.username).first()
if existing_username:
    raise HTTPException(status_code=400, detail="اسم المستخدم مستخدم مسبقاً")
```

**تحقق تلقائي:** جرّب التسجيل بـ `<script>alert(1)</script>` كاسم مستخدم — يجب أن يُرفض.

---

### T050 — Rate Limiting + Security Headers

**الملفات المستهدفة:**
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/routers/auth.py`

**التنفيذ:**
```
1. في requirements.txt أضف:
slowapi==0.1.9

2. في main.py أضف في البداية:

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

3. في main.py أضف Security Headers Middleware:

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

4. في main.py أضف health endpoint:

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "TrackMe", "version": "2.0"}

5. في auth.py أضف Rate Limiting:

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    # الكود الموجود بدون تغيير

@router.post("/register")
@limiter.limit("3/minute")
async def register(request: Request, ...):
    # الكود الموجود بدون تغيير
```

**تحقق تلقائي:** تأكد أن `/health` يرد بـ `{"status": "ok"}`.

---

## 🟡 M5-B — الأخطاء المتوسطة

> بعد اكتمال M5-B نفّذ تلقائياً:
> `git add . && git commit -m "[AUTO] M5-B: UX improvements, DB constraints, routing fixes" && git push origin main`

---

### T051 — إصلاح HTTP 401 + Interceptor + رسائل الخطأ

**الملفات المستهدفة:**
- `backend/app/utils/auth.py`
- `frontend/src/utils/api.js`
- جميع ملفات Views

**التنفيذ:**
```
1. في backend/app/utils/auth.py:
   استبدل كل:
   raise HTTPException(status_code=403, ...)
   بـ:
   raise HTTPException(status_code=401, detail="غير مصرح — يرجى تسجيل الدخول")

2. في frontend/src/utils/api.js أضف response interceptor:

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

3. في كل View فيه form أضف عرض الأخطاء:

<!-- في template -->
<Transition name="fade">
  <div v-if="errorMessage" class="alert alert-error">⚠️ {{ errorMessage }}</div>
</Transition>
<Transition name="fade">
  <div v-if="successMessage" class="alert alert-success">✓ {{ successMessage }}</div>
</Transition>

<!-- في CSS -->
.alert { padding: 12px 16px; border-radius: 10px; margin-bottom: 16px; font-weight: 500; }
.alert-error { background: rgba(239,68,68,0.1); color: var(--danger); border: 1px solid var(--danger); }
.alert-success { background: rgba(16,185,129,0.1); color: var(--success); border: 1px solid var(--success); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
```

---

### T052 — قيود قاعدة البيانات UNIQUE + Constraints

**الملفات المستهدفة:**
- `backend/app/models.py`

**التنفيذ:**
```
في models.py أضف UniqueConstraints وتأكد من وجود timestamps:

from sqlalchemy import Column, Integer, String, Float, Date, Time, Text, DateTime, UniqueConstraint
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint('email', name='uq_users_email'),
        UniqueConstraint('username', name='uq_users_username'),
    )
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    salary_type = Column(String(10), default='monthly')
    salary_amount = Column(Float, default=0.0)
    default_start_time = Column(Time, nullable=True)
    default_end_time = Column(Time, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

بعد التعديل شغّل:
python -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('Database updated successfully')
"
```

---

### T053 — صفحة 404 وتحسين Vue Router

**الملفات المستهدفة:**
- `frontend/src/views/NotFoundView.vue` (جديد)
- `frontend/src/router/index.js`

**التنفيذ:**
```
1. أنشئ frontend/src/views/NotFoundView.vue:

<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h2>الصفحة غير موجودة</h2>
      <p>الرابط الذي تبحث عنه غير موجود أو تم نقله</p>
      <router-link to="/dashboard" class="btn-primary">
        🏠 العودة للرئيسية
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.not-found-page {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.error-code {
  font-size: 8rem;
  font-weight: 800;
  color: var(--accent);
  line-height: 1;
  margin-bottom: 16px;
}
h2 { color: var(--text-primary); margin-bottom: 8px; }
p { color: var(--text-secondary); margin-bottom: 24px; }
</style>

2. في router/index.js أضف في نهاية routes:
{
  path: '/:pathMatch(.*)*',
  name: 'NotFound',
  component: () => import('../views/NotFoundView.vue')
}

3. أضف Navigation Guard للمصادقة:
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})
```

---

### T054 — إضافة /health endpoint وتعليمات UptimeRobot

**الملفات المستهدفة:**
- `backend/app/main.py` (endpoint موجود من T050 — تأكد فقط)
- `README.md` (أضف تعليمات UptimeRobot)

**التنفيذ:**
```
1. تأكد أن /health موجود في main.py (تم في T050)

2. في README.md أضف قسم:

## 🔔 إبقاء التطبيق مستيقظاً (UptimeRobot)

Render المجاني يوقف الـ Backend بعد 15 دقيقة خمول.
الحل: سجّل في uptimerobot.com وأضف monitor:
- URL: https://trackme-backend-xena.onrender.com/health
- Interval: كل 5 دقائق
- مجاني تماماً
```

---

### T055 — مكون Toast للإشعارات

**الملفات المستهدفة:**
- `frontend/src/components/ToastNotification.vue` (جديد)
- `frontend/src/App.vue`
- جميع Views

**التنفيذ:**
```
1. أنشئ frontend/src/components/ToastNotification.vue:

<template>
  <Transition name="toast">
    <div v-if="visible" :class="['toast-notification', `toast-${type}`]">
      <span class="toast-icon">{{ icons[type] }}</span>
      <span class="toast-text">{{ message }}</span>
    </div>
  </Transition>
</template>

<script>
export default {
  name: 'ToastNotification',
  data() {
    return {
      visible: false,
      message: '',
      type: 'success',
      icons: { success: '✓', error: '✕', warning: '⚠️', info: 'ℹ️' },
      timer: null
    }
  },
  methods: {
    show(message, type = 'success', duration = 3000) {
      if (this.timer) clearTimeout(this.timer)
      this.message = message
      this.type = type
      this.visible = true
      this.timer = setTimeout(() => { this.visible = false }, duration)
    }
  }
}
</script>

<style scoped>
.toast-notification {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 14px 28px;
  border-radius: 14px;
  font-weight: 600;
  font-size: 0.95rem;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: var(--shadow-lg);
  min-width: 250px;
  justify-content: center;
}
.toast-success { background: var(--success); color: white; }
.toast-error   { background: var(--danger);  color: white; }
.toast-warning { background: var(--warning); color: white; }
.toast-info    { background: var(--accent);  color: white; }
.toast-enter-active, .toast-leave-active { transition: all 0.35s cubic-bezier(0.4,0,0.2,1); }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(16px); }
</style>

2. في App.vue أضف:
<template>
  <div>
    <router-view />
    <ToastNotification ref="toast" />
  </div>
</template>

3. في كل View استخدمه بدلاً من alert():
// بدلاً من: alert('تم الحفظ')
// استخدم:
this.$root.$refs.toast.show('تم الحفظ بنجاح', 'success')
this.$root.$refs.toast.show('حدث خطأ', 'error')
```

---

## 🟢 M5-C — تحسينات الجودة والاحترافية

> بعد اكتمال M5-C نفّذ تلقائياً:
> `git add . && git commit -m "[AUTO] M5-C: Performance, UX polish, README update" && git push origin main`

---

### T056 — Lazy Loading + Auth Guard محسّن

**الملفات المستهدفة:**
- `frontend/src/router/index.js`

**التنفيذ:**
```
حوّل جميع imports في router/index.js إلى lazy loading:

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/attendance',
    name: 'Attendance',
    component: () => import('../views/AttendanceView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/expenses',
    name: 'Expenses',
    component: () => import('../views/ExpensesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/goals',
    name: 'Goals',
    component: () => import('../views/GoalsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('../views/ReportsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/SettingsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue')
  }
]

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.requiresGuest && token) {
    next('/dashboard')
  } else {
    next()
  }
})
```

---

### T057 — تحسين صفحة تسجيل الدخول

**الملفات المستهدفة:**
- `frontend/src/views/LoginView.vue`

**التنفيذ:**
```
أضف التحسينات التالية في LoginView.vue:

1. إظهار/إخفاء كلمة المرور:
<div class="input-wrapper">
  <input
    :type="showPassword ? 'text' : 'password'"
    v-model="password"
    placeholder="كلمة المرور"
    class="form-input"
  />
  <button
    type="button"
    @click="showPassword = !showPassword"
    class="toggle-password-btn"
    :title="showPassword ? 'إخفاء' : 'إظهار'"
  >
    {{ showPassword ? '🙈' : '👁️' }}
  </button>
</div>

2. Validation فوري:
<small v-if="passwordError" class="field-error">{{ passwordError }}</small>

methods: {
  validatePassword() {
    if (this.password.length > 0 && this.password.length < 8) {
      this.passwordError = 'كلمة المرور يجب أن تكون 8 أحرف على الأقل'
    } else {
      this.passwordError = ''
    }
  }
}

3. زر ذكي يمنع الضغط المتكرر:
<button
  @click="handleLogin"
  :disabled="isLoading || !!passwordError"
  class="btn-primary btn-full"
>
  <span v-if="isLoading" class="btn-spinner"></span>
  <span>{{ isLoading ? 'جاري الدخول...' : 'تسجيل الدخول' }}</span>
</button>

4. CSS إضافي:
.input-wrapper { position: relative; }
.toggle-password-btn {
  position: absolute;
  left: 12px; top: 50%;
  transform: translateY(-50%);
  background: none; border: none;
  cursor: pointer; font-size: 1.1rem;
}
.field-error { color: var(--danger); font-size: 0.8rem; margin-top: 4px; display: block; }
.btn-full { width: 100%; }
.btn-spinner {
  display: inline-block;
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  margin-left: 8px;
}
```

---

### T058 — تحديث README.md الشامل

**الملفات المستهدفة:**
- `README.md`

**التنفيذ:**
```
أنشئ README.md كاملاً في جذر المشروع:

# TrackMe 📊
> تطبيق تتبع الدوام والمالية الشخصية

## 🌐 الروابط المباشرة
- **التطبيق:** https://trackme-ugq1.onrender.com
- **API:** https://trackme-backend-xena.onrender.com
- **Health Check:** https://trackme-backend-xena.onrender.com/health

## 📱 تثبيت التطبيق
### على الهاتف (Android/iOS):
1. افتح الرابط في Chrome
2. اضغط القائمة (⋮) ثم "إضافة إلى الشاشة الرئيسية"
3. اضغط "إضافة"

### على الكمبيوتر (Chrome):
1. افتح الرابط في Chrome
2. اضغط أيقونة ⊕ في شريط العنوان
3. اضغط "Install"

## 🛠️ التطوير المحلي

### المتطلبات:
- Python 3.10+
- Node.js 18+

### تشغيل Backend:
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

### تشغيل Frontend:
cd frontend
npm install
npm run dev

## 🔒 الأمان
- كلمات المرور مشفرة بـ bcrypt
- JWT tokens للمصادقة
- Rate limiting على endpoints الحساسة
- Security headers على جميع الردود
- حماية كاملة ضد XSS و SQL Injection

## 🔔 المراقبة
- UptimeRobot يراقب التطبيق كل 5 دقائق
- تنبيه فوري على الإيميل عند التوقف

## 📁 هيكل المشروع
trackme/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   └── routers/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   ├── components/
│   │   ├── router/
│   │   └── utils/
│   └── package.json
└── README.md
```

---

## 🚀 M5-D — النشر والتحقق النهائي

> هذه المرحلة تنفّذها OpenCode تلقائياً بالكامل.

---

### T059 — الرفع النهائي على GitHub

**التنفيذ التلقائي:**
```bash
# تأكد أنك في جذر المشروع
git status

# أضف جميع التعديلات
git add .

# Commit شامل
git commit -m "[RELEASE] TrackMe v2.0 — Security hardening, XSS fix, Rate limiting, UI polish, 404 page, Toast notifications, Auth guard, Lazy loading"

# ارفع على GitHub
git push origin main

# انتظر النشر التلقائي على Render (5-10 دقائق)
echo "Pushed successfully — Render will deploy automatically"
```

---

### T060 — التحقق التلقائي بعد النشر (Automated QA)

**التنفيذ التلقائي:**
```python
# أنشئ ملف verify_deployment.py وشغّله:

import requests
import json

BASE_URL = "https://trackme-backend-xena.onrender.com"
FRONTEND_URL = "https://trackme-ugq1.onrender.com"

tests_passed = 0
tests_failed = 0

def test(name, condition, detail=""):
    global tests_passed, tests_failed
    if condition:
        print(f"✅ {name}")
        tests_passed += 1
    else:
        print(f"❌ {name} — {detail}")
        tests_failed += 1

# 1. Health Check
r = requests.get(f"{BASE_URL}/health")
test("Health endpoint يعمل", r.status_code == 200)
test("Health يرد بـ ok", r.json().get("status") == "ok")

# 2. Security Headers
test("X-Frame-Options موجود", "X-Frame-Options" in r.headers)
test("X-Content-Type-Options موجود", "X-Content-Type-Options" in r.headers)

# 3. Rate Limiting — محاولات تسجيل دخول متكررة
for i in range(6):
    r = requests.post(f"{BASE_URL}/api/auth/login",
        json={"username": "test", "password": "wrongpass"})
test("Rate limiting يعمل (429 بعد 5 محاولات)", r.status_code == 429)

# 4. XSS Protection
r = requests.post(f"{BASE_URL}/api/auth/register",
    json={"username": "<script>alert(1)</script>",
          "email": "x@x.com", "password": "Test123!"})
test("XSS في username مرفوض", r.status_code in [400, 422])

# 5. كلمة مرور ضعيفة
r = requests.post(f"{BASE_URL}/api/auth/register",
    json={"username": "testuser", "email": "t@t.com", "password": "weak"})
test("كلمة مرور ضعيفة مرفوضة", r.status_code in [400, 422])

# 6. مصروف بقيمة سالبة
# (يحتاج token — تخطّى إذا لم يكن متاحاً)

# النتيجة
print(f"\n{'='*40}")
print(f"النتيجة: {tests_passed} نجح / {tests_failed} فشل")
if tests_failed == 0:
    print("🎉 جميع الاختبارات نجحت!")
else:
    print("⚠️ بعض الاختبارات تحتاج مراجعة")

# شغّله بـ:
# pip install requests
# python verify_deployment.py
```

---

### T061 — تقرير إتمام المشروع

**التنفيذ التلقائي:**
```
بعد اكتمال جميع المهام، أنشئ ملف COMPLETION_REPORT.md:

# تقرير إتمام TrackMe v2.0

## ✅ المهام المنجزة
| المهمة | الوصف | الحالة |
|--------|-------|--------|
| T047 | إصلاح VITE_API_URL | ✅ يدوي |
| T048 | تحصين toFixed والبيانات الفارغة | ✅ |
| T049 | XSS + تقوية المدخلات | ✅ |
| T050 | Rate Limiting + Security Headers | ✅ |
| T051 | HTTP 401 + Interceptor + رسائل | ✅ |
| T052 | DB Constraints | ✅ |
| T053 | صفحة 404 + Auth Guard | ✅ |
| T054 | /health + UptimeRobot | ✅ |
| T055 | Toast Notifications | ✅ |
| T056 | Lazy Loading | ✅ |
| T057 | تحسين Login UX | ✅ |
| T058 | README شامل | ✅ |
| T059 | Git Push النهائي | ✅ |
| T060 | QA Tests | ✅ |

## 🔒 تحسينات الأمان
- ✅ XSS Protection
- ✅ Rate Limiting (5/min login, 3/min register)
- ✅ Security Headers
- ✅ Password Policy
- ✅ Email uniqueness
- ✅ Input sanitization

## 🎨 تحسينات UX
- ✅ Loading states
- ✅ Empty states
- ✅ Toast notifications
- ✅ 404 page
- ✅ Auth guard
- ✅ Show/hide password
- ✅ Real-time validation

## 📊 نتائج QA
[تُملأ تلقائياً من نتائج verify_deployment.py]
```

---

## 📋 ملخص المهام للمرجع السريع

| # | المهمة | النوع | الأولوية |
|---|--------|-------|---------|
| T047 | إصلاح VITE_API_URL | ⚠️ يدوي | 🔴 أول شيء |
| T048 | تحصين toFixed | OpenCode | 🔴 |
| T049 | XSS + Input validation | OpenCode | 🔴 |
| T050 | Rate Limiting + Headers | OpenCode | 🔴 |
| T051 | HTTP codes + Interceptor | OpenCode | 🟡 |
| T052 | DB Constraints | OpenCode | 🟡 |
| T053 | صفحة 404 + Router | OpenCode | 🟡 |
| T054 | /health + README | OpenCode | 🟡 |
| T055 | Toast Component | OpenCode | 🟡 |
| T056 | Lazy Loading | OpenCode | 🟢 |
| T057 | Login UX | OpenCode | 🟢 |
| T058 | README شامل | OpenCode | 🟢 |
| T059 | Git Push النهائي | OpenCode (auto) | 🚀 |
| T060 | QA Tests | OpenCode (auto) | 🚀 |
| T061 | Completion Report | OpenCode (auto) | 🚀 |

---

*تم التحديث — مايو 2026 — وضع الأتمتة الكاملة*

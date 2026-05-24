# TASKS — إصلاح جذري لمشكلة VITE_API_URL على Render
> **المشكلة الأساسية:** متغير VITE_API_URL لا يُحقن صحيح أثناء Build على Render
> **الأداة:** OpenCode (أتمتة كاملة)
> **بعد كل مرحلة:** git add . && git commit -m "[AUTO] وصف" && git push origin main

---

## 🤖 تعليمات OpenCode

```
أنت وكيل مستقل بصلاحيات كاملة.
نفّذ جميع المهام بالترتيب بدون توقف.
أصلح أي خطأ وحدك.
ارفع على GitHub تلقائياً بعد كل مرحلة.
لا تتوقف إلا إذا احتجت credentials خارجية.
```

---

## 🔴 المشكلة الجذرية — فهمها أولاً

```
السبب الحقيقي:
Vite يستبدل import.meta.env.VITE_API_URL أثناء البناء فقط.
إذا لم يكن المتغير موجوداً وقت البناء على Render،
يبقى النص الحرفي "VITE_API_URL=..." بدلاً من الرابط الفعلي.

النتيجة:
baseURL يصبح: "VITE_API_URL=https://trackme-backend-xena.onrender.com/api"
بدلاً من:     "https://trackme-backend-xena.onrender.com/api"

الحل الجذري:
نجعل الـ Frontend لا يعتمد على متغير البيئة وحده،
بل لديه fallback مضمون داخل الكود نفسه + نصلح render.yaml
```

---

## T062 — الحل الجذري لـ VITE_API_URL (أهم مهمة)

**الملفات المستهدفة:**
- `frontend/src/utils/api.js`
- `frontend/.env.production`
- `frontend/vite.config.js`
- `render.yaml`

**التنفيذ:**

```
=== الخطوة 1: frontend/src/utils/api.js ===

احذف الكود الموجود بالكامل واستبدله بهذا:

import axios from 'axios'

// حل جذري: الرابط مكتوب مباشرة كـ fallback
// لا يعتمد فقط على متغير البيئة
const getBaseURL = () => {
  // أولاً: جرّب متغير البيئة
  const envURL = import.meta.env.VITE_API_URL

  // تحقق أن المتغير رابط حقيقي وليس نص معطوب
  if (envURL &&
      envURL.startsWith('http') &&
      !envURL.includes('VITE_API_URL')) {
    return envURL
  }

  // ثانياً: إذا كنا في production استخدم الرابط المكتوب مباشرة
  if (import.meta.env.PROD) {
    return 'https://trackme-backend-xena.onrender.com/api'
  }

  // ثالثاً: للتطوير المحلي
  return 'http://localhost:8000/api'
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor — أضف token تلقائياً
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor — تعامل مع الأخطاء
api.interceptors.response.use(
  response => response,
  error => {
    // إذا الرد HTML بدلاً من JSON — مشكلة baseURL
    const contentType = error.response?.headers?.['content-type'] || ''
    if (contentType.includes('text/html')) {
      console.error('API Error: Received HTML instead of JSON. Check baseURL:', api.defaults.baseURL)
    }

    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

// للـ debugging — اطبع الـ baseURL في Console
console.log('API baseURL:', api.defaults.baseURL)

export default api


=== الخطوة 2: frontend/.env.production ===

أنشئ أو عدّل الملف بهذا المحتوى فقط:

VITE_API_URL=https://trackme-backend-xena.onrender.com/api


=== الخطوة 3: frontend/.env ===

أنشئ أو عدّل الملف:

VITE_API_URL=http://localhost:8000/api


=== الخطوة 4: frontend/vite.config.js ===

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],
    define: {
      // تأكد أن المتغيرات تُحقن صحيح
      '__API_URL__': JSON.stringify(
        env.VITE_API_URL || 'https://trackme-backend-xena.onrender.com/api'
      )
    },
    server: {
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: path => path.replace(/^\/api/, '/api')
        }
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: false
    }
  }
})


=== الخطوة 5: render.yaml (في جذر المشروع) ===

احذف المحتوى الموجود واستبدله بهذا كاملاً:

services:
  - type: web
    name: trackme-backend
    env: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: trackme-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: ENVIRONMENT
        value: production

  - type: web
    name: trackme-frontend
    env: node
    rootDir: frontend
    buildCommand: npm install && npm run build
    staticPublishPath: dist
    envVars:
      - key: VITE_API_URL
        value: https://trackme-backend-xena.onrender.com/api

databases:
  - name: trackme-db
    plan: free
```

**تحقق تلقائي بعد التنفيذ:**
```bash
# ابنِ الـ Frontend محلياً وتأكد من عدم وجود VITE_API_URL= في الملف المبني
cd frontend
npm run build
grep -r "VITE_API_URL=" dist/ && echo "❌ المشكلة لا تزال موجودة" || echo "✅ تم الإصلاح"
grep -r "trackme-backend-xena" dist/ && echo "✅ الرابط الصحيح موجود" || echo "❌ الرابط مفقود"
```

---

## T063 — إصلاح خطأ filter is not a function

**الملفات المستهدفة:**
- جميع ملفات Vue التي تستخدم `.filter()`

**التنفيذ:**
```
ابحث في جميع ملفات Vue عن كل استخدام لـ .filter() و .map() و .forEach()
وأضف تحققاً من النوع قبل كل استخدام:

ابحث عن هذا الأمر في terminal:
grep -rn "\.filter\|\.map\|\.forEach" frontend/src/views/

لكل نتيجة تجدها، طبّق هذا النمط:

❌ قبل:
this.records = response.data.filter(item => item.active)
this.items = response.data.map(item => item.name)

✅ بعد:
const data = response.data
this.records = Array.isArray(data) ? data.filter(item => item.active) : []
this.items = Array.isArray(data) ? data.map(item => item.name) : []

وكذلك للـ computed properties:
❌ قبل:
computed: {
  activeRecords() {
    return this.records.filter(r => r.status === 'worked')
  }
}

✅ بعد:
computed: {
  activeRecords() {
    if (!Array.isArray(this.records)) return []
    return this.records.filter(r => r.status === 'worked')
  }
}

أنشئ helper function في frontend/src/utils/helpers.js:

/**
 * تحويل آمن لأي قيمة إلى مصفوفة
 */
export const safeArray = (value) => {
  if (Array.isArray(value)) return value
  if (value === null || value === undefined) return []
  if (typeof value === 'object' && value.data) return safeArray(value.data)
  return []
}

/**
 * تحويل آمن لأي قيمة إلى رقم
 */
export const safeNumber = (value, decimals = 2) => {
  const num = parseFloat(value)
  if (isNaN(num)) return '0.' + '0'.repeat(decimals)
  return num.toFixed(decimals)
}

/**
 * تحقق من أن الـ API response صحيح وليس HTML
 */
export const isValidJSON = (data) => {
  if (typeof data === 'string') {
    return !data.trim().startsWith('<')
  }
  return true
}

ثم في كل View استخدم:
import { safeArray, safeNumber } from '../utils/helpers.js'

// بدلاً من:
this.records = response.data

// استخدم:
this.records = safeArray(response.data)
```

---

## T064 — إصلاح localStorage يحفظ HTML بدلاً من JSON

**الملفات المستهدفة:**
- `frontend/src/stores/auth.js`
- `frontend/src/views/LoginView.vue`

**التنفيذ:**
```
المشكلة: عندما الـ API يرد بـ HTML (بسبب خطأ baseURL)،
الكود يحاول حفظ HTML في localStorage كـ token.

الحل: أضف تحققاً صارماً قبل أي حفظ في localStorage.

في stores/auth.js أو LoginView.vue، ابحث عن كود تسجيل الدخول:

async login(credentials) {
  try {
    const response = await api.post('/auth/login', credentials)
    const data = response.data

    // تحقق أن الرد JSON حقيقي وليس HTML
    if (!data || typeof data !== 'object') {
      throw new Error('استجابة غير صالحة من الخادم')
    }

    if (!data.access_token || typeof data.access_token !== 'string') {
      throw new Error('لم يتم استلام token صالح')
    }

    // تأكد أن الـ token ليس HTML
    if (data.access_token.trim().startsWith('<')) {
      // امسح أي بيانات قديمة معطوبة
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      throw new Error('خطأ في إعدادات الخادم — يرجى التواصل مع المسؤول')
    }

    // احفظ البيانات الصحيحة
    localStorage.setItem('token', data.access_token)
    if (data.user) {
      localStorage.setItem('user', JSON.stringify(data.user))
    }

    return data

  } catch (error) {
    // امسح أي بيانات معطوبة عند الخطأ
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    throw error
  }
}

أضف أيضاً دالة تنظيف عند بدء التطبيق في App.vue:

mounted() {
  this.cleanCorruptedStorage()
},
methods: {
  cleanCorruptedStorage() {
    const token = localStorage.getItem('token')
    const user = localStorage.getItem('user')

    // امسح token إذا كان HTML أو undefined
    if (token && (token.trim().startsWith('<') || token === 'undefined')) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      console.warn('Cleared corrupted token from localStorage')
    }

    // امسح user إذا كان JSON غير صالح
    if (user) {
      try {
        JSON.parse(user)
      } catch {
        localStorage.removeItem('user')
        console.warn('Cleared corrupted user from localStorage')
      }
    }
  }
}
```

---

## T065 — اختبار محلي للتأكد قبل النشر

**التنفيذ التلقائي:**
```bash
# 1. شغّل Backend محلياً
cd backend
venv\Scripts\activate  # أو: source venv/bin/activate على Mac/Linux
uvicorn app.main:app --reload &

# 2. في terminal جديد، ابنِ Frontend وافحصه
cd frontend
npm run build

# 3. تحقق من الـ build
echo "=== فحص الـ build ==="
grep -r "VITE_API_URL=" dist/ 2>/dev/null && echo "❌ خطأ: المتغير لم يُستبدل" || echo "✅ المتغير استُبدل صحيح"
grep -r "localhost:8000\|trackme-backend" dist/ 2>/dev/null && echo "✅ الرابط موجود في الـ build" || echo "⚠️ الرابط غير موجود"

# 4. شغّل Frontend للتطوير
npm run dev
echo "افتح http://localhost:5173 وتحقق أن الـ Network tab يُظهر طلبات لـ localhost:8000"
```

---

## T066 — الرفع على GitHub والنشر النهائي

**التنفيذ التلقائي:**
```bash
# تأكد من الوضع الحالي
git status

# أضف جميع التعديلات
git add .

# Commit شامل
git commit -m "[FIX] Permanent fix for VITE_API_URL injection issue

- api.js: Added smart baseURL detection with hardcoded fallback
- vite.config.js: Fixed env variable injection during build
- render.yaml: Added explicit VITE_API_URL to frontend service
- helpers.js: Added safeArray, safeNumber, isValidJSON utilities
- auth.js: Added localStorage corruption detection and cleanup
- App.vue: Added storage cleanup on mount
- All Views: Protected .filter() and .map() calls with Array.isArray()
"

# ارفع على GitHub
git push origin main

echo ""
echo "✅ تم الرفع — Render سيبدأ النشر تلقائياً"
echo "انتظر 5-10 دقائق ثم افتح:"
echo "https://trackme-ugq1.onrender.com"
echo ""
echo "تحقق من Developer Tools → Network:"
echo "الطلبات يجب أن تذهب لـ: https://trackme-backend-xena.onrender.com/api/..."
```

---

## T067 — التحقق النهائي بعد النشر

**التنفيذ التلقائي:**
```python
# أنشئ verify_fix.py وشغّله بعد اكتمال النشر على Render

import requests
import time

FRONTEND = "https://trackme-ugq1.onrender.com"
BACKEND  = "https://trackme-backend-xena.onrender.com"

print("⏳ انتظر اكتمال النشر على Render...")
time.sleep(10)

results = []

def check(name, passed, detail=""):
    icon = "✅" if passed else "❌"
    msg = f"{icon} {name}"
    if not passed and detail:
        msg += f"\n   → {detail}"
    print(msg)
    results.append(passed)

# 1. Backend يعمل
try:
    r = requests.get(f"{BACKEND}/health", timeout=30)
    check("Backend يستجيب", r.status_code == 200)
    check("Health يرد بـ ok", r.json().get("status") == "ok")
except Exception as e:
    check("Backend يستجيب", False, str(e))

# 2. Security Headers
try:
    r = requests.get(f"{BACKEND}/health")
    check("X-Frame-Options موجود", "X-Frame-Options" in r.headers)
    check("X-Content-Type-Options موجود", "X-Content-Type-Options" in r.headers)
except:
    check("Security Headers", False)

# 3. تسجيل بكلمة مرور ضعيفة مرفوض
try:
    r = requests.post(f"{BACKEND}/api/auth/register",
        json={"username": "testuser99", "email": "test99@test.com", "password": "weak"},
        timeout=30)
    check("كلمة مرور ضعيفة مرفوضة", r.status_code in [400, 422],
          f"Status: {r.status_code}")
except Exception as e:
    check("كلمة مرور ضعيفة مرفوضة", False, str(e))

# 4. XSS في اسم المستخدم مرفوض
try:
    r = requests.post(f"{BACKEND}/api/auth/register",
        json={"username": "<script>alert(1)</script>",
              "email": "xss@test.com", "password": "Test123!"},
        timeout=30)
    check("XSS في username مرفوض", r.status_code in [400, 422],
          f"Status: {r.status_code}")
except Exception as e:
    check("XSS مرفوض", False, str(e))

# 5. Frontend يُحمَّل
try:
    r = requests.get(FRONTEND, timeout=30)
    check("Frontend يُحمَّل", r.status_code == 200)
    # تحقق أن الـ bundle لا يحتوي على VITE_API_URL= كنص
    check("لا يوجد VITE_API_URL= في الصفحة",
          "VITE_API_URL=" not in r.text,
          "المتغير لم يُستبدل صحيح في البناء")
except Exception as e:
    check("Frontend", False, str(e))

# النتيجة
passed = sum(results)
total  = len(results)
print(f"\n{'='*40}")
print(f"النتيجة: {passed}/{total} اختبار نجح")
if passed == total:
    print("🎉 جميع الاختبارات نجحت! TrackMe يعمل بشكل كامل.")
else:
    failed = total - passed
    print(f"⚠️ {failed} اختبار يحتاج مراجعة — راجع التفاصيل أعلاه")

# شغّله بـ:
# pip install requests
# python verify_fix.py
```

---

## 📋 ملخص المهام

| # | المهمة | الوقت | الأهمية |
|---|--------|-------|---------|
| T062 | الحل الجذري لـ VITE_API_URL | 30 دقيقة | 🔴 الأهم |
| T063 | إصلاح filter is not a function | 20 دقيقة | 🔴 |
| T064 | إصلاح localStorage يحفظ HTML | 20 دقيقة | 🔴 |
| T065 | اختبار محلي قبل النشر | 10 دقائق | 🟡 |
| T066 | رفع على GitHub + نشر | 5 دقائق | 🚀 |
| T067 | تحقق نهائي بعد النشر | 5 دقائق | 🚀 |

**الترتيب الإلزامي:** T062 ← T063 ← T064 ← T065 ← T066 ← T067

---

## ⚠️ ملاحظة يدوية واحدة بعد النشر

```
بعد اكتمال نشر Render:
1. افتح https://trackme-ugq1.onrender.com
2. افتح Developer Tools (F12) → Console
3. يجب أن ترى:
   ✅ API baseURL: https://trackme-backend-xena.onrender.com/api
   ❌ وليس: API baseURL: VITE_API_URL=https://...

إذا رأيت الخطأ رغم كل شيء:
→ اذهب إلى Render → trackme-frontend → Settings → Clear build cache & deploy
```

---

*تم الإنشاء — مايو 2026*

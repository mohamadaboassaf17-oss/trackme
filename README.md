# ◈ TrackMe — تتبع الدوام والمالية الشخصية

تطبيق ويب محلي لتتبع ساعات العمل والرواتب والمصاريف والأهداف المالية. يعمل بالكامل على الشبكة الداخلية بدون إنترنت.

---

## ✨ الميزات الرئيسية

- **تتبع الدوام** — تسجيل ساعات العمل اليومية، الغياب، والإجازات
- **حساب الراتب** — راتب شهري أو أسبوعي مع حساب المستحق بناءً على أيام الحضور
- **إدارة المصاريف** — تصنيف المصاريف مع فئات افتراضية ومخصصة
- **الأهداف المالية** — إنشاء أهداف ادخار مع أشرطة تقدم وتنبيهات
- **لوحة تحكم** — ملخص أسبوعي وشهري مع بطاقات KPI
- **تقارير ورسوم بيانية** — مقارنة الدخل بالمصاريف، توزيع الفئات، تقدم الأهداف
- **Dark/Light Mode** — مظهر داكن وفاتح مع حفظ التفضيل
- **متجاوب** — يعمل على الكمبيوتر والجوال مع شريط تنقل سفلي

---

## 🛠 المتطلبات الأساسية (Windows)

| البرنامج | الإصدار |
|----------|---------|
| **Python** | 3.10 أو أحدث |
| **Node.js** | 18 أو أحدث |

---

## 📦 خطوات التثبيت لأول مرة

### 1. Backend (Python / FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Frontend (Vue.js)

```bash
cd frontend
npm install
```

---

## 🚀 تشغيل التطبيق

### ⚡ الطريقة السريعة (بضغطة واحدة)

اضغط مرتين على ملف `run.bat` الموجود في مجلد المشروع.

### 🔧 الطريقة اليدوية

**الطرفية الأولى — Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**الطرفية الثانية — Frontend:**
```bash
cd frontend
npm run dev -- --host
```

### 📱 الوصول للتطبيق

| من | العنوان |
|----|---------|
| نفس الجهاز | `http://localhost:5173` |
| أجهزة أخرى على الشبكة | `http://[IP-ADDRESS]:5173` |

**لمعرفة عنوان IP:**
1. افتح CMD واكتب: `ipconfig`
2. ابحث عن `IPv4 Address` (مثلاً: `192.168.1.5`)
3. من أي جهاز على نفس الشبكة افتح: `http://192.168.1.5:5173`

---

## 📌 تثبيت TrackMe كتطبيق على جهازك

### الطريقة 1 — أيقونة سطح المكتب (تشغيل بضغطة واحدة)

1. اضغط مرتين على ملف `create_shortcut.vbs`
2. ستظهر أيقونة **TrackMe** على سطح المكتب
3. اضغط عليها لتشغيل التطبيق تلقائياً (Backend + Frontend + Chrome)
4. تظهر أيضاً أيقونة **إيقاف TrackMe** لإغلاق التطبيق

> ℹ️ يتم أيضاً إنشاء أيقونة في مجلد `Startup` ليشتغل التطبيق تلقائياً عند بدء Windows

| الأيقونة | الوظيفة |
|----------|---------|
| **TrackMe** | تشغيل Backend + Frontend + فتح Chrome |
| **إيقاف TrackMe** | إغلاق جميع خدمات التطبيق |

### الطريقة 2 — تثبيت من Chrome (PWA)

1. شغّل التطبيق أولاً (باستخدام `start_trackme.bat` أو أيقونة سطح المكتب)
2. افتح Chrome على `http://localhost:5173`
3. اضغط على أيقونة **⊕ تثبيت التطبيق** في شريط العنوان
4. اضغط **تثبيت** (Install)
5. سيظهر TrackMe كتطبيق مستقل:
   - في شريط المهام (Taskbar)
   - في قائمة ابدأ (Start Menu)
   - على سطح المكتب
   - بدون أشرطة المتصفح (واجهة نظيفة)

### الطريقة 3 — تشغيل تلقائي عند بدء Windows

- أيقونة `create_shortcut.vbs` تنشئ تلقائياً اختصاراً في مجلد بدء التشغيل
- للتأكد: `Win + R` ← اكتب `shell:startup` ← ستجد أيقونة TrackMe
- يمكن حذفها من المجلد لإلغاء التشغيل التلقائي

### ملفات التشغيل

| الملف | الوصف |
|-------|-------|
| `start_trackme.bat` | تشغيل كامل (Backend + Frontend + Chrome) بنوافذ مخفية |
| `stop_trackme.bat` | إيقاف جميع خدمات التطبيق |
| `create_shortcut.vbs` | إنشاء أيقونات سطح المكتب + التشغيل التلقائي |
| `generate_icons.py` | إنشاء أيقونات PWA (للتطوير فقط) |

---

## 🗃 التقنيات المستخدمة

| الطبقة | التقنية |
|--------|---------|
| الواجهة الأمامية | Vue.js 3 + Vite + Vue Router + Pinia |
| الواجهة الخلفية | Python 3 + FastAPI |
| قاعدة البيانات | SQLite (محلية — لا تحتاج خادم) |
| المصادقة | JWT + bcrypt |
| النشر | Render (Web Service + Static Site + PostgreSQL) |
| اللغة | العربية (RTL) |

---

## 👥 المستخدمون

- **التسجيل:** كل مستخدم ينشئ حسابه الخاص برقم سري
- **العزل:** كل مستخدم يرى بياناته فقط — لا مشاركة بين المستخدمين
- **الإعدادات:** راتب شهري أو أسبوعي + وقت دوام افتراضي

---

## 🌐 النشر على الإنترنت (Render)

التطبيق منشور على **Render** (الخطة المجانية) ويمكن الوصول إليه من أي مكان:

| الخدمة | الرابط | الحالة |
|--------|--------|--------|
| **الواجهة الأمامية** | [trackme-ugq1.onrender.com](https://trackme-ugq1.onrender.com) | 🟢 يعمل |
| **الـ API الخلفي** | [trackme-backend-xena.onrender.com](https://trackme-backend-xena.onrender.com) | 🟢 يعمل |
| **توثيق API** | [trackme-backend-xena.onrender.com/api/docs](https://trackme-backend-xena.onrender.com/api/docs) | 🟢 Swagger |

### التقنيات السحابية
- **Backend**: FastAPI + Uvicorn على Render Web Service
- **Frontend**: Vue.js 3 + Vite على Render Static Site
- **قاعدة البيانات**: PostgreSQL على Render (خطة مجانية)
- **المصادقة**: JWT + bcrypt

### ⚠️ ملاحظات الخطة المجانية
- Render يوقف الخدمة بعد 15 دقيقة من عدم الاستخدام
- أول طلب قد يستغرق 30-60 ثانية لاستيقاظ الخادم
- قاعدة البيانات: 1GB مجاناً، تنتهي بعد 90 يوم (تحتاج تجديد)

### الاختبارات الآلية (Playwright)
التطبيق يحتوي على اختبارات E2E و API باستخدام Playwright:

```bash
# تثبيت Playwright
npm install

# تشغيل اختبارات API (الـ Backend)
npx playwright test --project=api

# تشغيل اختبارات E2E (الواجهة الأمامية)
npx playwright test --project=e2e

# تشغيل جميع الاختبارات
npx playwright test
```

## 🔔 إبقاء التطبيق مستيقظاً (UptimeRobot)

Render المجاني يوقف الـ Backend بعد 15 دقيقة خمول.
الحل: سجّل في [uptimerobot.com](https://uptimerobot.com) وأضف monitor:
- **URL:** https://trackme-backend-xena.onrender.com/health
- **Interval:** كل 5 دقائق
- مجاني تماماً ولا يحتاج بطاقة اتمان

---

## 🤔 الأسئلة الشائعة

**المنفذ مشغول (Port in use):**
- تأكد أن لا يوجد برنامج آخر يستخدم المنفذ 8000 أو 5173
- يمكنك تغيير المنافذ في أوامر التشغيل

**الهاتف لا يتصل:**
- تأكد أن جهاز الكمبيوتر والهاتف على نفس شبكة WiFi
- تأكد أن جدار الحماية (Firewall) يسمح بالاتصال — اضغط Allow عند الطلب
- إذا لم يعمل: افتح إعدادات Windows Firewall وأضف استثناء للمنفذ 5173

**ظهور خطأ `python not found`:**
- حمّل Python من python.org
- أثناء التثبيت، فعّل خيار "Add Python to PATH"

**ظهور خطأ `npm not found`:**
- حمّل Node.js من nodejs.org

**ظهور خطأ `bcrypt` أو `passlib`:**
- شغّل: `pip install bcrypt --upgrade`
- ثم: `pip install -r requirements.txt`

---

## 📁 هيكل المشروع

```
TrackApp/
├── backend/
│   ├── app/
│   │   ├── routers/     # API endpoints
│   │   ├── utils/       # Auth helpers
│   │   ├── models.py    # نماذج البيانات
│   │   ├── schemas.py   # مخططات التحقق
│   │   └── main.py      # نقطة البداية
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   ├── manifest.json    # PWA manifest
│   │   ├── icon-192.png     # أيقونة التطبيق
│   │   └── icon-512.png     # أيقونة كبيرة
│   ├── src/
│   │   ├── views/       # صفحات التطبيق
│   │   ├── components/  # مكونات قابلة لإعادة الاستخدام
│   │   ├── stores/      # Pinia stores
│   │   ├── router/      # Vue Router
│   │   └── utils/       # API client
│   └── package.json
├── start_trackme.bat    # تشغيل بضغطة واحدة (نوافذ مخفية)
├── stop_trackme.bat     # إيقاف التطبيق
├── create_shortcut.vbs   # إنشاء أيقونات سطح المكتب
├── generate_icons.py    # مولد أيقونات PWA
├── run.bat              # تشغيل كلاسيكي
└── README.md
```

---

<p align="center">صُنع بـ ❤️ لتتبع الدوام والمالية — مايو 2026</p>

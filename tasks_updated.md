# مهام تطوير تطبيق TrackMe — النسخة المحدّثة

> **أداة التطوير:** OpenCode
> **ملاحظة:** نفّذ المهام بالترتيب. لا تنتقل للمرحلة التالية قبل اختبار الحالية.

---

## ✅ المهام المكتملة (M1 + M2 + M3)
T001 → T035 مكتملة — راجع تقرير المشروع النهائي.

---

## 🆕 المرحلة 4 — التحسينات والتعديلات الجديدة

---

### 4.1 — وقت الدوام الافتراضي (Default Shift Time)

#### T036 — حفظ وقت الدوام الافتراضي في إعدادات المستخدم

**المهمة لـ OpenCode:**
```
في صفحة الإعدادات (SettingsView.vue)، أضف قسماً جديداً باسم
"وقت الدوام الافتراضي" يحتوي على:
- حقل "وقت البداية الافتراضي" (time input)
- حقل "وقت النهاية الافتراضي" (time input)
- زر "حفظ الإعدادات"

في الـ Backend (routers/salary.py أو settings جديد):
- أضف حقلين للجدول Users: default_start_time و default_end_time (TIME, nullable)
- أضف endpoint: PUT /api/settings/shift-defaults
- أضف endpoint: GET /api/settings/shift-defaults

في قاعدة البيانات (models.py):
- أضف الحقلين default_start_time و default_end_time لجدول Users
- شغّل migration أو أعد إنشاء الجدول
```

**معايير القبول:**
- [ ] المستخدم يستطيع حفظ وقت بداية ونهاية افتراضي من صفحة الإعدادات
- [ ] القيم محفوظة في قاعدة البيانات مرتبطة بـ user_id

---

#### T037 — Pre-fill تلقائي + زر تسجيل سريع في صفحة الدوام

**المهمة لـ OpenCode:**
```
في صفحة الدوام (AttendanceView.vue):

1. عند فتح نموذج إضافة يوم جديد، اجلب الـ default_start_time
   و default_end_time من الـ API وضعهما تلقائياً في الحقول
   (يبقى قابلاً للتعديل يدوياً)

2. أضف زر "تسجيل يوم بالوقت الافتراضي" (Quick Log):
   - عند الضغط عليه يسجّل اليوم الحالي مباشرة بالوقت الافتراضي
   - بدون فتح النموذج
   - يظهر رسالة تأكيد "تم تسجيل يوم عمل بنجاح ✓"
   - إذا لم يكن هناك وقت افتراضي محفوظ، يظهر تنبيه
     "يرجى تحديد وقت الدوام الافتراضي في الإعدادات أولاً"
```

**معايير القبول:**
- [ ] النموذج يُملأ تلقائياً بالوقت الافتراضي عند الفتح
- [ ] زر التسجيل السريع يعمل بضغطة واحدة
- [ ] تظهر رسالة تأكيد بعد التسجيل السريع

---

### 4.2 — تحديث المظهر (UI Redesign)

#### T038 — نظام الألوان والثيم (Dark/Light Mode)

**المهمة لـ OpenCode:**
```
في ملف assets/style.css والـ App.vue:

1. أنشئ CSS Variables لنظام الألوان:

/* Light Mode */
:root {
  --bg-primary: #F8FAFC;
  --bg-secondary: #FFFFFF;
  --bg-card: #FFFFFF;
  --text-primary: #0F172A;
  --text-secondary: #64748B;
  --accent: #6366F1;        /* Indigo */
  --accent-hover: #4F46E5;
  --success: #10B981;
  --warning: #F59E0B;
  --danger: #EF4444;
  --border: #E2E8F0;
  --shadow: 0 1px 3px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
}

/* Dark Mode */
[data-theme="dark"] {
  --bg-primary: #0F172A;
  --bg-secondary: #1E293B;
  --bg-card: #1E293B;
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  --accent: #818CF8;
  --accent-hover: #6366F1;
  --border: #334155;
  --shadow: 0 1px 3px rgba(0,0,0,0.4);
  --shadow-lg: 0 10px 25px rgba(0,0,0,0.4);
}

2. في App.vue:
   - أضف زر تبديل Dark/Light في شريط التنقل (أيقونة 🌙/☀️)
   - احفظ التفضيل في localStorage
   - طبّق data-theme على <html> element
```

**معايير القبول:**
- [ ] زر التبديل يعمل فورياً بدون إعادة تحميل
- [ ] التفضيل محفوظ بعد إغلاق المتصفح
- [ ] جميع الألوان تتغير بسلاسة

---

#### T039 — إعادة تصميم المكونات بأسلوب SaaS احترافي

**المهمة لـ OpenCode:**
```
طبّق التصميم الاحترافي على جميع الصفحات:

1. البطاقات (Cards):
   - border-radius: 16px
   - box-shadow: var(--shadow-lg)
   - padding: 24px
   - border: 1px solid var(--border)
   - background: var(--bg-card)

2. الأزرار:
   - الزر الرئيسي: خلفية var(--accent)، نص أبيض، border-radius: 10px
   - padding: 10px 20px، font-weight: 600
   - تأثير hover: var(--accent-hover) مع transition 0.2s

3. الجداول:
   - header: خلفية var(--bg-primary)، نص var(--text-secondary)
   - صفوف متناوبة اللون بفارق خفيف
   - hover على كل صف

4. النماذج (Forms):
   - inputs: border: 1px solid var(--border)، border-radius: 10px
   - padding: 10px 14px
   - focus: border-color: var(--accent)، box-shadow خفيف

5. Sidebar/Navbar:
   - أيقونات + نص لكل قسم
   - active state واضح بلون var(--accent)
   - على الموبايل: bottom navigation bar بدلاً من sidebar

6. لوحة التحكم — الأرقام الكبيرة (KPI Cards):
   - 4 بطاقات في الأعلى: الراتب المستحق، المصاريف، المدّخر، الهدف التالي
   - رقم كبير bold + وصف صغير + أيقونة ملونة
```

**معايير القبول:**
- [ ] التصميم متسق في جميع الصفحات
- [ ] يعمل على الموبايل (responsive)
- [ ] Dark/Light يعملان بشكل صحيح مع التصميم الجديد

---

#### T040 — Responsive للموبايل (Mobile-First)

**المهمة لـ OpenCode:**
```
تأكد من أن التطبيق يعمل على شاشات الموبايل:

1. Breakpoints:
   - موبايل: max-width 768px
   - تابلت: 768px - 1024px
   - ديسكتوب: +1024px

2. على الموبايل:
   - Sidebar يتحول إلى Bottom Navigation Bar (4 أيقونات في الأسفل)
   - الجداول تصبح بطاقات (cards) بدلاً من rows
   - الأزرار تأخذ عرض كامل (width: 100%)
   - Font sizes أصغر قليلاً

3. تأكد من RTL يعمل صحيح على الموبايل أيضاً
```

**معايير القبول:**
- [ ] التطبيق قابل للاستخدام على شاشة 375px (iPhone SE)
- [ ] لا يوجد overflow أفقي
- [ ] Bottom navigation يعمل على الموبايل

---

### 4.3 — ملف طريقة التشغيل (README)

#### T041 — إنشاء ملف README.md شامل

**المهمة لـ OpenCode:**
```
أنشئ ملف README.md في جذر المشروع يحتوي على:

# TrackMe — دليل التشغيل الكامل

## المتطلبات الأساسية (Windows)
- Python 3.10 أو أحدث
- Node.js 18 أو أحدث
- Git (اختياري)

## خطوات التثبيت لأول مرة

### 1. Backend (Python/FastAPI)
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

### 2. Frontend (Vue.js)
cd frontend
npm install

## تشغيل التطبيق يومياً

### Backend:
cd backend
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

### Frontend:
cd frontend
npm run dev

## الوصول للتطبيق
- من نفس الجهاز: http://localhost:5173
- من الهاتف أو أجهزة أخرى على الشبكة:
  1. افتح CMD واكتب: ipconfig
  2. ابحث عن "IPv4 Address" مثلاً: 192.168.1.5
  3. من الهاتف افتح: http://192.168.1.5:5173

## ملف run.bat (تشغيل بضغطة واحدة على Windows)
أنشئ ملف run.bat في جذر المشروع:

@echo off
echo Starting TrackMe...
start cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"
timeout /t 3
start cmd /k "cd frontend && npm run dev -- --host"
echo.
echo TrackMe is running!
echo Local:   http://localhost:5173
echo Network: Check your IP with ipconfig
pause

## الأسئلة الشائعة
- إذا ظهر خطأ "port in use": غيّر المنفذ في الأمر
- إذا لم يتصل الهاتف: تأكد أن جهاز الكمبيوتر والهاتف على نفس الـ WiFi
- إذا طُلب منك كلمة مرور Firewall: اضغط Allow
```

**معايير القبول:**
- [ ] ملف README.md موجود في جذر المشروع
- [ ] ملف run.bat يشغّل Backend و Frontend معاً
- [ ] التعليمات واضحة لشخص غير تقني

---

## 📋 ملخص المهام الجديدة

| # | المهمة | الأولوية | الوقت المتوقع |
|---|--------|---------|--------------|
| T036 | حفظ وقت الدوام الافتراضي في DB | عالية | 1 ساعة |
| T037 | Pre-fill + زر تسجيل سريع | عالية | 1 ساعة |
| T038 | Dark/Light Mode System | عالية | 1 ساعة |
| T039 | إعادة تصميم المكونات (SaaS Style) | عالية | 2-3 ساعات |
| T040 | Responsive للموبايل | متوسطة | 1-2 ساعة |
| T041 | README + run.bat | عالية | 30 دقيقة |

**الترتيب المقترح:** T036 ← T037 ← T038 ← T039 ← T040 ← T041

---

## 🔧 كيفية استخدام هذا الملف مع OpenCode

1. افتح OpenCode في مجلد المشروع
2. انسخ محتوى كل مهمة (القسم داخل ``` ```) وأعطه لـ OpenCode
3. بعد كل مهمة: اختبر، ثم انتقل للتالية
4. ابدأ دائماً بـ T036 لأنها تعديل على قاعدة البيانات

---

*تم التحديث — مايو 2026*

# مهام النشر على Render — TrackMe
> **الهدف:** نشر التطبيق على Render مجاناً مع PostgreSQL
> **الأدوات:** OpenCode + GitHub + Render

---

## ⚠️ ملاحظة مهمة قبل البدء
Render المجاني يوقف التطبيق بعد 15 دقيقة من عدم الاستخدام،
ويحتاج ~30 ثانية للاستيقاظ عند أول طلب. هذا طبيعي في الخطة المجانية.

---

## 📋 المهام — 5 مراحل

---

## T042 — تحويل قاعدة البيانات من SQLite إلى PostgreSQL

**أعطِ OpenCode هذا:**
```
حوّل التطبيق من SQLite إلى PostgreSQL:

1. في requirements.txt أضف:
   psycopg2-binary==2.9.9
   python-dotenv==1.0.0

2. في backend/app/database.py عدّل الاتصال:

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trackme.db")

# Render يرسل URL يبدأ بـ postgres:// لكن SQLAlchemy يحتاج postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

3. في ملف backend/.env أضف:
   DATABASE_URL=sqlite:///./trackme.db
   SECRET_KEY=your-secret-key-change-this-in-production
   
   (للتطوير المحلي يبقى SQLite، على Render سيُستبدل تلقائياً)

4. تأكد أن models.py يستخدم Base من database.py بشكل صحيح
```

**معايير القبول:**
- [ ] التطبيق يعمل محلياً بعد التعديل
- [ ] لا أخطاء عند تشغيل Backend

---

## T043 — إنشاء ملفات النشر (Deployment Files)

**أعطِ OpenCode هذا:**
```
أنشئ الملفات التالية للنشر على Render:

1. ملف backend/render.yaml في جذر المشروع:

services:
  - type: web
    name: trackme-backend
    env: python
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: trackme-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true

  - type: web
    name: trackme-frontend
    env: node
    buildCommand: "cd frontend && npm install && npm run build"
    staticPublishPath: frontend/dist

databases:
  - name: trackme-db
    plan: free

2. ملف backend/Procfile:
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT

3. ملف frontend/vite.config.js — عدّل الـ proxy ليشير للـ Backend على Render:

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})

4. ملف frontend/.env.production:
VITE_API_URL=https://trackme-backend.onrender.com

(سنعدّل هذا الرابط بعد النشر)

5. في frontend/src/utils/api.js عدّل baseURL:
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})
```

**معايير القبول:**
- [ ] جميع الملفات موجودة
- [ ] Frontend يبني بدون أخطاء (npm run build)

---

## T044 — رفع الكود على GitHub

**هذه المهمة يدوية — اتبع الخطوات:**

```
1. افتح GitHub.com وسجّل دخول

2. أنشئ Repository جديد:
   - اسمه: trackme
   - Private (خاص) ✓
   - لا تضف README (الكود عندك محلياً)

3. افتح CMD في مجلد المشروع واكتب:

git init
git add .
git commit -m "TrackMe - Initial deployment"
git branch -M main
git remote add origin https://github.com/USERNAME/trackme.git
git push -u origin main

(استبدل USERNAME باسم حسابك على GitHub)

4. تأكد أن الكود ظهر على GitHub
```

**معايير القبول:**
- [ ] Repository موجود على GitHub
- [ ] جميع الملفات مرفوعة

---

## T045 — إنشاء قاعدة البيانات والـ Backend على Render

**هذه المهمة يدوية — اتبع الخطوات:**

```
الخطوة 1 — أنشئ حساب Render:
- اذهب إلى render.com
- سجّل دخول بحساب GitHub (أسهل)

الخطوة 2 — أنشئ PostgreSQL Database:
- اضغط "New +" ثم "PostgreSQL"
- الاسم: trackme-db
- Plan: Free
- اضغط "Create Database"
- احفظ الـ "Internal Database URL" (ستحتاجه)

الخطوة 3 — أنشئ Backend Service:
- اضغط "New +" ثم "Web Service"
- اختر Repository: trackme من GitHub
- الإعدادات:
  Name: trackme-backend
  Root Directory: backend
  Runtime: Python 3
  Build Command: pip install -r requirements.txt
  Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  Plan: Free

- في قسم "Environment Variables" أضف:
  DATABASE_URL = (الصق Internal Database URL من الخطوة 2)
  SECRET_KEY = (اكتب أي نص عشوائي طويل)

- اضغط "Create Web Service"
- انتظر حتى يظهر "Live" (5-10 دقائق)
- احفظ رابط الـ Backend مثل: https://trackme-backend.onrender.com
```

**معايير القبول:**
- [ ] قاعدة البيانات منشأة على Render
- [ ] Backend يعمل والرابط يرد بـ {"detail":"Not Found"} أو أي رد

---

## T046 — نشر Frontend وربطه بالـ Backend

**الجزء الأول — أعطِ OpenCode هذا:**
```
عدّل ملف frontend/.env.production:
VITE_API_URL=https://trackme-backend.onrender.com

(استبدل الرابط برابط Backend الحقيقي من Render)

ثم ارفع التعديل على GitHub:
git add .
git commit -m "Update API URL for production"
git push
```

**الجزء الثاني — يدوي على Render:**
```
- اضغط "New +" ثم "Static Site"
- اختر Repository: trackme
- الإعدادات:
  Name: trackme-app
  Root Directory: frontend
  Build Command: npm install && npm run build
  Publish Directory: dist
  Plan: Free

- في قسم "Environment Variables" أضف:
  VITE_API_URL = https://trackme-backend.onrender.com

- اضغط "Create Static Site"
- انتظر حتى يظهر "Live"
- احفظ الرابط النهائي مثل: https://trackme-app.onrender.com
```

**معايير القبول:**
- [ ] Frontend يفتح على الرابط
- [ ] صفحة تسجيل الدخول تظهر
- [ ] يمكن إنشاء حساب وتسجيل الدخول

---

## 📋 ملخص المهام

| # | المهمة | النوع | الوقت |
|---|--------|-------|-------|
| T042 | تحويل SQLite → PostgreSQL | OpenCode | 30 دقيقة |
| T043 | ملفات النشر | OpenCode | 20 دقيقة |
| T044 | رفع الكود على GitHub | يدوي | 10 دقائق |
| T045 | إنشاء DB + Backend على Render | يدوي | 15 دقيقة |
| T046 | نشر Frontend + ربط الكل | OpenCode + يدوي | 15 دقيقة |

**الترتيب الإلزامي:** T042 ← T043 ← T044 ← T045 ← T046

---

## 🌐 النتيجة النهائية

بعد اكتمال المهام:
- التطبيق متاح من أي مكان عبر الإنترنت
- يعمل على الموبايل والكمبيوتر
- رابط ثابت يمكن تثبيته من Chrome كـ PWA
- قاعدة بيانات PostgreSQL مجانية على Render

---

## ⚠️ حدود الخطة المجانية على Render

| الحد | التفاصيل |
|------|----------|
| Backend | يتوقف بعد 15 دقيقة خمول، يستيقظ تلقائياً |
| Database | 1GB مجاناً، تنتهي بعد 90 يوم (تحتاج تجديد) |
| Frontend | Static Site — مجاني بلا قيود ✓ |
| الحل | افتح التطبيق يومياً أو استخدم UptimeRobot لإبقائه مستيقظاً |

---

*تم إنشاء هذا الملف — مايو 2026*

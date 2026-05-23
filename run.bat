@echo off
chcp 65001 >nul
title TrackMe - تتبع الدوام والمالية

echo.
echo    ╔══════════════════════════════════════════╗
echo    ║          ◈  TrackMe | تتبع              ║
echo    ║    تتبع الدوام والمالية الشخصية          ║
echo    ╚══════════════════════════════════════════╝
echo.
echo    [1/2] تشغيل Backend...
start "TrackMe Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo    [2/2] تشغيل Frontend...
timeout /t 2 >nul
start "TrackMe Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev -- --host"

timeout /t 4 >nul
echo.
echo    ┌──────────────────────────────────────────┐
echo    │  ✓ TrackMe يعمل الآن!                    │
echo    │                                          │
echo    │  المحلي:    http://localhost:5173        │
echo    │  الشبكة:    http://[IP]:5173             │
echo    │                                          │
echo    │  لمعرفة الـ IP: افتح CMD واكتب ipconfig  │
echo    │  ابحث عن: IPv4 Address                   │
echo    └──────────────────────────────────────────┘
echo.
echo    اضغط أي زر لإغلاق هذه النافذة...
pause >nul

@echo off
chcp 65001 >nul
title TrackMe — جاري التشغيل...

echo.
echo    ╔══════════════════════════════════════════╗
echo    ║          ◈  TrackMe — تشغيل              ║
echo    ╚══════════════════════════════════════════╝
echo.

REM ── Stop old processes on ports 8000 and 5173 ──
echo    [*] إيقاف العمليات القديمة...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo    [✓] تم إيقاف العمليات القديمة
echo.

REM ── Start Backend (minimized window) ──
echo    [1/2] تشغيل Backend ...
start /min "TrackMe Backend" cmd /c "cd /d "%~dp0backend" && uvicorn app.main:app --host 0.0.0.0 --port 8000"
timeout /t 4 /nobreak >nul
echo    [✓] Backend يعمل على المنفذ 8000
echo.

REM ── Start Frontend (minimized window) ──
echo    [2/2] تشغيل Frontend ...
start /min "TrackMe Frontend" cmd /c "cd /d "%~dp0frontend" && npm run dev -- --host --port 5173"
timeout /t 5 /nobreak >nul
echo    [✓] Frontend يعمل على المنفذ 5173
echo.

REM ── Open Chrome ──
echo    [*] فتح المتصفح...
start chrome "http://localhost:5173"
echo    [✓] تم فتح Chrome
echo.
echo    ┌──────────────────────────────────────────┐
echo    │  ✓ TrackMe جاهز للاستخدام!               │
echo    │                                          │
echo    │  المحلي:    http://localhost:5173        │
echo    │  API:       http://localhost:8000/docs   │
echo    └──────────────────────────────────────────┘
echo.
timeout /t 2 >nul
exit

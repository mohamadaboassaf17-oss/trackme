@echo off
chcp 65001 >nul
title TrackMe — إيقاف...

echo.
echo    ╔══════════════════════════════════════════╗
echo    ║       ◈  TrackMe — إيقاف                ║
echo    ╚══════════════════════════════════════════╝
echo.

echo    [*] إيقاف Backend (المنفذ 8000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo    [✓] تم إيقاف Backend

echo    [*] إيقاف Frontend (المنفذ 5173)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo    [✓] تم إيقاف Frontend

echo.
echo    ┌──────────────────────────────────────────┐
echo    │  ✓ تم إيقاف TrackMe بنجاح                │
echo    └──────────────────────────────────────────┘
echo.
timeout /t 2 >nul
exit

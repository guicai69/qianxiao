@echo off
setlocal
cd /d "%~dp0"

echo.
echo  ============================================
echo    Badminton Venue Management - Launcher
echo  ============================================
echo.

echo [1/4] Checking MySQL service...
sc query MySQL84 | findstr /i "RUNNING" >nul 2>&1
if errorlevel 1 (
    echo       Starting MySQL84 ...
    net start MySQL84 >nul 2>&1
    if errorlevel 1 ( echo       [WARN] MySQL84 failed to start, run: net start MySQL84 ) else ( echo       MySQL84 started )
) else (
    echo       MySQL84 already running
)

echo [2/4] Starting Django backend (port 8000)...
set "PY=%~dp0.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
start "Badminton-Backend" cmd /k "cd /d %~dp0backend && %PY% manage.py runserver 0.0.0.0:8000"

echo [3/4] Starting Vite frontend (port 3000)...
start "Badminton-Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo [4/4] Opening browser...
timeout /t 6 /nobreak >nul
start "" http://localhost:3000

echo.
echo  ============================================
echo    Done!
echo      Frontend : http://localhost:3000
echo      Backend  : http://localhost:8000
echo      API docs : http://localhost:8000/api/docs/
echo  ============================================
echo.
echo   To stop: close the two windows, or run stop.bat
echo.
pause

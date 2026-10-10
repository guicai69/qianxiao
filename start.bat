@echo off
setlocal
cd /d "%~dp0"

echo.
echo  ============================================
echo    Badminton Venue Management - Launcher
echo  ============================================
echo.

REM ---- 0. Dependency check & install ----
echo [0/5] Checking dependencies...

if not exist "frontend\node_modules" (
    echo       Installing frontend deps via npm... (may take minutes)
    pushd frontend
    call npm install
    popd
    if errorlevel 1 (
        echo       [ERROR] npm install failed. Check Node.js and network.
        pause
        exit /b 1
    )
) else (
    echo       frontend deps OK
)

if not exist ".venv\Scripts\python.exe" (
    echo       Creating Python venv...
    python -m venv .venv
)

".venv\Scripts\python.exe" -c "import django, celery" >nul 2>&1
if errorlevel 1 (
    echo       Installing backend deps via pip... (may take minutes)
    ".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo       [ERROR] pip install failed. Check Python and network.
        pause
        exit /b 1
    )
) else (
    echo       backend deps OK
)

REM ---- 1. MySQL ----
echo [1/5] Checking MySQL service...
sc query MySQL84 | findstr /i "RUNNING" >nul 2>&1
if errorlevel 1 (
    echo       Starting MySQL84 ...
    net start MySQL84 >nul 2>&1
    if errorlevel 1 ( echo       [WARN] MySQL84 failed to start, run: net start MySQL84 ) else ( echo       MySQL84 started )
) else (
    echo       MySQL84 already running
)

REM ---- 2. Backend ----
echo [2/5] Starting Django backend (port 8000)...
start "Badminton-Backend" cmd /k "cd /d %~dp0backend && %~dp0.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000"

REM ---- 3. Frontend ----
echo [3/5] Starting Vite frontend (port 3000)...
start "Badminton-Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

REM ---- 4. Browser ----
echo [4/5] Opening browser...
timeout /t 8 /nobreak >nul
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

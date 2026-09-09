@echo off
echo Stopping servers on ports 8000 / 3000 ...

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /f /pid %%P >nul 2>&1
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do taskkill /f /pid %%P >nul 2>&1

echo Done.
timeout /t 2 /nobreak >nul

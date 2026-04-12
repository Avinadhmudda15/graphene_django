@echo off
title Graphene Trace - Django
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: python not found. Install Python 3.10+ and tick "Add to PATH".
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

echo [2/3] Installing dependencies ^(if needed^)...
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)

if not exist "db.sqlite3" (
    echo [3/3] First run: applying migrations...
    python manage.py migrate
) else (
    echo [3/3] Database found.
)

echo.
echo ========================================
echo  SENSORE — works in Chrome, Edge, Firefox, Safari
echo  On THIS computer use (easiest):
echo      http://localhost:8000/
echo  Or:  http://127.0.0.1:8000/
echo  Friendly name (see FRIENDLY_URL.txt once):
echo      http://sensore.local:8000/
echo  Phone/other PC: use your Wi-Fi IPv4 from ipconfig — NOT always .1.10
echo  Stop server: Ctrl+C in THIS window
echo ========================================
echo.
echo Starting server... browser will open in a few seconds.
echo If the page fails, wait until you see "Starting development server" below.
echo.

REM Open default browser shortly after server begins starting
start "" cmd /c "timeout /t 4 /nobreak >nul && start http://127.0.0.1:8000/"

python manage.py runserver 0.0.0.0:8000
if errorlevel 1 (
    echo.
    echo Server exited with an error. Read the message above.
    pause
)

@echo off
title NovaNest Platform - Startup Manager
color 0A
echo ===============================================================================
echo                     NOVANEST PLATFORM - MULTI-ENGINE LAUNCHER
echo ===============================================================================
echo.
echo Checking active services...

REM 1. Verify MySQL
netstat -ano | findstr :3306 >nul
if %errorlevel% equ 0 (
    echo [OK] MySQL Database is already active on port 3306.
) else (
    echo [!] Starting MySQL Server 8.0...
    net start MySQL80
)

echo.
echo Launching NovaNest engines in separate windows...
echo.

REM 2. Start FastAPI Backend on port 8001
echo [*] Starting FastAPI Backend on http://localhost:8001 ...
start "NovaNest - FastAPI Backend (:8001)" cmd /k "cd /d %~dp0 && uvicorn api.main:app --host 127.0.0.1 --port 8001 --reload"

REM 3. Start React Frontend on port 5173
echo [*] Starting React Frontend on http://localhost:5173 ...
start "NovaNest - React Frontend (:5173)" cmd /k "cd /d %~dp0frontend && npm run dev"

REM 4. Start Streamlit Lab on port 8502
echo [*] Starting Streamlit Lab on http://localhost:8502 ...
start "NovaNest - Streamlit Lab (:8502)" cmd /k "cd /d %~dp0 && streamlit run streamlit_app/app.py --server.port 8502"

echo.
echo ===============================================================================
echo                     ALL NOVANEST ENGINES LAUNCHED!
echo ===============================================================================
echo.
echo  Access URLs:
echo   - React Executive UI:    http://localhost:5173
echo   - FastAPI Backend API:   http://localhost:8001/docs
echo   - Streamlit Lab:         http://localhost:8502
echo   - MySQL Database:        localhost:3306 (novanest_db)
echo.
echo Refer to LOCALHOST_SERVICES_GUIDE.md for full details and troubleshooting.
echo To stop all services, run stop_novanest.bat
echo ===============================================================================
pause

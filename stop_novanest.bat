@echo off
title NovaNest Platform - Shutdown Manager
color 0C
echo ===============================================================================
echo                     NOVANEST PLATFORM - ENGINE SHUTDOWN
echo ===============================================================================
echo.
echo Stopping running NovaNest development engines...
echo.

REM Kill Uvicorn (FastAPI on 8001)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING') do (
    echo [*] Stopping FastAPI Backend (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill Vite (React on 5173)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    echo [*] Stopping React Frontend (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill Streamlit (Lab on 8502)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8502 ^| findstr LISTENING') do (
    echo [*] Stopping Streamlit Lab (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ===============================================================================
echo                     ALL DEVELOPMENT ENGINES STOPPED!
echo ===============================================================================
echo Note: MySQL database service remains active for persistence.
pause

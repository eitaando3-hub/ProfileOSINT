@echo off
REM ============================================
REM ProfileOSINT Launcher
REM Starts the app after Python + virtualenv setup
REM ============================================

setlocal enabledelayedexpansion

set ROOT=%~dp0
set VENV_PATH=%ROOT%venv
set DATA_PATH=%ROOT%data

cls
echo.
echo ============================================
echo  ProfileOSINT Launcher
echo ============================================
echo.

echo [1/4] Checking setup...
if not exist "%VENV_PATH%" (
    echo [ERROR] Virtual environment not found.
    echo Please run setup_all_in_one.bat first.
    pause
    exit /b 1
)

echo [OK] Setup detected

echo [2/4] Creating data directories...
if not exist "%DATA_PATH%" (
    mkdir "%DATA_PATH%"
    mkdir "%DATA_PATH%\profiles"
    mkdir "%DATA_PATH%\logs"
)

echo [OK] Data ready

echo [3/4] Activating virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"

echo [OK] Environment ready

echo [4/4] Starting ProfileOSINT...
python -m app.main

if errorlevel 1 (
    echo.
    echo [ERROR] Application failed to start.
    pause
    exit /b 1
)

endlocal

@echo off
REM ============================================
REM ProfileOSINT Launcher
REM Starts the app after Python + virtualenv setup
REM ============================================

setlocal enabledelayedexpansion

set ROOT=%~dp0
set VENV_PATH=%ROOT%venv
set DATA_PATH=%ROOT%data
set APP_MAIN=%ROOT%app\main.py

cls
echo.
echo ============================================
echo  ProfileOSINT Launcher
echo ============================================
echo.

echo [1/5] Checking setup...
if not exist "%VENV_PATH%" (
    echo [ERROR] Virtual environment not found.
    echo Please run setup_all_in_one.bat first.
    pause
    exit /b 1
)

echo [OK] Setup detected

echo [2/5] Creating data directories...
if not exist "%DATA_PATH%" (
    mkdir "%DATA_PATH%"
    mkdir "%DATA_PATH%\profiles"
    mkdir "%DATA_PATH%\logs"
)

echo [OK] Data ready

echo [3/5] Checking app entry point...
if exist "%APP_MAIN%" (
    echo [OK] App entry point found
) else (
    echo [WARN] app/main.py not found. Trying fallback launch.
)

echo [4/5] Activating virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"

echo [OK] Environment ready

echo [5/5] Starting ProfileOSINT...
if exist "%APP_MAIN%" (
    python "%APP_MAIN%"
) else (
    python -m app.main
)

if errorlevel 1 (
    echo.
    echo [ERROR] Application failed to start.
    echo.
    echo Possible causes:
    echo  - app/main.py path is different in this project
    echo  - requirements.txt is missing dependencies
    echo  - project entry point is not a Python module
    echo.
    pause
    exit /b 1
)

endlocal

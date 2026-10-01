@echo off
REM ============================================
REM ProfileOSINT Launcher
REM Automatically activates venv and runs app
REM ============================================

setlocal enabledelayedexpansion

set USB_ROOT=%~dp0
set VENV_PATH=%USB_ROOT%venv
set DATA_PATH=%USB_ROOT%data

echo.
echo ============================================
echo  ProfileOSINT Launcher
echo ============================================
echo.

REM Check venv exists
if not exist "%VENV_PATH%" (
    echo [ERROR] Virtual environment not found
    echo.
    echo Please run setup_windows.bat first
    echo.
    pause
    exit /b 1
)

REM Create data directories if missing
if not exist "%DATA_PATH%" (
    mkdir "%DATA_PATH%"
    mkdir "%DATA_PATH%\profiles"
    mkdir "%DATA_PATH%\logs"
)

echo [INFO] Activating virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"

echo [INFO] Starting ProfileOSINT...
echo.

python -m app.main

if errorlevel 1 (
    echo.
    echo [ERROR] Application crashed
    pause
    exit /b 1
)

endlocal

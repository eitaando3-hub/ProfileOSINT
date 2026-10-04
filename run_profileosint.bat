@echo off
REM Quick launcher with progress bar for Windows

setlocal enabledelayedexpansion

set USB_ROOT=%~dp0
set VENV_PATH=%USB_ROOT%venv
set DATA_PATH=%USB_ROOT%data

cls
echo.
echo ============================================
echo  ProfileOSINT Launcher
echo ============================================
echo.
echo [1/4] Checking virtual environment...

if not exist "%VENV_PATH%" (
    echo [ERROR] Virtual environment not found
    echo.
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)

echo [OK] Virtual environment found
echo.
pause

cls
echo.
echo ============================================
echo  ProfileOSINT Launcher
echo ============================================
echo.
echo [2/4] Creating data directories...

if not exist "%DATA_PATH%" (
    mkdir "%DATA_PATH%"
    mkdir "%DATA_PATH%\profiles"
    mkdir "%DATA_PATH%\logs"
)

echo [OK] Data directories ready
echo.
pause

cls
echo.
echo ============================================
echo  ProfileOSINT Launcher
echo ============================================
echo.
echo [3/4] Activating virtual environment...
echo.

call "%VENV_PATH%\Scripts\activate.bat"

echo [OK] Virtual environment activated
echo.
pause

cls
echo.
echo ============================================
echo  ProfileOSINT Launcher
echo ============================================
echo.
echo [4/4] Starting ProfileOSINT...
echo.

python -m app.main

if errorlevel 1 (
    echo.
    echo [ERROR] Application crashed
    pause
    exit /b 1
)

endlocal

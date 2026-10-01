@echo off
REM ============================================
REM ProfileOSINT Portable Setup for Windows
REM Compatible: Windows 10/11 Home/Pro
REM ============================================

setlocal enabledelayedexpansion

REM Get current directory (USB root)
set USB_ROOT=%~dp0
set VENV_PATH=%USB_ROOT%venv
set APP_PATH=%USB_ROOT%app
set DATA_PATH=%USB_ROOT%data

echo.
echo ============================================
echo  ProfileOSINT Portable Setup
echo ============================================
echo.
echo USB Root: %USB_ROOT%
echo.

REM Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in system PATH
    echo.
    echo Please install Python first:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [INFO] Python found in system PATH
python --version
echo.

REM Create data directory if not exists
if not exist "%DATA_PATH%" (
    echo [INFO] Creating data directory...
    mkdir "%DATA_PATH%"
    mkdir "%DATA_PATH%\profiles"
    mkdir "%DATA_PATH%\logs"
)

REM Check if venv already exists
if exist "%VENV_PATH%" (
    echo [INFO] Virtual environment already exists
    echo [INFO] Activating existing environment...
    goto activate_venv
)

echo [INFO] Creating virtual environment...
echo This may take a few minutes...
echo.

python -m venv "%VENV_PATH%"
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment created
echo.

:activate_venv
echo [INFO] Activating virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment activated
echo.

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] pip upgrade had issues, continuing anyway...
)

echo.
echo [INFO] Installing dependencies...
echo This may take several minutes...
echo.

pip install -r "%USB_ROOT%requirements.txt"
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Dependencies installed
echo.

echo ============================================
echo  Setup Complete!
echo ============================================
echo.
echo To run ProfileOSINT, use one of these options:
echo.
echo Option 1 (Automatic):
echo   Double-click: run_profileosint.bat
echo.
echo Option 2 (Manual):
echo   1. Double-click: activate_venv.bat
echo   2. Type: python -m app.main
echo.
echo ============================================
echo.
pause

endlocal

@echo off
REM ============================================
REM ProfileOSINT Portable Setup - Self-Installer
REM Automatically installs Python if missing, creates venv, installs deps, and launches app
REM Works on Windows 10/11 Home/Pro
REM ============================================

setlocal enabledelayedexpansion

set ROOT=%~dp0
set PYTHON_DIR=%ROOT%python
set PYTHON_EXE=%PYTHON_DIR%\python.exe
set VENV_PATH=%ROOT%venv
set DATA_PATH=%ROOT%data
set PY_INSTALLER=%ROOT%python_installer.exe
set PY_VERSION=3.12.7

cls
echo.
echo ============================================
echo  ProfileOSINT Self-Installer
echo ============================================
echo.

echo [1/7] Checking Python environment...

REM If portable Python exists, use it
if exist "%PYTHON_EXE%" (
    echo [OK] Portable Python found
    goto python_ready
)

REM If system Python exists, use it
python --version >nul 2>&1
if not errorlevel 1 (
    echo [OK] System Python found
    set PYTHON_EXE=python
    goto python_ready
)

REM Need to install Python
set /a progress=1
cls
echo.
echo ============================================
echo  ProfileOSINT Self-Installer
echo ============================================
echo.
echo [2/7] Python not found. Downloading installer...

REM Try to download official Python installer silently
powershell -NoProfile -ExecutionPolicy Bypass -Command "(New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/%PY_VERSION%/python-%PY_VERSION%-amd64.exe','%PY_INSTALLER%')"
if not exist "%PY_INSTALLER%" (
    echo [ERROR] Failed to download Python installer.
    echo.
    echo Please install Python manually:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python installer downloaded

echo [3/7] Installing Python silently...
"%PY_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

if not exist "%PYTHON_EXE%" (
    REM fallback if installed to user profile or default location
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    ) else if exist "%ProgramFiles%\Python312\python.exe" (
        set PYTHON_EXE=%ProgramFiles%\Python312\python.exe
    ) else if exist "%ProgramFiles(x86)%\Python312\python.exe" (
        set PYTHON_EXE=%ProgramFiles(x86)%\Python312\python.exe
    ) else (
        echo [ERROR] Python installation failed or not found in standard paths.
        pause
        exit /b 1
    )
)

:python_ready
echo [OK] Python ready: %PYTHON_EXE%

if "%PYTHON_EXE%" NEQ "python" (
    echo [4/7] Creating portable Python directory...
    if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"
)

echo [5/7] Creating data folders...
if not exist "%DATA_PATH%" (
    mkdir "%DATA_PATH%"
    mkdir "%DATA_PATH%\profiles"
    mkdir "%DATA_PATH%\logs"
)

echo [6/7] Creating virtual environment...
if not exist "%VENV_PATH%" (
    "%PYTHON_EXE%" -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo [ERROR] Virtual environment creation failed.
        pause
        exit /b 1
    )
)

echo [OK] Virtual environment ready

echo [7/7] Installing dependencies...
call "%VENV_PATH%\Scripts\activate.bat"
python -m pip install --upgrade pip --quiet
pip install -r "%ROOT%requirements.txt" --quiet

if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Setup Complete!
echo ============================================
echo.
echo [SUCCESS] Python + dependencies installed.
echo.
echo To run ProfileOSINT:
echo   run_profileosint.bat
echo.
echo If you want to build the EXE:
echo   build_exe.bat
echo.
echo ============================================
echo.
pause

endlocal

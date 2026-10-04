@echo off
REM ============================================
REM ProfileOSINT Portable Setup - Self-Installer
REM Automatically installs Python if missing, creates venv, installs deps, and launches app
REM Works on Windows 10/11 Home/Pro
REM ============================================

setlocal enabledelayedexpansion

set ROOT=%~dp0
set VENV_PATH=%ROOT%venv
set DATA_PATH=%ROOT%data
set PY_INSTALLER=%ROOT%python_installer.exe
set PY_VERSION=3.12.7
set REQUIREMENTS_FILE=%ROOT%requirements.txt
set APP_MAIN=%ROOT%app\main.py

cls
echo.
echo ============================================
echo  ProfileOSINT Self-Installer
echo ============================================
echo.

echo [1/8] Checking Python environment...

REM If portable Python exists, use it
if exist "%ROOT%python\python.exe" (
    set PYTHON_EXE=%ROOT%python\python.exe
    echo [OK] Portable Python found
    goto python_ready
)

REM If system Python exists, use it
where python >nul 2>&1
if not errorlevel 1 (
    echo [OK] System Python found
    set PYTHON_EXE=python
    goto python_ready
)

REM Need to install Python
cls
echo.
echo ============================================
echo  ProfileOSINT Self-Installer
echo ============================================
echo.
echo [2/8] Python not found. Downloading installer...

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

echo [3/8] Installing Python silently...
"%PY_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

set PYTHON_EXE=
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
if "%PYTHON_EXE%"=="" if exist "%ProgramFiles%\Python312\python.exe" set PYTHON_EXE=%ProgramFiles%\Python312\python.exe
if "%PYTHON_EXE%"=="" if exist "%ProgramFiles(x86)%\Python312\python.exe" set PYTHON_EXE=%ProgramFiles(x86)%\Python312\python.exe
if "%PYTHON_EXE%"=="" if exist "%SystemDrive%\Python312\python.exe" set PYTHON_EXE=%SystemDrive%\Python312\python.exe

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python installation failed or not found in standard paths.
    pause
    exit /b 1
)

:python_ready
echo [OK] Python ready: %PYTHON_EXE%

echo [4/8] Creating data folders...
if not exist "%DATA_PATH%" (
    mkdir "%DATA_PATH%"
    mkdir "%DATA_PATH%\profiles"
    mkdir "%DATA_PATH%\logs"
)

echo [5/8] Creating virtual environment...
if not exist "%VENV_PATH%" (
    "%PYTHON_EXE%" -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo [ERROR] Virtual environment creation failed.
        pause
        exit /b 1
    )
)

echo [OK] Virtual environment ready

echo [6/8] Checking project files...
if exist "%APP_MAIN%" (
    echo [OK] App entry point found: %APP_MAIN%
) else (
    echo [WARN] Could not find app/main.py. The launcher may still work if the project uses a different entry point.
)

if exist "%REQUIREMENTS_FILE%" (
    echo [OK] requirements.txt found
    echo [7/8] Installing dependencies...
    call "%VENV_PATH%\Scripts\activate.bat"
    python -m pip install --upgrade pip --quiet
    pip install -r "%REQUIREMENTS_FILE%" --quiet
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed.
        echo [INFO] You can rerun this script after fixing the dependency file.
        pause
        exit /b 1
    )
) else (
    echo [WARN] requirements.txt not found. Skipping dependency install.
    echo [INFO] If the project has dependencies, create requirements.txt and rerun setup.
    echo [7/8] Skipping dependency installation because no requirements file was found.
)

echo [8/8] Setup finished.

echo.
echo ============================================
echo  Setup Complete!
echo ============================================
echo.
echo [SUCCESS] Python + environment are ready.
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

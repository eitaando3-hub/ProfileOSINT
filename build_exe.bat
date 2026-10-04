@echo off
REM ============================================
REM ProfileOSINT EXE Builder
REM Automatically ensures Python + PyInstaller are available
REM ============================================

setlocal enabledelayedexpansion

set ROOT=%~dp0
set VENV_PATH=%ROOT%venv
set APP_MAIN=%ROOT%app\main.py
set PYTHON_EXE=

cls
echo.
echo ============================================
echo  ProfileOSINT EXE Builder
echo ============================================
echo.

echo [1/6] Checking Python...

if exist "%VENV_PATH%\Scripts\python.exe" (
    set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe
    echo [OK] Using venv Python
) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    echo [OK] Using local Python install
) else if exist "%ProgramFiles%\Python312\python.exe" (
    set PYTHON_EXE=%ProgramFiles%\Python312\python.exe
    echo [OK] Using system Python install
) else (
    echo [INFO] Python not found. Running self-installer...
    call setup_all_in_one.bat
    if errorlevel 1 exit /b 1
    set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe
)

echo [2/6] Checking entry point...
if exist "%APP_MAIN%" (
    echo [OK] Found app/main.py
) else (
    echo [WARN] app/main.py not found. Build may fail if entry point path is different.
)

echo [3/6] Installing PyInstaller...
"%PYTHON_EXE%" -m pip install pyinstaller --quiet

if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller.
    pause
    exit /b 1
)

echo [OK] PyInstaller ready

echo [4/6] Cleaning old build output...
if exist "%ROOT%build" rmdir /s /q "%ROOT%build"
if exist "%ROOT%dist" rmdir /s /q "%ROOT%dist"

echo [OK] Cleaned build folders

echo [5/6] Building EXE...
if exist "%APP_MAIN%" (
    "%PYTHON_EXE%" -m PyInstaller --onefile --windowed --name ProfileOSINT "%APP_MAIN%"
) else (
    echo [ERROR] No valid entry point found for EXE build.
    echo [INFO] Add app/main.py or update this script to point to the actual project entry file.
    pause
    exit /b 1
)

if errorlevel 1 (
    echo [ERROR] EXE build failed.
    pause
    exit /b 1
)

echo [OK] Build finished

echo [6/6] Build complete.

echo.
echo Output file:

echo dist\ProfileOSINT.exe

echo.
pause

endlocal

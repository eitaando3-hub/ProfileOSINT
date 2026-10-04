@echo off
REM ============================================
REM ProfileOSINT EXE Builder
REM Automatically ensures Python + PyInstaller are available
REM ============================================

setlocal enabledelayedexpansion

set ROOT=%~dp0
set VENV_PATH=%ROOT%venv
set PYTHON_EXE=

cls
echo.
echo ============================================
echo  ProfileOSINT EXE Builder
echo ============================================
echo.

echo [1/5] Checking Python...

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

echo [2/5] Installing PyInstaller...
"%PYTHON_EXE%" -m pip install pyinstaller --quiet

if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller.
    pause
    exit /b 1
)

echo [OK] PyInstaller ready

echo [3/5] Cleaning old build output...
if exist "%ROOT%build" rmdir /s /q "%ROOT%build"
if exist "%ROOT%dist" rmdir /s /q "%ROOT%dist"

echo [OK] Cleaned build folders

echo [4/5] Building EXE...
"%PYTHON_EXE%" -m PyInstaller --onefile --windowed --name ProfileOSINT app/main.py

if errorlevel 1 (
    echo [ERROR] EXE build failed.
    pause
    exit /b 1
)

echo [OK] Build finished

echo [5/5] Build complete.

echo.
echo Output file:

echo dist\ProfileOSINT.exe

echo.
pause

endlocal

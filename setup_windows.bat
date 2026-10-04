@echo off
REM ============================================
REM ProfileOSINT Portable Setup for Windows
REM With Progress Bar Display
REM Compatible: Windows 10/11 Home/Pro
REM ============================================

setlocal enabledelayedexpansion

REM Get current directory (USB root)
set USB_ROOT=%~dp0
set VENV_PATH=%USB_ROOT%venv
set APP_PATH=%USB_ROOT%app
set DATA_PATH=%USB_ROOT%data

REM Progress tracking
set PROGRESS=0
set MAX_PROGRESS=6

echo.
echo ============================================
echo  ProfileOSINT Portable Setup
echo ============================================
echo.
echo USB Root: %USB_ROOT%
echo.

REM Function to show progress bar
goto show_progress

:show_progress_func
setlocal enabledelayedexpansion
set /a percent=!PROGRESS! * 100 / !MAX_PROGRESS!
set bar=
for /l %%i in (1,1,!percent!) do set "bar=!bar!="
set empty=
for /l %%i in (!percent!,1,99) do set "empty=!empty! "
echo [!bar!!empty!] !percent!%%
endlocal
goto :eof

REM Check Python is available
set /a PROGRESS=1
cls
echo.
echo ============================================
echo  ProfileOSINT Portable Setup
echo ============================================
echo.
call :show_progress_func
echo [1/6] Checking Python installation...
echo.

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

echo [OK] Python found
python --version
echo.
pause

REM Create data directory
set /a PROGRESS=2
cls
echo.
echo ============================================
echo  ProfileOSINT Portable Setup
echo ============================================
echo.
call :show_progress_func
echo [2/6] Creating data directories...
echo.

if not exist "%DATA_PATH%" (
    mkdir "%DATA_PATH%"
    mkdir "%DATA_PATH%\profiles"
    mkdir "%DATA_PATH%\logs"
    echo [OK] Data directories created
) else (
    echo [OK] Data directories already exist
)
echo.
pause

REM Check if venv exists
if exist "%VENV_PATH%" (
    echo [OK] Virtual environment already exists
    echo Skipping venv creation...
    goto activate_venv
)

REM Create virtual environment
set /a PROGRESS=3
cls
echo.
echo ============================================
echo  ProfileOSINT Portable Setup
echo ============================================
echo.
call :show_progress_func
echo [3/6] Creating Python virtual environment...
echo This may take 1-2 minutes...
echo.

python -m venv "%VENV_PATH%"
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment created
echo.
pause

:activate_venv
set /a PROGRESS=4
cls
echo.
echo ============================================
echo  ProfileOSINT Portable Setup
echo ============================================
echo.
call :show_progress_func
echo [4/6] Activating virtual environment...
echo.

call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo.
pause

REM Upgrade pip
set /a PROGRESS=5
cls
echo.
echo ============================================
echo  ProfileOSINT Portable Setup
echo ============================================
echo.
call :show_progress_func
echo [5/6] Upgrading pip...
echo.

python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARNING] pip upgrade had issues, continuing anyway...
)

echo [OK] pip upgraded
echo.
pause

REM Install dependencies
set /a PROGRESS=6
cls
echo.
echo ============================================
echo  ProfileOSINT Portable Setup
echo ============================================
echo.
call :show_progress_func
echo [6/6] Installing dependencies...
echo This may take 3-5 minutes...
echo.
echo Installing: sherlock-project, requests...
echo.

pip install -r "%USB_ROOT%requirements.txt" --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed successfully
echo.

cls
echo.
echo ============================================
echo  Setup Complete!
echo ============================================
echo.
echo [SUCCESS] ProfileOSINT is ready to use
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

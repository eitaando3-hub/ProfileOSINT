@echo off
REM Windows launcher for ProfileOSINT portable EXE build
REM With progress bar display

setlocal enabledelayedexpansion

set ROOT=%~dp0
set EXE_PATH=%ROOT%dist\ProfileOSINT\ProfileOSINT.exe
set DATA_PATH=%ROOT%data

cls
echo.
echo ============================================
echo  ProfileOSINT EXE Launcher
echo ============================================
echo.
echo [1/3] Checking EXE...
echo.

if not exist "%EXE_PATH%" (
    echo [ERROR] ProfileOSINT.exe not found.
    echo Expected location: %EXE_PATH%
    echo.
    echo Please build it first:
    echo   1. Run: build_exe.bat
    echo   2. Wait for build to complete
    echo.
    pause
    exit /b 1
)

echo [OK] EXE found: %EXE_PATH%
echo.
pause

cls
echo.
echo ============================================
echo  ProfileOSINT EXE Launcher
echo ============================================
echo.
echo [2/3] Creating data directories...
echo.

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
echo  ProfileOSINT EXE Launcher
echo ============================================
echo.
echo [3/3] Starting ProfileOSINT...
echo.

"%EXE_PATH%"

if errorlevel 1 (
    echo.
    echo [ERROR] ProfileOSINT exited with an error.
    pause
    exit /b 1
)

endlocal

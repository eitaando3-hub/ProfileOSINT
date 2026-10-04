@echo off
REM PyInstaller build helper with progress bar
REM Automates the EXE build process for Windows 10/11

setlocal enabledelayedexpansion

set ROOT=%~dp0
set BUILD_LOG=%ROOT%build.log

cls
echo.
echo ============================================
echo  ProfileOSINT PyInstaller Builder
echo ============================================
echo.
echo [1/4] Checking PyInstaller...
echo.

pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller not found. Installing...
    pip install pyinstaller --quiet
    echo [OK] PyInstaller installed
) else (
    echo [OK] PyInstaller already installed
)

echo.
pause

cls
echo.
echo ============================================
echo  ProfileOSINT PyInstaller Builder
echo ============================================
echo.
echo [2/4] Cleaning previous build...
echo.

if exist "%ROOT%build" rmdir /s /q "%ROOT%build" >nul 2>&1
if exist "%ROOT%dist" rmdir /s /q "%ROOT%dist" >nul 2>&1
echo [OK] Previous build cleaned
echo.
pause

cls
echo.
echo ============================================
echo  ProfileOSINT PyInstaller Builder
echo ============================================
echo.
echo [3/4] Building EXE...
echo This may take 5-10 minutes...
echo.
echo Log file: %BUILD_LOG%
echo.

pyinstaller "%ROOT%ProfileOSINT.spec" --distpath "%ROOT%dist" --workpath "%ROOT%build" --log-level=INFO > "%BUILD_LOG%" 2>&1

if errorlevel 1 (
    echo [ERROR] Build failed. Check %BUILD_LOG% for details.
    pause
    exit /b 1
)

echo [OK] Build completed successfully
echo.
pause

cls
echo.
echo ============================================
echo  Build Complete!
echo ============================================
echo.
echo [SUCCESS] EXE created at:
echo   dist\ProfileOSINT\ProfileOSINT.exe
echo.
echo To run the application:
echo   Double-click: run_profileosint_exe.bat
echo.
echo ============================================
echo.
pause

endlocal

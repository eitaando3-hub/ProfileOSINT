@echo off
REM Quick activator for virtual environment
REM Run this to activate venv, then type commands manually

setlocal enabledelayedexpansion

set VENV_PATH=%~dp0venv

if not exist "%VENV_PATH%" (
    echo [ERROR] Virtual environment not found at: %VENV_PATH%
    echo.
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"

echo.
echo [SUCCESS] Virtual environment activated
echo.
echo You can now run commands like:
echo   python -m app.main
echo   python -m sherlock username
echo.
echo Type 'deactivate' to exit virtual environment
echo.

cmd /k

endlocal

# ProfileOSINT Portable Setup Guide (USB ready)

## Quick start

1. Copy this entire repository to a USB drive.
2. Double-click `setup_all_in_one.bat`.
3. Wait for automatic Python installation + dependency setup.
4. Run `run_profileosint.bat`.

## What this does automatically

- Detects whether Python is already installed.
- Downloads Python if missing.
- Creates a local virtual environment.
- Installs `requirements.txt`.
- Creates `data/profiles` and `data/logs`.
- Launches the app.

## Files included

```text
USB_ROOT/
├── setup_all_in_one.bat
├── run_profileosint.bat
├── build_exe.bat
├── ProfileOSINT.spec
├── requirements.txt
├── app/
├── data/
├── venv/
└── dist/
```

## Windows 10/11 Home/Pro compatibility

This setup is designed for both Windows 10 and Windows 11, Home and Pro editions.

## Notes

- No manual Python install is required if it is missing.
- The script downloads the official Python installer from python.org.
- Once setup finishes, the app will be ready to use.

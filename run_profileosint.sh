#!/bin/bash
# ProfileOSINT Launcher (Linux/macOS)
# Automatically activates venv and runs app

set -e

USB_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PATH="${USB_ROOT}/venv"
DATA_PATH="${USB_ROOT}/data"

echo ""
echo "============================================"
echo " ProfileOSINT Launcher"
echo "============================================"
echo ""

if [ ! -d "$VENV_PATH" ]; then
    echo "[ERROR] Virtual environment not found"
    echo ""
    echo "Please run setup_linux_mac.sh first"
    echo ""
    exit 1
fi

# Create data directories if missing
if [ ! -d "$DATA_PATH" ]; then
    mkdir -p "$DATA_PATH/profiles"
    mkdir -p "$DATA_PATH/logs"
fi

echo "[INFO] Activating virtual environment..."
source "$VENV_PATH/bin/activate"

echo "[INFO] Starting ProfileOSINT..."
echo ""

python -m app.main

echo ""
echo "[INFO] Application closed"
echo ""

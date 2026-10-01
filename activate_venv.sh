#!/bin/bash
# Quick activator for virtual environment (Linux/macOS)

set -e

USB_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PATH="${USB_ROOT}/venv"

if [ ! -d "$VENV_PATH" ]; then
    echo "[ERROR] Virtual environment not found at: $VENV_PATH"
    echo ""
    echo "Please run setup_linux_mac.sh first"
    exit 1
fi

echo "[INFO] Activating virtual environment..."
source "$VENV_PATH/bin/activate"

echo ""
echo "[SUCCESS] Virtual environment activated"
echo ""
echo "You can now run commands like:"
echo "  python -m app.main"
echo "  python -m sherlock username"
echo ""
echo "Type 'deactivate' to exit virtual environment"
echo ""

bash

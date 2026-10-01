#!/bin/bash
# ProfileOSINT Portable Setup for macOS/Linux
# This script sets up a portable Python environment

set -e

# Get script directory (USB root)
USB_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PATH="${USB_ROOT}/venv"
APP_PATH="${USB_ROOT}/app"
DATA_PATH="${USB_ROOT}/data"

echo ""
echo "============================================"
echo " ProfileOSINT Portable Setup"
echo " Linux/macOS"
echo "============================================"
echo ""
echo "USB Root: $USB_ROOT"
echo ""

# Check Python is available
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found in system PATH"
    echo ""
    echo "Please install Python first:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-venv"
    echo ""
    exit 1
fi

echo "[INFO] Python found in system PATH"
python3 --version
echo ""

# Create data directory if not exists
if [ ! -d "$DATA_PATH" ]; then
    echo "[INFO] Creating data directory..."
    mkdir -p "$DATA_PATH/profiles"
    mkdir -p "$DATA_PATH/logs"
fi

# Check if venv already exists
if [ -d "$VENV_PATH" ]; then
    echo "[INFO] Virtual environment already exists"
    echo "[INFO] Activating existing environment..."
    source "$VENV_PATH/bin/activate"
    echo "[SUCCESS] Virtual environment activated"
else
    echo "[INFO] Creating virtual environment..."
    echo "This may take a few minutes..."
    echo ""
    
    python3 -m venv "$VENV_PATH"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        exit 1
    fi
    
    echo "[SUCCESS] Virtual environment created"
    echo ""
    
    echo "[INFO] Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    
    echo "[SUCCESS] Virtual environment activated"
    echo ""
    
    echo "[INFO] Upgrading pip..."
    python -m pip install --upgrade pip
    
    echo ""
    echo "[INFO] Installing dependencies..."
    echo "This may take several minutes..."
    echo ""
    
    pip install -r "${USB_ROOT}/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        exit 1
    fi
    
    echo ""
    echo "[SUCCESS] Dependencies installed"
fi

echo ""
echo "============================================"
echo " Setup Complete!"
echo "============================================"
echo ""
echo "To run ProfileOSINT, use one of these options:"
echo ""
echo "Option 1 (Automatic):"
echo "  bash run_profileosint.sh"
echo ""
echo "Option 2 (Manual):"
echo "  source activate_venv.sh"
echo "  python -m app.main"
echo ""
echo "============================================"
echo ""

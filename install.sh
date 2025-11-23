#!/bin/bash

echo "=================================================="
echo "AutoPack Installer"
echo "=================================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo "Please install Python 3.11 from https://www.python.org/"
    exit 1
fi

echo "[OK] Python found"
python3 --version
echo

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo "[WARN] Python 3.11 or higher is recommended"
    echo "Current version: $PYTHON_VERSION"
    read -p "Continue anyway? (y/n): " continue
    if [ "$continue" != "y" ] && [ "$continue" != "Y" ]; then
        exit 1
    fi
fi

echo
echo "Installing dependencies..."
echo

echo "[1/4] Installing bpy..."
python3 -m pip install bpy==4.5.4 --extra-index-url https://download.blender.org/pypi/
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install bpy"
    exit 1
fi

echo
echo "[2/4] Installing Pillow..."
python3 -m pip install Pillow
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install Pillow"
    exit 1
fi

echo
echo "[3/4] Installing requests..."
python3 -m pip install requests
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install requests"
    exit 1
fi

echo
echo "[4/4] Installing zstandard..."
python3 -m pip install zstandard
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install zstandard"
    exit 1
fi

echo
echo "[OK] All dependencies installed!"
echo

# Check if config.py exists
if [ ! -f "config.py" ]; then
    if [ -f "config.example.py" ]; then
        echo "Creating config.py from template..."
        cp config.example.py config.py
        echo "[OK] config.py created"
        echo
        echo "[IMPORTANT] Please edit config.py and add your Roblox API key and user ID!"
    else
        echo "[WARN] config.example.py not found, skipping config setup"
    fi
else
    echo "[OK] config.py already exists"
fi

echo
echo "=================================================="
echo "Installation complete!"
echo "=================================================="
echo
echo "Next steps:"
echo "1. Edit config.py with your Roblox API key and user ID"
echo "2. Run: python3 main.py"
echo


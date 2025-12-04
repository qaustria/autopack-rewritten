#!/bin/bash

set -e

echo "=================================================="
echo "AutoPack Installer (Linux/macOS)"
echo "=================================================="
echo

# Find python executable
if command -v python3 &>/dev/null; then
    PY=python3
elif command -v python &>/dev/null; then
    PY=python
else
    echo "[ERROR] Python 3 is not installed."
    exit 1
fi

echo "[OK] Found Python: $PY"
$PY --version
echo

# Check Python version (must be 3.11.x)
PY_MAJOR=$($PY -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PY -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -ne 3 ] || [ "$PY_MINOR" -ne 11 ]; then
    echo "[WARN] AutoPack requires Python 3.11 for bpy."
    echo "Detected version: $PY_MAJOR.$PY_MINOR"
    read -p "Continue anyway? (y/n): " c
    if [[ "$c" != "y" && "$c" != "Y" ]]; then
        exit 1
    fi
fi

echo
echo "Installing dependencies..."
echo

# Allow user to use pre-downloaded bpy wheel
if ls ./bpy-*.whl 1> /dev/null 2>&1; then
    echo "[Found] Local bpy wheel detected:"
    ls bpy-*.whl
    read -p "Use local wheel instead of slow pip download? (y/n): " use_local
    if [[ "$use_local" == "y" || "$use_local" == "Y" ]]; then
        echo "[1/4] Installing local bpy wheel..."
        $PY -m pip install ./bpy-*.whl
        echo "[OK] Installed bpy from local wheel"
    else
        echo "[1/4] Installing bpy from Blender servers..."
        $PY -m pip install bpy==4.5.4 --pre --extra-index-url https://download.blender.org/pip/
    fi
else
    echo "[1/4] Installing bpy..."
    $PY -m pip install bpy==4.5.4 --pre --extra-index-url https://download.blender.org/pip/
fi

echo
echo "[2/4] Installing Pillow..."
$PY -m pip install Pillow

echo
echo "[3/4] Installing requests..."
$PY -m pip install requests

echo
echo "[4/4] Installing zstandard..."
$PY -m pip install zstandard


echo
echo "[OK] All dependencies installed!"
echo

# Config
if [ ! -f "config.py" ]; then
    if [ -f "config.example.py" ]; then
        echo "Creating config.py from template..."
        cp "config.example.py" "config.py"
        echo "[OK] config.py created"
        echo
        echo "[IMPORTANT] Please edit config.py and add your Roblox API key and user ID!"
    else
        echo "[WARN] config.example.py not found — skipping config creation."
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
echo "2. Run: $PY main.py"
echo

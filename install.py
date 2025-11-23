#!/usr/bin/env python3
"""AutoPack installer script"""

import sys
import subprocess
import os
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a pip install command and handle errors"""
    print(f"\n[{description}]")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"[OK] {description} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install {description}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False

def check_python_version():
    """Check if Python version is 3.11+"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("[WARN] Python 3.11 or higher is recommended")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("Installation cancelled.")
            sys.exit(1)
    else:
        print("[OK] Python version is compatible")

def install_dependencies():
    """Install all required dependencies"""
    dependencies = [
        (["python", "-m", "pip", "install", "bpy==4.5.4", 
          "--extra-index-url", "https://download.blender.org/pypi/"], "bpy"),
        (["python", "-m", "pip", "install", "Pillow"], "Pillow"),
        (["python", "-m", "pip", "install", "requests"], "requests"),
        (["python", "-m", "pip", "install", "zstandard"], "zstandard"),
    ]
    
    for cmd, name in dependencies:
        if not run_command(cmd, name):
            print(f"\n[ERROR] Installation failed at {name}")
            sys.exit(1)

def setup_config():
    """Create config.py if it doesn't exist"""
    config_path = Path("config.py")
    example_path = Path("config.example.py")
    
    if config_path.exists():
        print("\n[OK] config.py already exists")
    else:
        if example_path.exists():
            shutil.copy(example_path, config_path)
            print("\n[OK] Created config.py from template")
            print("[IMPORTANT] Please edit config.py and add your Roblox API key and user ID!")
        else:
            print("\n[WARN] config.example.py not found, skipping config setup")

def main():
    print("=" * 50)
    print("AutoPack Installer")
    print("=" * 50)
    print()
    
    print("Checking Python installation...")
    check_python_version()
    print()
    
    print("Installing dependencies...")
    install_dependencies()
    print()
    
    print("Setting up configuration...")
    setup_config()
    print()
    
    print("=" * 50)
    print("Installation complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("1. Edit config.py with your Roblox API key and user ID")
    print("2. Run: python main.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)


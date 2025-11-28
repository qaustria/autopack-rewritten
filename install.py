#!/usr/bin/env python3
"""AutoPack installer script"""

import sys
import subprocess
import os
import shutil
import tempfile
from pathlib import Path
from urllib.request import urlretrieve
import platform

TARGET_VERSION = "3.11.9"
TARGET_DIR = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Programs" / "Python" / "Python311"
TARGET_EXE = TARGET_DIR / "python.exe"

def run_command(cmd, description, python_exe):
    print(f"\n[{description}]")
    pretty_cmd = " ".join(cmd)
    print(f"Running: {pretty_cmd}")
    try:
        subprocess.run(cmd, check=True)
        print(f"[OK] {description} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install {description}")
        print(f"Command: {pretty_cmd}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False

def install_python311():
    if platform.system() != "Windows":
        print("[WARN] Automatic Python install is only supported on Windows. Please install Python 3.11.9 manually.")
        return None
    url = f"https://www.python.org/ftp/python/{TARGET_VERSION}/python-{TARGET_VERSION}-amd64.exe"
    temp_dir = Path(tempfile.gettempdir())
    installer = temp_dir / f"python-{TARGET_VERSION}-amd64.exe"
    print(f"Downloading Python {TARGET_VERSION} from {url}")
    try:
        urlretrieve(url, installer)
    except Exception as e:
        print(f"[ERROR] Failed to download Python installer: {e}")
        return None

    cmd = [
        str(installer),
        "/quiet",
        "InstallAllUsers=0",
        "PrependPath=1",
        "Include_test=0",
        f'TargetDir="{TARGET_DIR}"'
    ]
    print(f"Installing Python {TARGET_VERSION}...")
    try:
        subprocess.run(" ".join(cmd), check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Python installer failed: {e}")
        return None

    if not TARGET_EXE.exists():
        print(f"[ERROR] Expected python executable not found at {TARGET_EXE}")
        return None
    return TARGET_EXE

def ensure_python311():
    if sys.version_info[:2] == (3, 11):
        print(f"[OK] Using Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return Path(sys.executable)

    if os.environ.get("AUTOPACK_PY311_DONE") == "1":
        print("[WARN] Re-run detected but Python 3.11 is still not active. Please install Python 3.11.9 manually.")
        return Path(sys.executable)

    print("[INFO] Python 3.11 not detected. Attempting to install 3.11.9...")
    new_exe = install_python311()
    if not new_exe:
        sys.exit(1)

    env = os.environ.copy()
    env["AUTOPACK_PY311_DONE"] = "1"
    env["PATH"] = f"{new_exe.parent};{new_exe.parent / 'Scripts'};" + env.get("PATH", "")

    print(f"[INFO] Re-running installer with {new_exe}")
    subprocess.check_call([str(new_exe), Path(__file__).resolve()], env=env)
    sys.exit(0)

def install_dependencies(python_exe):
    deps = [
        ([str(python_exe), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], "pip/setuptools/wheel"),
        ([str(python_exe), "-m", "pip", "install", "bpy==4.5.4", "--pre", "--extra-index-url", "https://download.blender.org/pip/"], "bpy"),
        ([str(python_exe), "-m", "pip", "install", "Pillow"], "Pillow"),
        ([str(python_exe), "-m", "pip", "install", "requests"], "requests"),
        ([str(python_exe), "-m", "pip", "install", "zstandard"], "zstandard"),
    ]
    for cmd, name in deps:
        if not run_command(cmd, name, python_exe):
            print(f"\n[ERROR] Installation failed at {name}")
            sys.exit(1)

def setup_config():
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

    python_exe = ensure_python311()
    print()

    print(f"Installing dependencies with: {python_exe}")
    install_dependencies(python_exe)
    print()

    print("Setting up configuration...")
    setup_config()
    print()

    print("=" * 50)
    print("Installation complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    print(f"1. Edit config.py with your Roblox API key and user ID")
    print(f"2. Run: {python_exe} main.py")
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


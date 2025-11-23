@echo off
echo AutoPack Installer
echo ===================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11 from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Check Python version
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo Checking Python version...
python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>nul
if errorlevel 1 (
    echo [WARN] Python 3.11 or higher is recommended
    echo Current version: %PYTHON_VERSION%
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
)
echo.

echo Installing dependencies...
echo.

echo [1/4] Installing bpy...
python -m pip install bpy==4.5.4 --extra-index-url https://download.blender.org/pypi/
if errorlevel 1 (
    echo [ERROR] Failed to install bpy
    pause
    exit /b 1
)

echo.
echo [2/4] Installing Pillow...
python -m pip install Pillow
if errorlevel 1 (
    echo [ERROR] Failed to install Pillow
    pause
    exit /b 1
)

echo.
echo [3/4] Installing requests...
python -m pip install requests
if errorlevel 1 (
    echo [ERROR] Failed to install requests
    pause
    exit /b 1
)

echo.
echo [4/4] Installing zstandard...
python -m pip install zstandard
if errorlevel 1 (
    echo [ERROR] Failed to install zstandard
    pause
    exit /b 1
)

echo.
echo [OK] All dependencies installed!
echo.

REM Check if config.py exists
if not exist "config.py" (
    echo Creating config.py from template...
    copy config.example.py config.py >nul
    echo [OK] config.py created
    echo.
    echo [IMPORTANT] Please edit config.py and add your Roblox API key and user ID!
) else (
    echo [OK] config.py already exists
)

echo.
echo ===================
echo Installation complete!
echo ===================
echo.
echo Next steps:
echo 1. Edit config.py with your Roblox API key and user ID
echo 2. Run: python main.py
echo.
pause


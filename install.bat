@echo off
@echo off
setlocal enabledelayedexpansion

set TARGET_PY_VERSION=3.11.9
set TARGET_DIR=%LOCALAPPDATA%\Programs\Python\Python311
set TARGET_EXE=%TARGET_DIR%\python.exe

echo AutoPack Installer
echo ===================
echo.

set NEED_INSTALL=0
python --version >nul 2>&1
if errorlevel 1 (
    set NEED_INSTALL=1
) else (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set CURRENT_VERSION=%%v
    python -c "import sys; import re; import sys; import sys; sys.exit(0 if sys.version_info[:2]==(3,11) else 1)" 2>nul
    if errorlevel 1 set NEED_INSTALL=1
)

if %NEED_INSTALL%==1 (
    echo Python 3.11 not found. Installing %TARGET_PY_VERSION%...
    set INSTALLER=%TEMP%\python-%TARGET_PY_VERSION%-amd64.exe
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/%TARGET_PY_VERSION%/python-%TARGET_PY_VERSION%-amd64.exe -OutFile '%INSTALLER%'" || (
        echo [ERROR] Failed to download Python installer.
        pause
        exit /b 1
    )
    "%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 TargetDir="%TARGET_DIR%"
    if not exist "%TARGET_EXE%" (
        echo [ERROR] Python installer did not produce %TARGET_EXE%
        pause
        exit /b 1
    )
    set PATH=%TARGET_DIR%;%TARGET_DIR%\Scripts;%PATH%
) else (
    echo [OK] Python 3.11 detected
    set TARGET_EXE=python
)

echo Using Python: %TARGET_EXE%
%TARGET_EXE% --version
echo.

echo Installing dependencies...
echo.

echo Updating pip, setuptools, wheel...
%TARGET_EXE% -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [ERROR] Failed to update pip/setuptools/wheel
    pause
    exit /b 1
)

echo.
echo [1/4] Installing bpy (this may take a while)...
%TARGET_EXE% -m pip install bpy==4.5.4 --pre --extra-index-url https://download.blender.org/pip/
if errorlevel 1 (
    echo [ERROR] Failed to install bpy
    pause
    exit /b 1
)

echo.
echo [2/4] Installing Pillow...
%TARGET_EXE% -m pip install Pillow
if errorlevel 1 (
    echo [ERROR] Failed to install Pillow
    pause
    exit /b 1
)

echo.
echo [3/4] Installing requests...
%TARGET_EXE% -m pip install requests
if errorlevel 1 (
    echo [ERROR] Failed to install requests
    pause
    exit /b 1
)

echo.
echo [4/4] Installing zstandard...
%TARGET_EXE% -m pip install zstandard
if errorlevel 1 (
    echo [ERROR] Failed to install zstandard
    pause
    exit /b 1
)

echo.
echo [OK] All dependencies installed!
echo.

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
echo 2. Run: %TARGET_EXE% main.py
echo.
pause


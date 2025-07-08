@echo off
:: Voicemeeter Control Installer Build Script
:: This script automates the build process for creating the installer

echo ========================================
echo Voicemeeter Control Installer Build Script
echo ========================================
echo.

:: Check if we're running with admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges
) else (
    echo Warning: Not running as administrator
    echo If you're in Program Files, the build will use temp directory
)
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

:: Check if Git is installed (required for voicemeeter library)
git --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Git is not installed or not in PATH
    echo Git is required to install the Voicemeeter library
    echo Please install Git from https://git-scm.com/
    echo.
    echo Or manually install the library with:
    echo   pip install git+https://github.com/chvolkmann/voicemeeter-remote-python.git
    echo.
    pause
)

:: Create build directory first
if not exist "build_output" mkdir build_output

:: Check current directory permissions by trying to create a test file
echo. > test_write_permission.tmp 2>nul
if exist test_write_permission.tmp (
    del test_write_permission.tmp
    echo Working directory: %CD%
) else (
    echo Protected directory detected - build will use temp folder
)
echo.

:: Install required packages
echo Installing required Python packages...
echo ----------------------------------------
pip install pyinstaller pillow pyqt5 pyyaml keyboard
pip install git+https://github.com/chvolkmann/voicemeeter-remote-python.git

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install required packages
    echo Try running these commands manually:
    echo   pip install --user pyinstaller pillow pyqt5 pyyaml keyboard
    echo   pip install --user git+https://github.com/chvolkmann/voicemeeter-remote-python.git
    pause
    exit /b 1
)

:: Check for required source files
echo.
echo Checking for source files...
echo ----------------------------------------

set "missing_files=0"

if not exist "voicemeeter_control.py" (
    echo ERROR: voicemeeter_control.py not found!
    set "missing_files=1"
)

if not exist "volume_display.py" (
    echo ERROR: volume_display.py not found!
    set "missing_files=1"
)

if not exist "hotkey_handler.py" (
    echo ERROR: hotkey_handler.py not found!
    set "missing_files=1"
)

if not exist "config.yaml" (
    echo ERROR: config.yaml not found!
    set "missing_files=1"
)

if not exist "LICENSE" (
    echo ERROR: LICENSE not found!
    set "missing_files=1"
)

if not exist "icon.png" (
    echo WARNING: icon.png not found - a placeholder will be created
)

if "%missing_files%"=="1" (
    echo.
    echo ERROR: Required files are missing!
    echo Please ensure all files are in the current directory.
    pause
    exit /b 1
)

echo All required files found!

:: Check for build script
if not exist "build_installer.py" (
    echo.
    echo ERROR: build_installer.py not found!
    echo Please save the installer builder script first.
    pause
    exit /b 1
)

:: Run the installer builder
echo.
echo Running installer builder...
echo ========================================
python build_installer.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo All build files are in: build_output\
echo.
echo Next steps:
echo 1. Download and install Inno Setup from:
echo    https://jrsoftware.org/isdl.php
echo.
echo 2. Open build_output\installer\setup.iss in Inno Setup
echo.
echo 3. Press F9 or click Build -^> Compile to create the installer
echo.
echo 4. Your installer will be in: build_output\installer_output\
echo.
echo Note: This program requires Voicemeeter to be installed!
echo Get it from: https://vb-audio.com/Voicemeeter/
echo.
echo Press any key to open the build folder...
pause >nul
start "" "build_output"
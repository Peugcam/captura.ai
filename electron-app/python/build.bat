@echo off
REM GTA Analytics - Build Python Executable
REM =========================================

echo ========================================
echo GTA Analytics - Python Build
echo ========================================
echo.

REM Check if Python installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [2/4] Installing PyInstaller...
pip install pyinstaller

echo.
echo [3/4] Building executable...
pyinstaller --onefile ^
    --name capture ^
    --icon=..\assets\icon.ico ^
    --console ^
    --clean ^
    capture.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [4/4] Testing executable...
if exist "dist\capture.exe" (
    echo SUCCESS! Executable created: dist\capture.exe
    echo.
    echo File size:
    dir dist\capture.exe | find "capture.exe"
) else (
    echo ERROR: Executable not found!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Test: dist\capture.exe --server https://gta-analytics-v2.fly.dev --fps 0.5
echo 2. Copy to electron-app: copy dist\capture.exe ..\..\dist\python\
echo.
pause

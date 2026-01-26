@echo off
REM ============================================================================
REM Certify Intel - Windows Setup Script
REM ============================================================================
REM This script automates the installation process for Windows users.
REM Run this script from inside the extracted project folder.
REM ============================================================================

echo.
echo ============================================================
echo   Certify Intel - Automated Setup for Windows
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check if we're in the right directory (look for backend folder)
if not exist "backend" (
    echo.
    echo [ERROR] Cannot find 'backend' folder.
    echo Please run this script from inside the Certify Intel project folder.
    echo.
    echo Expected structure:
    echo   certify_intel/
    echo     backend/
    echo     frontend/
    echo     setup.bat  ^<-- Run from here
    echo.
    pause
    exit /b 1
)

echo [OK] Project structure verified
echo.

REM Navigate to backend
cd backend

REM Check if virtual environment already exists
if exist "venv" (
    echo [INFO] Virtual environment already exists. Skipping creation.
) else (
    echo [STEP 1/5] Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo.
echo [STEP 2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

echo.
echo [STEP 3/5] Installing Python dependencies...
echo This may take 2-5 minutes depending on your internet connection...
echo.
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Some packages may have failed to install.
    echo This is often due to Windows Long Path limitations.
    echo.
    echo TRY THIS FIX:
    echo 1. Move this folder to a shorter path (e.g., C:\certify_intel)
    echo 2. Or enable Windows Long Paths (requires admin):
    echo    - Open Registry Editor (regedit)
    echo    - Navigate to: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem
    echo    - Set LongPathsEnabled to 1
    echo    - Restart your computer
    echo 3. Then run this script again
    echo.
    pause
    exit /b 1
)
echo [OK] Dependencies installed

echo.
echo [STEP 4/5] Setting up configuration file...
if exist ".env" (
    echo [INFO] .env file already exists. Skipping.
) else (
    copy .env.example .env >nul
    echo [OK] Configuration file created (.env)
    echo.
    echo [IMPORTANT] To enable AI features, edit backend\.env and add your API keys:
    echo   - OPENAI_API_KEY=your-openai-key
    echo   - GOOGLE_AI_API_KEY=your-gemini-key
)

echo.
echo [STEP 5/5] Installing Playwright browsers (for web scraping)...
playwright install chromium >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Playwright browser installation skipped or failed.
    echo        Web scraping features may not work until you run:
    echo        playwright install chromium
) else (
    echo [OK] Playwright browsers installed
)

echo.
echo ============================================================
echo   SETUP COMPLETE!
echo ============================================================
echo.
echo To start the server, run:
echo   cd backend
echo   venv\Scripts\activate
echo   python main.py
echo.
echo Then open Chrome and go to: http://localhost:8000
echo.
echo Login credentials:
echo   Email:    admin@certifyhealth.com
echo   Password: certifyintel2024
echo.
echo ============================================================
echo.

REM Ask if user wants to start the server now
set /p START_NOW="Start the server now? (Y/N): "
if /i "%START_NOW%"=="Y" (
    echo.
    echo Starting Certify Intel server...
    echo Press Ctrl+C to stop the server.
    echo.
    python main.py
)

pause

@echo off
setlocal
set SCRIPT_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%Install_CertifyIntel.ps1"
if errorlevel 1 (
  echo.
  echo Installer failed. See error above.
  echo.
  pause
  exit /b 1
)
pause

@echo off
REM Certify Intel - Weekly Data Refresh Script
REM Schedule this with Windows Task Scheduler to run weekly
REM Author: Certify Intel Team
REM Date: January 2026

echo ============================================
echo Certify Intel Weekly Refresh
echo Started: %date% %time%
echo ============================================

REM Navigate to backend directory
cd /d "%~dp0..\backend"

REM Activate Python environment if exists
if exist "..\venv\Scripts\activate.bat" (
    call "..\venv\Scripts\activate.bat"
)

REM Run the weekly refresh
echo Running weekly data refresh...
python -c "import asyncio; from scheduler import trigger_refresh_now; asyncio.run(trigger_refresh_now())"

REM Send weekly digest email
echo Sending weekly summary email...
python -c "from alerts import send_weekly_summary; send_weekly_summary()"

REM Run discovery scan
echo Running discovery scan...
python discovery_agent.py --max 10

echo ============================================
echo Weekly refresh completed: %date% %time%
echo ============================================

REM Log completion
echo %date% %time% - Weekly refresh completed >> weekly_refresh.log

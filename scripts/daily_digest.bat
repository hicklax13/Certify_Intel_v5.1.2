@echo off
REM Certify Intel - Daily Digest Script
REM Schedule this with Windows Task Scheduler to run daily at 6 AM
REM Author: Certify Intel Team

echo ============================================
echo Certify Intel Daily Digest
echo Started: %date% %time%
echo ============================================

cd /d "%~dp0..\backend"

REM Activate Python environment if exists
if exist "..\venv\Scripts\activate.bat" (
    call "..\venv\Scripts\activate.bat"
)

REM Check high-priority competitors
echo Checking high-priority competitors...
python -c "import asyncio; from scheduler import trigger_refresh_now; from main import SessionLocal, Competitor; db=SessionLocal(); ids=[c.id for c in db.query(Competitor).filter(Competitor.threat_level=='High').all()]; db.close(); asyncio.run(trigger_refresh_now(ids)) if ids else print('No high-priority competitors')"

REM Send daily digest
echo Sending daily digest email...
python -c "from alerts import send_daily_digest; send_daily_digest()"

echo ============================================
echo Daily digest completed: %date% %time%
echo ============================================

echo %date% %time% - Daily digest completed >> daily_digest.log

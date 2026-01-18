# Certify Intel - Scheduler Setup Guide

## Overview

This guide explains how to set up automated data refresh using Windows Task Scheduler or the built-in APScheduler.

---

## Option 1: Windows Task Scheduler (Recommended for Windows)

### Weekly Full Refresh (Sundays at 2 AM)

1. **Open Task Scheduler**
   - Press `Win + R`, type `taskschd.msc`, press Enter

2. **Create New Task**
   - Click "Create Task" in the right panel

3. **General Tab**
   - Name: `Certify Intel - Weekly Refresh`
   - Description: `Weekly full competitor data refresh and summary email`
   - Run whether user is logged on or not: ✓
   - Run with highest privileges: ✓

4. **Triggers Tab**
   - New → Weekly
   - Start: 2:00 AM
   - Recur every 1 week on: Sunday

5. **Actions Tab**
   - New → Start a program
   - Program: `C:\Users\conno\Downloads\Certify_Health_Intelv1\scripts\weekly_refresh.bat`

6. **Conditions Tab**
   - Wake computer to run: ✓ (optional)

7. **Settings Tab**
   - Allow task to run on demand: ✓
   - Stop task if it runs longer than: 2 hours

### Daily High-Priority Check (Daily at 6 AM)

1. **Create another task**:
   - Name: `Certify Intel - Daily Digest`
   - Trigger: Daily at 6:00 AM
   - Action: `C:\Users\conno\Downloads\Certify_Health_Intelv1\scripts\daily_digest.bat`

---

## Option 2: APScheduler (Built-in Python Scheduler)

### Start the Scheduler

```bash
cd backend
python scheduler.py
```

This runs the built-in scheduler with:

- Weekly refresh: Sundays at 2 AM
- Daily high-priority check: Daily at 6 AM

### Run as Windows Service

To run the scheduler as a Windows service:

```bash
# Install pywin32
pip install pywin32

# Create service
python -c "
import win32serviceutil
import win32service
import subprocess

class CertifySchedulerService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'CertifyIntelScheduler'
    _svc_display_name_ = 'Certify Intel Scheduler'
    
    def SvcDoRun(self):
        subprocess.run(['python', 'scheduler.py'])
    
    def SvcStop(self):
        pass
"
```

---

## Option 3: Celery Beat (For Docker/Production)

If running with Docker, Celery Beat handles scheduling automatically:

```bash
# Start with Docker Compose
docker-compose up -d celery-beat
```

The beat schedule is defined in `celery_app.py`:

- `weekly-full-refresh`: Every 7 days
- `daily-high-priority-check`: Every 24 hours
- `daily-digest`: Every 24 hours

---

## Verifying Scheduled Tasks

### Check Windows Task Status

```cmd
schtasks /query /tn "Certify Intel - Weekly Refresh"
```

### View Last Run Results

```cmd
type C:\Users\conno\Downloads\Certify_Health_Intelv1\scripts\weekly_refresh.log
```

### Manual Trigger for Testing

```bash
# Run weekly refresh manually
cd backend
python -c "import asyncio; from scheduler import trigger_refresh_now; asyncio.run(trigger_refresh_now())"

# Send digest manually
python -c "from alerts import send_weekly_summary; send_weekly_summary()"
```

---

## Schedule Summary

| Task | Schedule | Script |
|------|----------|--------|
| Weekly Full Refresh | Sundays 2:00 AM | `weekly_refresh.bat` |
| Daily High-Priority | Daily 6:00 AM | `daily_digest.bat` |
| Daily Email Digest | Daily 6:00 AM | (included in daily_digest.bat) |

---

## Troubleshooting

### Task Not Running

1. Check Task Scheduler history: Task Scheduler → View → Show All Running Tasks
2. Verify Python is in PATH
3. Check the log files in `scripts/` folder

### Email Not Sending

1. Verify `.env` has SMTP credentials
2. Test manually: `python test_email.py --send`
3. Check spam folder

### Database Errors

1. Ensure backend server is running (or database is accessible)
2. Check `backend/certify_intel.db` exists

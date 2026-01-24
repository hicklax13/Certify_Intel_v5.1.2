# Phase 3A: Static Endpoint Testing Results & Execution Guide

**Status**: ✅ READY FOR IMMEDIATE EXECUTION
**Date**: 2026-01-24
**Test Suite**: run_tests.py (449 lines, 9 automated tests)
**Duration**: ~5 minutes (setup + 2-3 minutes test execution)
**Expected Result**: 7-9/9 tests pass, 0 failures

---

## Execution Instructions

### Prerequisites Check
Before running tests, ensure:
- Python 3.9+ is installed
- Backend code is available at `/home/user/Project_Intel_v4/backend/`
- Port 8000 is available (not in use)
- Internet connection available (for discovery agent and news monitoring)

### Step 1: Install Backend Dependencies

```bash
cd /home/user/Project_Intel_v4/backend
pip install -r requirements.txt
```

**Expected output:**
```
Collecting fastapi...
Collecting sqlalchemy...
Collecting uvicorn...
...
Successfully installed [40+ packages]
```

**Duration**: 30-60 seconds on first install

**Troubleshooting**:
- If pip fails: `python -m pip install --upgrade pip`
- If specific package fails: `pip install [package-name]` individually
- For Playwright: `pip install playwright && playwright install chromium` (optional for Phase 3A)

### Step 2: Start the Backend Server (Terminal 1)

```bash
cd /home/user/Project_Intel_v4/backend
python main.py
```

**Expected output:**
```
Certify Intel Backend starting...
============================================================
Validating configuration...

Available Scrapers:
  ✅ Playwright Base Scraper
  ✅ SEC Edgar (yfinance)
  ✅ News Monitor (Google News RSS)
  ✅ Known Data Fallback

Disabled Scrapers (Paid APIs):
  ❌ Crunchbase
  ❌ PitchBook
  ❌ LinkedIn (live scraping)

Optional Features:
  ⚠️ AI Features - DISABLED
  ⚠️ Email Alerts - DISABLED
  ⚠️ Slack Notifications - DISABLED
============================================================

INFO: Started server process [PID]
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Duration**: 5-10 seconds to start

**Troubleshooting**:
- If "Address already in use": Kill existing process: `lsof -i :8000` then `kill -9 [PID]`
- If database locked: `rm backend/certify_intel.db` (will recreate on start)
- If missing dependencies: Go back to Step 1

### Step 3: Wait for Backend to Stabilize

Wait approximately **5-10 seconds** for backend to fully initialize. You should see no errors in the backend logs.

Verify backend is running:
```bash
# In Terminal 2 (before running tests)
curl -s http://localhost:8000/api/health | python -m json.tool
# Expected: {"status": "ok"} or similar
```

### Step 4: Run the Test Suite (Terminal 2)

```bash
cd /home/user/Project_Intel_v4
python run_tests.py
```

**Expected output** (example):
```
======================================================================
PHASE 3A: CORE WORKFLOW STATIC ENDPOINT TESTS
======================================================================
Testing: http://localhost:8000
User: admin@certifyhealth.com
======================================================================

✅ [14:30:15] Test HEALTH: API Health Check
   → API is responding

✅ [14:30:16] Test A1: Authentication - Valid Credentials
   → Token: eyJhbGciOiJIUzI1NiIs...

✅ [14:30:17] Test A2: Dashboard Display
   → Loaded 30+ competitors

✅ [14:30:18] Test A3: Competitors List
   → Retrieved 30+ competitors

✅ [14:30:19] Test A3b: Search Competitors
   → Found 10 matches for 'health'

✅ [14:30:20] Test A4: Competitor Detail
   → Retrieved: Phreesia

✅ [14:30:25] Test A5: Excel Export
   → Generated 125000 byte file

✅ [14:30:27] Test A6: JSON Export
   → Generated valid JSON (5000 chars)

✅ [14:30:28] Test C3: Changes Log
   → Retrieved 15 recent changes

⚠️ [14:30:35] Test D1: Discovery Agent
   → Discovery agent initiated (may timeout)

======================================================================
TEST SUMMARY
======================================================================
✅ Passed:  9/9
⚠️ Warnings: 0/9
❌ Failed:  0/9
======================================================================

🎉 PHASE 3A - STATIC TESTS SUCCESSFUL!
System is ready for Phase 3B (Data Integrity Tests)
```

**Duration**: 2-3 minutes for all tests

**Troubleshooting**:
- If "Connection refused": Backend not running or not ready. Wait 10 seconds and retry.
- If "Authentication failed": Credentials may have changed. Check backend code for default user.
- If "Timeout": May be slow network or system. Increase timeout in run_tests.py if needed.

---

## Test Cases Detailed Description

### Test HEALTH: API Health Check
**What it does**: Sends GET request to `/api/health` endpoint
**Success criteria**: Server responds with status code 200
**Why it matters**: Confirms backend is running and responding
**Blocking**: Yes - all other tests fail if this fails

### Test A1: Authentication
**What it does**: Sends login request with hardcoded credentials
- Username: `admin@certifyhealth.com`
- Password: `certifyintel2024`
**Success criteria**: Receives JWT token in response
**Why it matters**: All other tests require valid JWT token
**Blocking**: Yes - all other tests fail if this fails

### Test A2: Dashboard Display
**What it does**: Calls `/api/dashboard` endpoint with JWT token
**Success criteria**: Returns dashboard data with 30+ competitors
**Why it matters**: Users see dashboard on login
**Blocking**: No - system works without dashboard

### Test A3: Competitors List
**What it does**: Calls `/api/competitors` endpoint to retrieve all competitors
**Success criteria**: Returns list of 30+ competitors with full data
**Why it matters**: Core list view in UI
**Blocking**: No - but important

### Test A3b: Search Competitors
**What it does**: Calls `/api/competitors/search?q=health` to filter competitors
**Success criteria**: Returns matching competitors (10+ expected with 'health' keyword)
**Why it matters**: Users need to search/filter
**Blocking**: No

### Test A4: Competitor Details
**What it does**: Calls `/api/competitors/1` to get single competitor
**Success criteria**: Returns full competitor record with 50+ fields
**Why it matters**: Detail view for single competitor
**Blocking**: No - but important

### Test A5: Excel Export
**What it does**: Calls `/api/export/excel` to download Excel file
**Success criteria**: Returns valid XLSX file (100KB+)
**Why it matters**: Export feature for sales teams
**Blocking**: No - may be file system dependent

### Test A6: JSON Export
**What it does**: Calls `/api/export/json` to get JSON data
**Success criteria**: Returns valid JSON array with all competitors
**Why it matters**: Power BI integration
**Blocking**: No

### Test C3: Changes Log
**What it does**: Calls `/api/changes` to get change history
**Success criteria**: Returns 10+ recent changes
**Why it matters**: Audit trail and alerts
**Blocking**: No

### Test D1: Discovery Agent
**What it does**: Calls `/api/discovery/run` to trigger discovery
**Success criteria**: Agent initiates (may timeout due to network)
**Why it matters**: Find new competitors automatically
**Blocking**: No - enhancement feature

---

## Expected Results Summary

### Success Scenarios

**Excellent** (All 9 pass):
```
✅ Passed: 9/9
⚠️ Warnings: 0/9
❌ Failed: 0/9
→ System fully functional, ready for Phase 3B/4
```

**Good** (8/9 with 1 warn):
```
✅ Passed: 8/9
⚠️ Warnings: 1/9
❌ Failed: 0/9
→ Minor issue (likely discovery agent timeout or file system)
→ Proceed to Phase 3B/4, monitor issue
```

**Acceptable** (7/9 with 2 warn):
```
✅ Passed: 7/9
⚠️ Warnings: 2/9
❌ Failed: 0/9
→ Some optional features missing but core works
→ Can proceed to Phase 3B/4, fix issues later
```

**Not Passing** (Any failures):
```
✅ Passed: X/9
⚠️ Warnings: X/9
❌ Failed: X/9
→ Must fix issues before proceeding
→ Review troubleshooting guide below
```

---

## Troubleshooting Guide

### Issue 1: "Connection refused" when running tests

**Symptom**: `requests.exceptions.ConnectionError: Connection refused`

**Cause**: Backend not running or not ready

**Solution**:
```bash
# Verify backend is running
lsof -i :8000
# Should show python process

# If not running, start it
cd /home/user/Project_Intel_v4/backend
python main.py

# Wait 10 seconds for startup, then retry tests
```

### Issue 2: "Authentication failed"

**Symptom**: `Test A1 FAILS - Authentication error`

**Cause**: Credentials wrong or auth system broken

**Solution**:
```bash
# Check credentials in backend code
grep -n "admin@certifyhealth.com" backend/extended_features.py

# Or test auth directly
curl -X POST http://localhost:8000/token \
  -d "username=admin@certifyhealth.com&password=certifyintel2024&grant_type=password"

# If that fails, check that extended_features.py is loaded in main.py
```

### Issue 3: "Connection timeout" on tests

**Symptom**: Tests hang or timeout after 30 seconds

**Cause**: Backend busy, network slow, or database locked

**Solution**:
```bash
# Check backend logs for errors
# If database locked:
rm /home/user/Project_Intel_v4/backend/certify_intel.db
# Restart backend (it will recreate DB)

# If backend is hanging:
# Kill it and restart
# Look for errors in backend output
```

### Issue 4: "Excel export returns empty or fails"

**Symptom**: Test A5 WARNS or FAILS

**Cause**: File system permissions or missing library

**Solution**:
```bash
# Check openpyxl is installed
python -c "import openpyxl; print('OK')"

# If missing:
pip install openpyxl reportlab

# Check write permissions
touch /tmp/test.xlsx
# Should succeed

# Retry test
```

### Issue 5: "Discovery agent timeout"

**Symptom**: Test D1 WARNS - Discovery agent took too long

**Cause**: Network timeout (expected, not an error)

**Solution**:
```bash
# This is normal - discovery agent makes external API calls
# Status: ⚠️ WARN is acceptable
# It's an enhancement feature, not critical

# Can increase timeout in run_tests.py if desired:
# Change DEFAULT_TIMEOUT from 10 to 30
```

### Issue 6: Dashboard/Export returns empty

**Symptom**: Tests A2, A5, A6 return no data

**Cause**: Database not initialized or seeded

**Solution**:
```bash
# Check if database exists
ls -la /home/user/Project_Intel_v4/backend/certify_intel.db

# If missing or empty, it will auto-create on start
# But data may need to be seeded:
cd /home/user/Project_Intel_v4/backend

# Check if seed_db.py exists
ls -la seed_db.py

# If exists, run it
python seed_db.py

# Restart backend and retry tests
```

---

## Manual Test Verification (Optional)

If you want to verify tests manually before running suite:

```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "username=admin@certifyhealth.com&password=certifyintel2024&grant_type=password" \
  | grep -o '"access_token":\"[^\"]*' | cut -d'\"' -f4)

# Test health
curl http://localhost:8000/api/health | python -m json.tool

# Test competitors list
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/competitors | python -m json.tool | head -20

# Test search
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/competitors/search?q=health | python -m json.tool

# Test single competitor
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/competitors/1 | python -m json.tool | head -30
```

---

## After Tests Complete

### If Tests Pass (7+ pass, 0 failures):

```bash
# Document results
# Create PHASE_3A_RESULTS.md (you are reading it)

# Proceed to Phase 3B or Phase 4
# Phase 3B: Optional data integrity tests (1 hour)
# Phase 4: Export validation (1 hour)

# To proceed to Phase 3B:
# Follow instructions in PHASE_3_TEST_PLAN.md

# To proceed to Phase 4:
# Follow instructions in PHASE_4_EXPORT_VALIDATION_PLAN.md
```

### If Tests Fail:

```bash
# Review troubleshooting section above
# Fix identified issues
# Retry Phase 3A with: python run_tests.py

# Common fixes:
# 1. Restart backend (ctrl+c, then python main.py)
# 2. Clear database: rm certify_intel.db
# 3. Reinstall dependencies: pip install -r requirements.txt

# After fixes:
# python run_tests.py  # Try again
```

---

## Phase 3A Success Criteria

### Minimum Success (MVP)
- ✅ 7/9 tests pass
- ✅ 0 critical failures (A1, A3, A4 must pass)
- ✅ Core endpoints responding
- ✅ Database initialized
- ✅ Authentication working

### Expected Success
- ✅ 8-9/9 tests pass
- ✅ 0-1 warnings acceptable
- ✅ All core workflows functional
- ✅ Exports working

### Excellent Success
- ✅ 9/9 tests pass
- ✅ 0 warnings
- ✅ Discovery agent working
- ✅ All features operational

---

## Next Steps Decision Tree

```
Phase 3A Complete?
├─ YES, 9/9 pass
│  └─ ✅ PROCEED TO PHASE 3B or PHASE 4
│     ├─ Phase 3B: Data integrity tests (optional, 1 hour)
│     └─ Phase 4: Export validation (1 hour)
│
├─ YES, 7-8/9 pass
│  └─ ✅ PROCEED TO PHASE 4 (core features work)
│     └─ Document warnings, monitor
│
└─ NO, Any failures
   └─ ⏸️ MUST FIX FIRST
      ├─ Identify failing test
      ├─ Use troubleshooting guide above
      ├─ Fix issue
      └─ Retry: python run_tests.py
```

---

## Phase 3A Test Commands Quick Reference

```bash
# Setup (one time)
cd /home/user/Project_Intel_v4/backend
pip install -r requirements.txt

# Terminal 1: Start backend
python main.py

# Terminal 2: Run tests (wait 5 seconds after backend starts)
cd /home/user/Project_Intel_v4
python run_tests.py

# Optional: Manual verification
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "username=admin@certifyhealth.com&password=certifyintel2024&grant_type=password" \
  | grep -o '"access_token":\"[^\"]*' | cut -d'\"' -f4)

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/competitors | python -m json.tool
```

---

## Environment Information

**Test Suite Location**: `/home/user/Project_Intel_v4/run_tests.py`
**Backend Location**: `/home/user/Project_Intel_v4/backend/`
**Database Location**: `/home/user/Project_Intel_v4/backend/certify_intel.db`
**Configuration**: `/home/user/Project_Intel_v4/backend/.env`

**Requirements**:
- Python 3.9+
- pip (Python package manager)
- Internet connection (for discovery agent and news monitoring)
- Port 8000 available

**Optional for Phase 3B**:
- Playwright: `pip install playwright && playwright install chromium`
- yfinance: `pip install yfinance pandas`

---

## Conclusion

Phase 3A test execution is ready. This is the first validation that the system's core endpoints are working correctly.

**Expected Duration**: ~8 minutes total
- 1 minute: Install dependencies
- 1 minute: Start backend
- 3 minutes: Run tests
- 3 minutes: Review and document results

**Next Step**: Execute `python run_tests.py` and document results in this file

---

**Phase 3A is ready for immediate execution.**

For detailed information about each test, see `PHASE_3_TEST_PLAN.md`
For setup guidance, see `PHASE_3A_SETUP_GUIDE.md`
For overall context, see `PHASE_3_EXECUTION_GUIDE.md`

*Document will be updated with actual test results once Phase 3A is executed.*

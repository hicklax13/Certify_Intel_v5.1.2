# Phase 3: Core Workflows Testing
## Complete Execution Guide

**Status**: Ready for Agent Execution
**Date**: 2026-01-24
**Target**: Test all core workflows and verify system functionality

---

## Phase 3 Overview

Phase 3 consists of 3 sub-phases:
- **Phase 3A**: Static endpoint tests (no external dependencies)
- **Phase 3B**: Data integrity tests (with optional scrapers)
- **Phase 3C**: Integration tests (end-to-end workflows)

Current status: **Phase 3A ready for immediate execution**

---

## Phase 3A: Static Endpoint Tests

### What Gets Tested
9 automated tests covering critical API endpoints:

1. **HEALTH** - API is running
2. **A1** - Authentication (login)
3. **A2** - Dashboard display
4. **A3** - Competitors list
5. **A3b** - Search functionality
6. **A4** - Competitor details
7. **A5** - Excel export
8. **A6** - JSON export
9. **C3** - Changes log
10. **D1** - Discovery agent

### Prerequisites
```bash
# Step 1: Install dependencies
cd backend
pip install -r requirements.txt

# Step 2: Start backend (Terminal 1)
python main.py

# Step 3: Run tests (Terminal 2)
cd ..
python run_tests.py
```

### Expected Output
```
======================================================================
TEST SUMMARY
======================================================================
✅ Passed:  7-9/9
⚠️ Warnings: 0-2/9
❌ Failed:  0/9
======================================================================

🎉 PHASE 3A - STATIC TESTS SUCCESSFUL!
System is ready for Phase 3B (Data Integrity Tests)
```

### Expected Duration
- Setup: 2-3 minutes (install, start backend, run tests)
- Tests: 2-3 minutes
- **Total: ~5 minutes**

### Success Criteria
- ✅ Failures = 0
- ✅ Passed ≥ 7/9
- ✅ All core endpoints working

---

## Phase 3B: Data Integrity Tests (Optional)

### What Gets Tested
- Database persistence (data survives restart)
- Change detection accuracy
- Data transformation (scraping → storage)
- Known data fallback (when scrapers unavailable)

### Prerequisites
```bash
# Same as Phase 3A, plus:
pip install playwright
playwright install chromium
pip install yfinance pandas
```

### Test Workflows
1. Add new competitor → Verify stored in database
2. Trigger scrape → Verify data updated
3. Check ChangeLog → Verify changes tracked
4. Export → Verify all data included

### Expected Duration
- 30 minutes - 1 hour

### Success Criteria
- ✅ All database operations working
- ✅ Changes tracked accurately
- ✅ Data persistence verified

---

## Phase 3C: Integration Tests (Optional)

### What Gets Tested
- Full end-to-end workflows
- Multiple components working together
- Scheduler execution
- Discovery agent finding competitors

### Test Workflows
1. **Workflow A**: Login → Dashboard → Search → View → Export → Logout
2. **Workflow B**: Add Competitor → Scrape → Data Appears → Verify
3. **Workflow C**: Scheduled job → Scrape → Change detection → Alert
4. **Workflow D**: Discovery agent → Find competitors → Add → Scrape

### Expected Duration
- 1-2 hours

### Success Criteria
- ✅ All workflows complete end-to-end
- ✅ Data flows correctly through system
- ✅ All features working together

---

## Quick Start: Phase 3A Execution

### For Impatient Users (TL;DR)
```bash
# Install
cd backend && pip install -r requirements.txt

# Terminal 1: Start backend
python main.py

# Terminal 2: Run tests (wait ~5 seconds first)
cd .. && python run_tests.py

# Result: Check summary at end of output
```

### For Careful Users (Step-by-Step)
See `PHASE_3A_SETUP_GUIDE.md` for detailed instructions

---

## Test Documentation

### Available Test Specs
1. `PHASE_3_TEST_PLAN.md` (400+ lines)
   - Detailed specification of all tests
   - Success criteria for each test
   - Known limitations
   - Troubleshooting guide

2. `PHASE_3_READINESS.md` (361 lines)
   - Quick start guide
   - Prerequisites checklist
   - Expected results by phase
   - Agent guidance

3. `PHASE_3A_SETUP_GUIDE.md` (NEW - 400+ lines)
   - Step-by-step setup instructions
   - Expected output examples
   - Issue troubleshooting
   - Success metrics

### Test Results Documentation
After running Phase 3A, create `PHASE_3A_RESULTS.md`:
```markdown
# Phase 3A Test Results

**Date**: [date run]
**Status**: PASS / PARTIAL / FAIL

## Summary
- Passed: X/9
- Warnings: X/9
- Failed: X/9

## Issues Found
[List any failures or blockers]

## Next Steps
[Recommend Phase 3B, Phase 4, or fixes needed]
```

---

## Phase 3 Workflow Breakdown

### Workflow A: User Login → Export Journey
```
User starts → Login (A1)
→ See Dashboard (A2)
→ Search (A3b)
→ View Details (A4)
→ Export (A5, A6)
→ Logout
```
**Tests**: A1, A2, A3b, A4, A5, A6
**Critical**: Yes - core user journey
**Expected**: All pass

### Workflow B: Add Competitor → Scrape → Verify
```
Admin → Add new competitor (POST /api/competitors)
→ Click refresh (POST /api/scrape/{id})
→ Verify data appears (GET /api/competitors/{id})
→ Check ChangeLog (GET /api/changes)
```
**Tests**: A3 (list), A4 (verify), C3 (changes)
**Critical**: Yes - data collection pipeline
**Expected**: All pass

### Workflow C: Scheduled Scrape → Change Detection
```
Scheduler runs → Scrapes all competitors
→ Compares new vs old data
→ Detects changes
→ Logs to ChangeLog (C3)
→ Sends alerts (optional)
```
**Tests**: C3 (changes logged)
**Critical**: Medium - alerts are nice-to-have
**Expected**: Pass with warnings OK

### Workflow D: Discovery Agent
```
User → Trigger discovery (POST /api/discovery/run)
→ Agent searches for new competitors
→ Returns candidates
→ User adds selected ones
```
**Tests**: D1 (discovery agent)
**Critical**: Low - enhancement feature
**Expected**: Pass or warn (network timeouts OK)

---

## What Happens If Tests Fail

### Failure: HEALTH (API not responding)
**Cause**: Backend not running or wrong port
**Fix**:
```bash
# Check if running
lsof -i :8000

# If running, kill and restart
kill -9 [PID]
python main.py
```

### Failure: A1 (Authentication)
**Cause**: Credentials wrong or auth system broken
**Fix**:
```bash
# Check credentials in code
grep -n "admin@certifyhealth.com" backend/extended_features.py

# Verify auth manager working
python -c "from extended_features import auth_manager; print('Auth OK')"
```

### Failure: A2-A4 (Dashboard/Data endpoints)
**Cause**: Database not initialized or corrupted
**Fix**:
```bash
# Reinitialize database
rm backend/certify_intel.db
python main.py  # Will recreate automatically

# Reseed data
cd backend && python seed_db.py
```

### Failure: A5 (Excel export)
**Cause**: File system permission or missing library
**Fix**:
```bash
# Check write permissions
touch /tmp/test.xlsx  # Should succeed

# Reinstall reporting libraries
pip install openpyxl reportlab
```

### Failure: D1 (Discovery agent)
**Cause**: Network timeout (expected, not a failure)
**Fix**: This is normal - discovery agent calls external APIs. Warn but continue.

---

## Post-Phase 3A Steps

### If Phase 3A Passes (0 failures)
```
✅ MOVE TO PHASE 4
   - Export validation
   - Excel, PDF, JSON format testing
   - Duration: 1 hour
```

### If Phase 3A Has Warnings (0 failures, 1-2 warnings)
```
✅ MOVE TO PHASE 3B (Optional)
   - Data integrity testing
   - Scraper testing
   - Change detection verification
   - Duration: 1 hour
```

### If Phase 3A Fails (any failures)
```
⏸️ MUST FIX FIRST
   1. Identify failing test
   2. Check troubleshooting in PHASE_3_TEST_PLAN.md
   3. Fix issue
   4. Verify with: python run_tests.py
   5. Document fix
   6. Try again
```

---

## Success Metrics

### Phase 3A Success
```
✅ 7-9/9 tests pass
✅ 0 critical failures
✅ All core endpoints working
✅ System ready for Phase 4
```

### System Readiness Level After Phase 3A
```
Minimum: MVP-ready (core features work)
Expected: Production-ready (all workflows work)
Excellent: Fully-featured (with optional APIs)
```

---

## Files Prepared for Phase 3

### Test Infrastructure
```
run_tests.py              - Executable test suite (9 tests)
PHASE_3_TEST_PLAN.md     - Complete specification (400+ lines)
PHASE_3_READINESS.md     - Quick start guide (361 lines)
PHASE_3A_SETUP_GUIDE.md  - Detailed setup (this helps running tests)
```

### Documentation
```
PLAN.md                  - Master plan with phase status
WORK_SUMMARY.md          - Complete work summary
PHASE_1_SUMMARY.md       - Phase 1 details
PHASE_2_SUMMARY.md       - Phase 2 details
SCRAPERS.md             - Data sources guide
CLAUDE.md               - Project overview
.env.example            - Configuration template
```

---

## Agent Guidance

### For Agents Running Phase 3A
1. **Review** `PHASE_3A_SETUP_GUIDE.md` (5 min read)
2. **Install** dependencies (1 min)
3. **Start** backend (30 sec)
4. **Run** tests (3 min)
5. **Document** results in PHASE_3A_RESULTS.md (10 min)
6. **Report** findings to team

### For Agents Fixing Issues
1. **Check** error message in test output
2. **Reference** PHASE_3_TEST_PLAN.md troubleshooting
3. **Fix** identified issue
4. **Retest** with `python run_tests.py`
5. **Document** fix for team

### For Agents Continuing to Phase 4
1. **Verify** Phase 3A passed
2. **Move to** Phase 4 (export validation)
3. **Update** PLAN.md with Phase 4 status
4. **Create** PHASE_4_RESULTS.md
5. **Proceed** or escalate if blocked

---

## Expected Timeline

```
Phase 3A:     5 minutes (setup + tests)
Phase 3B:     1 hour (optional, data integrity)
Phase 3C:     2 hours (optional, integration)
Phase 4:      1 hour (export validation)
Phase 5:      1 hour (data quality)
────────────────────────────────
Total:        ~10 hours (all phases)
```

Or for minimal testing:
```
Phase 3A:     5 minutes
Phase 4:      1 hour
Phase 5:      1 hour
────────────────────
Total:        ~2 hours (core validation)
```

---

## Summary

Phase 3 testing is **fully prepared and ready to execute**:

✅ 9 automated tests written
✅ Test specifications documented
✅ Setup guide created
✅ Success criteria defined
✅ Troubleshooting guide available

**To begin Phase 3A**:
```bash
cd backend && pip install -r requirements.txt
python main.py  # Terminal 1
cd .. && python run_tests.py  # Terminal 2
```

**Expected result**: 7-9/9 tests pass in 2-3 minutes

**Next step**: Document results and proceed to Phase 4

---

**Phase 3 is ready. Agents can execute immediately.**

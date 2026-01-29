# Quick Reference Card - All Commands & Information

**Print this page or bookmark it for easy reference during testing**

---

## Project Overview (One-Liner)

Certify Health Intel: Production-ready competitive intelligence platform tracking 30+ competitors using free/open-source data sources (Playwright, yfinance, Google News RSS). No paid APIs required.

---

## File Locations

```
/home/user/Project_Intel_v4/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # App entry point
│   ├── requirements.txt        # Python dependencies
│   └── certify_intel.db        # SQLite database
├── frontend/                   # Web UI (HTML/JS)
├── run_tests.py               # Automated test suite ⭐
├── CLAUDE.md                  # Project overview
├── PLAN.md                    # Development plan
├── TESTING_INDEX.md           # Documentation index ⭐
├── PHASE_3A_EXECUTION_SUMMARY.md  # Quick start ⭐
├── PHASE_3_TEST_PLAN.md       # Complete test specs
├── PHASE_4_EXPORT_VALIDATION_PLAN.md
└── PHASE_5_DATA_QUALITY_PLAN.md
```

---

## Essential Commands

### 🚀 Phase 3A: Run All Endpoint Tests (5-8 minutes)

```bash
# Terminal 1: Start backend
cd /home/user/Project_Intel_v4/backend
pip install -r requirements.txt
python main.py

# Terminal 2: Run tests (wait ~5 sec after backend starts)
cd /home/user/Project_Intel_v4
python run_tests.py
```

**Expected output**:
```
✅ Passed:  7-9/9
⚠️ Warnings: 0-2/9
❌ Failed:  0/9
🎉 PHASE 3A SUCCESS!
```

### Check Backend Health

```bash
# Verify backend is running
curl http://localhost:8000/api/health
# Expected: {"status": "ok"}

# Check what's using port 8000
lsof -i :8000

# Kill process on port 8000 if needed
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Get Authentication Token (Manual Testing)

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "username=admin@certifyintel.com&password=MSFWINTERCLINIC2026&grant_type=password" \
  | grep -o '"access_token":\"[^\"]*' | cut -d'\"' -f4)

echo $TOKEN  # Print token
```

### Phase 4: Test Exports Manually

```bash
# Excel export
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/export/excel -o competitors.xlsx

# JSON export
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/export/json > competitors.json

# Verify JSON is valid
python -m json.tool competitors.json > /dev/null && echo "Valid" || echo "Invalid"
```

### Phase 5: Test Data Quality

```bash
# Quality scores
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/scores | python -m json.tool | head -50

# Stale data
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/stale | python -m json.tool

# Audit trail
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/data-quality/audit/1 | python -m json.tool | head -50
```

---

## Quick Status Check

```bash
# See what's running on port 8000
lsof -i :8000

# Check if test suite works
python run_tests.py --help  # Or just run it

# Git status
git status
git log --oneline -5

# Check Python version
python --version  # Should be 3.9+

# List all documentation files
ls -lah *.md
```

---

## Default Credentials

**User**: `admin@certifyintel.com`
**Password**: `MSFWINTERCLINIC2026`

⚠️ **Security Note**: Change these default credentials after first login (Settings → User Management)

---

## Configuration

**File**: `/home/user/Project_Intel_v4/backend/.env`

**Key settings**:
```
SECRET_KEY=your-secret-key          # Required
DATABASE_URL=sqlite:///./certify_intel.db  # Default SQLite
DEBUG=false                         # Set to false for production

# Optional features
OPENAI_API_KEY=                     # For AI summaries (optional)
SMTP_SERVER=                        # For email alerts (optional)
SLACK_WEBHOOK_URL=                  # For Slack (optional)
```

See `.env.example` for all options.

---

## Important Files

| File | Purpose | Size |
|------|---------|------|
| `run_tests.py` | Automated tests (9 tests) | 449 lines |
| `CLAUDE.md` | Project overview | 440 lines |
| `PLAN.md` | Development plan | 400+ lines |
| `TESTING_INDEX.md` | Navigation guide | 500+ lines |
| `PHASE_3_TEST_PLAN.md` | Test specification | 400+ lines |
| `PHASE_3A_EXECUTION_SUMMARY.md` | Quick start | 525 lines |
| `PHASE_4_EXPORT_VALIDATION_PLAN.md` | Export tests | 400+ lines |
| `PHASE_5_DATA_QUALITY_PLAN.md` | Quality tests | 500+ lines |
| `SCRAPERS.md` | Data sources | 350+ lines |
| `.env.example` | Configuration | 247 lines |

**Total documentation**: 6,000+ lines

---

## Test Results Expected

### Phase 3A (Static Endpoint Tests)
- **Tests**: 9 automated tests
- **Duration**: 2-3 minutes
- **Pass criteria**: 7-9/9 pass, 0 failures
- **Result file**: PHASE_3A_RESULTS.md

### Phase 4 (Export Validation)
- **Tests**: 5 export/data tests
- **Duration**: ~1 hour
- **Pass criteria**: All 5 pass, valid files
- **Result file**: PHASE_4_RESULTS.md

### Phase 5 (Data Quality)
- **Tests**: 8 quality tests
- **Duration**: ~1.5 hours
- **Pass criteria**: All 8 pass, scores calculated
- **Result file**: PHASE_5_RESULTS.md

---

## API Endpoints (Common)

```
GET  /api/health                      Health check
POST /api/token                       Get JWT token
GET  /api/competitors                 List all
GET  /api/competitors/{id}            Single competitor
GET  /api/competitors/search?q=       Search
GET  /api/dashboard                   Dashboard data
GET  /api/export/excel                Excel file
GET  /api/export/json                 JSON data
GET  /api/changes                     Change log
POST /api/discovery/run               Discovery agent
GET  /api/data-quality/scores         Quality metrics
GET  /api/data-quality/stale          Stale data
POST /api/competitors/{id}/correct    Manual correction
GET  /api/data-quality/audit/{id}     Audit trail
```

---

## Git Commands

```bash
# Check status
git status

# See recent commits
git log --oneline -10

# Current branch
git rev-parse --abbrev-ref HEAD

# Push changes
git push -u origin claude/add-claude-documentation-CzASg

# See what's different
git diff

# See staged changes
git diff --staged

# Undo uncommitted changes
git checkout -- .
```

---

## Troubleshooting Quick Fixes

### "Connection refused" error
```bash
# Start backend
cd backend && python main.py
# Wait 5 seconds
```

### "Address already in use" error
```bash
# Kill existing process on port 8000
lsof -i :8000 | tail -1 | awk '{print $2}' | xargs kill -9
```

### "Database is locked" error
```bash
# Delete and recreate database
rm backend/certify_intel.db
python backend/main.py  # Will auto-create
```

### "Module not found" error
```bash
# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Test timeout
```bash
# Give backend more time to start
# Wait 10 seconds after seeing "Uvicorn running" message
sleep 10
python run_tests.py
```

---

## Success Criteria Quick Check

| Criterion | Status | Action |
|-----------|--------|--------|
| Code cleaned (Phase 1) | ✅ | Continue |
| Config documented (Phase 2) | ✅ | Continue |
| Tests prepared (Phase 3) | ✅ | Continue |
| Phase 3A: 7+/9 pass | ⏳ | Run tests |
| Phase 4: All exports work | ⏳ | After 3A |
| Phase 5: Quality works | ⏳ | After 4 |
| Ready for production | ⏳ | After all |

---

## Documentation Decision Tree

```
I want to...

├─ Understand the project
│  └─ Read: CLAUDE.md
│
├─ Get project status
│  └─ Read: PLAN.md or FINAL_STATUS_REPORT.md
│
├─ See all documentation
│  └─ Read: TESTING_INDEX.md (THIS HELPS!)
│
├─ Run Phase 3A tests
│  ├─ Quick: PHASE_3A_EXECUTION_SUMMARY.md
│  ├─ Setup: PHASE_3A_SETUP_GUIDE.md
│  └─ Reference: PHASE_3_TEST_PLAN.md
│
├─ Run Phase 4 tests
│  └─ Read: PHASE_4_EXPORT_VALIDATION_PLAN.md
│
├─ Run Phase 5 tests
│  └─ Read: PHASE_5_DATA_QUALITY_PLAN.md
│
├─ Understand data sources
│  └─ Read: SCRAPERS.md
│
├─ Configure the system
│  └─ Read: .env.example
│
├─ Know what's been done
│  └─ Read: WORK_SUMMARY.md
│
├─ Troubleshoot an issue
│  └─ Check: Corresponding PHASE_X_*.md
│
└─ Check deployment status
   └─ Read: DEPLOYMENT_READINESS_CHECKLIST.md
```

---

## Timeline At A Glance

| Phase | What | Duration | Status |
|-------|------|----------|--------|
| 1 | Remove paid APIs | ~7 hrs | ✅ DONE |
| 2 | Document config | ~3.5 hrs | ✅ DONE |
| 3 | Build tests | ~6 hrs | ✅ DONE |
| 3A | Run 9 tests | 3-5 min | ⏳ NEXT |
| 3B | Data integrity | 30-60 min | ⏳ Optional |
| 3C | Integration | 1-2 hrs | ⏳ Optional |
| 4 | Export validation | 1 hr | ⏳ After 3A |
| 5 | Data quality | 1.5 hrs | ⏳ After 4 |
| **Total** | | ~21.5 + 3-6 hrs | ⏳ In progress |

---

## Key Metrics

- **Files created**: 15+
- **Lines of documentation**: 6,000+
- **Test cases**: 26+
- **Automated tests**: 9
- **Code removed**: ~737 lines
- **Code added**: ~2,500 lines
- **Git commits**: 10+
- **System features**: 15+

---

## Contact & Help

**For questions about**...

- **Project**: See CLAUDE.md
- **Status**: See PLAN.md
- **Navigation**: See TESTING_INDEX.md (you're reading the quick version)
- **Any phase**: See PHASE_X_*.md
- **Data sources**: See SCRAPERS.md
- **Configuration**: See .env.example
- **Deployment**: See DEPLOYMENT_READINESS_CHECKLIST.md

---

## Important Reminders

✅ **All preparation is complete**
✅ **System is ready to test**
✅ **Documentation is comprehensive**
✅ **Tests are automated**
⏳ **Backend must be running for tests**
⏳ **Results need to be documented**
⏳ **No paid API keys needed**

---

## Next Action

```bash
cd /home/user/Project_Intel_v4/backend
pip install -r requirements.txt
python main.py &
sleep 5
cd ..
python run_tests.py
```

**Expected**: ✅ Passed: 7-9/9, ❌ Failed: 0/9

---

**Keep this page handy during testing!**

*Last updated: 2026-01-24*
*Branch: claude/add-claude-documentation-CzASg*
*Status: Ready for Phase 3A execution*

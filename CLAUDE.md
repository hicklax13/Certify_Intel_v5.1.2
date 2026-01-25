# Certify Intel - Development Documentation

## Session Summary - 2026-01-25 🔴 BLOCKED - Desktop App Installation Issue

**Date**: January 25, 2026
**Version**: 2.0.1
**Status**: 🔴 **BLOCKED** - Desktop installer builds but app fails to start after installation
**Session Type**: Desktop App Build & Troubleshooting

---

## CRITICAL ISSUE: Desktop App Backend Startup Failure

### Problem Summary
The desktop app installer (`20260125_Certify_Intel_v2.0.1_Setup.exe`) builds successfully, but after installation, the app fails with **"Failed to start the backend server"** error.

### Root Cause Analysis
The issue is related to how the backend executable (`certify_backend.exe`) loads configuration files (`.env` and `certify_intel.db`) when running as an installed application vs. running from the build directory.

**Key Discovery**: PyInstaller extracts bundled files to a temporary directory (`C:\Users\...\AppData\Local\Temp\_MEI######`), but the `.env` file needs to be in the **executable's directory**, not the temp extraction folder.

### What Works
- ✅ Backend runs correctly when executed directly from `backend-bundle/` folder
- ✅ `.env` file loads correctly when running from `backend-bundle/`
- ✅ SECRET_KEY, OPENAI_API_KEY, and other environment variables are detected
- ✅ Server starts and shows `Uvicorn running on http://127.0.0.1:8000`
- ✅ Installer builds successfully with electron-builder

### What Fails
- ❌ Installed app cannot start the backend server
- ❌ After installation, the backend cannot find the `.env` file
- ❌ Error: "Failed to start the backend server. Please try again."

### Technical Details

**Successful Manual Test Output:**
```
Loading .env from: C:\Users\conno\Downloads\Project_Intel_v4\desktop-app\backend-bundle\.env
Using database from: C:\Users\conno\Downloads\Project_Intel_v4\desktop-app\backend-bundle\certify_intel.db
Certify Intel Backend Starting...
Bundle directory: C:\Users\conno\AppData\Local\Temp\_MEI367242
Executable directory: C:\Users\conno\Downloads\Project_Intel_v4\desktop-app\backend-bundle
SECRET_KEY loaded: Yes
OPENAI_API_KEY loaded: Yes
✅ AI Features (Executive Summaries, Discovery Agent, Web Extraction) - ENABLED
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**The Problem**: When the app is INSTALLED (not run from build folder), the paths change:
- Build folder: `C:\Users\conno\Downloads\Project_Intel_v4\desktop-app\backend-bundle\`
- Installed location: `C:\Users\conno\AppData\Local\Programs\certify-intel\` (or similar)

The `.env` file is in `backend-bundle/` during build, but after installation, the backend exe may be looking in a different location within the installed app structure.

---

## Complete Error History This Session

### Error 1: "fatal: not a git repository"
**Cause**: User downloaded repo as ZIP instead of cloning
**Fix**: Used GitHub web UI to create release instead

### Error 2: GitHub Actions billing/spending limit
**Cause**: GitHub Actions requires payment for private repos or has usage limits
**Fix**: Built locally instead of using GitHub Actions

### Error 3: "bash: pyinstaller: command not found"
**Cause**: PyInstaller not in PATH
**Fix**: Used `python -m PyInstaller` instead

### Error 4: "Error: spawn certify_backend.exe ENOENT"
**Cause**: Backend executable not bundled with Electron app
**Fix**: Built backend with PyInstaller and copied to `backend-bundle/`

### Error 5: "No module named 'PIL'"
**Cause**: PIL/Pillow not included in PyInstaller bundle
**Fix**: Added PIL to `hiddenimports` in `certify_backend.spec`

### Error 6: "SyntaxError: unmatched ']'"
**Cause**: Manual edit of spec file introduced syntax error
**Fix**: Provided complete clean spec file

### Error 7: "Missing required environment variables: SECRET_KEY"
**Cause**: `.env` file was in wrong location - backend was looking in temp extraction folder
**Fix**: Modified `__main__.py` to load `.env` from executable directory instead of bundle directory

### Error 8 (CURRENT): "Failed to start the backend server" (after installation)
**Cause**: UNRESOLVED - The installed app structure differs from build folder structure
**Status**: Needs investigation into how electron-builder packages backend-bundle

---

## Files Modified This Session

### `backend/__main__.py` (CRITICAL FIX)
Added `get_exe_dir()` function to distinguish between:
- `bundle_dir`: Temp folder where PyInstaller extracts files (`sys._MEIPASS`)
- `exe_dir`: Actual directory where the `.exe` is located (`os.path.dirname(sys.executable)`)

Modified to load `.env` from `exe_dir` instead of `bundle_dir`.

### `backend/certify_backend.spec`
- Added PIL to `hiddenimports`: `'PIL'`, `'PIL._imaging'`, `'PIL.Image'`
- Removed PIL from `excludes` list

### Other files from earlier in session:
- `desktop-app/package.json` - Version 2.0.1, artifact naming
- `.github/workflows/build-release.yml` - Release configuration
- `README.md` - Comprehensive documentation
- `docs/DESKTOP_APP_BUILD_PLAN.md` - Version conventions

---

## User's Environment

- **OS**: Windows 10/11
- **Python**: 3.14.2
- **Node.js**: v24.13.0
- **Git**: 2.52.0
- **PyInstaller**: Installed via pip
- **electron-builder**: 24.13.3
- **Electron**: 28.3.3

---

## User's API Keys (Configured)

```
SECRET_KEY=certify-intel-prod-secret-key-2026-xK9mN2pL
AI_PROVIDER=hybrid
OPENAI_API_KEY=sk-proj-XeJdkFBbWOjsK3F... (configured)
GOOGLE_API_KEY=AIzaSyCmkjdGbkKjXcL... (configured)
GOOGLE_CX=840c244744f8f47ab (configured)
DATABASE_URL=sqlite:///./certify_intel.db
```

---

## Next Steps to Resolve (For Future Session)

### Investigation Needed
1. **Examine installed app structure**
   - Where does electron-builder put `backend-bundle/` after installation?
   - Is it in `resources/app.asar.unpacked/`?
   - Is the `.env` file included in the package?

2. **Check Electron main.js**
   - How does it spawn the backend process?
   - What working directory does it use?
   - Does it pass the correct path to backend exe?

3. **Verify backend-bundle in package**
   - Check `desktop-app/package.json` build configuration
   - Ensure `backend-bundle` is in `extraResources` or `files`
   - Verify `.env` file is not being excluded

### Potential Fixes
1. **Bundle .env into the PyInstaller exe**
   - Add `.env` to `datas` in spec file
   - Backend reads from bundled .env first, then exe_dir

2. **Create .env at install time**
   - Electron's first-run setup wizard creates `.env`
   - Store in app data directory

3. **Use app data directory**
   - Store `.env` and database in `%APPDATA%/Certify Intel/`
   - Works across updates and reinstalls

4. **Environment variables in Electron**
   - Pass config via environment variables when spawning backend
   - Electron reads config and passes to child process

---

## Build Commands Reference

### Build Backend Executable
```bash
cd /c/Users/conno/Downloads/Project_Intel_v4/backend
python -m PyInstaller certify_backend.spec --clean --noconfirm
```

### Copy Files to backend-bundle
```bash
cp backend/dist/certify_backend.exe desktop-app/backend-bundle/
cp backend/certify_intel.db desktop-app/backend-bundle/
# Create .env in backend-bundle with required keys
```

### Build Electron Installer (Windows)
```bash
cd desktop-app
npm run build:win
```

### Test Backend Manually
```bash
cd desktop-app/backend-bundle
./certify_backend.exe
# Should show: SECRET_KEY loaded: Yes
```

---

## Previous Session Summary - 2026-01-25 (Earlier)

### What Was Accomplished
- ✅ Desktop App Release Configuration (v2.0.1)
- ✅ Comprehensive Documentation Update
- ✅ Fixed `.env` loading from executable directory
- ✅ Fixed PIL missing module error
- ✅ Backend works when run manually from backend-bundle
- ✅ Installer builds successfully

### What Remains Blocked
- ❌ Installed app fails to start backend
- ❌ Need to investigate Electron + installed backend path issues

---

## Previous Session Summary - 2026-01-24 ✅ COMPLETE

**Date**: January 24, 2026
**Status**: 🟢 **PRODUCTION READY** (web version)
**Session Type**: Complete Development & Testing Cycle

### What Was Accomplished

✅ **All 5 Planning Phases Completed**
- Phase 1: Removed all paid API scrapers (~737 lines deleted)
- Phase 2: Created comprehensive configuration documentation (247 line .env.example)
- Phase 3: Built automated test suite (9 tests, 449 lines + 4,000+ doc lines)
- Phase 4: Created export validation plan (5 comprehensive test cases)
- Phase 5: Created data quality testing plan (8 comprehensive test cases)

✅ **Desktop App Build Infrastructure (Phases 1-8)**
- Created `backend/__main__.py` entry point for PyInstaller
- Created `backend/certify_backend.spec` for bundling
- Set up `.github/workflows/build-release.yml` for CI/CD
- Enhanced `electron/main.js` with auto-updater
- Fixed Playwright type fallback issue in `scraper.py`

✅ **Testing Completed (Tasks 3-9)**
- Task 3: Automated tests - 8/10 pass, 2 warnings, 0 failures
- Task 4: Core endpoints validated
- Task 5: Export functionality working
- Task 6: Data quality system working
- Task 7: Performance - 3-12ms response times
- Task 8: Security audit passed (JWT, SQL injection prevention)
- Task 9: Backup/recovery tested

---

## Project Overview

**Certify Health Intel** is a production-ready **Competitive Intelligence Platform** designed to track, analyze, and counter 30+ competitors in the healthcare technology space. It provides a centralized, real-time dashboard to aggregate data from multiple sources and empower sales, product, and leadership teams with actionable competitive insights.

### Target Users
- Executive Leadership (strategic planning)
- Sales Teams (battlecards, feature comparisons)
- Product Management (feature gaps, competitor releases)
- Strategy & Operations (market shifts, M&A activity)

---

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.9+) with Uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **API**: RESTful with 40+ endpoints
- **Task Scheduling**: APScheduler
- **Web Scraping**: Playwright, BeautifulSoup4, lxml
- **AI/ML**: OpenAI GPT-4, LangChain, tiktoken
- **Reporting**: ReportLab (PDF), openpyxl (Excel)
- **Authentication**: JWT tokens with passlib
- **Other**: pandas, yfinance, python-jose, httpx, requests

### Frontend
- **Architecture**: Single Page Application (SPA)
- **Languages**: HTML5, Vanilla JavaScript (ES6+), CSS3
- **Visualization**: Chart.js
- **PWA**: Service workers for offline support
- **Design**: Glassmorphism, dark-mode aesthetic with CSS variables

### Desktop Application
- **Framework**: Electron (wraps web app as native desktop)
- **Build Tools**: electron-builder
- **Platforms**: Windows (.exe), macOS (.dmg)
- **Backend Integration**: Python backend spawned as child process

---

## Core Features

### 1. Real-Time Intelligence & Monitoring
- **Automated Tracking**: Monitors 30+ data points per competitor
- **Change Detection**: Alerts system for significant updates
- **Discovery Agent**: "Certify Scout" autonomously crawls web for emerging threats
- **News Monitoring**: Real-time news feed aggregation

### 2. Multi-Source Data Collection (15+ Scrapers)
**Finance & Legal**: SEC Edgar, CrunchBase, PitchBook, USPTO patents
**Employment**: Glassdoor, Indeed, LinkedIn, H1B visa filings
**Industry-Specific**: HIMSS Conference, KLAS ratings, App Stores
**Market Intelligence**: SimilarWeb, Twitter/LinkedIn, G2/Capterra, sentiment analysis

### 3. Advanced Analytics
- **Executive Summaries**: AI-generated weekly strategic briefings (GPT-4)
- **Market Positioning Map**: Threat level and market focus visualization
- **Feature Gap Analysis**: Side-by-side product comparison matrices
- **Threat Analysis**: Risk scoring and prioritization
- **Pricing Analytics**: Competitor pricing trends
- **Win/Loss Tracking**: Record competitive deal outcomes

### 4. Reporting & Export
- **Excel Export**: Data-validated exports with auto-fit columns
- **PDF Reports**: Battlecard generation for sales teams
- **JSON Export**: Power Query integration for Power BI
- **Historical Data**: Trend analysis and seeding
- **Change Logs**: Complete audit trail

### 5. User Management & Security
- **Role-Based Access Control**: Admin, Analyst, Viewer roles
- **JWT Authentication**: Secure token-based auth
- **Audit Logs**: Full change history with user attribution
- **Multi-user Collaboration**: User invitations and team workflows

### 6. Data Quality & Verification
- **Data Quality Scores**: Freshness and completeness tracking
- **Source Attribution**: Every data point traced to its source
- **Manual Corrections**: User-initiated corrections with reason logging
- **Verification Workflow**: Track last verification timestamp
- **Stale Data Detection**: Identify fields needing refresh

### 7. Automated Scheduling
- **Weekly Refresh**: Sundays at 2 AM (full database)
- **Daily Check**: 6 AM (high-threat competitors)
- **Database Backups**: Daily automated backups
- **Email Alerts**: Daily digest and weekly summaries

---

## Project Structure

```
Project_Intel_v4/
├── backend/                          # FastAPI Python backend (~8,651 lines)
│   ├── main.py                      # App entry point (3,164 lines)
│   ├── __main__.py                  # PyInstaller entry point (MODIFIED)
│   ├── certify_backend.spec         # PyInstaller spec (MODIFIED)
│   ├── database.py                  # SQLAlchemy ORM models (11 tables)
│   ├── analytics.py                 # Data analysis engine (807 lines)
│   ├── extended_features.py         # Auth, caching, advanced features
│   ├── discovery_agent.py           # AI web scraping logic
│   ├── scheduler.py                 # APScheduler automation
│   ├── alerts.py                    # Notifications (Email/Slack/Teams)
│   ├── reports.py                   # PDF/Excel generation
│   ├── extractor.py                 # GPT-4 data extraction
│   ├── scraper.py                   # Base Playwright scraper class
│   ├── [15+ Specialized Scrapers]   # Domain-specific collectors
│   ├── certify_intel.db             # SQLite database (471KB)
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Configuration template
│   └── Dockerfile                   # Docker configuration
│
├── frontend/                         # Web UI SPA
│   ├── index.html                   # Main SPA template
│   ├── login.html                   # Authentication UI
│   ├── app_v2.js                    # Core logic (4,084 lines)
│   ├── styles.css                   # Styling (46,758 bytes)
│   └── ...
│
├── desktop-app/                      # Electron wrapper
│   ├── electron/
│   │   ├── main.js                  # Electron main process
│   │   ├── preload.js               # Security bridge
│   │   └── ...
│   ├── backend-bundle/              # Contains backend exe, .env, db
│   ├── package.json                 # Build config (v2.0.1)
│   └── ...
│
└── client_docs/                      # Documentation & templates
```

---

## Alternative: Run Web Version (Works Now)

While the desktop app is blocked, the **web version works perfectly**:

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python main.py
# Open http://localhost:8000 in browser
```

---

## Code Statistics

- **Backend**: ~8,651 lines of Python across 60 modules
- **Frontend**: ~4,084 lines of JavaScript (main app logic)
- **Database**: 471KB SQLite file, 11+ core tables
- **Scrapers**: 15+ specialized data collection modules
- **API**: 40+ endpoints
- **Competitors**: 30+ tracked competitors
- **Data Points**: 30+ fields per competitor

---

## Git Workflow

**Current Branch**: `claude/review-and-plan-yxWoy`

When pushing changes:
```bash
git add .
git commit -m "Clear, descriptive commit message"
git push -u origin claude/review-and-plan-yxWoy
```

---

*Last Updated: 2026-01-25*
*Project Status: Desktop App BLOCKED, Web Version Production-Ready*
*Maturity Level: Production-Ready (Web), In Development (Desktop)*

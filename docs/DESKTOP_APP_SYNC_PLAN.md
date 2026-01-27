# Master Plan: Desktop App vs Web App Synchronization & Feature Completion

**Version**: v5.5.0
**Created**: January 27, 2026
**Author**: Claude Opus 4.5
**Status**: APPROVED - Execution in Progress

---

## Phase 0: Documentation & Version Control (FIRST PRIORITY)

**These steps MUST be completed before any implementation begins:**

### Step 0.1: Save Plan to Local Workspace
- Copy this plan file to: `c:\Users\conno\Downloads\Project_Intel_v5.0.1\docs\DESKTOP_APP_SYNC_PLAN.md`
- This makes the plan part of the project repository

### Step 0.2: Update CLAUDE.md
- Add new session log for this planning session
- Add reference to this plan file
- Update "Next 5 Tasks To Complete" section
- Document the 67 identified issues

### Step 0.3: Push to GitHub
- Stage all changes: `git add .`
- Commit with message: "Docs: Add Desktop App Sync Plan v5.5.0"
- Push to origin: `git push origin master`

### Step 0.4: Verify on GitHub
- Confirm commit appears on master branch
- Verify plan file is accessible in docs/ folder

---

## Executive Summary

Based on comprehensive analysis of the codebase, screenshots, and installed applications, I've identified **67 issues** across multiple categories that need to be addressed to achieve full parity between the desktop app and web app.

---

## Part 1: Discrepancy Analysis (Screenshots Comparison)

### Visual Discrepancies Identified

| # | Feature | Desktop App (Old Screenshot) | Web App (Current) | Issue Type |
|---|---------|------------------------------|-------------------|------------|
| 1 | Logo | "CERTIFY HEALTH" (circular) | "CERTIFY INTEL" (rectangle) | Branding Mismatch |
| 2 | News Feed Menu | MISSING | Present | Missing Feature |
| 3 | Sales & Marketing Menu | MISSING | Present | Missing Feature |
| 4 | Sidebar Items | 9 items | 11 items | Missing 2 Items |
| 5 | Dashboard Stats | Shows numbers (82, 1, 79, 2) | Shows dashes (-) loading | Data Loading Issue |
| 6 | AI Summary Section | "GPT-4" badge, auto-generating | Edit Prompt/Generate Summary/Clear buttons | Different UI |
| 7 | Status Indicator | "Auto-Pilot Active" (Export Excel below) | "System Online" only | UI Difference |
| 8 | Header Logout | "CI" avatar + "Logout" text | User icon only | Different Design |
| 9 | Threat Criteria Button | Present with gear icon | Present with star icon | Icon Difference |
| 10 | Refresh Data Button | Present (blue) | Present (blue) | Consistent |

### Root Cause Analysis

**FINDING**: The installed desktop app files ARE up-to-date (verified by reading index.html), but the user's screenshot shows an OLD version of the app. This indicates:

1. **Old Installation Still Running**: User may have launched an older installation
2. **Multiple Installations**: Old version may exist at different location
3. **Caching Issue**: Browser/Electron cache serving old files

---

## Part 2: Master To-Do List

### Category A: Desktop App Cleanup & Rebuild (8 Tasks)

| ID | Task | Priority | Status | Description |
|----|------|----------|--------|-------------|
| A-001 | Remove ALL old installations | CRITICAL | PENDING | Find and delete any Certify Intel installations outside of AppData\Local\Programs |
| A-002 | Kill any running Certify Intel processes | CRITICAL | PENDING | taskkill /F /IM "Certify Intel.exe" and certify_backend.exe |
| A-003 | Clear Electron cache | HIGH | PENDING | Delete %APPDATA%/Certify Intel/ cache folder |
| A-004 | Create proper .env file for backend-bundle | CRITICAL | PENDING | Copy backend/.env to desktop-app/backend-bundle/.env |
| A-005 | Verify SECRET_KEY matches database | CRITICAL | PENDING | Ensure SECRET_KEY=certify-intel-secret-key-2024 |
| A-006 | Rebuild PyInstaller backend | HIGH | PENDING | python -m PyInstaller certify_backend.spec --clean |
| A-007 | Rebuild Electron app | HIGH | PENDING | npm run build:win |
| A-008 | Clean install new desktop app | HIGH | PENDING | Run new installer, verify all features |

### Category B: Frontend File Synchronization (6 Tasks)

| ID | Task | Priority | Status | Description |
|----|------|----------|--------|-------------|
| B-001 | Verify desktop-app/frontend/app.js matches frontend/app_v2.js | HIGH | VERIFIED | Files are identical |
| B-002 | Verify desktop-app/frontend/index.html matches frontend/index.html | HIGH | VERIFIED | Files are identical |
| B-003 | Verify desktop-app/frontend/styles.css matches frontend/styles.css | HIGH | VERIFIED | Files are identical |
| B-004 | Verify sales_marketing.js present in desktop | HIGH | VERIFIED | File exists |
| B-005 | Verify all image assets present | MEDIUM | PENDING | Check logo, favicon, icons |
| B-006 | Add browser_tab_icon.jpg to desktop frontend | LOW | PENDING | Referenced in index.html line 15 |

### Category C: Backend API Endpoint Verification (15 Tasks)

| ID | Task | Priority | Status | Description |
|----|------|----------|--------|-------------|
| C-001 | Test /api/dashboard/stats | HIGH | PENDING | Should return 82, 1, 79, 2 |
| C-002 | Test /api/competitors | HIGH | PENDING | Should return 82 competitors |
| C-003 | Test /api/analytics/summary | HIGH | PENDING | AI executive summary |
| C-004 | Test /api/news-feed | HIGH | PENDING | News aggregation |
| C-005 | Test /api/sales-marketing/dimensions | HIGH | PENDING | 9 competitive dimensions |
| C-006 | Test /api/products/coverage | MEDIUM | PENDING | Product coverage stats |
| C-007 | Test /api/scheduler/status | MEDIUM | PENDING | Scheduler job status |
| C-008 | Test /api/discovery/history | MEDIUM | PENDING | Discovery history |
| C-009 | Test /api/changes | MEDIUM | PENDING | Change log |
| C-010 | Test /api/data-quality/overview | MEDIUM | PENDING | Data quality dashboard |
| C-011 | Test /api/ai/status | MEDIUM | PENDING | AI provider status |
| C-012 | Test /api/export/excel | MEDIUM | PENDING | Excel export |
| C-013 | Test /api/knowledge-base/scan | LOW | PENDING | KB import scanning |
| C-014 | Test /api/teams | LOW | PENDING | Team management |
| C-015 | Test /token authentication | CRITICAL | PENDING | Login flow |

### Category D: Missing/Non-Functional Features (18 Tasks)

| ID | Task | Priority | Status | Description |
|----|------|----------|--------|-------------|
| D-001 | News Feed page loads correctly | HIGH | PENDING | Verify 13+ sources working |
| D-002 | News Feed filters work | HIGH | PENDING | Sentiment, source, date filters |
| D-003 | Sales & Marketing page loads | HIGH | PENDING | 9 dimensions, radar chart |
| D-004 | Sales dimensions can be edited | HIGH | PENDING | PUT endpoint works |
| D-005 | AI dimension suggestions work | MEDIUM | PENDING | /ai-suggest endpoint |
| D-006 | Battlecard generation works | MEDIUM | PENDING | PDF/HTML generation |
| D-007 | Comparison page tabs work | HIGH | PENDING | General, Products, Dimensions |
| D-008 | Product comparison matrix works | HIGH | PENDING | Side-by-side products |
| D-009 | Dimension radar chart works | MEDIUM | PENDING | Chart.js radar |
| D-010 | Quick Actions cards work | MEDIUM | PENDING | 6 action cards on dashboard |
| D-011 | Discovery Agent modal works | MEDIUM | PENDING | Run discovery from dashboard |
| D-012 | Scheduler modal works | MEDIUM | PENDING | Configure refresh schedule |
| D-013 | Data Quality page works | MEDIUM | PENDING | Confidence scores, verification |
| D-014 | Change Log export works | MEDIUM | PENDING | CSV/Excel export |
| D-015 | Settings page works | LOW | PENDING | API keys, notifications |
| D-016 | Knowledge Base import works | LOW | PENDING | CSV/Excel/PDF import UI |
| D-017 | Team collaboration works | LOW | PENDING | Annotations, discussions |
| D-018 | Competitor detail modal works | MEDIUM | PENDING | Full competitor view |

### Category E: Database & Data Issues (6 Tasks)

| ID | Task | Priority | Status | Description |
|----|------|----------|--------|-------------|
| E-001 | Verify 82 competitors in desktop DB | HIGH | PENDING | SELECT COUNT(*) FROM competitor |
| E-002 | Verify 789 products in desktop DB | MEDIUM | PENDING | Product coverage |
| E-003 | Verify 1,539 news articles in desktop DB | MEDIUM | PENDING | News cache |
| E-004 | Verify admin user exists | CRITICAL | PENDING | admin@certifyintel.com |
| E-005 | Verify password hash matches SECRET_KEY | CRITICAL | PENDING | Hash with correct key |
| E-006 | Copy latest certify_intel.db to bundle | HIGH | PENDING | Fresh database with all data |

### Category F: Configuration Issues (7 Tasks)

| ID | Task | Priority | Status | Description |
|----|------|----------|--------|-------------|
| F-001 | Create .env in backend-bundle | CRITICAL | PENDING | Not .env.example, actual .env |
| F-002 | Set SECRET_KEY correctly | CRITICAL | PENDING | certify-intel-secret-key-2024 |
| F-003 | Set DESKTOP_MODE=true | HIGH | PENDING | Auto-authentication for desktop |
| F-004 | Set AI provider keys | MEDIUM | PENDING | OPENAI_API_KEY, GOOGLE_AI_API_KEY |
| F-005 | Verify DATA_PATH environment var | MEDIUM | PENDING | Points to resources/data |
| F-006 | Set admin credentials | HIGH | PENDING | ADMIN_EMAIL, ADMIN_PASSWORD |
| F-007 | Update package.json publish config | LOW | PENDING | GitHub repo for auto-update |

### Category G: Build & Release Process (7 Tasks)

| ID | Task | Priority | Status | Description |
|----|------|----------|--------|-------------|
| G-001 | Update version to v5.5.0 | HIGH | PENDING | Reflect all fixes |
| G-002 | Build backend with PyInstaller | HIGH | PENDING | certify_backend.exe |
| G-003 | Copy .env to backend-bundle | CRITICAL | PENDING | Before building Electron |
| G-004 | Copy latest database | HIGH | PENDING | certify_intel.db with 82 competitors |
| G-005 | Build Electron installer | HIGH | PENDING | npm run build:win |
| G-006 | Test installer fresh | HIGH | PENDING | Install on clean path |
| G-007 | Upload to GitHub releases | MEDIUM | PENDING | v5.5.0 release |

---

## Part 3: Feature Comparison Matrix

### Pages/Features Status

| Feature | Backend API | Frontend UI (Web) | Frontend UI (Desktop) | Notes |
|---------|-------------|-------------------|----------------------|-------|
| Dashboard | /api/dashboard/stats | Working | Should work | Stats cards, charts |
| AI Summary | /api/analytics/summary | Working | Should work | GPT-4/Gemini |
| Competitors | /api/competitors | Working | Should work | CRUD operations |
| Competitor Details | /api/competitors/{id} | Working | Should work | Full detail view |
| News Feed | /api/news-feed | Working | Should work | 13+ sources |
| Sales & Marketing | /api/sales-marketing/* | Working | Should work | 9 dimensions |
| Battlecards | /api/sales-marketing/battlecards | Working | Should work | PDF generation |
| Comparison | Multiple APIs | Working | Needs testing | 3 tabs |
| Product Matrix | /api/products/* | Working | Needs testing | Product comparison |
| Discovery | /api/discovery/* | Working | Needs testing | AI agent |
| Change Log | /api/changes | Working | Needs testing | Export support |
| Data Quality | /api/data-quality/* | Working | Needs testing | Confidence scores |
| Settings | Multiple APIs | Working | Needs testing | API config |
| Knowledge Base | /api/knowledge-base/* | Backend only | No UI | Needs frontend |
| Teams | /api/teams/* | Backend only | No UI | Needs frontend |

---

## Part 4: Implementation Plan

### Phase 1: Desktop App Clean Reinstall (Day 1 - First 2 Hours)

**Goal**: Ensure clean installation with correct configuration

1. Kill all running Certify Intel processes
2. Find and delete ALL old installations
3. Clear Electron cache folders
4. Create proper .env file with correct SECRET_KEY
5. Copy latest database (certify_intel.db)
6. Rebuild PyInstaller backend
7. Rebuild Electron app
8. Fresh install to clean location
9. Verify login works with admin credentials
10. Verify all 11 menu items appear

### Phase 2: Feature Verification (Day 1 - Next 2 Hours)

**Goal**: Test every feature in desktop app

1. Test Dashboard - stats load correctly
2. Test AI Summary - generates insights
3. Test Competitors - list loads, CRUD works
4. Test News Feed - articles load, filters work
5. Test Sales & Marketing - dimensions load, radar chart
6. Test Battlecards - can generate PDFs
7. Test Comparison - all 3 tabs work
8. Test Discovery - can run discovery
9. Test Change Log - export works
10. Test Data Quality - scores display
11. Test Settings - config saves

### Phase 3: Bug Fixes (Day 1-2)

**Goal**: Fix any broken features found in Phase 2

- Document each broken feature
- Fix frontend code as needed
- Fix backend endpoints as needed
- Update CSS styling
- Rebuild and retest

### Phase 4: Final Release (Day 2)

**Goal**: Release working version

1. Update version to v5.5.0
2. Rebuild both backend and frontend
3. Test full installer
4. Commit all changes to GitHub
5. Create GitHub release with installer
6. Update documentation (CLAUDE.md, TODO_LIST.md)
7. Verify auto-update works from old version

---

## Part 5: Critical Files to Modify

### Configuration Files
- `desktop-app/backend-bundle/.env` - CREATE (not just .env.example)
- `desktop-app/package.json` - Update version to 5.5.0
- `backend/certify_backend.spec` - Verify datas includes needed files

### Frontend Files (if issues found)
- `frontend/index.html` - Main UI structure
- `frontend/app_v2.js` - Core JavaScript logic
- `frontend/sales_marketing.js` - Sales module
- `frontend/styles.css` - Styling

### Backend Files (if issues found)
- `backend/main.py` - API endpoints
- `backend/database.py` - Database models
- `backend/__main__.py` - Entry point for PyInstaller

### Build Files
- `backend/dist/certify_backend.exe` - Rebuild
- `desktop-app/dist/*.exe` - Rebuild installer

---

## Part 6: Verification Checklist

### Pre-Installation Verification
- [ ] All old installations removed
- [ ] .env file created with correct SECRET_KEY
- [ ] Database has 82 competitors
- [ ] Backend builds without errors
- [ ] Electron builds without errors

### Post-Installation Verification
- [ ] App launches without errors
- [ ] Splash screen shows then closes
- [ ] Login page appears
- [ ] Login with admin@certifyintel.com works
- [ ] Dashboard loads with stats (82 competitors)
- [ ] All 11 sidebar menu items present
- [ ] News Feed page works
- [ ] Sales & Marketing page works
- [ ] AI Summary generates
- [ ] Export Excel downloads file
- [ ] All buttons clickable

### Feature-by-Feature Verification
- [ ] Dashboard Quick Actions work
- [ ] Competitor detail modal opens
- [ ] Add competitor form works
- [ ] News filtering works
- [ ] Sales dimension editing works
- [ ] Battlecard PDF generates
- [ ] Comparison tabs switch
- [ ] Product matrix displays
- [ ] Radar chart renders
- [ ] Discovery runs
- [ ] Change log exports

---

## Part 7: Summary Statistics

| Category | Total Tasks | Critical | High | Medium | Low |
|----------|-------------|----------|------|--------|-----|
| A: Cleanup & Rebuild | 8 | 3 | 4 | 0 | 1 |
| B: File Sync | 6 | 0 | 4 | 1 | 1 |
| C: API Verification | 15 | 1 | 4 | 9 | 1 |
| D: Missing Features | 18 | 0 | 7 | 9 | 2 |
| E: Database | 6 | 2 | 2 | 2 | 0 |
| F: Configuration | 7 | 2 | 2 | 2 | 1 |
| G: Build & Release | 7 | 1 | 5 | 1 | 0 |
| **TOTAL** | **67** | **9** | **28** | **24** | **6** |

---

**Plan Created**: January 27, 2026
**Plan Author**: Claude Opus 4.5
**Project**: Certify Intel v5.0.1 Desktop App Synchronization
**Total Tasks**: 67 (9 Critical, 28 High, 24 Medium, 6 Low)

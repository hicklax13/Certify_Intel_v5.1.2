# Certify Health Intel - Development Plan
## Core Functionality Completion (Free/Open Source Only)

**Status**: Phase 1 In Progress
**Last Updated**: 2026-01-24
**Focus**: Core scrapers only (no paid APIs)

---

## OVERVIEW

This plan focuses on completing core functionality using **only free/open-source resources** - no paid API keys required. All scrapers requiring paid subscriptions (Crunchbase, PitchBook, LinkedIn, SimilarWeb) are removed.

---

## USABLE SCRAPERS (No API Key Required)

✅ **Fully Functional:**
- Playwright Base Scraper - Website content extraction
- SEC Edgar (via yfinance) - Public company financials
- News Monitor (Google News RSS) - Real-time news
- Known Data Scrapers - Pre-populated data for demo/fallback

❌ **Remove (Paid APIs):**
- Crunchbase (subscription required) - **TO REMOVE**
- PitchBook (enterprise only) - **TO REMOVE**
- LinkedIn live scraping (violates ToS) - **TO REMOVE**
- SimilarWeb API (paid) - **TO REMOVE**
- HubSpot (paid) - **TO REMOVE**

---

## PHASE 1: Remove Non-Functional Paid API Scrapers (2-3 days)

### Task 1.1: Remove Crunchbase Scraper ❌ NOT STARTED
- **Files**: `/backend/crunchbase_scraper.py`, remove imports from `main.py` and `scheduler.py`
- **Effort**: 30 minutes
- **Description**: Delete Crunchbase scraper entirely (already broken with NotImplementedError)
- **Acceptance**: No references to crunchbase scraper remain in codebase

### Task 1.2: Remove PitchBook Scraper ❌ NOT STARTED
- **Files**: `/backend/pitchbook_scraper.py`, remove imports from `main.py` and `scheduler.py`
- **Effort**: 30 minutes
- **Description**: Delete PitchBook scraper entirely (enterprise subscription only)
- **Acceptance**: No references to pitchbook scraper remain in codebase

### Task 1.3: Disable LinkedIn Live Scraping ❌ NOT STARTED
- **Files**: `/backend/linkedin_tracker.py`
- **Effort**: 30 minutes
- **Description**: Remove live scraping component, keep known data only
- **Acceptance**: Known data still works, live scraping component removed

### Task 1.4: Add Startup Configuration Validation ❌ NOT STARTED
- **Files**: `/backend/main.py` (startup event)
- **Effort**: 1 hour
- **Description**:
  - Validate required env vars on startup
  - Add message listing which scrapers are available vs disabled
  - Exit cleanly if critical setup missing
  - Warn about optional APIs (OPENAI_API_KEY)
- **Acceptance**: App startup shows clear list of available scrapers

### Task 1.5: Verify Playwright Scraper Works ❌ NOT STARTED
- **Files**: `/backend/scraper.py`, `/backend/main.py` scrape endpoints
- **Effort**: 2 hours
- **Description**:
  - Test on 5+ competitor websites
  - Verify website content is extracted
  - Verify data flows to database
  - Fix any errors
- **Acceptance**: Playwright scraper successfully extracts data from test URLs

### Task 1.6: Verify yfinance Scraper Works ❌ NOT STARTED
- **Files**: `/backend/sec_edgar_scraper.py`
- **Effort**: 1 hour
- **Description**:
  - Test on public companies: PHR, HCAT, VEEV, etc.
  - Verify revenue, net income, margins populated
  - Verify data appears in database
- **Acceptance**: Financial data for 5+ public companies successfully retrieved

### Task 1.7: Verify News Monitor Works ❌ NOT STARTED
- **Files**: `/backend/news_monitor.py`, `/backend/main.py` news endpoints
- **Effort**: 1 hour
- **Description**:
  - Test competitor news feed
  - Verify articles from Google News RSS appear
  - Check sentiment detection works
- **Acceptance**: Real news articles appear for competitor names

### Task 1.8: Update .env.example ❌ NOT STARTED
- **Files**: `/backend/.env.example`
- **Effort**: 30 minutes
- **Description**:
  - Document required vs optional vars
  - Remove references to disabled APIs (Crunchbase, PitchBook, etc.)
  - Add notes about which features work without paid APIs
- **Acceptance**: Clear documentation of what is/isn't available

---

## PHASE 2: Validation & Configuration (1 day)

### Task 2.1: Startup Config Validation Script ❌ NOT STARTED
- Remove broken scraper imports from `main.py`
- Verify startup flow logs available scrapers
- Ensure no references to removed scrapers

### Task 2.2: Document Available Scrapers ❌ NOT STARTED
- Create README section listing available data sources
- Document frequency of data collection
- List fields available per source

---

## PHASE 3: Core Workflows (1-2 days)

### Workflow A: Login → Dashboard → Search → View → Export ❌ NOT STARTED
- [ ] Login with valid credentials works
- [ ] Dashboard shows all competitors with real data
- [ ] Search filters by name
- [ ] View competitor details with all populated fields
- [ ] Export to Excel/PDF contains actual data
- [ ] Logout works

### Workflow B: Add Competitor → Auto-Scrape → Data Appears ❌ NOT STARTED
- [ ] Admin adds new competitor
- [ ] Click "Refresh" triggers scrape
- [ ] Playwright extracts website content
- [ ] Data parsed and stored in database
- [ ] Fields appear in UI within 5 seconds

### Workflow C: Scheduled Scrape → Change Detection → Alert ❌ NOT STARTED
- [ ] Scheduler triggers on schedule
- [ ] Scrapes website for each competitor
- [ ] Detects changes in data
- [ ] Logs to ChangeLog table
- [ ] Shows in UI (alerts optional if email not configured)

### Workflow D: Discovery Agent → Find New Competitors ❌ NOT STARTED
- [ ] Run discovery agent manually
- [ ] Returns list of competitors not in database
- [ ] User can add with one click

---

## PHASE 4: Export & Reporting (1 day)

### Task 4.1: Verify Excel Export ❌ NOT STARTED
- All fields present
- Correct data in cells
- Formatting works

### Task 4.2: Verify PDF Battlecard ❌ NOT STARTED
- Generates without errors
- Contains correct competitor data
- Formatting is clean

### Task 4.3: Verify JSON Export ❌ NOT STARTED
- Valid JSON format
- Compatible with Power BI

---

## PHASE 5: Data Quality (1 day)

### Task 5.1: Manual Data Correction ❌ NOT STARTED
- Can manually correct competitor data
- Manual corrections don't get overwritten by scraper
- Changes logged in audit trail

### Task 5.2: Data Quality Scores ❌ NOT STARTED
- Data quality scores calculated
- Shows in dashboard

---

## DATA COLLECTION STRATEGY

For each competitor, data collected from:

| Data Category | Source | Method | Frequency |
|---|---|---|---|
| **Website Content** | Company website | Playwright scraper | Weekly |
| **Financial Data** | SEC (public) / yfinance | yfinance API | Weekly |
| **News & Press** | Google News RSS | News Monitor | Daily |
| **Known Data** | Pre-loaded database | Fallback data | Always available |
| **Job Postings** | Indeed-like sources | Known data | Weekly |
| **Patents** | USPTO (public) | Known data | Monthly |
| **Employee Reviews** | Glassdoor (known data) | Pre-populated | Static |
| **Ratings** | G2/Capterra (known data) | Pre-populated | Static |
| **Tech Stack** | Website analysis | Playwright + detection | Monthly |

**Available Fields:**
- ✅ Company basics (name, website, logo, description)
- ✅ Public financials (revenue, income, margins, stock symbol)
- ✅ Website metrics (traffic, engagement, content)
- ✅ News feed (recent articles, announcements)
- ✅ Known data (employees, ratings, reviews)
- ✅ Tech stack (tools, vendors, infrastructure)

**Unavailable (Paid APIs):**
- ❌ Funding rounds (Crunchbase - removed)
- ❌ Valuation (PitchBook - removed)
- ❌ LinkedIn employee count (removed)
- ❌ Website traffic (SimilarWeb - removed)

---

## PRIORITY TASK LIST

| # | Phase | Task | Effort | Status |
|---|-------|------|--------|--------|
| 1 | 1 | Remove Crunchbase imports | 30 min | ❌ NOT STARTED |
| 2 | 1 | Remove PitchBook imports | 30 min | ❌ NOT STARTED |
| 3 | 1 | Disable LinkedIn live scraping | 30 min | ❌ NOT STARTED |
| 4 | 1 | Add startup config validation | 1 hr | ❌ NOT STARTED |
| 5 | 1 | Test Playwright scraper | 2 hrs | ❌ NOT STARTED |
| 6 | 1 | Test yfinance scraper | 1 hr | ❌ NOT STARTED |
| 7 | 1 | Test News Monitor | 1 hr | ❌ NOT STARTED |
| 8 | 1 | Update .env.example | 30 min | ❌ NOT STARTED |
| 9 | 2 | Verify scraper registrations | 1 hr | ❌ NOT STARTED |
| 10 | 3 | Test Workflow A | 2 hrs | ❌ NOT STARTED |
| 11 | 3 | Test Workflow B | 2 hrs | ❌ NOT STARTED |
| 12 | 3 | Test Workflow C | 2 hrs | ❌ NOT STARTED |
| 13 | 3 | Test Workflow D | 1 hr | ❌ NOT STARTED |
| 14 | 4 | Test Excel export | 1 hr | ❌ NOT STARTED |
| 15 | 4 | Test PDF battlecard | 1 hr | ❌ NOT STARTED |
| 16 | 4 | Test JSON export | 1 hr | ❌ NOT STARTED |
| 17 | 5 | Test manual corrections | 1 hr | ❌ NOT STARTED |
| 18 | 5 | Test data quality scores | 1 hr | ❌ NOT STARTED |

**Total Estimated Effort: ~22 hours (~3 days)**

---

## SUCCESS CRITERIA

✅ Core data collection works **without any paid API keys**
✅ Crunchbase/PitchBook completely removed (no broken references)
✅ Startup clearly lists available scrapers
✅ Full workflow: Add competitor → Scrape (Playwright + yfinance) → Data appears → Export
✅ News feed shows real articles from Google News
✅ Scheduler runs automatically using available scrapers only
✅ Graceful fallback to "known data" when live scraping unavailable
✅ No error messages for unavailable paid APIs
✅ All exports contain actual collected data

---

## WHAT WILL BE COMPLETED

**Fully Functional Competitive Intelligence Platform with:**

- ✅ Competitor database (add/edit/delete)
- ✅ Website content scraping (Playwright)
- ✅ Financial data for public companies (yfinance)
- ✅ Real-time news monitoring (Google News RSS)
- ✅ Pre-populated data for quick demos
- ✅ Dashboard with charts and analytics
- ✅ Excel/PDF/JSON exports
- ✅ Change detection and logging
- ✅ Automated scheduling
- ✅ User authentication and RBAC

**Not Included (Requires Paid APIs):**
- ❌ Venture funding data (Crunchbase)
- ❌ Enterprise valuation (PitchBook)
- ❌ LinkedIn employee tracking (restricted)
- ❌ Website traffic analytics (SimilarWeb)

---

## AGENT INSTRUCTIONS

When working on this plan:

1. **Reference this file** when starting any task
2. **Update status** as you complete tasks (❌ NOT STARTED → 🟡 IN PROGRESS → ✅ COMPLETED)
3. **Update Last Updated** timestamp when making changes
4. **Add notes** if you discover issues or blockers
5. **Commit changes** to plan when you complete phases
6. **Link related tasks** if dependencies are found

Example status update:
```markdown
### Task 1.1: Remove Crunchbase Scraper 🟡 IN PROGRESS
- Started: 2026-01-24 14:30
- Files modified: main.py, scheduler.py
- Status: Removed scraper file, now removing imports
```

---

*This plan is a living document. Update it as you work and discoveries are made.*

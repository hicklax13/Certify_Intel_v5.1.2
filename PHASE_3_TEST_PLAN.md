# Phase 3: Core Workflows Testing Plan

**Status**: In Progress
**Date Started**: 2026-01-24
**Objective**: Verify all 4 core workflows work end-to-end

---

## Test Scope

This phase tests the **core user journeys** - the critical paths that users will follow. We verify:
- ✅ Authentication & authorization work
- ✅ Data displays correctly in dashboard
- ✅ Scraping endpoints function
- ✅ Data appears after scraping
- ✅ Change detection logs changes
- ✅ Exports contain correct data
- ✅ Discovery agent finds competitors

---

## Available API Endpoints (Verified)

### Authentication
- `POST /token` - Login (OAuth2 form)
- Endpoint: `api_routes.py:38`

### Dashboard & Analytics
- `GET /api/analytics/summary` - Dashboard data
- `GET /api/analytics/threats` - Threat analysis
- `GET /api/analytics/market-share` - Market share
- `GET /api/dashboard/stats` - Dashboard stats
- Endpoints: `main.py:362-1445`

### Scraping
- `POST /api/scrape/all` - Scrape all competitors
- `POST /api/scrape/{competitor_id}` - Scrape one competitor
- Endpoints: `main.py:1506-1525`

### Export
- `GET /api/export/excel` - Export to Excel
- `GET /api/export/json` - Export to JSON
- Endpoints: `main.py:1316-1397`

### Discovery
- `POST /api/discovery/run` - Run discovery agent
- `POST /api/discovery/run-live` - Live discovery
- Endpoints: `main.py:1545-2200`

### Competitors
- `GET /api/competitors` - Get all competitors
- `POST /api/competitors` - Add competitor
- `GET /api/competitors/{id}` - Get one competitor
- `PUT /api/competitors/{id}` - Update competitor
- `DELETE /api/competitors/{id}` - Delete competitor
- `GET /api/changes` - Get change log

---

## Workflow 1: Login → Dashboard → Search → View → Export → Logout

**Goal**: Verify basic user journey from login to export

### Test A.1: Authentication ✅ READY
**Endpoint**: `POST /token`
**Test**:
1. Login with valid credentials (admin@certifyhealth.com / certifyintel2024)
2. Verify JWT token returned
3. Verify token can be used in subsequent requests

**Success Criteria**:
- Returns 200 status
- Response contains `access_token`
- Token is valid JWT format

**Code Location**: `api_routes.py:38-56`

---

### Test A.2: Dashboard Display ✅ READY
**Endpoint**: `GET /api/analytics/summary`
**Test**:
1. Fetch dashboard summary
2. Verify competitor data displayed
3. Verify threat levels calculated
4. Verify charts data available

**Success Criteria**:
- Returns 200 status
- Response contains competitor list
- Each competitor has threat_level, status, last_updated
- Data is recent (not stale)

**Code Location**: `main.py:362-475`

---

### Test A.3: Search Functionality ✅ READY
**Endpoint**: `GET /api/competitors?search=phreesia`
**Test**:
1. Search for competitor by name
2. Verify filtered results returned
3. Verify partial matches work

**Success Criteria**:
- Returns competitors matching search term
- Case-insensitive search works
- Partial matches return results

**Code Location**: `main.py:1131-1180`

---

### Test A.4: View Competitor Details ✅ READY
**Endpoint**: `GET /api/competitors/{competitor_id}`
**Test**:
1. Get details for a competitor
2. Verify all 50+ fields populated
3. Verify logo/branding displayed
4. Verify data sources shown

**Success Criteria**:
- Returns 200 status
- Response contains all competitor fields
- Fields have reasonable values (not null/empty)
- Last updated timestamp is recent

**Code Location**: `main.py:1181-1226`

---

### Test A.5: Export to Excel ✅ READY
**Endpoint**: `GET /api/export/excel`
**Test**:
1. Request Excel export
2. Verify file is returned
3. Verify all competitors included
4. Verify all fields present

**Success Criteria**:
- Returns 200 status
- Response has correct MIME type (application/vnd.openxmlformats)
- File is valid Excel format
- Contains all competitor data

**Code Location**: `main.py:1316-1395`

---

### Test A.6: Export to JSON ✅ READY
**Endpoint**: `GET /api/export/json`
**Test**:
1. Request JSON export
2. Verify valid JSON returned
3. Verify Power BI compatible format

**Success Criteria**:
- Returns 200 status
- Response is valid JSON
- Can be parsed without errors
- Compatible with Power BI

**Code Location**: `main.py:1397-1410`

---

## Workflow 2: Add Competitor → Auto-Scrape → Data Appears

**Goal**: Verify new competitor can be added and scraped

### Test B.1: Add New Competitor ✅ READY
**Endpoint**: `POST /api/competitors`
**Test**:
1. Create new competitor record
2. Verify record stored in database
3. Verify ID returned

**Success Criteria**:
- Returns 200 status
- Response contains competitor ID
- Competitor appears in GET /api/competitors

**Code Location**: `main.py:1139-1180`

---

### Test B.2: Trigger Scrape ✅ READY
**Endpoint**: `POST /api/scrape/{competitor_id}`
**Test**:
1. Trigger scrape for competitor
2. Verify scraping started
3. Check data updates in database

**Success Criteria**:
- Returns 202 (accepted)
- Scraping job started
- Data fields updated within 10 seconds

**Code Location**: `main.py:1525-1545`

---

### Test B.3: Data Appears in UI ✅ READY
**Endpoint**: `GET /api/competitors/{competitor_id}`
**Test**:
1. Get competitor details after scrape
2. Verify new data populated
3. Verify scraped fields not empty

**Success Criteria**:
- Returns competitor with populated fields
- Revenue, description, website metrics updated
- Last_updated timestamp is recent

**Code Location**: `main.py:1181-1226`

---

## Workflow 3: Scheduled Scrape → Change Detection → Alert

**Goal**: Verify changes are detected and logged

### Test C.1: Scheduled Scrape Runs ✅ READY
**Endpoint**: Internal scheduler
**Test**:
1. Verify scheduler initialized
2. Check scheduled jobs configured
3. Verify jobs will run on schedule

**Success Criteria**:
- Scheduler available (SCHEDULER_AVAILABLE = True)
- Jobs registered for:
  - Weekly refresh (Sunday 2 AM)
  - Daily check (6 AM)
  - Database backup (daily)

**Code Location**: `main.py:220-223`, `scheduler.py`

---

### Test C.2: Change Detection ✅ READY
**Endpoint**: Internal during scrape
**Test**:
1. Update competitor data
2. Trigger scrape
3. Verify changes logged in ChangeLog

**Success Criteria**:
- ChangeLog table populated
- Contains previous_value and new_value
- Includes change_type and severity
- Timestamp recorded

**Code Location**: `database.py` (ChangeLog model), `main.py` (scrape logic)

---

### Test C.3: Change Visible in UI ✅ READY
**Endpoint**: `GET /api/changes`
**Test**:
1. Fetch change log
2. Verify recent changes listed
3. Verify severity levels shown

**Success Criteria**:
- Returns list of recent changes
- Includes competitor name, field, old/new values
- Ordered by date (newest first)
- Severity levels accurate

**Code Location**: `main.py:810-850`

---

## Workflow 4: Discovery Agent → Find New Competitors

**Goal**: Verify discovery agent finds new competitors

### Test D.1: Run Discovery Agent ✅ READY
**Endpoint**: `POST /api/discovery/run`
**Test**:
1. Trigger discovery agent
2. Verify DuckDuckGo search initiated
3. Check candidate competitors returned

**Success Criteria**:
- Returns 200 status
- Response contains list of discovered competitors
- Each includes: name, website, reason_discovered
- Candidates not in database already

**Code Location**: `main.py:1545-1585`, `discovery_agent.py`

---

### Test D.2: Qualify Candidates ✅ READY
**Endpoint**: Discovery agent internal
**Test**:
1. Verify AI qualification (if OpenAI available)
2. Filter out irrelevant results
3. Rank by relevance

**Success Criteria**:
- Relevant competitors ranked high
- Non-competitors filtered out
- Results sorted by relevance score

**Code Location**: `discovery_agent.py`

---

### Test D.3: Add Discovered Competitor ✅ READY
**Endpoint**: `POST /api/competitors` (with `source: "discovery"`
**Test**:
1. Add discovered competitor to system
2. Verify linked to discovery run
3. Verify can be scraped immediately

**Success Criteria**:
- Competitor created
- Source tracked as "discovery"
- Can be scraped immediately
- Appears in dashboard

**Code Location**: `main.py:1139-1180`

---

## Test Execution Plan

### Phase 3A: Static Endpoint Tests (No Dependencies)
These tests verify endpoints work without external services:

1. **Test A.2**: Dashboard display (verify data structure)
2. **Test A.3**: Search functionality
3. **Test A.4**: View competitor details
4. **Test A.6**: JSON export format
5. **Test C.2**: Change detection structure

**Expected Duration**: 30 minutes
**Success Rate Target**: 100%

---

### Phase 3B: Data Integrity Tests (Database)
These tests verify data flows correctly through system:

1. **Test A.1**: Authentication
2. **Test A.5**: Excel export completeness
3. **Test B.1**: Add new competitor
4. **Test B.3**: Verify scraped data stored
5. **Test C.3**: Change log populated

**Expected Duration**: 1 hour
**Success Rate Target**: 100%

---

### Phase 3C: Integration Tests (End-to-End)
These tests verify complete workflows:

1. **Test B.2**: Trigger scrape and verify results
2. **Test C.1**: Scheduler configuration
3. **Test D.1**: Discovery agent execution
4. **Full Workflow A**: Login → Export sequence
5. **Full Workflow B**: Add → Scrape → Verify sequence

**Expected Duration**: 2-3 hours
**Success Rate Target**: 95%+ (allow for external service timeouts)

---

## Test Results Template

For each test, document:
```
### Test [ID]: [Name]
**Status**: ✅ PASS / ⚠️ PARTIAL / ❌ FAIL
**Date Tested**: [date]
**Notes**: [any observations]
**Blocking Issues**: [if failed]
**Next Steps**: [action if needed]
```

---

## Known Limitations

### May Not Work (Dependency Issues)
- **Playwright scraper**: Requires `pip install playwright && playwright install chromium`
- **yfinance**: Requires `pip install yfinance pandas`
- **OpenAI features**: Requires valid OPENAI_API_KEY
- **Email alerts**: Requires SMTP configuration
- **Real news**: Google News RSS may rate-limit requests

### Expected Fallbacks
- No Playwright → Known data used
- No yfinance → Known financial data used
- No OpenAI → Heuristic responses returned
- No SMTP → Changes logged but not emailed
- News rate-limited → Cached articles shown

---

## Success Criteria for Phase 3

**Minimum Success** (MVP Threshold):
- ✅ Authentication works
- ✅ Dashboard displays (with known data)
- ✅ Competitor CRUD works
- ✅ Change detection works
- ✅ Exports valid format
- ✅ Discovery agent structure works

**Expected Success** (With Free APIs):
- All above PLUS:
- ✅ Playwright scraper works (website content)
- ✅ yfinance works (financial data)
- ✅ News Monitor works (Google News RSS)
- ✅ Full workflows end-to-end

**Excellent Success** (With Optional APIs):
- All above PLUS:
- ✅ OpenAI features work (if key provided)
- ✅ Email alerts work (if SMTP configured)
- ✅ Slack notifications work (if webhook provided)

---

## Reporting

After Phase 3, document:
1. **Tests Passed**: Count and percentage
2. **Tests Failed**: List with root causes
3. **Blockers**: Any show-stoppers
4. **Recommendations**: What needs fixing
5. **Readiness Assessment**: Is system production-ready?

---

## Next Steps

1. Execute Phase 3A (static endpoint tests) - ~30 min
2. Execute Phase 3B (data integrity tests) - ~1 hour
3. Execute Phase 3C (integration tests) - ~2-3 hours
4. Document all results
5. Fix any critical issues
6. Move to Phase 4 (export validation) or Phase 5 (data quality)

---

**This plan provides comprehensive coverage of all critical user journeys.**

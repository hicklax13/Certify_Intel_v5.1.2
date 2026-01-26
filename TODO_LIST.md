# Certify Intel - Master TODO List

> **IMPORTANT FOR ALL AGENTS**: This is the authoritative task list for the Certify Intel project.
> **CHECK THIS FILE FIRST** at the start of every coding session to understand priorities and pending work.

---

## How to Use This File

1. **Start of Session**: Review all pending tasks and their priorities
2. **During Work**: Update task status as you progress
3. **End of Session**: Mark completed tasks and add any new tasks discovered

### Task Status Values
- `PENDING` - Not started
- `IN_PROGRESS` - Currently being worked on
- `BLOCKED` - Cannot proceed (see notes)
- `COMPLETED` - Done (move to Completed section with date)

### Priority Levels
- `CRITICAL` - Must be done immediately
- `HIGH` - Should be done this session
- `MEDIUM` - Should be done soon
- `LOW` - Nice to have

---

## Active Tasks

### v5.0.1 - Data Refresh Enhancement (COMPLETED - January 26, 2026)

**Goal**: Replace modal-based refresh progress with inline Dashboard display + AI-powered change summary

#### Phase 1: Inline Progress Bar
| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| 5.0.1-023 | Add inline progress HTML to Dashboard | ✅ COMPLETED | HIGH | New component below "Last Data Refresh" indicator |
| 5.0.1-024 | Add inline progress CSS styles | ✅ COMPLETED | HIGH | Animated progress bar, live update styling |
| 5.0.1-025 | Update JS for inline progress display | ✅ COMPLETED | HIGH | Replace modal functions with inline display |

#### Phase 2: Enhanced Backend Tracking
| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| 5.0.1-026 | Expand scrape_progress object | ✅ COMPLETED | HIGH | Add recent_changes, change_details, errors arrays |
| 5.0.1-027 | Track field-level changes in scraper | ✅ COMPLETED | HIGH | Record old/new values during scrape |
| 5.0.1-028 | Add /api/scrape/session endpoint | ✅ COMPLETED | MEDIUM | Return full session details with changes |

#### Phase 3: AI-Powered Summary
| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| 5.0.1-029 | Add /api/scrape/generate-summary endpoint | ✅ COMPLETED | HIGH | GPT-4 analysis of refresh changes |
| 5.0.1-030 | Update refresh complete modal with AI summary | ✅ COMPLETED | HIGH | Show AI summary + change details accordion |

#### Phase 4: Refresh History
| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| 5.0.1-031 | Add RefreshSession database model | ✅ COMPLETED | MEDIUM | New database table for session persistence |
| 5.0.1-032 | Test full refresh flow end-to-end | ✅ COMPLETED | HIGH | End-to-end testing of all components |

---

### v5.0.2 - Gemini Hybrid AI Integration (PENDING)

**Goal**: Add Google Gemini as a secondary AI provider alongside OpenAI for cost savings and new features.
**Estimated Savings**: ~90% cost reduction on bulk tasks

#### Phase 1: Core Infrastructure (Required)
| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| 5.0.2-001 | Add Gemini API dependencies | PENDING | HIGH | Add google-generativeai to requirements.txt |
| 5.0.2-002 | Create Gemini provider module | PENDING | HIGH | New file: backend/gemini_provider.py |
| 5.0.2-003 | Update .env.example with Gemini keys | PENDING | HIGH | Add GOOGLE_AI_API_KEY, GOOGLE_AI_MODEL |
| 5.0.2-004 | Create AI router/dispatcher | PENDING | HIGH | Route tasks to cheapest/best model |
| 5.0.2-005 | Update extractor.py for hybrid support | PENDING | HIGH | Support both OpenAI and Gemini |
| 5.0.2-006 | Add fallback logic | PENDING | MEDIUM | Switch providers on failure/rate-limit |
| 5.0.2-007 | Update CLAUDE.md with new config | PENDING | MEDIUM | Document new environment variables |

#### Phase 2: Existing Feature Migration (Optional)
| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| 5.0.2-008 | Migrate executive summaries | PENDING | MEDIUM | Option to use Gemini Flash |
| 5.0.2-009 | Migrate Discovery Agent | PENDING | MEDIUM | Use Gemini for bulk web analysis |
| 5.0.2-010 | Migrate data extraction | PENDING | MEDIUM | Hybrid extraction with cost optimization |
| 5.0.2-011 | Add model selection to UI | PENDING | LOW | Let users choose AI provider per task |

#### Phase 3: New Gemini-Powered Features (Future)
| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| 5.0.2-012 | Screenshot analysis | PENDING | LOW | Capture & analyze competitor websites visually |
| 5.0.2-013 | PDF/Document analysis | PENDING | LOW | Upload competitor whitepapers for insights |
| 5.0.2-014 | Video intelligence | PENDING | LOW | Analyze competitor demos/webinars |
| 5.0.2-015 | Real-time grounding | PENDING | LOW | Use Gemini's built-in web search |
| 5.0.2-016 | Bulk news processing | PENDING | LOW | Process 1000s of articles with Flash-Lite |

#### Phase 4: Testing & Documentation
| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| 5.0.2-017 | Unit tests for Gemini provider | PENDING | MEDIUM | Test API calls, error handling |
| 5.0.2-018 | Integration tests | PENDING | MEDIUM | Test hybrid routing logic |
| 5.0.2-019 | Cost comparison testing | PENDING | MEDIUM | Verify savings vs OpenAI-only |
| 5.0.2-020 | Update README | PENDING | LOW | Document Gemini setup |
| 5.0.2-021 | Update .env.example | PENDING | LOW | Complete configuration guide |

---

### v5.0.3 - Desktop App Fix (BLOCKED)

| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| 5.0.3-001 | Fix .env path in installed app | BLOCKED | HIGH | Resolve PyInstaller path issue |
| 5.0.3-002 | Test installed app end-to-end | PENDING | HIGH | Verify desktop app works |
| 5.0.3-003 | Auto-updater implementation | PENDING | LOW | Push updates to installed apps |

---

### v5.1.0 - Cloud Deployment (PENDING)

| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| 5.1.0-001 | Docker production config | PENDING | MEDIUM | Production-ready Docker setup |
| 5.1.0-002 | Cloud deployment guide | PENDING | MEDIUM | AWS/GCP/Azure instructions |
| 5.1.0-003 | CI/CD pipeline | PENDING | LOW | Automated testing & deployment |

---

### v5.2.0 - Team Features (PENDING)

| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| 5.2.0-001 | Multi-user improvements | PENDING | LOW | Better team collaboration |
| 5.2.0-002 | Role-based dashboards | PENDING | LOW | Custom views per role |
| 5.2.0-003 | Shared annotations | PENDING | LOW | Team notes on competitors |

---

### Live News Feed Implementation (PENDING)

**Reference**: `docs/LIVE_NEWS_FEED_IMPLEMENTATION_PLAN.md`

#### Phase 1: Quick Wins (No API Keys Needed)
| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| NEWS-001 | Add SEC EDGAR endpoint | PENDING | MEDIUM | 8-K filings for leadership changes, M&A |
| NEWS-002 | Enhance USPTO PatentsView | PENDING | MEDIUM | Already partially implemented |
| NEWS-003 | Replace RSS with pygooglenews | PENDING | MEDIUM | Better filtering than raw RSS |
| NEWS-004 | Upgrade sentiment to Hugging Face ML | PENDING | MEDIUM | Replace keyword-based sentiment |

#### Phase 2: API Key Sources (Free Registration)
| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| NEWS-005 | Add GNews API integration | PENDING | LOW | Secondary news source |
| NEWS-006 | Add NewsData.io integration | PENDING | LOW | Tech/healthcare specialty |
| NEWS-007 | Add MediaStack integration | PENDING | LOW | International coverage |

#### Phase 3: AI Subscription Integration
| ID | Task | Status | Priority | Details |
|----|------|--------|----------|---------|
| NEWS-008 | ChatGPT Deep Research integration | PENDING | LOW | "Generate Report" button on Battlecards |
| NEWS-009 | Gemini Deep Research integration | PENDING | LOW | Alternative research option |
| NEWS-010 | Firecrawl MCP integration | PENDING | LOW | Website scraping for competitor profiles |

#### Files to Modify
| File | Changes |
|------|---------|
| `backend/main.py` | Add `/api/news-feed` endpoint |
| `backend/news_monitor.py` | Add new source integrations |
| `frontend/index.html` | Add sidebar item + page section |
| `frontend/app_v2.js` | Add `loadNewsFeed()` and dropdown population |
| `frontend/styles.css` | Badge styles for sentiment |
| `backend/requirements.txt` | Add `pygooglenews`, `transformers` |

---

## Completed Tasks

### v5.0.1 - Data Quality Enhancement (COMPLETED - January 26, 2026)

| Phase | Description | Completed |
|-------|-------------|-----------|
| Phase 1 | Source Attribution & Confidence Scoring | Jan 26, 2026 |
| Phase 2 | Multi-Source Data Triangulation | Jan 26, 2026 |
| Phase 3 | Product-Specific Pricing Structure | Jan 26, 2026 |
| Phase 4 | Customer Count Verification System | Jan 26, 2026 |
| Phase 5 | Enhanced Scraper with Source Tracking | Jan 26, 2026 |
| Phase 6 | UI Enhancements - Confidence Indicators | Jan 26, 2026 |
| Phase 7 | Data Quality Dashboard | Jan 26, 2026 |

### v5.0.1 - Data Refresh Enhancement (COMPLETED - January 26, 2026)

| Phase | Description | Completed |
|-------|-------------|-----------|
| Phase 1 | Inline Progress Bar (HTML/CSS/JS) | Jan 26, 2026 |
| Phase 2 | Enhanced Backend Tracking | Jan 26, 2026 |
| Phase 3 | AI-Powered Refresh Summary | Jan 26, 2026 |
| Phase 4 | Refresh History & Persistence | Jan 26, 2026 |

### v5.0.1 - C-Suite Meeting Prep (COMPLETED - January 25, 2026)

| ID | Task | Completed |
|----|------|-----------|
| 5.0.1-019 | Fix dashboard stats display | Jan 25, 2026 |
| 5.0.1-020 | User-specific prompt management | Jan 25, 2026 |
| 5.0.1-021 | AI summary progress bar | Jan 25, 2026 |
| 5.0.1-022 | Code cleanup duplicate endpoints | Jan 25, 2026 |

### v5.0.1 - UI/UX Session (COMPLETED - January 25, 2026)

| ID | Task | Completed |
|----|------|-----------|
| 5.0.1-009 | Fix admin login password hash | Jan 25, 2026 |
| 5.0.1-010 | Update login page logo | Jan 25, 2026 |
| 5.0.1-011 | Style secondary buttons | Jan 25, 2026 |
| 5.0.1-012 | Style user avatar button | Jan 25, 2026 |
| 5.0.1-013 | Style notification button | Jan 25, 2026 |
| 5.0.1-014 | Add prompt caching system | Jan 25, 2026 |
| 5.0.1-015 | Update AI prompt for live data | Jan 25, 2026 |
| 5.0.1-016 | Enhance backend data for AI | Jan 25, 2026 |
| 5.0.1-017 | Add Last Data Refresh indicator | Jan 25, 2026 |
| 5.0.1-018 | Add uvicorn startup to main.py | Jan 25, 2026 |

---

## Summary Statistics

| Category | Total | Pending | In Progress | Completed | Blocked |
|----------|-------|---------|-------------|-----------|---------|
| v5.0.1 Data Refresh | 10 | 0 | 0 | 10 | 0 |
| v5.0.2 Gemini Integration | 21 | 21 | 0 | 0 | 0 |
| v5.0.3 Desktop App | 3 | 2 | 0 | 0 | 1 |
| v5.1.0 Cloud Deployment | 3 | 3 | 0 | 0 | 0 |
| v5.2.0 Team Features | 3 | 3 | 0 | 0 | 0 |
| Live News Feed | 10 | 10 | 0 | 0 | 0 |
| **TOTAL** | **50** | **39** | **0** | **10** | **1** |

---

## Recommended Next Steps

1. **IMMEDIATE**: Start v5.0.2 Gemini Hybrid Integration (Core Infrastructure - Tasks 5.0.2-001 to 5.0.2-007)
2. **NEXT**: Live News Feed Implementation (NEWS-001 to NEWS-010)
3. **FUTURE**: Cloud Deployment (v5.1.0), Team Features (v5.2.0)

---

**Last Updated**: January 26, 2026
**Updated By**: Claude Opus 4.5

---

## Session Log: January 26, 2026

**Session**: Data Refresh Enhancement Implementation
**Duration**: ~3.5 hours
**Tasks Completed**: 10

### Changes Made:
1. **Phase 1 - Inline Progress Bar**
   - Added inline progress HTML to Dashboard (index.html)
   - Added CSS animations and styling (styles.css)
   - Updated JavaScript for inline progress display (app_v2.js)

2. **Phase 2 - Enhanced Backend Tracking**
   - Expanded scrape_progress object with recent_changes, change_details, errors
   - Added field-level change tracking in scraper
   - Added /api/scrape/session endpoint

3. **Phase 3 - AI-Powered Summary**
   - Added /api/scrape/generate-summary endpoint with GPT integration
   - Updated refresh complete modal with AI summary section
   - Added change details accordion

4. **Phase 4 - Refresh History**
   - Added RefreshSession database model
   - Added /api/refresh-history endpoint
   - Integrated session persistence with scraping workflow

### Files Modified:
- `frontend/index.html` - Inline progress HTML, enhanced modal
- `frontend/styles.css` - Progress bar and AI summary CSS
- `frontend/app_v2.js` - Inline progress functions, modal updates
- `backend/main.py` - New endpoints, enhanced tracking
- `backend/database.py` - RefreshSession model
- `TODO_LIST.md` - Task status updates

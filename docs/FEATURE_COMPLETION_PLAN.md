# Feature Completion Plan

## Overview

This document outlines the implementation plan to make the following features fully functional:
1. **Data Refresh** - Automated competitor data updates
2. **Live News Feed** - Real-time news aggregation and display
3. **Competitor Discovery Agent** - AI-powered competitor discovery
4. **Change Logs** - Activity and data change tracking
5. **Analytics and Reports** - Dashboard analytics and PDF/Excel exports

**Created**: January 27, 2026
**Version**: v5.2.0
**Estimated Effort**: 3-4 days

---

## Current State Assessment

### 1. Data Refresh
| Component | Status | Issues |
|-----------|--------|--------|
| Manual refresh button | Partial | Works but limited scraping |
| Playwright scraper | Working | Needs better error handling |
| SEC EDGAR integration | Working | Public company data only |
| yfinance integration | Working | Stock data extraction |
| Scheduled refresh | Partial | APScheduler configured but not tested |
| Progress tracking | Working | RefreshSession table exists |

**Gap**: Scrapers need comprehensive website extraction, AI summary generation after refresh, and reliable scheduling.

### 2. Live News Feed
| Component | Status | Issues |
|-----------|--------|--------|
| Google News RSS | Working | pygooglenews integration |
| NewsAPI | Partial | Requires API key |
| GNews API | Partial | Requires API key |
| MediaStack API | Partial | Requires API key |
| NewsData.io API | Partial | Requires API key |
| News caching | Working | NewsArticleCache table |
| Sentiment analysis | Partial | ML model loaded but not applied |
| News page UI | Working | Basic display |

**Gap**: Need to integrate all sources with graceful degradation, apply ML sentiment, and add dimension tagging.

### 3. Competitor Discovery Agent
| Component | Status | Issues |
|-----------|--------|--------|
| DuckDuckGo search | Working | Rate limited |
| AI analysis | Partial | GPT/Gemini integration exists |
| Auto-add competitors | Not Working | Discovery results not persisted |
| Deduplication | Not Working | No duplicate checking |
| Industry filtering | Partial | Healthcare filter exists |

**Gap**: Need end-to-end flow from search to competitor creation with deduplication.

### 4. Change Logs
| Component | Status | Issues |
|-----------|--------|--------|
| ChangeLog table | Working | Records exist |
| ActivityLog table | Working | Records exist |
| UI display | Partial | Basic list view |
| Filtering | Not Working | No date/type filters |
| Export | Not Working | No export functionality |

**Gap**: Need filtering, pagination, and export capabilities.

### 5. Analytics and Reports
| Component | Status | Issues |
|-----------|--------|--------|
| Dashboard stats | Partial | Basic counts |
| Charts | Partial | Chart.js integrated |
| PDF export | Partial | ReportLab exists |
| Excel export | Partial | openpyxl exists |
| Market map | Not Working | No visualization |
| Threat analysis | Partial | Basic scoring |

**Gap**: Need comprehensive analytics dashboard, working exports, and market positioning.

---

## Implementation Plan

### Phase 1: Data Refresh Enhancement (Day 1)

#### Task 1.1: Fix Playwright Scraper
**File**: `backend/scraper.py`

- Add comprehensive website extraction (about, products, pricing pages)
- Implement retry logic with exponential backoff
- Add screenshot capture for visual verification
- Handle JavaScript-heavy sites better

```python
# Key changes:
async def scrape_competitor_comprehensive(self, competitor_id: int):
    """Scrape all key pages for a competitor."""
    pages_to_scrape = [
        "/", "/about", "/products", "/pricing",
        "/solutions", "/customers", "/company"
    ]
    # Extract and consolidate data from all pages
```

#### Task 1.2: Implement AI Summary After Refresh
**File**: `backend/main.py`

- After scrape completes, generate AI summary of changes
- Store summary in RefreshSession table
- Display summary in UI refresh dialog

#### Task 1.3: Fix Scheduled Refresh
**File**: `backend/scheduler.py`

- Verify APScheduler job configuration
- Add logging for job execution
- Implement staggered refresh to avoid rate limits

#### Task 1.4: Add Bulk Refresh with Progress
**File**: `backend/main.py`, `frontend/app_v2.js`

- Add endpoint for bulk refresh of all competitors
- Real-time progress via WebSocket or polling
- Error aggregation and retry failed items

---

### Phase 2: Live News Feed Completion (Day 1-2)

#### Task 2.1: Integrate All News Sources
**File**: `backend/news_monitor.py`

- Add graceful degradation when API keys missing
- Implement source priority and deduplication
- Cache results with appropriate TTL

```python
async def fetch_all_news(self, competitor_name: str) -> List[NewsArticle]:
    """Fetch from all available sources with fallback."""
    sources = [
        self.google_news_rss,      # Always available
        self.gnews_api,            # If key exists
        self.newsapi,              # If key exists
        self.mediastack,           # If key exists
        self.newsdata,             # If key exists
    ]
    # Aggregate, deduplicate, and sort
```

#### Task 2.2: Apply ML Sentiment Analysis
**File**: `backend/ml_sentiment.py`, `backend/news_monitor.py`

- Load FinBERT model on startup (if not already)
- Apply sentiment to all news articles
- Store sentiment scores in cache

#### Task 2.3: Add Dimension Tagging
**File**: `backend/news_monitor.py`

- Use AI to tag news with relevant dimensions
- Store tags in DimensionNewsTag table
- Filter news by dimension in UI

#### Task 2.4: Enhance News Page UI
**File**: `frontend/app_v2.js`

- Add sentiment filter (positive/negative/neutral)
- Add dimension filter
- Add date range picker
- Implement infinite scroll or pagination

---

### Phase 3: Competitor Discovery Agent (Day 2)

#### Task 3.1: Fix Discovery Flow
**File**: `backend/discovery_agent.py`

- Complete end-to-end discovery flow
- Add deduplication against existing competitors
- Score discovery results by relevance

```python
async def discover_and_add(self, industry: str, limit: int = 10):
    """Discover new competitors and add to database."""
    # 1. Search multiple sources
    # 2. AI analysis for relevance
    # 3. Deduplication check
    # 4. Create competitor records
    # 5. Initial scrape for new competitors
```

#### Task 3.2: Add Industry-Specific Filters
**File**: `backend/discovery_agent.py`

- Healthcare technology focus
- EMR/EHR, patient engagement, analytics
- Exclude non-competitors (consulting, hardware)

#### Task 3.3: Create Discovery UI
**File**: `frontend/app_v2.js`

- Discovery button with industry selection
- Preview results before adding
- Bulk add selected discoveries

---

### Phase 4: Change Logs Enhancement (Day 2-3)

#### Task 4.1: Add Filtering
**File**: `backend/main.py`, `frontend/app_v2.js`

- Filter by competitor
- Filter by field changed
- Filter by date range
- Filter by user

#### Task 4.2: Add Pagination
**File**: `backend/main.py`

- Paginate large result sets
- Add sorting options

#### Task 4.3: Add Export
**File**: `backend/reports.py`

- Export change log to CSV
- Export to Excel with formatting

---

### Phase 5: Analytics and Reports (Day 3-4)

#### Task 5.1: Complete Dashboard Analytics
**File**: `backend/analytics.py`, `frontend/app_v2.js`

- Competitor count by threat level
- News sentiment trends
- Data freshness metrics
- Dimension score averages

#### Task 5.2: Create Market Map
**File**: `frontend/app_v2.js`

- 2D positioning chart (market share vs growth)
- Interactive competitor bubbles
- Category grouping

#### Task 5.3: Fix PDF Export
**File**: `backend/reports.py`

- Generate comprehensive competitor report
- Include charts as images
- Add executive summary section

#### Task 5.4: Fix Excel Export
**File**: `backend/reports.py`

- Export all competitors with all fields
- Include dimension scores
- Add charts sheet

#### Task 5.5: Add Comparison Reports
**File**: `backend/reports.py`

- Side-by-side competitor comparison
- Feature matrix export
- Dimension radar chart

---

## API Endpoints to Implement/Fix

### Data Refresh
| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/refresh/all` | POST | Bulk refresh all competitors |
| `GET /api/refresh/status` | GET | Current refresh job status |
| `POST /api/refresh/schedule` | POST | Configure scheduled refresh |

### News Feed
| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/news/sources` | GET | List available news sources |
| `POST /api/news/refresh/{id}` | POST | Refresh news for competitor |
| `GET /api/news/sentiment-stats` | GET | Sentiment distribution |

### Discovery
| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/discover/search` | POST | Search for new competitors |
| `POST /api/discover/add` | POST | Add discovered competitors |
| `GET /api/discover/history` | GET | Past discovery sessions |

### Change Logs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/changelog` | GET | Filtered change log |
| `GET /api/changelog/export` | GET | Export to CSV/Excel |

### Analytics
| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/analytics/dashboard` | GET | Dashboard metrics |
| `GET /api/analytics/market-map` | GET | Market positioning data |
| `GET /api/reports/pdf/{id}` | GET | PDF competitor report |
| `GET /api/reports/excel/all` | GET | Excel export all |

---

## Success Criteria

| Feature | Criteria |
|---------|----------|
| Data Refresh | All 82 competitors refresh successfully with <5% error rate |
| Live News Feed | Displays recent news for all competitors with sentiment |
| Discovery Agent | Can find and add new competitors with deduplication |
| Change Logs | Filterable, exportable activity history |
| Analytics | Dashboard shows accurate metrics, exports work |

---

## Files to Modify

| File | Changes |
|------|---------|
| `backend/scraper.py` | Comprehensive scraping, retry logic |
| `backend/news_monitor.py` | Multi-source integration, sentiment |
| `backend/discovery_agent.py` | End-to-end flow, deduplication |
| `backend/analytics.py` | Dashboard metrics, market map |
| `backend/reports.py` | PDF/Excel generation |
| `backend/main.py` | New/fixed endpoints |
| `backend/scheduler.py` | Reliable scheduled jobs |
| `frontend/app_v2.js` | UI enhancements |

---

## Dependencies

- All existing dependencies in requirements.txt
- Vertex AI (optional, for enhanced AI features)
- API keys (optional, for enhanced news sources)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Rate limiting | Staggered requests, caching |
| API key costs | Graceful degradation without keys |
| Large data volumes | Pagination, streaming |
| Scraper failures | Retry logic, error logging |

---

**Next Steps**: After this plan is approved and committed to GitHub, begin implementation with Phase 1.

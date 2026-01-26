# Live News Feed Implementation Plan

## Overview
Add a dedicated "News Feed" page to Certify Intel that displays an aggregated, filterable table of news articles mentioning tracked competitors.

---

## Data Sources (FREE)

| Source | Cost | Limit | Already Implemented |
|--------|------|-------|---------------------|
| **Google News RSS** | FREE | Unlimited | ✅ Yes (`news_monitor.py`) |
| **NewsAPI.org** | FREE tier | 100 req/day | ✅ Yes (needs API key) |
| **Bing News API** | FREE tier | 1000 req/mo | ✅ Yes (needs API key) |
| **GNews API** | FREE tier | 100 req/day | ❌ Can add |
| **MediaStack** | FREE tier | 500 req/mo | ❌ Can add |

**Recommendation**: Use Google News RSS (already implemented, unlimited, no API key required).

---

## Implementation Steps

### Step 1: Backend - New Aggregated Endpoint

**File**: `backend/main.py`

Add endpoint: `GET /api/news-feed`

**Query Parameters**:
| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `competitor_id` | Yes | int | Filter by specific competitor |
| `start_date` | Yes | string | Start of date range (YYYY-MM-DD) |
| `end_date` | Yes | string | End of date range (YYYY-MM-DD) |
| `sentiment` | No | string | Filter: positive, negative, neutral |
| `event_type` | No | string | Filter: funding, acquisition, product_launch, partnership |

**Response Schema**:
```json
{
  "articles": [
    {
      "title": "Article Title",
      "url": "https://...",
      "source": "TechCrunch",
      "published_date": "2026-01-25T10:30:00Z",
      "competitor_name": "Phreesia",
      "competitor_id": 1,
      "sentiment": "positive",
      "event_type": "funding",
      "snippet": "Brief description..."
    }
  ],
  "total_count": 45,
  "filters_applied": {
    "competitor_id": 1,
    "date_range": "2026-01-01 to 2026-01-25"
  }
}
```

---

### Step 2: Frontend - New Sidebar Menu Item

**File**: `frontend/index.html`

Add after "Change Log" in sidebar:
```html
<a href="#" class="nav-item" onclick="showPage('newsfeed')">
    <span class="nav-icon">📰</span>
    <span class="nav-text">News Feed</span>
</a>
```

---

### Step 3: Frontend - News Feed Page Section

**File**: `frontend/index.html`

Add new page section:
```html
<section id="newsfeedPage" class="page" style="display:none;">
    <h2>Live News Feed</h2>
    <p class="page-description">Real-time news monitoring for tracked competitors</p>

    <!-- Required Filters -->
    <div class="filter-bar">
        <div class="filter-group">
            <label for="newsCompetitor">Competitor *</label>
            <select id="newsCompetitor" required>
                <option value="">-- Select Competitor --</option>
            </select>
        </div>
        <div class="filter-group">
            <label for="newsStartDate">From Date *</label>
            <input type="date" id="newsStartDate" required>
        </div>
        <div class="filter-group">
            <label for="newsEndDate">To Date *</label>
            <input type="date" id="newsEndDate" required>
        </div>
        <div class="filter-group">
            <label for="newsSentiment">Sentiment</label>
            <select id="newsSentiment">
                <option value="">All</option>
                <option value="positive">Positive</option>
                <option value="neutral">Neutral</option>
                <option value="negative">Negative</option>
            </select>
        </div>
        <button class="btn-primary" onclick="loadNewsFeed()">Search News</button>
    </div>

    <!-- Results Table -->
    <div class="table-card">
        <table class="data-table" id="newsFeedTable">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Competitor</th>
                    <th>Headline</th>
                    <th>Source</th>
                    <th>Sentiment</th>
                    <th>Event Type</th>
                </tr>
            </thead>
            <tbody id="newsFeedBody">
                <tr><td colspan="6" class="empty-state">Select a competitor and date range to view news</td></tr>
            </tbody>
        </table>
    </div>
</section>
```

---

### Step 4: Frontend - JavaScript Functions

**File**: `frontend/app_v2.js`

```javascript
// Populate competitor dropdown on News Feed page
function populateNewsCompetitorDropdown() {
    const select = document.getElementById('newsCompetitor');
    if (!select) return;
    select.innerHTML = '<option value="">-- Select Competitor --</option>' +
        competitors.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
}

// Load news feed based on filters
async function loadNewsFeed() {
    const competitorId = document.getElementById('newsCompetitor').value;
    const startDate = document.getElementById('newsStartDate').value;
    const endDate = document.getElementById('newsEndDate').value;
    const sentiment = document.getElementById('newsSentiment').value;

    // Validate required fields
    if (!competitorId || !startDate || !endDate) {
        alert('Please fill in all required fields: Competitor, From Date, and To Date');
        return;
    }

    const tbody = document.getElementById('newsFeedBody');
    tbody.innerHTML = '<tr><td colspan="6" class="loading">Loading news articles...</td></tr>';

    try {
        let url = `/api/news-feed?competitor_id=${competitorId}&start_date=${startDate}&end_date=${endDate}`;
        if (sentiment) url += `&sentiment=${sentiment}`;

        const data = await fetchAPI(url);

        if (data.articles?.length) {
            tbody.innerHTML = data.articles.map(article => `
                <tr>
                    <td>${formatDate(article.published_date)}</td>
                    <td>${article.competitor_name}</td>
                    <td><a href="${article.url}" target="_blank">${article.title}</a></td>
                    <td>${article.source}</td>
                    <td><span class="badge badge-${article.sentiment}">${article.sentiment}</span></td>
                    <td>${article.event_type || '-'}</td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No news articles found for this selection</td></tr>';
        }
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="6" class="error-state">Error loading news feed</td></tr>';
    }
}
```

---

### Step 5: Backend Endpoint Implementation

**File**: `backend/main.py`

```python
@app.get("/api/news-feed")
async def get_news_feed(
    competitor_id: int,
    start_date: str,
    end_date: str,
    sentiment: Optional[str] = None,
    event_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Aggregated news feed with required filtering.
    Uses FREE Google News RSS (no API key required).
    """
    db = SessionLocal()
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    db.close()

    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    # Fetch news using existing NewsMonitor
    monitor = NewsMonitor()
    digest = monitor.fetch_news(competitor.name)

    # Parse date range
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Filter articles
    filtered = []
    for article in digest.articles:
        # Parse article date
        try:
            article_date = datetime.strptime(article.published_date[:10], "%Y-%m-%d")
        except:
            continue

        # Apply date filter
        if not (start <= article_date <= end):
            continue

        # Apply sentiment filter
        if sentiment and article.sentiment != sentiment:
            continue

        # Apply event type filter
        if event_type and article.event_type != event_type:
            continue

        filtered.append({
            **asdict(article),
            "competitor_name": competitor.name,
            "competitor_id": competitor_id
        })

    return {
        "articles": filtered,
        "total_count": len(filtered),
        "filters_applied": {
            "competitor_id": competitor_id,
            "competitor_name": competitor.name,
            "date_range": f"{start_date} to {end_date}",
            "sentiment": sentiment,
            "event_type": event_type
        }
    }
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `backend/main.py` | Add `/api/news-feed` endpoint |
| `frontend/index.html` | Add sidebar item + page section |
| `frontend/app_v2.js` | Add `loadNewsFeed()` and dropdown population |
| `frontend/styles.css` | Badge styles for sentiment (if not exists) |

---

## Required User Inputs

| Field | Required | Validation |
|-------|----------|------------|
| Competitor | ✅ Yes | Must select from dropdown |
| From Date | ✅ Yes | Valid date, not future |
| To Date | ✅ Yes | Valid date, >= From Date |
| Sentiment | ❌ No | Optional filter |

---

## Estimated Effort

| Task | Time |
|------|------|
| Backend endpoint | 15 min |
| Frontend HTML | 10 min |
| Frontend JS | 15 min |
| CSS styling | 5 min |
| Testing | 10 min |
| **Total** | **~55 min** |

---

## Future Enhancements (Optional)

1. **Multi-competitor selection** - Select multiple competitors at once
2. **Export to CSV** - Download results
3. **Email alerts** - Notify when new articles match criteria
4. **Keyword search** - Search within article titles/snippets
5. **Auto-refresh** - Poll for new articles every X minutes

---

## No Additional Costs Required

This implementation uses the **existing Google News RSS** integration which is:
- ✅ FREE (no API key required)
- ✅ Unlimited requests
- ✅ Already implemented in `news_monitor.py`
- ✅ No external dependencies to install

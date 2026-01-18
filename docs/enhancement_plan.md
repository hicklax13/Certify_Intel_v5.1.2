# Certify Intel - MVP Enhancement Plan

**Date**: January 17, 2026  
**Status**: Proposed Enhancements  
**Impact**: High - Will significantly improve platform value

---

## Overview

These 10 enhancement tasks will transform the MVP into a comprehensive competitive intelligence powerhouse. Each task is prioritized by impact and implementation complexity.

---

## Enhancement Tasks

### Task 1: AI-Powered Threat Scoring (Priority: 🔴 Critical)

**Current State**: Threat levels are manually assigned (High/Medium/Low)

**Enhancement**: Use GPT-4 to automatically calculate threat scores based on:

- Funding velocity
- Customer growth rate
- Product feature overlap with Certify Health
- Market segment overlap
- Recent news sentiment

**Implementation**:

```python
# backend/threat_analyzer.py
def calculate_threat_score(competitor: Competitor) -> dict:
    """Use AI to calculate dynamic threat score."""
    prompt = f"""
    Analyze this competitor's threat to Certify Health:
    - Name: {competitor.name}
    - Funding: {competitor.funding_total}
    - Customers: {competitor.customer_count}
    - Products: {competitor.product_categories}
    - Features: {competitor.key_features}
    
    Score from 0-100 and explain why.
    """
    # Returns: {"score": 78, "reasoning": "...", "key_risks": [...]}
```

**Files to Create**:

- `backend/threat_analyzer.py`
- Update `main.py` with `/api/competitors/{id}/threat-analysis`
- Add threat score visualization to dashboard

**Estimated Effort**: 4 hours

---

### Task 2: Real-Time News Monitoring (Priority: 🔴 Critical)

**Current State**: Basic news mentions count only

**Enhancement**: Integrate NewsAPI or Google News to:

- Fetch real-time competitor news articles
- Analyze sentiment (positive/negative/neutral)
- Alert on major announcements (funding, acquisitions, product launches)

**Implementation**:

```python
# backend/news_monitor.py
class NewsMonitor:
    def fetch_competitor_news(self, company_name: str, days: int = 7):
        # NewsAPI integration
        # Returns articles with sentiment analysis
        
    def detect_major_events(self, articles: list):
        # Identify funding announcements, acquisitions, etc.
```

**API Options**:

- NewsAPI.org ($449/mo for business)
- Google News RSS (Free)
- Bing News API (Azure)

**Files to Create**:

- `backend/news_monitor.py`
- Add news feed to battlecard modal
- Create news alerts endpoint

**Estimated Effort**: 6 hours

---

### Task 3: Price Change Alerts (Priority: 🟡 High)

**Current State**: Prices stored but no change detection

**Enhancement**: Automatic alerts when competitors change pricing:

- Track price history over time
- Alert when price increases/decreases by >10%
- Show price trend charts

**Implementation**:

```python
# backend/price_tracker.py
class PriceTracker:
    def check_for_changes(self, competitor_id: int):
        # Compare current vs last known price
        # Create ChangeLog entry if different
        # Trigger email alert for significant changes
```

**Database Addition**:

```sql
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY,
    competitor_id INTEGER,
    base_price VARCHAR,
    price_unit VARCHAR,
    recorded_at TIMESTAMP
);
```

**Files to Create/Modify**:

- `backend/price_tracker.py`
- Add `PriceHistory` model to `main.py`
- Create price trend chart component

**Estimated Effort**: 3 hours

---

### Task 4: G2/Capterra Review Integration (Priority: 🟡 High)

**Current State**: G2 ratings manually entered

**Enhancement**: Scrape actual review data:

- Overall rating with breakdown
- Recent review excerpts
- Feature-by-feature scores
- Comparison with Certify Health

**Implementation**:

```python
# backend/review_scraper.py
class ReviewScraper:
    def scrape_g2_reviews(self, company_slug: str):
        # Scrape G2 page for ratings and reviews
        return {
            "overall_rating": 4.5,
            "total_reviews": 234,
            "ratings_breakdown": {...},
            "recent_reviews": [...],
            "pros": [...],
            "cons": [...]
        }
```

**Files to Create**:

- `backend/review_scraper.py`
- Add reviews tab to competitor detail modal
- Create reviews comparison chart

**Estimated Effort**: 5 hours

---

### Task 5: LinkedIn Company Data (Priority: 🟡 High)

**Current State**: Employee count is manually tracked

**Enhancement**: Pull LinkedIn company data:

- Real-time employee count
- Employee growth trends
- Open job postings (indicates expansion)
- Key hiring patterns (sales = aggressive growth)

**Implementation**:

```python
# backend/linkedin_tracker.py
class LinkedInTracker:
    def get_company_data(self, company_name: str):
        # Use LinkedIn API or scraping
        return {
            "employee_count": 234,
            "employee_growth_6mo": "+15%",
            "open_jobs": 45,
            "job_categories": {"Sales": 12, "Engineering": 20},
            "recent_hires": [...]
        }
```

**Note**: LinkedIn scraping requires careful handling. Consider:

- LinkedIn API (limited access)
- Third-party enrichment APIs (Apollo, Clearbit)

**Estimated Effort**: 6 hours

---

### Task 6: Market Share Visualization (Priority: 🟢 Medium)

**Current State**: Basic pie chart of customer counts

**Enhancement**: Interactive market analysis dashboard:

- Treemap of market segments
- Bubble chart (customers vs funding vs growth)
- Quadrant analysis (Growth Rate vs Market Share)
- Trend lines over time

**Implementation**:

```javascript
// frontend/analytics.js
function renderMarketQuadrant() {
    // D3.js or Chart.js scatter plot
    // X-axis: Market Share
    // Y-axis: Growth Rate
    // Quadrants: Stars, Question Marks, Cash Cows, Dogs
}
```

**Files to Create/Modify**:

- Add D3.js to frontend
- Create new analytics visualizations
- Add "Market Analysis" page

**Estimated Effort**: 4 hours

---

### Task 7: Mobile-Responsive PWA (Priority: 🟢 Medium)

**Current State**: Desktop-only dashboard

**Enhancement**: Progressive Web App for mobile access:

- Responsive dashboard design
- Push notifications for alerts
- Offline capability
- Install as app on phone

**Implementation**:

```javascript
// frontend/service-worker.js
// Cache strategies for offline use

// manifest.json
{
    "name": "Certify Intel",
    "short_name": "CI",
    "start_url": "/app",
    "display": "standalone",
    "icons": [...]
}
```

**Files to Create**:

- `frontend/service-worker.js`
- `frontend/manifest.json`
- Update `styles.css` with responsive breakpoints

**Estimated Effort**: 5 hours

---

### Task 8: Competitive Win/Loss Tracker (Priority: 🟢 Medium)

**Current State**: No sales outcome tracking

**Enhancement**: Track competitive deals:

- Log wins/losses against each competitor
- Win rate by competitor
- Common reasons for wins/losses
- Identify most competitive deals

**Implementation**:

```python
# New database model
class CompetitiveDeal(Base):
    competitor_id: int
    deal_name: str
    deal_value: float
    outcome: str  # "Won", "Lost"
    loss_reason: str  # Optional
    notes: str
    deal_date: datetime
```

**Dashboard Addition**:

- Win/Loss ratio per competitor
- Loss reason analysis
- Trend over time

**Estimated Effort**: 4 hours

---

### Task 9: Competitor Timeline (Priority: 🟢 Medium)

**Current State**: Changes logged but not visualized

**Enhancement**: Visual timeline of competitor events:

- Funding rounds
- Product launches
- Leadership changes
- Acquisitions
- Price changes

**Implementation**:

```javascript
// frontend/timeline.js
function renderCompetitorTimeline(competitorId) {
    // Fetch events from API
    // Render using Timeline.js or custom D3
}
```

**Files to Create**:

- Add timeline view to competitor detail
- Aggregate events from ChangeLog + News

**Estimated Effort**: 3 hours

---

### Task 10: API Webhooks for Integrations (Priority: 🟢 Medium)

**Current State**: No outbound integrations

**Enhancement**: Webhook system for real-time integrations:

- Trigger webhooks on competitor changes
- Integrate with Slack, Teams, Salesforce
- Custom webhook endpoints

**Implementation**:

```python
# backend/webhooks.py
class WebhookManager:
    def register_webhook(self, url: str, events: list):
        # Store webhook configuration
        
    def trigger_webhook(self, event: str, data: dict):
        # POST to all registered webhooks
```

**Use Cases**:

- Push to Slack channel on price change
- Update Salesforce competitor records
- Trigger HubSpot workflows

**Estimated Effort**: 3 hours

---

## Priority Matrix

| Priority | Task | Impact | Effort |
|----------|------|--------|--------|
| 🔴 Critical | AI Threat Scoring | Very High | 4h |
| 🔴 Critical | News Monitoring | Very High | 6h |
| 🟡 High | Price Change Alerts | High | 3h |
| 🟡 High | G2 Review Integration | High | 5h |
| 🟡 High | LinkedIn Data | High | 6h |
| 🟢 Medium | Market Visualization | Medium | 4h |
| 🟢 Medium | Mobile PWA | Medium | 5h |
| 🟢 Medium | Win/Loss Tracker | Medium | 4h |
| 🟢 Medium | Competitor Timeline | Medium | 3h |
| 🟢 Medium | API Webhooks | Medium | 3h |

**Total Estimated Effort**: 43 hours (~5-6 days)

---

## Recommended Implementation Order

1. **AI Threat Scoring** - Immediate value for sales team
2. **Price Change Alerts** - Quick win, high visibility
3. **News Monitoring** - Real-time competitive awareness
4. **G2 Review Integration** - Actionable sales intelligence
5. **Competitor Timeline** - Better context for changes
6. **Market Visualization** - Executive reporting
7. **Win/Loss Tracker** - Sales feedback loop
8. **LinkedIn Data** - Expansion signals
9. **Mobile PWA** - Field accessibility
10. **API Webhooks** - Integration ecosystem

---

## Dependencies

| Task | Dependencies |
|------|--------------|
| AI Threat Scoring | OpenAI API key |
| News Monitoring | NewsAPI subscription |
| LinkedIn Data | LinkedIn API or enrichment service |
| G2 Reviews | Playwright scraping |
| Mobile PWA | None |
| Webhooks | None |

---

## Ready to Proceed?

Select which tasks to implement:

- [ ] All 10 tasks
- [ ] Critical only (1-2)
- [ ] High priority (1-5)
- [ ] Custom selection

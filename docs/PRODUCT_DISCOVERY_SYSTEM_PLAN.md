# Product Discovery & Tracking System

**Version**: v5.1.0 Proposal
**Created**: January 26, 2026
**Status**: PROPOSED - Awaiting Approval

---

## Problem Statement

We cannot currently guarantee 100% product/service coverage because:

1. **No systematic product discovery** - Only 15/123 competitors have product data
2. **CompetitorProduct table is empty** - Individual products aren't being tracked
3. **No product launch monitoring** - No alerts when competitors add new products
4. **Static scraping** - Only 4 pages scraped per competitor (homepage, pricing, about, features)

---

## Proposed Solution Architecture

### Phase 1: Product Discovery Crawler (~2 days)

**Goal**: Systematically discover ALL products/services for each competitor

#### 1.1 Product Page Crawler

```
For each competitor:
  1. Visit homepage
  2. Find "Products", "Solutions", "Services", "Platform" navigation links
  3. Crawl all product/solution pages (max depth 2)
  4. Extract individual product names and descriptions
  5. Create CompetitorProduct records
```

**Key Capabilities**:
- Follow navigation to find products/solutions sections
- Handle dynamic menus (JavaScript rendered)
- Extract product names, descriptions, categories
- Detect pricing pages for each product
- Handle multiple product lines (e.g., Epic has 50+ modules)

#### 1.2 Multi-Source Verification

To be 100% certain we have all products, cross-reference:

| Source | What It Tells Us | API/Method |
|--------|------------------|------------|
| **Competitor Website** | Official product listing | Playwright crawler |
| **G2.com** | Products listed for comparison | Scrape /products page |
| **Capterra** | Product categories | Scrape profile |
| **KLAS** | Healthcare-specific products | KLAS API |
| **SEC Filings** | Revenue segments = product lines | SEC EDGAR |
| **Press Releases** | New product announcements | News API |
| **App Stores** | Mobile products | iOS/Android API |
| **LinkedIn Jobs** | Product names in job titles | Scrape |
| **Patents** | Future products | USPTO API |

#### 1.3 Product Schema

```python
class CompetitorProduct(Base):
    # Identification
    product_name: str          # "Phreesia Intake"
    product_slug: str          # "phreesia-intake" (for URLs)
    product_category: str      # "Patient Intake"
    product_subcategory: str   # "Digital Check-in"

    # Discovery tracking
    discovery_source: str      # "website_crawl", "g2", "press_release"
    discovery_date: datetime
    product_page_url: str      # Direct link to product page

    # Verification
    is_verified: bool          # Confirmed to exist
    verification_sources: int  # How many sources confirm this product
    last_verified: datetime

    # Status
    status: str                # "active", "deprecated", "beta", "announced"
    launch_date: datetime
    deprecation_date: datetime
```

---

### Phase 2: Automated Data Feeds per Product (~3 days)

**Goal**: Live, refreshed data for EVERY product

#### 2.1 Product-Level Data Points

For each discovered product, track:

| Data Point | Update Frequency | Source(s) |
|------------|-----------------|-----------|
| Product Name | On change | Website |
| Description | Monthly | Website |
| Pricing | Weekly | Website, G2 |
| Key Features | Monthly | Website, G2, KLAS |
| Target Segment | Monthly | Website |
| Customer Reviews | Daily | G2, Capterra, KLAS |
| Average Rating | Daily | G2, Capterra |
| Implementation Time | Monthly | G2, KLAS |
| Integration Partners | Monthly | Website, Integration pages |
| Certifications | Monthly | Website |

#### 2.2 Data Feed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SCHEDULER (APScheduler)                   │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ Hourly       │ Daily        │ Weekly       │ Monthly        │
│ - News       │ - Reviews    │ - Pricing    │ - Full crawl   │
│ - Alerts     │ - Ratings    │ - Features   │ - Verification │
│              │ - Traffic    │ - Jobs       │ - Patents      │
└──────────────┴──────────────┴──────────────┴────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA AGGREGATOR                           │
│  - Merge data from multiple sources                          │
│  - Resolve conflicts (prefer higher confidence)              │
│  - Detect new products (alert)                               │
│  - Detect deprecated products (alert)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 COMPETITOR PRODUCTS TABLE                    │
│  - 123 competitors × ~5-50 products each = 600-6000 rows    │
│  - Full audit trail via DataSource                           │
│  - Confidence scoring per field                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Phase 3: New Product Detection System (~2 days)

**Goal**: Automatically detect when competitors launch new products

#### 3.1 Detection Methods

| Method | How It Works | Latency |
|--------|--------------|---------|
| **Website Diff** | Compare product page list weekly | 7 days |
| **Press Release Monitor** | Scan for "launches", "introduces", "announces" | Same day |
| **G2 New Listings** | Check G2 for new product entries | 1-2 days |
| **Job Posting Analysis** | New product names in job titles | 1 week |
| **SEC 8-K Filings** | Material events = new products | Same day |
| **Patent Filings** | Future products in pipeline | 6+ months |

#### 3.2 Alert System

When a new product is detected:

1. **Create CompetitorProduct** record with status="announced"
2. **Send Alert** via email/Slack/Teams
3. **Queue Deep Scrape** to gather product details
4. **AI Analysis** to assess competitive impact
5. **Update Battlecard** if threat level changes

---

### Phase 4: 100% Coverage Guarantee (~1 day)

**Goal**: Verification that we have ALL products

#### 4.1 Coverage Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│              PRODUCT COVERAGE DASHBOARD                      │
├─────────────────────────────────────────────────────────────┤
│ TOTAL COMPETITORS: 123                                       │
│ TOTAL PRODUCTS TRACKED: 847                                  │
│                                                              │
│ Coverage by Source:                                          │
│   ✅ Website Crawl: 123/123 (100%)                          │
│   ✅ G2 Cross-Reference: 89/123 (72%)                       │
│   ✅ KLAS Cross-Reference: 45/123 (37%)                     │
│   ⚠️ SEC Filings (public only): 12/12 (100%)               │
│                                                              │
│ Products by Category:                                        │
│   Patient Intake: 34 competitors, 67 products               │
│   Practice Management: 45 competitors, 89 products          │
│   RCM: 28 competitors, 52 products                          │
│   Patient Engagement: 56 competitors, 112 products          │
│   ...                                                        │
│                                                              │
│ ⚠️ GAPS DETECTED:                                           │
│   - Competitor X: No products found (website blocked)        │
│   - Competitor Y: Only 1 product but news mentions 3         │
└─────────────────────────────────────────────────────────────┘
```

#### 4.2 Verification Workflow

```
For each competitor:
  1. Count products from website crawl
  2. Count products from G2/Capterra
  3. Count products mentioned in news
  4. Count revenue segments in SEC filings

  IF counts don't match:
    - Flag for manual review
    - Queue additional investigation
    - Alert analyst
```

---

## Implementation Plan

### Phase 1: Product Discovery Crawler (Week 1)

| Task | Description | Effort |
|------|-------------|--------|
| 1.1 | Create `product_discovery_crawler.py` | 4 hours |
| 1.2 | Add navigation detection (Products/Solutions links) | 2 hours |
| 1.3 | Implement product page extraction | 4 hours |
| 1.4 | Add G2 product list scraper | 2 hours |
| 1.5 | Add Capterra product list scraper | 2 hours |
| 1.6 | Create API endpoint `/api/products/discover/{competitor_id}` | 2 hours |

### Phase 2: Data Feeds per Product (Week 1-2)

| Task | Description | Effort |
|------|-------------|--------|
| 2.1 | Create `product_data_feed.py` scheduler | 4 hours |
| 2.2 | Add product-level pricing scraper | 3 hours |
| 2.3 | Add product-level feature extraction | 3 hours |
| 2.4 | Add review aggregation per product | 4 hours |
| 2.5 | Create API endpoints for product data | 2 hours |
| 2.6 | Add product comparison matrix | 4 hours |

### Phase 3: New Product Detection (Week 2)

| Task | Description | Effort |
|------|-------------|--------|
| 3.1 | Create `new_product_detector.py` | 4 hours |
| 3.2 | Add press release product mention parser | 3 hours |
| 3.3 | Add G2/Capterra new listing monitor | 2 hours |
| 3.4 | Add job posting product name extractor | 2 hours |
| 3.5 | Create alert system for new products | 2 hours |

### Phase 4: Coverage Dashboard (Week 2)

| Task | Description | Effort |
|------|-------------|--------|
| 4.1 | Create coverage dashboard API | 3 hours |
| 4.2 | Add gap detection logic | 2 hours |
| 4.3 | Create frontend coverage widget | 3 hours |
| 4.4 | Add verification workflow | 2 hours |

---

## Total Estimated Effort

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 1: Discovery Crawler | 16 hours | Playwright |
| Phase 2: Data Feeds | 20 hours | Phase 1 |
| Phase 3: Detection System | 13 hours | Phase 1 |
| Phase 4: Coverage Dashboard | 10 hours | Phase 1-3 |
| **TOTAL** | **59 hours** | - |

---

## Expected Outcomes

After implementation:

1. **100% Product Coverage** - Every competitor's products discovered and tracked
2. **Live Data Feeds** - All product data refreshed on schedule
3. **New Product Alerts** - Notified within 24 hours of product launches
4. **Confidence Scoring** - Know exactly how reliable each data point is
5. **Gap Detection** - Automatic alerts when coverage drops

---

## Files to Create

| File | Purpose | Lines |
|------|---------|-------|
| `backend/product_discovery_crawler.py` | Crawl competitor websites for products | ~400 |
| `backend/product_data_feed.py` | Scheduled product data updates | ~300 |
| `backend/new_product_detector.py` | Monitor for new product launches | ~250 |
| `backend/routers/products.py` | API endpoints for product operations | ~350 |
| `frontend/product_coverage.js` | Coverage dashboard UI | ~200 |

---

## Approval Required

This plan requires:

1. [ ] Approval to proceed with implementation
2. [ ] Decision on G2/Capterra scraping (may violate ToS)
3. [ ] Budget for potential API costs (KLAS subscription?)
4. [ ] Priority relative to other pending work

---

**Created by**: Claude Opus 4.5
**Date**: January 26, 2026

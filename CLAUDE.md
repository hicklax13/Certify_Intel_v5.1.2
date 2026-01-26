# Certify Intel - Development Documentation

---

## AGENT START-OF-SESSION CHECKLIST

> **IMPORTANT**: Before starting any work, ALL agents MUST complete this checklist:

1. **READ `TODO_LIST.md`** - Review all pending tasks and priorities
2. **CHECK current task status** - Identify what needs to be done this session
3. **UPDATE task status** - Mark tasks as IN_PROGRESS when starting work
4. **MARK COMPLETED** - Update TODO_LIST.md when tasks are finished
5. **ADD NEW TASKS** - Document any new tasks discovered during work

**Primary Task File**: [`TODO_LIST.md`](TODO_LIST.md)

---

## Project Overview

**Certify Intel** is a production-ready Competitive Intelligence Platform designed to track, analyze, and counter 30+ competitors in the healthcare technology space. It provides a centralized, real-time dashboard for sales, product, and leadership teams.

**Version**: v5.0.7
**Status**: 🟢 Web Version Production-Ready | 🔴 Desktop App Blocked
**Last Updated**: January 26, 2026, 9:30 AM EST

---

## Quick Start (Web Version)

```bash
cd backend
python main.py
```

Then open: http://localhost:8000

**Default Login:** `admin@certifyhealth.com` / `certifyintel2024`

**If login fails, reset password:**
```bash
cd backend
python -c "
import os, hashlib
from dotenv import load_dotenv
from database import SessionLocal, User
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', '')
new_hash = hashlib.sha256(f'{SECRET_KEY}certifyintel2024'.encode()).hexdigest()
db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@certifyhealth.com').first()
if user: user.hashed_password = new_hash; db.commit(); print('Password reset!')
db.close()
"
```

---

## Current State Summary

### Completed Features (v5.0.7)
| Module | Status | Tasks |
|--------|--------|-------|
| Data Quality Enhancement (7 phases) | ✅ Complete | 10/10 |
| Data Refresh Enhancement (4 phases) | ✅ Complete | 10/10 |
| Gemini Hybrid AI (4 phases) | ✅ Complete | 21/21 |
| Live News Feed (4 phases) | ✅ Complete | 17/17 |
| Sales & Marketing Module (5 phases) | ✅ Complete | 26/26 |
| Cloud Deployment (v5.1.0) | ✅ Complete | 3/3 |
| Team Features (v5.2.0) | ✅ Complete | 3/3 |
| **TOTAL** | **96% Complete** | **80/83** |

### Pending/Blocked Features
| Module | Status | Reason |
|--------|--------|--------|
| Desktop App (v5.0.3) | 🔴 BLOCKED | PyInstaller .env path issue |

---

## Last 5 Tasks Completed

| # | Task ID | Description | Date |
|---|---------|-------------|------|
| 1 | 5.2.0-003 | Shared annotations - Team notes on competitors | Jan 26, 2026 |
| 2 | 5.2.0-002 | Role-based dashboards - Custom views per role | Jan 26, 2026 |
| 3 | 5.2.0-001 | Multi-user improvements - Team collaboration | Jan 26, 2026 |
| 4 | 5.1.0-003 | CI/CD pipeline - GitHub Actions & GitLab CI | Jan 26, 2026 |
| 5 | 5.1.0-002 | Cloud deployment guide (AWS/GCP/Azure) | Jan 26, 2026 |

---

## Next 5 Tasks To Complete

| # | Task ID | Description | Priority | Blocker |
|---|---------|-------------|----------|---------|
| 1 | 5.0.3-001 | Fix .env path in PyInstaller desktop app | HIGH | Technical - path resolution |
| 2 | 5.0.3-002 | Test installed desktop app end-to-end | HIGH | Depends on 5.0.3-001 |
| 3 | - | All other features complete | - | None |
| 4 | - | Production deployment | MEDIUM | None |
| 5 | 5.1.0-003 | Set up CI/CD pipeline | LOW | None |

---

## Latest Session - January 26, 2026

### Session #9: v5.0.7 Sales & Marketing Module Complete (9:00 AM)

**Feature Implementation: Sales & Marketing Module Phase 4 & 5**

Completed the final integration and AI enhancement phases:

✅ **Task 5.0.7-019: NewsMonitor Integration**
- Added `dimension_tags` field to NewsArticle dataclass
- Added `_tag_dimensions_batch()` method for batch article tagging
- Added `store_dimension_tags()` method to persist tags to database
- Auto-tags news articles with competitive dimensions

✅ **Task 5.0.7-020: Win/Loss Tracker Integration**
- Added `DimensionCorrelation` dataclass
- Added `dimension_factors` parameter to `log_deal()` method
- Added `_calculate_dimension_impact()` for correlation analysis
- Tracks which dimensions impact deal win rates

✅ **Task 5.0.7-021: Reports Integration**
- Created `DimensionBattlecardPDFGenerator` class
- Color-coded dimension scorecard in PDF export
- Evidence section by dimension
- Integrated with ReportManager

✅ **Task 5.0.7-022: Battlecard Page Widget**
- Added dimension widget to existing battlecardsPage
- Quick dimension overview with color-coded scores
- Links to full Sales & Marketing module

✅ **Task 5.0.7-023 to 5.0.7-025: AI Enhancement Endpoints**
- `/competitors/{id}/auto-score-reviews` - Auto-score from G2/Glassdoor reviews
- `/competitors/{id}/auto-update-from-news` - Update evidence from news articles
- `/news/auto-tag/{competitor_id}` - Enhanced auto-tagging

✅ **Task 5.0.7-026: End-to-End Testing**
- Created comprehensive test suite (`test_sales_marketing.py`)
- Unit tests for all dimension components
- Integration tests for NewsMonitor, WinLossTracker, Reports

**Files Created:**
- `backend/tests/test_sales_marketing.py` - ~300 lines

**Files Modified:**
- `backend/news_monitor.py` - Dimension tagging integration
- `backend/win_loss_tracker.py` - Dimension correlation
- `backend/reports.py` - DimensionBattlecardPDFGenerator
- `backend/routers/sales_marketing.py` - 3 new AI endpoints
- `frontend/index.html` - Dimension widget HTML
- `frontend/sales_marketing.js` - Widget functions
- `frontend/styles.css` - Widget CSS

---

### Session #8: v5.0.7 Sales & Marketing Module Phase 1-3 (7:00 AM)

**Feature Implementation: Sales & Marketing Module Core**

Created the comprehensive 9-dimension competitive evaluation framework:

✅ **Phase 1: Database Schema Extension (5 tasks)**
- Added 29 dimension fields to Competitor model
- Created CompetitorDimensionHistory, Battlecard, TalkingPoint, DimensionNewsTag tables

✅ **Phase 2: Backend Module Implementation (5 tasks)**
- Created `sales_marketing_module.py` (~600 lines)
- Created `dimension_analyzer.py` (~450 lines)
- Created `battlecard_generator.py` (~650 lines)
- Created `routers/sales_marketing.py` (~700 lines)

✅ **Phase 3: Frontend Implementation (8 tasks)**
- Full Sales & Marketing page with 4 tabs
- Dimension scorecard with 1-5 scoring
- Dynamic battlecard generation
- Radar chart comparison
- Talking points manager

**The 9 Competitive Dimensions:**
| ID | Name | Icon |
|---|------|------|
| product_packaging | Product Modules & Packaging | 📦 |
| integration_depth | Interoperability & Integration | 🔗 |
| support_service | Customer Support & Service | 🎧 |
| retention_stickiness | Retention & Product Stickiness | 🔒 |
| user_adoption | User Adoption & Ease of Use | 👥 |
| implementation_ttv | Implementation & Time to Value | ⏱️ |
| reliability_enterprise | Reliability & Enterprise Readiness | 🏢 |
| pricing_flexibility | Pricing & Commercial Flexibility | 💰 |
| reporting_analytics | Reporting & Analytics | 📊 |

---

### Session #7: v5.0.2 Gemini Hybrid AI Integration (5:00 AM)

**Feature Implementation: Google Gemini as Secondary AI Provider**

Implemented hybrid AI system for ~90% cost reduction on bulk tasks:

✅ **Task 5.0.2-001: Added Gemini API Dependencies**
- Added `google-generativeai>=0.8.0` to `backend/requirements.txt`

✅ **Task 5.0.2-002: Created Gemini Provider Module** (`backend/gemini_provider.py`)
- `GeminiConfig` - Configuration dataclass
- `AIResponse` - Unified response format for all providers
- `GeminiProvider` - Core provider with text/JSON generation
- `GeminiExtractor` - Data extraction compatible with GPTExtractor
- `AIRouter` - Task-based routing between providers

✅ **Task 5.0.2-003: Updated Environment Configuration** (`backend/.env.example`)
- Added `GOOGLE_AI_API_KEY`, `GOOGLE_AI_MODEL`
- Added `AI_PROVIDER` (openai/gemini/hybrid)
- Added `AI_BULK_TASKS`, `AI_QUALITY_TASKS` for routing
- Added `AI_FALLBACK_ENABLED` for automatic failover

✅ **Task 5.0.2-004: Created AI Router/Dispatcher**
- Task-based routing (bulk tasks → Gemini, quality tasks → OpenAI)
- Environment-configurable routing preferences
- Provider availability checking

✅ **Task 5.0.2-005: Updated extractor.py for Hybrid Support**
- Added `HybridExtractor` class with provider routing
- Updated `extract_competitor_data()` with `use_hybrid` parameter
- Added `get_extractor()` factory function

✅ **Task 5.0.2-006: Added Fallback Logic**
- Automatic fallback when primary provider fails
- Rate limit handling with provider switching
- Configurable via `AI_FALLBACK_ENABLED`

✅ **Task 5.0.2-007: Updated CLAUDE.md Documentation**
- Added Gemini configuration section
- Documented cost savings and model options

**Files Created:**
- `backend/gemini_provider.py` - ~450 lines (GeminiProvider, GeminiExtractor, AIRouter)

**Files Modified:**
- `backend/requirements.txt` - Added google-generativeai
- `backend/.env.example` - Added Gemini configuration section
- `backend/extractor.py` - Added HybridExtractor, updated imports
- `CLAUDE.md` - Added Gemini documentation
- `TODO_LIST.md` - Updated task statuses, added Live News Feed plan

**Model Pricing Reference:**
| Model | Input (per 1M) | Output (per 1M) |
|-------|---------------|-----------------|
| gemini-2.5-flash | $0.075 | $0.30 |
| gemini-2.5-flash-lite | $0.019 | $0.075 |
| gemini-2.5-pro | $1.25 | $10.00 |
| gpt-4o-mini | $0.15 | $0.60 |

---

### Session #6: Data Quality Enhancement - Phase 1 (12:00 AM)

**Feature Implementation: Source Attribution & Confidence Scoring**

Based on `IMPLEMENTATION_PLAN_DATA_QUALITY.md`, implemented the foundational data quality infrastructure:

✅ **Enhanced DataSource Model** (`backend/database.py`)
- Added 15+ new columns for confidence scoring and source attribution
- New fields: `source_reliability` (A-F Admiralty Code), `information_credibility` (1-6 scale)
- Added `confidence_score` (0-100), `confidence_level` (high/moderate/low)
- Added verification tracking: `is_verified`, `verified_by`, `verification_date`, `corroborating_sources`
- Added temporal tracking: `data_as_of_date`, `staleness_days`

✅ **New Database Models**
- `CompetitorProduct` - Track individual products per competitor with category/positioning
- `ProductPricingTier` - Healthcare-specific pricing models (per_visit, per_provider, percentage_collections)
- `ProductFeatureMatrix` - Feature comparison across products
- `CustomerCountEstimate` - Detailed customer count with verification and segmentation

✅ **Confidence Scoring Module** (`backend/confidence_scoring.py`)
- Implements Admiralty Code framework for intelligence reliability
- Source type definitions with default reliability ratings
- `calculate_confidence_score()` - Composite scoring algorithm
- `triangulate_data_points()` - Multi-source data verification
- SEC filings get 90/100 (high), website scrapes get 35/100 (low)

✅ **New API Endpoints** (`backend/main.py`)
- `GET /api/competitors/{id}/data-sources` - Enhanced source data with confidence
- `GET /api/data-quality/low-confidence?threshold=40` - Find unverified data
- `GET /api/data-quality/confidence-distribution` - Overall data quality stats
- `POST /api/sources/set-with-confidence` - Set source with auto-scoring
- `POST /api/sources/verify/{id}/{field}` - Mark data as verified
- `GET /api/source-types` - Available source types with reliability ratings
- `POST /api/data-quality/recalculate-confidence` - Batch recalculate scores

✅ **Enhanced Scraper Integration**
- `run_scrape_job_with_progress()` now creates DataSource records with confidence scoring
- `_update_data_source_with_confidence()` helper function added
- All scraped data automatically tracked with source attribution

**Files Created:**
- `backend/confidence_scoring.py` - New module (280 lines)

**Files Modified:**
- `backend/database.py` - Enhanced DataSource + 4 new models
- `backend/main.py` - New imports + 8 new API endpoints + scraper integration

---

### Session #6 (continued): Data Quality Enhancement - Phase 2 (12:30 AM)

**Feature Implementation: Multi-Source Data Triangulation**

✅ **DataTriangulator Module** (`backend/data_triangulator.py`)
- Cross-references data from multiple independent sources
- Authority-based source selection (SEC > API > Manual > Website)
- Automatic agreement detection (20% tolerance for numeric values)
- Source data collection from:
  - Website scrapes (existing DataSource records)
  - SEC EDGAR filings (for public companies via yfinance)
  - News article mentions (pattern matching for customer counts)
  - Manual verified entries

✅ **Triangulation API Endpoints**
- `POST /api/triangulate/{competitor_id}` - Triangulate all key fields for a competitor
- `POST /api/triangulate/{competitor_id}/{field_name}` - Triangulate specific field
- `POST /api/triangulate/all` - Background job to triangulate all competitors
- `GET /api/triangulation/status` - Overview of verification status

✅ **Automatic Triangulation on Scrape**
- After each scrape completes, triangulation runs automatically
- Key fields verified: customer_count, employee_count, base_price
- Confidence scores updated based on source agreement
- Verified flag set when multiple sources corroborate

**Test Results:**
```
Sources: website_scrape (3000+), sec_filing (3500), news_article (3200)
Result: Best value=3500 from SEC filing
Confidence: 100/100 (high), 3 sources agreeing
```

**Files Created:**
- `backend/data_triangulator.py` - New module (420 lines)

**Files Modified:**
- `backend/main.py` - Added triangulation imports, 5 new endpoints, scraper integration

---

### Session #6 (continued): Data Quality Enhancement - Phase 3 (1:00 AM)

**Feature Implementation: Product-Specific Pricing Structure**

✅ **Product & Pricing API Endpoints** (`backend/main.py`)
- `GET /api/competitors/{id}/products` - Get all products with pricing tiers
- `POST /api/products` - Create new product for a competitor
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product and associated pricing/features

✅ **Pricing Tier Management**
- `GET /api/products/{id}/pricing-tiers` - Get pricing tiers for a product
- `POST /api/pricing-tiers` - Create pricing tier with confidence scoring
- `PUT /api/pricing-tiers/{id}` - Update pricing tier
- `DELETE /api/pricing-tiers/{id}` - Delete pricing tier
- `POST /api/pricing-tiers/{id}/verify` - Mark pricing as verified

✅ **Pricing Comparison & Models**
- `GET /api/pricing/compare?category=X&pricing_model=Y` - Compare pricing across competitors
- `GET /api/pricing/models` - List healthcare pricing model types (per_visit, per_provider, percentage_collections, etc.)

✅ **Feature Matrix Endpoints**
- `GET /api/products/{id}/features` - Get features grouped by category
- `POST /api/features` - Add feature to product
- `DELETE /api/features/{id}` - Remove feature
- `GET /api/features/compare?category=X` - Cross-competitor feature comparison

✅ **GPT-Powered Product Extraction** (`backend/extractor.py`)
- `extract_products_and_pricing()` - Extract multiple products and pricing tiers from content
- `extract_feature_matrix()` - Extract features organized by category
- Healthcare-specific pricing model detection
- `POST /api/competitors/{id}/extract-products` - Trigger GPT extraction and store results
- `POST /api/products/{id}/extract-features` - Extract features for a product

✅ **Pydantic Models for Validation**
- `ProductCreate`, `ProductResponse` - Product request/response schemas
- `PricingTierCreate`, `PricingTierResponse` - Pricing tier schemas
- `FeatureMatrixCreate` - Feature creation schema

**Healthcare Pricing Models Supported:**
| Model | Description | Example |
|-------|-------------|---------|
| `per_visit` | Per patient encounter | $3.00/visit |
| `per_provider` | Monthly per provider | $400/provider/month |
| `per_location` | Per practice location | $1,500/location/month |
| `subscription_flat` | Fixed monthly fee | $299/month |
| `percentage_collections` | % of collected revenue | 4-8% of collections |
| `custom_enterprise` | Negotiated pricing | Contact Sales |

**Files Modified:**
- `backend/main.py` - Added 15+ new endpoints for product/pricing management (~450 lines)
- `backend/extractor.py` - Added `extract_products_and_pricing()` and `extract_feature_matrix()` methods (~180 lines)

---

### Session #6 (continued): Data Quality Enhancement - Phase 4 (2:00 AM)

**Feature Implementation: Customer Count Verification System**

✅ **Customer Count Pydantic Models** (`backend/main.py`)
- `CustomerCountCreate` - Create new customer count estimates
- `CustomerCountResponse` - Full response with verification and confidence data
- `CustomerCountVerifyRequest` - Request schema for verification with additional sources

✅ **Customer Count CRUD Endpoints**
- `GET /api/competitors/{id}/customer-counts` - Get all customer count estimates for a competitor
- `GET /api/competitors/{id}/customer-count/latest` - Get most recent verified count
- `POST /api/customer-counts` - Create new customer count estimate with auto-confidence scoring
- `PUT /api/customer-counts/{id}` - Update existing estimate
- `DELETE /api/customer-counts/{id}` - Delete estimate

✅ **Customer Count Verification**
- `POST /api/customer-counts/{id}/verify` - Verify count with additional sources
- Automatic source agreement scoring (0-1 scale)
- Confidence recalculation with corroboration bonus
- Verification method tracking (sec_filing, triangulation, sales_intel, manual)

✅ **Customer Count Triangulation**
- `POST /api/competitors/{id}/triangulate-customer-count` - Multi-source triangulation
- Collects data from: website scrapes, SEC filings, existing estimates
- Creates new CustomerCountEstimate with triangulated result
- Extracts numeric values from display strings ("3,000+" → 3000, type: "minimum")

✅ **Customer Count Comparison & History**
- `GET /api/customer-counts/compare` - Compare counts across all competitors
- `GET /api/customer-counts/history/{id}` - Historical trend with growth calculation
- `GET /api/customer-counts/units` - Available count unit types with descriptions

**Customer Count Unit Types:**
| Unit | Description |
|------|-------------|
| `healthcare_organizations` | Distinct hospital/clinic/practice entities |
| `providers` | Individual physicians or clinicians |
| `locations` | Physical practice sites or facilities |
| `users` | All user accounts (staff, admins, etc.) |
| `lives_covered` | Patient lives managed through platform |
| `encounters` | Annual patient encounters processed |
| `beds` | Licensed hospital beds served |

**Files Modified:**
- `backend/main.py` - Added 10+ new endpoints for customer count management (~400 lines)

---

### Session #6 (continued): Data Quality Enhancement - Phase 5 (2:30 AM)

**Feature Implementation: Enhanced Scraper with Source Tracking**

✅ **New Data Classes** (`backend/extractor.py`)
- `FieldSourceInfo` - Source metadata for individual extracted fields
- `ExtractedDataWithSource` - Enhanced extraction result with full provenance tracking
- Tracks: source_page, source_url, extraction_context, per-field confidence

✅ **EnhancedGPTExtractor Class** (`backend/extractor.py`)
- Multi-page extraction with source tracking
- Confidence scoring matrix based on page type + field relevance
- Context snippet extraction showing where values were found
- Converts results to DataSource records for database storage

✅ **Confidence Scoring Matrix**
| Page Type | Field | Base Confidence |
|-----------|-------|----------------|
| pricing | base_price | 75 |
| pricing | pricing_model | 75 |
| about | customer_count | 65 |
| about | employee_count | 65 |
| about | year_founded | 80 |
| customers | key_customers | 75 |
| features | key_features | 70 |
| homepage | (default) | 50 |

✅ **New API Endpoints**
- `POST /api/scrape/enhanced/{competitor_id}` - Run enhanced scrape with source tracking
- `GET /api/scrape/enhanced/{competitor_id}/sources` - Get all sources from latest scrape

**Enhanced Scrape Features:**
- Scrapes multiple pages (homepage, pricing, about, features, customers)
- Tracks which page each data point came from
- Calculates confidence based on field/page relevance
- Stores context snippets showing extraction source
- Respects manual corrections (locked fields)
- Runs triangulation after extraction

**Files Modified:**
- `backend/extractor.py` - Added FieldSourceInfo, ExtractedDataWithSource, EnhancedGPTExtractor (~300 lines)
- `backend/main.py` - Added enhanced scrape endpoints (~200 lines)

---

### Session #6 (continued): Data Quality Enhancement - Phase 6 (3:00 AM)

**Feature Implementation: UI Enhancements - Confidence Indicators & Source Attribution Display**

✅ **Confidence Indicator CSS Styles** (`frontend/styles.css`)
- Added 350+ lines of new CSS for confidence indicators
- Confidence badges with color-coded levels (high/moderate/low)
- Animated tooltip displays with confidence scores
- Confidence bar visualizations for tables
- Source type badges with category-specific colors
- Data Sources modal styling with responsive design

✅ **Data Sources Modal** (`frontend/index.html`)
- New modal component for viewing source attribution
- Table displaying all data fields with:
  - Field name and current value
  - Source type badge (SEC, API, Website, Manual, etc.)
  - Confidence bar with percentage score
  - Verification status indicator
  - Last updated timestamp
- Legend explaining confidence levels
- Link to run enhanced scrape if no sources available

✅ **Enhanced createSourcedValue Function** (`frontend/app_v2.js`)
- Now displays confidence indicator next to each value
- Color-coded indicator (green/yellow/red) based on confidence level
- Tooltip showing exact confidence score and level
- Support for additional source types (sec_filing, api_verified, etc.)
- Default confidence scores based on source type when not specified

✅ **New JavaScript Functions** (`frontend/app_v2.js`)
- `viewDataSources(competitorId)` - Opens Data Sources modal for a competitor
- `renderDataSourcesTable(sources)` - Renders the sources table HTML
- `closeDataSourcesModal(event)` - Modal close handler
- `createConfidenceIndicator(score, level, sourceType)` - Creates confidence badge HTML
- `getConfidenceLevelFromScore(score)` - Converts numeric score to level
- `formatFieldName(field)` - Formats field names for display
- `formatSourceType(type)` - Formats source type labels
- `truncateText(text, maxLength)` - Truncates long text with ellipsis
- `triggerEnhancedScrape(competitorId)` - Triggers enhanced scrape from modal

✅ **UI Updates**
- Added "📋 Sources" button to competitor cards
- Added source view icon to Top Threats table
- Confidence indicators appear next to customer count, pricing, employees, etc.

**Confidence Indicator Visual Reference:**
| Indicator | Level | Score Range | Description |
|-----------|-------|-------------|-------------|
| ✓ (green) | High | 70-100 | Verified from authoritative sources |
| ~ (yellow) | Moderate | 40-69 | Credible but not fully verified |
| ! (red) | Low | 0-39 | Unverified marketing claims |
| ? (gray) | Unknown | N/A | No confidence data available |

**Source Type Badge Colors:**
| Type | Color | Background |
|------|-------|------------|
| SEC Filing | Green | #dcfce7 |
| API Verified | Blue | #dbeafe |
| Website Scrape | Yellow | #fef3c7 |
| Manual Entry | Purple | #f3e8ff |
| News Article | Red | #fee2e2 |
| KLAS Report | Cyan | #cffafe |

**Files Modified:**
- `frontend/styles.css` - Added ~350 lines of confidence/source styling
- `frontend/index.html` - Added Data Sources Modal HTML
- `frontend/app_v2.js` - Updated createSourcedValue + added 150+ lines of new functions

---

### Session #6 (continued): Data Quality Enhancement - Phase 7 (4:00 AM)

**Feature Implementation: Data Quality Dashboard**

✅ **New API Endpoint** (`backend/main.py`)
- `GET /api/data-quality/overview` - Comprehensive data quality metrics
  - Total competitors and data points
  - Confidence distribution (high/moderate/low/unscored)
  - Verification rate
  - Staleness rate (90-day threshold)
  - Key field coverage with average confidence per field
  - Source type breakdown with data point counts
  - Competitor quality rankings sorted by average confidence

✅ **Enhanced Data Quality Page** (`frontend/index.html`)
- New confidence distribution stat cards (High, Moderate, Low, Verification Rate)
- Confidence Distribution doughnut chart
- Source Type Breakdown grid with visual cards
- Field Coverage with Confidence analysis grid
- Competitor Quality Ranking table with tier filtering
- "Recalculate Scores" button for batch confidence recalculation

✅ **New CSS Styles** (`frontend/styles.css`)
- Added ~280 lines of Phase 7 styling
- `.confidence-stats-grid` - 4-column layout for confidence cards
- `.source-type-card` - Visual cards for each source type
- `.field-confidence-card` - Dual-bar display (coverage + confidence)
- `.competitor-quality-row` - Ranked list with medals for top 3
- Responsive adjustments for mobile

✅ **New JavaScript Functions** (`frontend/app_v2.js`)
- `loadDataQualityOverview()` - Fetches and displays overview data
- `updateConfidenceCards(distribution)` - Updates confidence stat cards
- `renderConfidenceDistributionChart(distribution)` - Doughnut chart with Chart.js
- `renderSourceTypeBreakdown(sourceTypes)` - Source type grid with icons
- `renderFieldConfidenceAnalysis(fieldCoverage)` - Field analysis grid
- `renderCompetitorQualityRanking(scores)` - Competitor ranking list
- `filterQualityRanking()` - Filter by quality tier
- `filterByConfidence(level)` - View data by confidence level
- `recalculateAllConfidence()` - Batch recalculate all scores

**Data Quality Dashboard Sections:**
| Section | Description |
|---------|-------------|
| Confidence Distribution Cards | High/Moderate/Low counts with percentages |
| Confidence Distribution Chart | Doughnut visualization of distribution |
| Source Type Breakdown | Grid of source types with avg confidence |
| Field Coverage Analysis | Coverage % and avg confidence per key field |
| Competitor Quality Ranking | Ranked list with quality tier badges |

**Quality Tiers:**
| Tier | Avg Confidence | Badge Color |
|------|---------------|-------------|
| Excellent | 70+ | Green |
| Good | 50-69 | Blue |
| Fair | 30-49 | Yellow |
| Poor | <30 | Red |

**Files Modified:**
- `backend/main.py` - Added `/api/data-quality/overview` endpoint (~100 lines)
- `frontend/index.html` - Enhanced Data Quality page HTML (~80 lines)
- `frontend/styles.css` - Added Phase 7 dashboard styles (~280 lines)
- `frontend/app_v2.js` - Added Phase 7 JavaScript functions (~250 lines)

**Data Quality Enhancement Plan Status:** ✅ ALL 7 PHASES COMPLETE

---

### Session #5: CSS Fix & Data Refresh Planning (10:30 PM)

**Bug Fixes:**

✅ **Dashboard Stats CSS Fix**
- Fixed CSS specificity issue causing stat card numbers to be invisible
- Root cause: `.stat-value` rule at line 2967 in styles.css set `color: var(--text-white)` (white on white)
- Solution: Scoped rule to `.complete-stats .stat-value` so it only applies to refresh complete modal
- Dashboard now displays Total Competitors, High/Medium/Low Threat counts correctly

✅ **Refresh Description Text**
- Fixed two-line text wrapping in "Data is automatically refreshed..." message
- Changed `max-width: 400px` to `white-space: nowrap` in `.refresh-description` class

**Planning Documents Created:**

📋 **IMPLEMENTATION_PLAN_DATA_REFRESH.md** - Comprehensive 4-phase plan for:
- Phase 1: Inline progress bar on Dashboard (not modal)
- Phase 2: Enhanced backend tracking with field-level change details
- Phase 3: AI-powered refresh summary generation
- Phase 4: Refresh history persistence and audit trail

**Files Modified This Session:**
- `frontend/styles.css` - CSS specificity fixes (lines 661-666, 2962-2971)
- `IMPLEMENTATION_PLAN_DATA_REFRESH.md` - New file created

---

### Session #4: C-Suite Meeting Prep - User Prompts & AI Progress (9:11 PM)

**Bug Fixes:**

✅ **Dashboard Stats Fix**
- Removed duplicate `/api/dashboard/stats` endpoint that was causing conflicts
- Added null-safety checks in frontend `updateStatsCards()` function
- Dashboard threat level counts now display correctly

**New Features:**

✅ **User-Specific Prompt Management**
- New `UserSavedPrompt` database model for per-user prompt storage
- Full CRUD API endpoints: `GET/POST/PUT/DELETE /api/user/prompts`
- Updated "Edit AI Instructions" modal with:
  - Dropdown to select from saved prompts
  - "Save As New" button with custom naming
  - "Load" and "Delete" buttons for saved prompts
  - "Load Default" button to reset to system default
- Prompts are private to each user account

✅ **AI Summary Progress Bar**
- Real-time progress modal during AI summary generation
- 5-step progress tracking with visual indicators
- Elapsed time display
- Progress polling every 500ms
- Backend progress tracking via `/api/analytics/summary/progress`

**Code Cleanup:**

✅ Removed duplicate endpoints in main.py (dashboard/stats, competitors, scrape/all)
✅ Consolidated endpoint definitions

---

### Session #3: Multi-User System & Activity Logging

**Features Implemented:**

✅ **Multi-User Account System**
- User registration endpoint (`/api/auth/register`)
- Registration form on login page with toggle
- Personal data isolation (AI prompts, Win/Loss deals per user)
- Shared competitor data across all users
- Admin "Invite Team Member" option in user dropdown

✅ **Activity Logging & Audit Trail**
- All data changes logged with username and timestamp
- "Refresh Data" button logs who triggered it
- New `ActivityLog` and `UserSettings` database tables
- `/api/activity-logs` endpoint for viewing all user actions
- Change logs shared across all users

✅ **User-Specific Settings**
- Notification preferences stored per user
- Schedule settings stored per user
- Settings persisted to database (not in-memory)

✅ **UI Improvements**
- Sidebar collapse button redesigned as "tab handle"
- Vertical pill shape with grip line and arrow indicator
- Smoother hover/click animations

### Session #2: UI/UX Enhancements

✅ **Notification Button** - Off-white (#F5F5F5), 40x40px, larger bell icon
✅ **Date/Time Format** - Shows "Sun, Jan 25, 2026, 03:08 PM EST" with timezone
✅ **AI Summary Icon** - Green ChatGPT-style logo
✅ **AI Summary Collapsible** - Toggle button to expand/collapse
✅ **Sidebar Collapsible** - Tab handle button, collapses to 70px icons-only mode
✅ **AI Model** - Updated to `gpt-4.1`

### Session #1: Core Fixes

✅ Fixed admin login (password hash)
✅ Styled buttons (secondary, user avatar, notification)
✅ Prompt caching for instant loading
✅ Added "Last Data Refresh" indicator
✅ Added `python main.py` uvicorn startup

---

## Complete Feature Inventory (Current State as of v5.0.1)

### Dashboard Page
| Feature | Status | Description |
|---------|--------|-------------|
| Threat Level Stats Cards | ✅ Working | Shows Total, High, Medium, Low competitor counts |
| AI Executive Summary | ✅ Working | GPT-4 generated competitive analysis |
| AI Summary Progress Modal | ✅ Working | 5-step real-time progress during generation |
| AI Chat Interface | ✅ Working | Ask follow-up questions about competitors |
| Edit AI Instructions | ✅ Working | Customize AI prompts per user |
| User Saved Prompts | ✅ Working | Save, load, delete personal prompts |
| Last Data Refresh Indicator | ✅ Working | Shows timestamp of last refresh |
| Refresh Data Button | ✅ Working | Triggers scrape for all competitors |
| Refresh Progress Modal | ✅ Working | Shows scrape progress (modal-based) |
| Threat Distribution Chart | ✅ Working | Pie chart of threat levels |
| Pricing Models Chart | ✅ Working | Bar chart of pricing strategies |

### Competitors Page
| Feature | Status | Description |
|---------|--------|-------------|
| Competitor List/Grid | ✅ Working | View all competitors with key data |
| Add Competitor | ✅ Working | Create new competitor profiles |
| Edit Competitor | ✅ Working | Update competitor information |
| Delete Competitor | ✅ Working | Soft delete with confirmation |
| Individual Refresh | ✅ Working | Scrape single competitor |
| Competitor Insights | ✅ Working | AI analysis of specific competitor |
| Battlecard View | ✅ Working | Sales-ready competitor summary |
| Public/Private Badge | ✅ Working | Shows stock ticker for public companies |

### Compare Page
| Feature | Status | Description |
|---------|--------|-------------|
| Side-by-Side Comparison | ✅ Working | Compare 2-4 competitors |
| Feature Matrix | ✅ Working | Grid of capabilities |
| Export Comparison | ✅ Working | Download as PDF/Excel |

### Change Log Page
| Feature | Status | Description |
|---------|--------|-------------|
| Activity Timeline | ✅ Working | Shows all data changes |
| User Attribution | ✅ Working | Who made each change |
| Filter by Competitor | ✅ Working | View changes for specific competitor |
| Filter by Date | ✅ Working | Date range filtering |

### Analytics & Reports Page
| Feature | Status | Description |
|---------|--------|-------------|
| Market Positioning | ✅ Working | Bubble chart visualization |
| Win/Loss Tracking | ✅ Working | Record competitive deals |
| Export to Excel | ✅ Working | Full data export |
| PDF Battlecards | ✅ Working | Generate sales materials |

### Data Quality Page
| Feature | Status | Description |
|---------|--------|-------------|
| Completeness Score | ✅ Working | % of fields populated |
| Stale Records | ✅ Working | Identifies outdated data |
| Quality Tier Distribution | ✅ Working | Chart of data quality |

### Settings Page
| Feature | Status | Description |
|---------|--------|-------------|
| Notification Preferences | ✅ Working | Per-user notification settings |
| Schedule Settings | ✅ Working | Per-user schedule preferences |
| API Keys Management | ✅ Working | Configure external services |

### Authentication & Users
| Feature | Status | Description |
|---------|--------|-------------|
| Login | ✅ Working | JWT-based authentication |
| User Registration | ✅ Working | Self-service signup |
| Role-Based Access | ✅ Working | Admin, Analyst, Viewer roles |
| Activity Logging | ✅ Working | All actions logged with user |
| Invite Team Member | ✅ Working | Admin can invite users |

### Data Collection (Scrapers)
| Feature | Status | Description |
|---------|--------|-------------|
| Website Scraping | ✅ Working | Playwright-based content extraction |
| SEC Edgar | ✅ Working | Public company filings |
| USPTO Patents | ✅ Working | Patent searches |
| Glassdoor Reviews | ✅ Working | Employee sentiment |
| Indeed Jobs | ✅ Working | Hiring patterns |
| App Store Reviews | ✅ Working | Product ratings |
| News Monitoring | ✅ Working | Google News integration |
| Discovery Agent | ✅ Working | Find new competitors |

### Known Limitations
| Feature | Status | Issue |
|---------|--------|-------|
| Desktop App | 🔴 Blocked | .env path not found after PyInstaller |
| Inline Refresh Progress | 🟡 Planned | Currently uses modal, not inline |
| AI Refresh Summary | 🟡 Planned | No AI analysis of refresh results |
| Gemini Integration | 🟡 Planned | OpenAI only currently |

---

## Data Refresh Enhancement Plan Summary

**Document**: `IMPLEMENTATION_PLAN_DATA_REFRESH.md`

### Phase 1: Inline Progress Bar (Priority: HIGH)
Replace modal-based progress with embedded Dashboard component showing:
- Real-time percentage and progress bar
- Current competitor being scanned
- Live feed of changes as they're detected

### Phase 2: Enhanced Backend Tracking (Priority: HIGH)
Expand `scrape_progress` object to include:
- Field-level change details (old value → new value)
- Recent changes array for live display
- Error tracking

### Phase 3: AI-Powered Refresh Summary (Priority: HIGH)
New `/api/scrape/generate-summary` endpoint that:
- Uses GPT-4 to analyze all detected changes
- Provides actionable insights ("2 competitors raised prices")
- Displays in enhanced completion modal

### Phase 4: Refresh History (Priority: MEDIUM)
New `RefreshSession` database model to:
- Persist each refresh session with results
- Store AI summaries for audit trail
- Enable viewing past refresh history

---

## Next 10 Immediate Tasks (For Next Session)

| # | Task ID | Task | Priority | Est. Time |
|---|---------|------|----------|-----------|
| 1 | 5.0.1-023 | Add inline progress HTML to Dashboard | HIGH | 15 min |
| 2 | 5.0.1-024 | Add inline progress CSS styles | HIGH | 15 min |
| 3 | 5.0.1-025 | Update JS for inline progress display | HIGH | 30 min |
| 4 | 5.0.1-026 | Expand backend scrape_progress object | HIGH | 15 min |
| 5 | 5.0.1-027 | Track field-level changes in scraper | HIGH | 30 min |
| 6 | 5.0.1-028 | Add /api/scrape/session endpoint | MEDIUM | 15 min |
| 7 | 5.0.1-029 | Add /api/scrape/generate-summary endpoint | HIGH | 30 min |
| 8 | 5.0.1-030 | Update refresh complete modal with AI summary | HIGH | 20 min |
| 9 | 5.0.1-031 | Add RefreshSession database model | MEDIUM | 10 min |
| 10 | 5.0.1-032 | Test full refresh flow end-to-end | HIGH | 20 min |

**Total Estimated Time**: ~3.5 hours

---

## Configuration

Copy `backend/.env.example` to `backend/.env` and configure:

```env
# Required
SECRET_KEY=your-secret-key-here

# Optional - AI Features (OpenAI)
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4.1

# Optional - AI Features (Gemini) - v5.0.2+
# Get key: https://aistudio.google.com/app/apikey
GOOGLE_AI_API_KEY=your-gemini-key
GOOGLE_AI_MODEL=gemini-2.5-flash

# AI Provider Configuration - v5.0.2+
# Options: "openai", "gemini", or "hybrid" (recommended)
AI_PROVIDER=hybrid

# Task-specific routing (only used when AI_PROVIDER=hybrid)
AI_BULK_TASKS=gemini      # Cheaper for high-volume operations
AI_QUALITY_TASKS=openai   # Better quality for summaries
AI_FALLBACK_ENABLED=true  # Auto-switch on failure

# Optional - Enhanced Search
GOOGLE_API_KEY=your-google-key
GOOGLE_CX=your-search-engine-id

# Desktop Mode
DESKTOP_MODE=false
ADMIN_EMAIL=admin@yourcompany.com
```

See `backend/.env.example` for full configuration options.

### Gemini Integration (v5.0.2+)

The hybrid AI provider system allows using both OpenAI and Google Gemini:

| Provider | Best For | Cost (per 1M tokens) |
|----------|----------|---------------------|
| OpenAI GPT-4 | Executive summaries, complex reasoning | ~$5-15 |
| Gemini Flash | Bulk extraction, data processing | ~$0.075 |
| Gemini Flash Lite | High-volume classification | ~$0.019 |
| Gemini Pro | Complex analysis (when needed) | ~$1.25 |

**Cost Savings**: ~90% reduction on bulk operations when using hybrid mode.

**Files**:
- `backend/gemini_provider.py` - Gemini provider, extractor, and AI router
- `backend/extractor.py` - HybridExtractor class for automatic routing

---

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.9+) with Uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **API**: RESTful with 40+ endpoints
- **AI/ML**: OpenAI GPT-4.1, LangChain
- **Authentication**: JWT tokens with SHA256 hashing

### Frontend
- **Architecture**: Single Page Application (SPA)
- **Languages**: HTML5, Vanilla JavaScript (ES6+), CSS3
- **Visualization**: Chart.js
- **Design**: Glassmorphism, dark-mode aesthetic

### Desktop Application
- **Framework**: Electron
- **Build Tools**: electron-builder, PyInstaller
- **Platforms**: Windows (.exe), macOS (.dmg)

---

## Project Structure

```
Project_Intel_v5.0.1/
├── backend/                    # FastAPI Python backend
│   ├── main.py                # App entry point
│   ├── database.py            # SQLAlchemy models
│   ├── api_routes.py          # Additional API routes
│   ├── extended_features.py   # Auth, caching
│   ├── analytics.py           # Data analysis
│   ├── reports.py             # PDF/Excel generation
│   ├── [scrapers]             # 15+ data collectors
│   ├── .env.example           # Configuration template
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # Web UI SPA
│   ├── index.html             # Main dashboard
│   ├── login.html             # Authentication
│   ├── app_v2.js              # Core JavaScript
│   └── styles.css             # Styling
│
├── desktop-app/               # Electron wrapper
│   ├── electron/              # Electron files
│   └── package.json           # Build config
│
├── docs/                      # Documentation
├── client_docs/               # Client materials
└── CLAUDE.md                  # This file
```

---

## Core Features

### 1. Real-Time Intelligence
- Automated tracking of 30+ data points per competitor
- Change detection and alerting
- Discovery Agent ("Certify Scout") for emerging threats

### 2. Multi-Source Data Collection
- SEC Edgar, USPTO Patents
- Glassdoor, Indeed, LinkedIn
- HIMSS, KLAS, App Stores
- News monitoring

### 3. Advanced Analytics
- AI-generated executive summaries
- Market positioning visualization
- Feature gap analysis
- Win/Loss tracking

### 4. Multi-User System
- User registration and authentication
- Role-based access (Admin, Analyst, Viewer)
- Personal settings and prompts
- Shared competitor data
- Activity audit trail

### 5. Reporting
- Excel exports with data validation
- PDF battlecards
- JSON export for Power BI

---

## Data Model

| Data Type | Visibility |
|-----------|------------|
| Competitors | Shared - all users see same data |
| Knowledge Base | Shared - all users see same data |
| Activity Logs | Shared - all users see who changed what |
| AI Prompts | Personal - each user has own customization |
| Win/Loss Deals | Personal - each user tracks their own |
| Settings | Personal - notification/schedule preferences |

---

## API Endpoints (Key)

### Authentication
- `POST /token` - Login
- `POST /api/auth/register` - Register new user
- `GET /api/auth/me` - Current user info

### Competitors
- `GET /api/competitors` - List all
- `POST /api/competitors` - Create new
- `PUT /api/competitors/{id}` - Update
- `DELETE /api/competitors/{id}` - Delete

### Activity & Audit
- `GET /api/activity-logs` - View all activity
- `GET /api/activity-logs/summary` - Activity summary
- `GET /api/changes/history/{id}` - Competitor change history

### Settings (User-Specific)
- `GET/POST /api/settings/notifications`
- `GET/POST /api/settings/schedule`

---

## Build Commands

### Run Development Server
```bash
cd backend
python main.py
```

### Build Desktop App (Windows)
```bash
cd backend
python -m PyInstaller certify_backend.spec --clean --noconfirm

cd ../desktop-app
npm run build:win
```

---

## Known Issues

### Desktop App (v2.0.1)
- **Issue**: Backend server fails to start after installation
- **Cause**: PyInstaller extracts to temp folder, .env not found
- **Status**: Blocked - needs path resolution fix

---

## Next Steps

### IMMEDIATE: v5.0.1 - Data Refresh Enhancement
**See**: `IMPLEMENTATION_PLAN_DATA_REFRESH.md`

1. Add inline progress bar to Dashboard (Phase 1)
2. Enhance backend change tracking (Phase 2)
3. Add AI-powered refresh summary (Phase 3)
4. Persist refresh history (Phase 4)

### v5.0.2 - Gemini Hybrid Integration
1. Add `google-generativeai` to requirements
2. Create `gemini_provider.py` module
3. AI router for hybrid model selection
4. ~90% cost reduction on bulk tasks

### v5.0.3 - Desktop App Fix
1. Fix PyInstaller .env path loading
2. End-to-end testing

### v5.1.0 - Cloud Deployment
1. Docker production config
2. AWS/GCP/Azure deployment guide

---

## Contributing

1. Create feature branch from `master`
2. Make changes with clear commit messages
3. Test locally with `python main.py`
4. Create pull request

**Security Note**: Never commit `.env` files or API keys. Use `.env.example` as template.

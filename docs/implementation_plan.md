# Certify Health Intel - Remaining Tasks Implementation Plan

**Date**: January 17, 2026  
**MVP Deadline**: February 9, 2026  
**Days Remaining**: 23 days

---

## Current State

The project has a **functional MVP** with:

- ✅ FastAPI backend with SQLite database
- ✅ Web dashboard (HTML/JS/CSS)
- ✅ Discovery agent (seed list mode)
- ✅ Report generation (PDF/Excel)
- ✅ Alert system (email/Slack/Teams/SMS)
- ✅ Scheduler for automated refreshes

---

## High Priority Tasks for MVP Completion

### 1. 🔴 Expand Competitor Database to 40+ Companies

**Current State**: ~10-15 competitors in database  
**Target**: 40+ competitors with complete data

#### Proposed Changes

##### [MODIFY] [seed_db.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/seed_db.py)

- Add 25-30 additional healthcare IT competitors
- Include known companies: Kyruus, Notable Health, Klara, Mend, Relatient, etc.
- Ensure all 32 data fields are populated

**Effort**: ~2 hours

---

### 2. 🔴 Enable Live Discovery Search

**Current State**: Using hardcoded seed list in `discovery_agent.py`  
**Target**: Real DuckDuckGo API calls for autonomous discovery

#### Proposed Changes

##### [MODIFY] [discovery_agent.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/discovery_agent.py)

- Replace seed list simulation with actual DuckDuckGo search
- Add rate limiting to avoid API blocks
- Implement search query rotation

**Effort**: ~1 hour

---

### 3. 🔴 Enable OpenAI GPT-4 Qualification

**Current State**: AI qualification logic is commented out  
**Target**: Use GPT-4 for intelligent competitor scoring

#### Proposed Changes

##### [MODIFY] [discovery_agent.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/discovery_agent.py)

- Uncomment OpenAI API integration
- Add fallback for when API key is not available
- Implement cost controls (token limits)

**Effort**: ~30 minutes

---

### 4. 🟡 Configure Production Email Alerts

**Current State**: SMTP credentials not configured  
**Target**: Working email alerts for competitor changes

#### Proposed Changes

##### [MODIFY] [.env](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/.env)

- Configure SMTP_HOST, SMTP_USER, SMTP_PASSWORD
- Set ALERT_TO_EMAILS for recipient list
- Test daily digest and weekly summary

**Effort**: ~30 minutes (requires SMTP credentials)

---

### 5. 🟡 Celery Task Queue Integration

**Current State**: TODO comments in code  
**Target**: Background processing for scraping jobs

#### Proposed Changes

##### [MODIFY] [requirements.txt](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/requirements.txt)

- Add celery and redis dependencies

##### [NEW] [tasks.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/tasks.py)

- Create Celery app configuration
- Define async scrape and extract tasks

**Effort**: ~2 hours

---

### 7. 🟢 Frontend Implementation & Branding (Current Phase)

**Goal**: Clone Certify Health's branding and build visualizations for the 10 new data sources.

#### Branding Specification

- **Primary Color**: `#3A95ED` (Certify Blue)
- **Secondary Color**: `#122753` (Navy)
- **Font**: 'Poppins', sans-serif
- **UI Style**: Minimal rounding (3px), clean shadows, two-tone cards.

#### Proposed Changes

1. **Global Styles**:
   - Update `frontend/index.css` with CSS variables.
   - Import 'Poppins' from Google Fonts.
   - Refactor buttons and cards to match branding.

2. **New Components** (`frontend/modules/`):
   - `CrunchbaseCard`: Funding timelines.
   - `GlassdoorWidget`: Sentiment scores.
   - `JobTracker`: Hiring trend graphs.
   - `PatentView`: Innovation radar charts.
   - `MarketIntel`: Valuation & M&A tables.

3. **Global Styles**:
    - Update `frontend/index.css` with CSS variables.
    - Import 'Poppins' from Google Fonts.
    - Refactor buttons and cards to match branding.

4. **New Components** (`frontend/modules/`):
    - `CrunchbaseCard`: Funding timelines.
    - `GlassdoorWidget`: Sentiment scores.
    - `JobTracker`: Hiring trend graphs.
    - `PatentView`: Innovation radar charts.
    - `MarketIntel`: Valuation & M&A tables.

5. **Dashboard Layout**:
    - Update `frontend/index.html` header/nav to match website.
    - Create "Intelligence Streams" view to consolidate new data.

**Effort**: ~1 hour

---

### 8. 🟢 Enhanced Public Company Data (Current Priority)

**Goal**: Display comprehensive financial metrics for public companies on Battlecards.

#### Data Requirements

- **Valuation**: EV, P/E, EV/EBITDA, P/B, PEG
- **Operating**: EPS, EBITDA, Revenue, FCF, Profit Margin
- **Risk**: Beta, Short Interest, Volume, Float
- **Capital**: Shares Outstanding, Inst. Ownership, Dividend, Earnings Date

#### Proposed Changes

##### [MODIFY] [requirements.txt](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/requirements.txt)

- Add `yfinance`

##### [MODIFY] [main.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/main.py)

- Update `/api/stock/{company_name}` to use `yfinance.Ticker(ticker).info`
- Map all requested fields to the response JSON.

##### [MODIFY] [app.js](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/frontend/app.js)

- Update `loadCompanyStockData`
- Render a new "Financial Deep Dive" grid in the Battlecard modal.
- Add Public/Private badge with Ticker/Exchange in header.

**Effort**: ~1 hour

---

### 9. 🟢 Enhanced Private Company Data (New)

**Goal**: Create a rich "Private Intelligence" view mirroring the public company depth.

#### Data Sources & Fields

1. **Capital & Valuation**:
    - **Total Funding**: From DB / Crunchbase.
    - **Latest Deal**: SEC Form D (Date & Amount) via `sec_edgar_scraper`.
    - **Investors**: From DB.

2. **Growth & Operations**:
    - **Headcount**: LinkedIn Tracker.
    - **Growth Rate (6mo)**: LinkedIn Tracker.
    - **Hiring Demand**: Active job openings (Indeed/LinkedIn).
    - **Est. Revenue**: Calculated (Headcount × $150k ARR).

#### Proposed Changes

##### [MODIFY] [sec_edgar_scraper.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/sec_edgar_scraper.py)

- Implement `get_latest_form_d(company_name)` to find capital raises.

##### [MODIFY] [main.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/main.py)

- Update `get_stock_data` (rename to `get_financial_data`) to handle private logic.
- Return unified grid object.

##### [MODIFY] [app.js](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/frontend/app.js)

- Implement "Private Intelligence" grid in Battlecard.
- Display "Private" badge with Series/Stage info if available.

**Effort**: ~1.5 hours

---

### 10. 🟢 Alternative Data Intelligence (New)

**Goal**: Add reliable "Health & Maturity" proxies for private companies.

#### Data Sources & Fields

1. **Government Revenue**:
    - **Contracts**: Prime contract awards from USAspending.gov.
    - **Agency Focus**: Top agency (e.g., VA, HHS).

2. **Workforce Quality (H-1B)**:
    - **Avg Salary**: Engineering salary benchmark from H-1B filings.
    - **Recent Filings**: Count of recent visa applications (growth signal).

3. **Innovation & Sentiment**:
    - **Patents**: Total patents & recent filings (USPTO).
    - **App Ratings**: Avg rating & download volume (App Store/Play Store).
    - **Employee Sentiment**: Glassdoor rating & CEO approval.

#### Proposed Changes

##### [NEW] [gov_contracts_scraper.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/gov_contracts_scraper.py)

- Fetch award data from USAspending API.

##### [NEW] [h1b_scraper.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/h1b_scraper.py)

- Scrape/Fetch H-1B salary data.

##### [MODIFY] [main.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/main.py)

- Integrate new scrapers into `get_financial_data`.

##### [MODIFY] [app.js](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/frontend/app.js)

- Add "Alternative Signals" section to Private Grid.

**Effort**: ~2 hours

---

### 11. 🔎 Google Ecosystem Intelligence (New)

**Goal**: Capture "Digital Exhaust" via Google Ads, Trends, and Tech Stack.

#### Data Sources & Fields

1. **Advertising & Spend**:
    - **Ad Creatives**: Active ad count & types (Google Transparency).
    - **Paid Keywords**: Top bidding terms (SEMRush/SpyFu proxy).
    - **Video Frequency**: YouTube upload cadence.

2. **Brand & Traffic**:
    - **Search Volume**: Google Trends index (Brand Awareness).
    - **Review Velocity**: Google Maps review count & growth.
    - **Physical Traffic**: "Popular Times" busyness index (Retail/Hospitality).

3. **Technical Maturity**:
    - **Tech Stack**: Presence of Enterprise tools (GTM, Floodlight, Adobe Analytics).

#### Proposed Changes

##### [NEW] [google_ecosystem_scraper.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/google_ecosystem_scraper.py)

- Handles Trends, Ads Transparency, and YouTube metadata.

##### [NEW] [tech_stack_scraper.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/tech_stack_scraper.py)

- Analyzes site headers/scripts for marketing tech.

##### [MODIFY] [main.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/main.py)

- Integrate new Google scrapers.

##### [MODIFY] [app.js](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/frontend/app.js)

- Add "Digital Footprint" section to Private Grid.

---

### 12. 🧠 Deep Dive Intelligence (New)

**Goal**: "Qualitative Quantified" metrics for complete holistic scoring.

#### Data Sources & Fields

1. **Product & Sentiment**:
    - **B2B Reviews**: G2 / Capterra scores & badges.
    - **Consumer Trust**: Trustpilot score.
    - **Community**: Reddit sentiment scoring.

2. **SEO & Digital Assets**:
    - **Authority**: Domain Authority (DA) proxy.
    - **Performance**: Page Speed scores.
    - **Organic Reach**: Top organic keywords.

3. **Management & Risk**:
    - **Pedigree**: Founder exit history & Board composition.
    - **Risk Flags**: WARN acts, broken links check, Compliance badges (SOC2).

#### Proposed Changes

##### [NEW] [sentiment_scraper.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/sentiment_scraper.py)

- Aggregates G2, Capterra, Trustpilot, and Reddit.

##### [NEW] [seo_scraper.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/seo_scraper.py)

- Fetches domain metrics and performance stats.

##### [NEW] [risk_management_scraper.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/risk_management_scraper.py)

- Analyzes team pedigree and compliance signals.

##### [MODIFY] [main.py](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/backend/main.py)

- Integrate new Deep Dive modules.

##### [MODIFY] [app.js](file:///c:/Users/conno/Downloads/Certify_Health_Intelv1/frontend/app.js)

- Add "Sentiment", "SEO", and "Management/Risk" tabs/sections.

**Effort**: ~2.5 hours

| Order | Task | Effort | Impact |
|-------|------|--------|--------|
| 1 | Expand competitor database | 2h | High - meets 40+ requirement |
| 2 | Enable live discovery search | 1h | High - autonomous capability |
| 3 | Enable GPT-4 qualification | 30m | Medium - improves accuracy |
| 4 | Configure email alerts | 30m | Medium - notification capability |
| 5 | Celery task queue | 2h | Low - performance optimization |
| 6 | Cloud deployment | 4-8h | Low - can be done last |

---

## User Decision Required

> [!IMPORTANT]
> Which task would you like me to implement first?

**Options:**

1. **Task 1**: Expand competitor database to 40+ companies
2. **Task 2**: Enable live DuckDuckGo discovery
3. **Task 3**: Uncomment and enable OpenAI GPT-4
4. **All of the above** in order
5. **Different priority** (please specify)

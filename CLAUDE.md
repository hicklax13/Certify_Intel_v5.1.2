# Certify Intel - Development Documentation

## Project Overview

**Certify Intel** is a production-ready Competitive Intelligence Platform designed to track, analyze, and counter 30+ competitors in the healthcare technology space. It provides a centralized, real-time dashboard for sales, product, and leadership teams.

**Version**: v5.0.2
**Status**: 🟢 Web Version Production-Ready | 🔴 Desktop App Blocked
**Last Updated**: January 26, 2026, 12:15 AM EST

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

## Latest Session - January 26, 2026

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

# Optional - AI Features
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4.1

# Optional - Enhanced Search
GOOGLE_API_KEY=your-google-key
GOOGLE_CX=your-search-engine-id

# Desktop Mode
DESKTOP_MODE=false
ADMIN_EMAIL=admin@yourcompany.com
```

See `backend/.env.example` for full configuration options.

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

# Certify Health Intel - Claude Documentation

## Project Overview

**Certify Health Intel** is a production-ready **Competitive Intelligence Platform** designed to track, analyze, and counter 30+ competitors in the healthcare technology space. It provides a centralized, real-time dashboard to aggregate data from multiple sources and empower sales, product, and leadership teams with actionable competitive insights.

### Target Users
- Executive Leadership (strategic planning)
- Sales Teams (battlecards, feature comparisons)
- Product Management (feature gaps, competitor releases)
- Strategy & Operations (market shifts, M&A activity)

---

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.9+) with Uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **API**: RESTful with 40+ endpoints
- **Task Scheduling**: APScheduler
- **Web Scraping**: Playwright, BeautifulSoup4, lxml
- **AI/ML**: OpenAI GPT-4, LangChain, tiktoken
- **Reporting**: ReportLab (PDF), openpyxl (Excel)
- **Authentication**: JWT tokens with passlib
- **Other**: pandas, yfinance, python-jose, httpx, requests

### Frontend
- **Architecture**: Single Page Application (SPA)
- **Languages**: HTML5, Vanilla JavaScript (ES6+), CSS3
- **Visualization**: Chart.js
- **PWA**: Service workers for offline support
- **Design**: Glassmorphism, dark-mode aesthetic with CSS variables

### Desktop Application
- **Framework**: Electron (wraps web app as native desktop)
- **Build Tools**: electron-builder
- **Platforms**: Windows (.exe), macOS (.dmg)
- **Backend Integration**: Python backend spawned as child process

---

## Core Features

### 1. Real-Time Intelligence & Monitoring
- **Automated Tracking**: Monitors 30+ data points per competitor
- **Change Detection**: Alerts system for significant updates
- **Discovery Agent**: "Certify Scout" autonomously crawls web for emerging threats
- **News Monitoring**: Real-time news feed aggregation

### 2. Multi-Source Data Collection (15+ Scrapers)
**Finance & Legal**: SEC Edgar, CrunchBase, PitchBook, USPTO patents
**Employment**: Glassdoor, Indeed, LinkedIn, H1B visa filings
**Industry-Specific**: HIMSS Conference, KLAS ratings, App Stores
**Market Intelligence**: SimilarWeb, Twitter/LinkedIn, G2/Capterra, sentiment analysis

### 3. Advanced Analytics
- **Executive Summaries**: AI-generated weekly strategic briefings (GPT-4)
- **Market Positioning Map**: Threat level and market focus visualization
- **Feature Gap Analysis**: Side-by-side product comparison matrices
- **Threat Analysis**: Risk scoring and prioritization
- **Pricing Analytics**: Competitor pricing trends
- **Win/Loss Tracking**: Record competitive deal outcomes

### 4. Reporting & Export
- **Excel Export**: Data-validated exports with auto-fit columns
- **PDF Reports**: Battlecard generation for sales teams
- **JSON Export**: Power Query integration for Power BI
- **Historical Data**: Trend analysis and seeding
- **Change Logs**: Complete audit trail

### 5. User Management & Security
- **Role-Based Access Control**: Admin, Analyst, Viewer roles
- **JWT Authentication**: Secure token-based auth
- **Audit Logs**: Full change history with user attribution
- **Multi-user Collaboration**: User invitations and team workflows

### 6. Data Quality & Verification
- **Data Quality Scores**: Freshness and completeness tracking
- **Source Attribution**: Every data point traced to its source
- **Manual Corrections**: User-initiated corrections with reason logging
- **Verification Workflow**: Track last verification timestamp
- **Stale Data Detection**: Identify fields needing refresh

### 7. Automated Scheduling
- **Weekly Refresh**: Sundays at 2 AM (full database)
- **Daily Check**: 6 AM (high-threat competitors)
- **Database Backups**: Daily automated backups
- **Email Alerts**: Daily digest and weekly summaries

---

## Project Structure

```
Project_Intel_v4/
├── backend/                          # FastAPI Python backend (~8,651 lines)
│   ├── main.py                      # App entry point (3,164 lines)
│   ├── database.py                  # SQLAlchemy ORM models (11 tables)
│   ├── analytics.py                 # Data analysis engine (807 lines)
│   ├── extended_features.py         # Auth, caching, advanced features
│   ├── discovery_agent.py           # AI web scraping logic
│   ├── scheduler.py                 # APScheduler automation
│   ├── alerts.py                    # Notifications (Email/Slack/Teams)
│   ├── reports.py                   # PDF/Excel generation
│   ├── extractor.py                 # GPT-4 data extraction
│   ├── scraper.py                   # Base Playwright scraper class
│   ├── [15+ Specialized Scrapers]   # Domain-specific collectors
│   │   ├── crunchbase_scraper.py
│   │   ├── glassdoor_scraper.py
│   │   ├── sec_edgar_scraper.py
│   │   ├── klas_scraper.py
│   │   ├── appstore_scraper.py
│   │   ├── pitchbook_scraper.py
│   │   ├── himss_scraper.py
│   │   └── ...more
│   ├── seed_db.py                   # Initial data loading
│   ├── certify_intel.db             # SQLite database (471KB)
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Configuration template
│   └── Dockerfile                   # Docker configuration
│
├── frontend/                         # Web UI SPA
│   ├── index.html                   # Main SPA template
│   ├── login.html                   # Authentication UI
│   ├── app_v2.js                    # Core logic (4,084 lines)
│   ├── styles.css                   # Styling (46,758 bytes)
│   ├── mobile-responsive.css        # Mobile optimization
│   ├── enhanced_analytics.js        # Advanced charting
│   ├── visualizations.js            # Chart.js integration
│   ├── service-worker.js            # PWA offline support
│   ├── manifest.json                # PWA configuration
│   └── static/                      # Assets
│
├── desktop-app/                      # Electron wrapper
│   ├── electron/
│   │   ├── main.js                  # Electron main process
│   │   ├── preload.js               # Security bridge
│   │   ├── splash.html              # Loading screen
│   │   └── setup-wizard.html        # First-run setup
│   ├── package.json                 # Build config
│   ├── resources/icons/             # App icons
│   ├── build-windows.bat            # Windows build
│   └── build-mac.sh                 # macOS build
│
└── client_docs/                      # Documentation & templates
    └── Certify Health Material/
```

---

## Database Schema (11 Core Tables)

1. **competitors** - Main competitor records (30+ fields each)
2. **change_log** - Change tracking and alerts
3. **data_sources** - Source attribution per field
4. **data_change_history** - Audit log with user attribution
5. **users** - User accounts with roles
6. **system_prompts** - Dynamic AI prompts
7. **knowledge_base** - Internal documents for RAG
8. **system_settings** - Global configuration
9. **win_loss_deals** - Competitive deal outcomes
10. **webhooks** - Outbound webhook configuration
11. Additional tracking tables for historical data and analytics

---

## Key API Endpoints (40+)

### Competitor Management
- `GET/POST/PUT/DELETE /api/competitors` - CRUD operations
- `POST /api/competitors/{id}/correct` - Manual corrections with audit trail

### Analytics & Intelligence
- `GET /api/analytics/summary` - Dashboard summary
- `GET /api/analytics/executive-summary` - AI-generated briefing
- `POST /api/analytics/chat` - Conversational AI
- `GET /api/analytics/threats` - Threat analysis
- `GET /api/analytics/market-share` - Market positioning

### Data Quality
- `GET /api/data-quality/scores` - Quality metrics
- `GET /api/data-quality/stale` - Stale data detection
- `POST /api/data-quality/verify/{id}` - Verification workflow

### Discovery & Automation
- `POST /api/discovery/run` - AI discovery agent
- `POST /api/discovery/schedule` - Schedule scans
- `GET /api/discovery/context` - Discovery context

### Reporting & Export
- `GET /api/export/excel` - Download Excel dashboard
- `GET /api/export/json` - JSON for Power Query
- `POST /api/alerts/send-digest` - Email alerts

### Scraping
- `POST /api/scrape/all` - Full refresh
- `POST /api/scrape/{id}` - Single competitor scrape

---

## Development Workflow

### Getting Started

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Fill in OpenAI API key and other secrets in .env
   python main.py  # Starts FastAPI on http://localhost:8000
   ```

2. **Frontend**
   - Access via `http://localhost:8000` (frontend served by FastAPI)
   - Or open `frontend/index.html` directly (requires backend running)

3. **Desktop App** (optional)
   ```bash
   cd desktop-app
   npm install
   npm start  # Development
   npm run build  # Build for distribution
   ```

### Configuration (backend/.env)
- `OPENAI_API_KEY` - Required for AI features
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` - Email alerts
- `SLACK_WEBHOOK_URL` - Slack notifications (optional)
- `TEAMS_WEBHOOK_URL` - Teams notifications (optional)
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` - SMS alerts (optional)
- `DATABASE_URL` - SQLite or PostgreSQL
- `SECRET_KEY` - JWT signing key
- `DEBUG` - Debug mode (True/False)

---

## Recent Development (Phase 2)

The project is actively developed with recent commits focusing on:

1. **UI Finalization** - Competitor card layout, modal fixes, news feed repair
2. **Excel Export** - Data-validated export endpoint
3. **Historical Data** - Seeding and trend analysis
4. **Real SEC Data** - Live financial data fetching via yfinance
5. **Automated Scheduling** - Daily backups and refresh jobs

---

## Important Concepts & Patterns

### Data Quality System
- Every competitor field has a **quality score** and **freshness timestamp**
- **Source attribution** tracks where each piece of data came from
- **Stale data detection** identifies fields that need refresh
- **Manual corrections** are logged with user, timestamp, and reason

### Audit Trail
- **data_change_history** table logs every modification
- User attribution on all changes
- Reason logging for manual corrections
- Timestamp of verification for data quality

### AI Integration
- **GPT-4 Executive Summaries**: Auto-generated strategic briefings
- **Discovery Agent**: AI-powered web scraping for emerging threats
- **Conversational Analytics**: Chat interface for competitive analysis
- **Dynamic Prompts**: System prompts stored in database for customization

### Scraper Architecture
- **Base Scraper Class**: `scraper.py` provides Playwright foundation
- **Specialized Scrapers**: Domain-specific implementations for each source
- **Data Extraction**: GPT-4 powered extraction for unstructured data
- **Retry Logic**: Built-in resilience for web scraping

### Role-Based Access Control (RBAC)
- **Admin**: Full system access, user management, configuration
- **Analyst**: Full data access, can create and modify intelligence
- **Viewer**: Read-only access to dashboards and reports

### Task Scheduling
- **APScheduler**: Cron-based job scheduling
- **Weekly Refresh**: Every Sunday 2 AM (full competitor scrape)
- **Daily Check**: 6 AM (high-threat competitors only)
- **Database Backups**: Daily automated backups
- **Email Digests**: Automated summary reports

---

## Code Statistics

- **Backend**: ~8,651 lines of Python across 60 modules
- **Frontend**: ~4,084 lines of JavaScript (main app logic)
- **Database**: 471KB SQLite file, 11+ core tables
- **Scrapers**: 15+ specialized data collection modules
- **API**: 40+ endpoints
- **Competitors**: 30+ tracked competitors
- **Data Points**: 30+ fields per competitor

---

## Common Tasks

### Adding a New Scraper
1. Create new file: `backend/[source]_scraper.py`
2. Inherit from `Scraper` base class
3. Implement scraping logic with Playwright
4. Add GPT-4 extraction for unstructured data
5. Register in `main.py` scraper routing
6. Add to scheduler if needed

### Adding a New API Endpoint
1. Create route in `backend/main.py`
2. Follow RESTful conventions
3. Include authentication decorator (`@app.get`, `@require_auth`)
4. Add data validation with Pydantic models
5. Log changes to database for audit trail
6. Return appropriate status codes

### Generating Reports
- **PDF**: Use `ReportLab` in `backend/reports.py`
- **Excel**: Use `openpyxl` in `backend/reports.py`
- **JSON**: Serialize models with `json` serialization

### Managing Data Quality
1. Check `data_quality/scores` endpoint
2. Identify stale fields (freshness < threshold)
3. Manually correct with `/competitors/{id}/correct`
4. Verify data with `/data-quality/verify/{id}`
5. Log reasons in `data_change_history`

---

## Deployment Options

### Browser-Based
- Access via web browser (desktop, tablet, mobile)
- Requires backend server running
- Responsive design included

### Desktop Application
- Windows: Standalone `.exe` executable
- macOS: `.dmg` installer
- Backend bundled as child process
- Auto-updates from GitHub Releases

### Docker
- Use included `Dockerfile` for containerization
- Simplifies deployment across environments

### White-Label (Version B)
- Customizable branding template
- Setup wizard for end-users
- Separate build configuration

---

## System Requirements

**Development**
- Python 3.9+
- Node.js 18+ (for Electron desktop app)
- OpenAI API key (GPT-4 required)
- Git

**Runtime**
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Python runtime with FastAPI dependencies
- SQLite (zero-config setup)

---

## Troubleshooting & Tips

### Common Issues

**Backend won't start**
- Verify `.env` file has `OPENAI_API_KEY`
- Check Python version is 3.9+
- Run `pip install -r requirements.txt` again
- Check port 8000 isn't already in use

**Scrapers failing**
- Check internet connection
- Verify OpenAI API key validity
- Monitor API rate limits
- Review logs in terminal

**AI features not working**
- Verify `OPENAI_API_KEY` in `.env`
- Check OpenAI account has active API access
- Monitor API usage and billing

**Desktop app not launching**
- Verify Node.js installed (`node --version`)
- Run `npm install` in `desktop-app/`
- Check backend is running before launching Electron

---

## Git Workflow

**Current Branch**: `claude/add-claude-documentation-CzASg`

When pushing changes:
```bash
git add .
git commit -m "Clear, descriptive commit message"
git push -u origin claude/add-claude-documentation-CzASg
```

---

## Next Steps & Contributing

When working on new features:

1. **Plan the task** - Understand requirements clearly
2. **Read existing code** - Understand patterns and conventions
3. **Write tests** - Especially for critical functionality
4. **Follow patterns** - Match existing code style and architecture
5. **Document changes** - Update this file if adding major features
6. **Commit regularly** - Clear, descriptive commit messages

---

## Questions?

For questions about:
- **Features**: Check `README.md` or client_docs
- **Code patterns**: Review similar implementations in codebase
- **Architecture**: See structure overview above
- **Deployment**: Check docker/build configuration files

---

*Last Updated: 2026-01-24*
*Project Status: Phase 2 - Active Development*
*Maturity Level: Production-Ready*

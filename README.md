# Certify Intel

**Competitive Intelligence Platform for Healthcare Technology**

![Version](https://img.shields.io/badge/version-5.0.1-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Web-lightgrey)
![Status](https://img.shields.io/badge/status-Production%20Ready%20(Web)-green)
![License](https://img.shields.io/badge/license-Proprietary-red)

---

## Quick Start (Web Version)

```bash
# Clone the repository
git clone https://github.com/hicklax13/Project_Intel_v5.0.1.git
cd Project_Intel_v5.0.1/backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, SECRET_KEY required)

# Start the server
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Open in browser
# http://localhost:8000
# Login: admin@certifyhealth.com / certifyintel2024
```

---

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Web Version** | ✅ Production Ready | Fully functional at localhost:8000 |
| **Desktop App** | 🔴 Blocked | PyInstaller .env path issue (see CLAUDE.md) |
| **AI Features** | ✅ Working | Requires OpenAI API key |
| **Scrapers** | ✅ Working | 15+ sources with fallback data |

---

## Table of Contents

1. [Overview](#overview)
2. [Who Is This For?](#who-is-this-for)
3. [Key Features](#key-features)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Technology Stack](#technology-stack)
7. [API Reference](#api-reference)
8. [Development Roadmap](#development-roadmap)
9. [Project Structure](#project-structure)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)

---

## Overview

**Certify Intel** is a production-ready competitive intelligence platform designed to track, analyze, and counter 30+ competitors in the healthcare technology space. It provides a centralized, real-time dashboard that aggregates data from multiple sources to deliver actionable competitive insights.

### What It Does

- **Tracks 30+ competitors** with 30+ data points each (pricing, customers, employee count, funding, etc.)
- **Aggregates data from 15+ sources** including SEC filings, job boards, app stores, and industry databases
- **Generates AI-powered insights** using GPT-4 for executive summaries and strategic analysis
- **Delivers reports** in multiple formats: Excel dashboards, PDF battlecards, and JSON for Power BI
- **Monitors changes** with real-time alerts when competitors update their messaging, pricing, or strategy

### Key Differentiators

| Feature | Certify Intel | Traditional Methods |
|---------|---------------|---------------------|
| Data freshness | Real-time to daily | Manual quarterly reviews |
| Sources covered | 15+ automated | 2-3 manual |
| Time to insight | Seconds | Days to weeks |
| Consistency | 100% systematic | Varies by analyst |
| Cost | One-time setup | Ongoing analyst hours |

---

## Who Is This For?

### Executive Leadership
- High-level market summaries and threat analysis
- Strategic planning with data-driven insights
- M&A activity monitoring
- Market positioning visualization

### Sales Teams
- Instant access to competitive battlecards
- Feature comparison matrices for sales calls
- Win/loss tracking and analysis
- Real-time competitive objection handling

### Product Management
- Feature gap identification
- Competitor release monitoring
- Product roadmap guidance
- Pricing strategy intelligence

### Strategy & Operations
- Market shift tracking
- Funding event monitoring
- Employee growth analysis
- Industry trend identification

---

## Key Features

### 1. Real-Time Intelligence & Monitoring

**Automated Competitor Tracking**
- Monitors 30+ data points per competitor
- Configurable refresh schedules (daily, weekly, on-demand)
- Change detection with configurable alert thresholds
- Historical trend tracking

**AI Discovery Agent ("Certify Scout")**
- Autonomously crawls the web for emerging threats
- Identifies new market entrants
- Discovers competitor news and announcements
- Uses GPT-4 for intelligent content analysis

**Alert System**
- Email notifications for significant changes
- Slack and Microsoft Teams integration
- Configurable alert thresholds per competitor

### 2. Multi-Source Data Collection (15+ Scrapers)

| Category | Sources | Data Collected |
|----------|---------|----------------|
| **Finance & Legal** | SEC Edgar, yfinance | Funding rounds, revenue estimates, stock data |
| **Employment** | Glassdoor, Indeed, LinkedIn, H1B filings | Employee count, growth rate, hiring trends |
| **Industry** | HIMSS Conference, KLAS Ratings | Industry rankings, conference presence |
| **App Ecosystem** | App Store, Google Play | App ratings, reviews, feature lists |
| **Market Intelligence** | Google News RSS, G2/Capterra | Web traffic, user reviews, market share |
| **Social & News** | News APIs, RSS Feeds | Announcements, sentiment, PR activity |

### 3. Advanced Analytics

**AI Executive Summaries**
- GPT-4 generated weekly strategic briefings
- Highlights key competitive movements
- Identifies threats and opportunities
- Provides actionable recommendations

**Market Positioning Map**
- Visual competitor landscape
- Threat level scoring (1-10 scale)
- Market focus categorization
- Company size comparison

**Feature Gap Analysis**
- Side-by-side product comparisons
- Feature matrix generation
- Competitive advantage identification

### 4. Reporting & Export

| Format | Description | Use Case |
|--------|-------------|----------|
| **Excel** | Data-validated spreadsheets with auto-fit columns | Data analysis, sharing |
| **PDF** | Sales battlecards with competitive positioning | Sales meetings |
| **JSON** | Power Query compatible format | Power BI integration |

### 5. Data Quality & Verification

- Quality scores (freshness and completeness)
- Source attribution for every data point
- Manual correction with audit trail
- Stale data detection and alerts

### 6. User Management & Security

| Role | Capabilities |
|------|--------------|
| **Admin** | Full system access, user management, configuration |
| **Analyst** | Full data access, create/modify intelligence, run scrapers |
| **Viewer** | Read-only access to dashboards and reports |

---

## Installation

### Option 1: Web Version (Recommended)

```bash
# Clone the repository
git clone https://github.com/hicklax13/Project_Intel_v5.0.1.git
cd Project_Intel_v5.0.1/backend

# Install Python dependencies
pip install -r requirements.txt

# Create and configure environment file
cp .env.example .env
# Edit .env with your API keys

# Start the server
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Open **http://localhost:8000** in your browser.

**Default Login:**
- Email: `admin@certifyhealth.com`
- Password: `certifyintel2024`

### Option 2: Docker

```bash
cd backend
docker-compose up
```

### Option 3: Desktop App (Currently Blocked)

> ⚠️ **Note**: The desktop app installer builds but fails to start due to a PyInstaller .env path issue. See `CLAUDE.md` for details. Use the web version instead.

---

## Configuration

### Required Environment Variables

```bash
# backend/.env

# Required - AI Features
OPENAI_API_KEY=sk-proj-...        # Get from https://platform.openai.com/api-keys
SECRET_KEY=your-random-secret     # Any random string for JWT signing

# Required - Database
DATABASE_URL=sqlite:///./certify_intel.db

# Optional - AI Model (default: gpt-4o)
OPENAI_MODEL=gpt-4o               # Or gpt-4.1-mini for cost savings
AI_PROVIDER=hybrid                # openai, google, or hybrid

# Optional - Google Custom Search (enhanced news discovery)
GOOGLE_API_KEY=AIzaSy...          # Get from Google Cloud Console
GOOGLE_CX=your-search-engine-id   # Get from Programmable Search Engine

# Optional - Desktop Mode (auto-login)
DESKTOP_MODE=true
ADMIN_EMAIL=admin@certifyhealth.com
```

### Optional Integrations

```bash
# Email Notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=team@company.com

# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Microsoft Teams
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
```

---

## Technology Stack

### Backend (Python 3.9+)

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | High-performance async API |
| Server | Uvicorn | ASGI server |
| Database | SQLite + SQLAlchemy | Lightweight, zero-config storage |
| AI/ML | OpenAI GPT-4, LangChain | Intelligence and summarization |
| Web Scraping | Playwright, BeautifulSoup | Dynamic and static page scraping |
| PDF Generation | ReportLab | Battlecard and report creation |
| Excel Export | openpyxl | Data-validated spreadsheets |
| Scheduling | APScheduler | Background job management |
| Authentication | JWT (python-jose), passlib | Secure token-based auth |

### Frontend

| Component | Technology | Purpose |
|-----------|------------|---------|
| Core | HTML5, Vanilla JS (ES6+), CSS3 | No framework dependencies |
| Visualization | Chart.js | Interactive charts and maps |
| Design | CSS Variables, Glassmorphism | Dark-mode premium aesthetic |
| PWA | Service Workers | Offline support and caching |

### Desktop Application

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Electron 28.x | Cross-platform desktop wrapper |
| Build | electron-builder | Windows/macOS installers |
| Backend Bundle | PyInstaller | Python bundled as executable |

---

## API Reference

### Authentication

```bash
# Login to get token
POST /api/auth/login
Body: { "username": "admin@certifyhealth.com", "password": "certifyintel2024" }
Response: { "access_token": "eyJ...", "token_type": "bearer" }

# Use token in requests
Authorization: Bearer eyJ...
```

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/competitors` | List all competitors |
| GET | `/api/competitors/{id}` | Get single competitor |
| POST | `/api/competitors` | Create competitor |
| PUT | `/api/competitors/{id}` | Update competitor |
| DELETE | `/api/competitors/{id}` | Delete competitor |

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/summary` | Dashboard summary stats |
| GET | `/api/analytics/executive-summary` | AI-generated briefing |
| POST | `/api/analytics/chat` | Conversational AI analysis |
| GET | `/api/analytics/threats` | Threat analysis report |

### Export Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/export/excel` | Download Excel dashboard |
| GET | `/api/export/json` | JSON for Power Query |
| POST | `/api/reports/battlecard/{id}` | Generate PDF battlecard |

---

## Development Roadmap

### Current: v5.0.1
- ✅ Web version production ready
- ✅ 15+ scrapers with fallback data
- ✅ AI-powered executive summaries
- ✅ Export to Excel/PDF/JSON
- 🔴 Desktop app blocked (PyInstaller issue)

### Next: v5.0.2 - Gemini Hybrid AI Integration
- Add Google Gemini as secondary AI provider
- ~90% cost reduction on bulk tasks
- New features: Screenshot analysis, PDF analysis
- See `MASTER_TODO.md` for full task list (21 tasks)

### Future: v5.0.3 - Desktop App Fix
- Resolve PyInstaller .env path issue
- End-to-end desktop app testing

### Future: v5.1.0 - Cloud Deployment
- Docker production configuration
- AWS/GCP/Azure deployment guides
- CI/CD pipeline

---

## Project Structure

```
Project_Intel_v5.0.1/
├── backend/                    # Python FastAPI backend (~8,651 lines)
│   ├── main.py                # Application entry point
│   ├── database.py            # SQLAlchemy models (11 tables)
│   ├── analytics.py           # Data analysis engine
│   ├── extended_features.py   # Auth, caching, advanced features
│   ├── discovery_agent.py     # AI web scraping logic
│   ├── scheduler.py           # APScheduler automation
│   ├── alerts.py              # Notifications (Email/Slack/Teams)
│   ├── reports.py             # PDF/Excel generation
│   ├── extractor.py           # GPT-4 data extraction
│   ├── scraper.py             # Base Playwright scraper class
│   ├── *_scraper.py           # 15+ specialized scrapers
│   ├── certify_intel.db       # SQLite database
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Configuration template
│   └── Dockerfile             # Docker configuration
│
├── frontend/                   # Web UI SPA
│   ├── index.html             # Main application
│   ├── login.html             # Authentication UI
│   ├── app_v2.js              # Core logic (4,084 lines)
│   ├── styles.css             # Design system
│   └── service-worker.js      # PWA offline support
│
├── desktop-app/                # Electron wrapper (blocked)
│   ├── electron/
│   │   ├── main.js            # Electron main process
│   │   └── preload.js         # Security bridge
│   └── package.json           # Build configuration
│
├── CLAUDE.md                   # Development documentation
├── MASTER_TODO.md              # Task tracking for development
├── README.md                   # This file
│
└── docs/                       # Additional documentation
```

### Code Statistics

- **Backend**: ~8,651 lines of Python across 60+ modules
- **Frontend**: ~4,084 lines of JavaScript
- **Database**: 471KB SQLite, 11 core tables
- **Scrapers**: 15+ specialized data collectors
- **API Endpoints**: 40+

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `python main.py` exits immediately | Use `python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload` instead |
| Port 8000 in use | Kill existing process or change port |
| AI features not working | Verify `OPENAI_API_KEY` in `.env` |
| Login fails | Use `admin@certifyhealth.com` / `certifyintel2024` |
| Pydantic warnings | These are deprecation warnings, app still works |

### Logs Location

- **Backend**: Console output when running uvicorn
- **Desktop (Windows)**: `%APPDATA%\certify-intel\logs\`
- **Desktop (macOS)**: `~/Library/Logs/certify-intel/`

### Getting Help

- Check `CLAUDE.md` for detailed development context
- Check `MASTER_TODO.md` for current task status
- Open an issue on GitHub

---

## Contributing

### For Claude Agents

1. Read `CLAUDE.md` for project context
2. Check `MASTER_TODO.md` for current tasks
3. Update `MASTER_TODO.md` after completing tasks
4. Commit with clear, descriptive messages

### Development Workflow

1. Create feature branch from `main`
2. Make changes following existing code patterns
3. Test locally
4. Commit with clear messages
5. Push and create Pull Request

### Code Style

- Python: Follow PEP 8, use type hints
- JavaScript: ES6+, no framework dependencies
- CSS: BEM naming, CSS variables for theming

---

## License

Proprietary - Certify Health Internal Use Only

---

## Credits

- **Lead Developer**: Connor Hickey
- **Organization**: Certify Health
- **Repository**: [GitHub - Project_Intel_v5.0.1](https://github.com/hicklax13/Project_Intel_v5.0.1)

---

*Last Updated: January 25, 2026*
*Version: 5.0.1*

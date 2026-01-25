# Certify Intel - Development Documentation

## Project Overview

**Certify Intel** is a production-ready Competitive Intelligence Platform designed to track, analyze, and counter 30+ competitors in the healthcare technology space. It provides a centralized, real-time dashboard for sales, product, and leadership teams.

**Version**: v5.0.1
**Status**: 🟢 Web Version Production-Ready | 🔴 Desktop App Blocked
**Last Updated**: January 25, 2026

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

## Latest Session - January 25, 2026

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

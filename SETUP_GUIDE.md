# Certify Intel - Quick Start Setup Guide

> **Version**: v5.0.7 | **Last Updated**: January 26, 2026
> **Status**: Production-Ready Web Application

---

## Prerequisites

Before installing, ensure you have:

| Requirement | Windows | macOS | Version |
|-------------|---------|-------|---------|
| Python | [python.org](https://www.python.org/downloads/) | `brew install python` | 3.9+ |
| Git | [git-scm.com](https://git-scm.com/download/win) | `brew install git` | Any |
| Web Browser | Chrome/Edge/Firefox | Chrome/Safari/Firefox | Modern |

---

## Quick Start (5 Minutes)

### Step 1: Download the Project

**Option A: Download ZIP (Recommended for First-Time Users)**
1. Go to: https://github.com/YOUR_USERNAME/Project_Intel_v5.0.1
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Extract the ZIP to your desired location

**Option B: Clone with Git**
```bash
git clone https://github.com/YOUR_USERNAME/Project_Intel_v5.0.1.git
cd Project_Intel_v5.0.1
```

---

### Step 2: Install Dependencies

#### Windows (PowerShell)

```powershell
# Navigate to backend folder
cd Project_Intel_v5.0.1\backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

#### macOS / Linux (Terminal)

```bash
# Navigate to backend folder
cd Project_Intel_v5.0.1/backend

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 3: Configure Environment

The `.env` file is already configured with default settings. If you need to customize:

```bash
# Copy example config (only if .env doesn't exist)
cp .env.example .env
```

**Default Configuration (Already Set):**
```env
SECRET_KEY=certify-intel-secret-key-2024
AI_PROVIDER=hybrid
DESKTOP_MODE=true
ADMIN_EMAIL=admin@certifyintel.com
ADMIN_PASSWORD=MSFWINTERCLINIC2026
```

---

### Step 4: Start the Server

#### Windows
```powershell
cd backend
python main.py
```

#### macOS / Linux
```bash
cd backend
python3 main.py
```

**Expected Output:**
```
==================================================
  Certify Intel Backend Starting...
  Open http://localhost:8000 in your browser
==================================================

INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

### Step 5: Login

1. Open your browser to: **http://localhost:8000**
2. Login with:
   - **Email**: `admin@certifyintel.com`
   - **Password**: `MSFWINTERCLINIC2026`
3. Click the **"Show"** button to preview your password before logging in

---

## Troubleshooting

### Port Already in Use

**Windows:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace XXXX with PID from above)
taskkill /PID XXXX /F
```

**macOS / Linux:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Python Not Found

**Windows:**
- Ensure Python is added to PATH during installation
- Try `py` instead of `python`

**macOS:**
```bash
# Install via Homebrew
brew install python
# Use python3 instead of python
python3 main.py
```

### Module Not Found Errors

```bash
# Ensure virtual environment is activated
# Windows:
.\venv\Scripts\Activate
# macOS/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Login Not Working

If you can't login with the default credentials:

```bash
# Delete the database to recreate admin user
# Windows:
del backend\certify_intel.db
# macOS/Linux:
rm backend/certify_intel.db

# Restart the server
python main.py
```

### Deprecation Warnings

The warnings you see on startup are normal and do not affect functionality:
- `google.generativeai` - Will be updated in future version
- `PydanticDeprecatedSince20` - Pydantic v2 migration notices
- `datetime.utcnow()` - Python datetime deprecation

These are cosmetic warnings and can be safely ignored.

---

## Optional: Configure AI Features

For full AI capabilities, add API keys to `backend/.env`:

### OpenAI (GPT-4)
```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4.1
```

### Google Gemini (Cost-Effective)
```env
GOOGLE_AI_API_KEY=your-gemini-key
GOOGLE_AI_MODEL=gemini-2.5-flash
```

### News API Keys (Optional)
```env
GNEWS_API_KEY=your-key          # 100 requests/day free
MEDIASTACK_API_KEY=your-key     # 500 requests/month free
NEWSDATA_API_KEY=your-key       # 200 requests/day free
```

---

## Project Structure

```
Project_Intel_v5.0.1/
├── backend/                    # Python FastAPI server
│   ├── main.py                 # Entry point
│   ├── .env                    # Configuration (DO NOT COMMIT)
│   ├── requirements.txt        # Python dependencies
│   └── certify_intel.db        # SQLite database (auto-created)
│
├── frontend/                   # Web UI (served by backend)
│   ├── index.html              # Main dashboard
│   ├── login.html              # Login page
│   ├── app_v2.js               # Core JavaScript
│   └── styles.css              # Styling
│
├── docs/                       # Documentation
├── CLAUDE.md                   # Development documentation
├── TODO_LIST.md                # Task tracking
└── SETUP_GUIDE.md              # This file
```

---

## Default Login Credentials

| Field | Value |
|-------|-------|
| Email | `admin@certifyintel.com` |
| Password | `MSFWINTERCLINIC2026` |

---

## Support

- **Documentation**: See `CLAUDE.md` for full development documentation
- **Task List**: See `TODO_LIST.md` for project status
- **Issues**: Report bugs on GitHub Issues

---

## Quick Reference Commands

| Action | Windows | macOS/Linux |
|--------|---------|-------------|
| Start Server | `python main.py` | `python3 main.py` |
| Activate venv | `.\venv\Scripts\Activate` | `source venv/bin/activate` |
| Install deps | `pip install -r requirements.txt` | Same |
| Kill port 8000 | `taskkill /PID XXXX /F` | `lsof -ti:8000 \| xargs kill -9` |
| Delete database | `del certify_intel.db` | `rm certify_intel.db` |

---

**Happy Analyzing!**

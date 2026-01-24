# Mock MVP Verification Walkthrough

## Overview

We have transitioned to a **Partial Mock Strategy**.

- **Mocked Integrations**: HubSpot, SimilarWeb, and PitchBook do **NOT** require API keys and will generate high-fidelity mock data.
- **Live Integrations**: **OpenAI** and **Google Search** (via Custom Search JSON API) **DO** require valid API keys in `.env` for the AI Engine and Research tools to function.

Ensure your `.env` has valid `OPENAI_API_KEY`, `GOOGLE_API_KEY`, and `GOOGLE_CX` values.

## 1. Backend Verification

The backend has been updated to automatically generate mock data if API keys are missing.

### HubSpot (Win/Loss Deals)

- **Logic**: If no `HUBSPOT_ACCESS_TOKEN` is found, `sync_deals()` generates **25 mock deals** spread over the last 6 months.
- **Verification**:
  - Build/Run the app.
  - Check the **Win/Loss Analysis** tab.
  - **Success Criteria**: You should see populated charts (e.g., "Win Rate", "Deal Volume") instead of empty placeholders.

### SimilarWeb (Traffic Data)

- **Logic**: If no `RAPIDAPI_KEY` is found, `get_traffic_data()` generates deterministic traffic stats based on the domain name hash (e.g., "phreesia.com" always gets the same distinct number).
- **Verification**:
  - Go to a **Competitor Profile**.
  - Look at the **Strategic Insight** or **Traffic Widget** (if visualization exists).
  - **Success Criteria**: Numbers like "12,648 Visits" appear, and they differ between competitors.

### PitchBook (M&A Targets)

- **Logic**: Returns a curated list of 3-5 "Acquisition Targets" with realistic financial stats.
- **Verification**:
  - Go to the **M&A / Market Intelligence** tab.
  - **Success Criteria**: A table lists companies like "InnovateHealth AI" and "OrthoConnect".

## 2. Running the Demo

1. Ensure your `.env` does **NOT** have invalid keys (empty is fine).
2. Start the backend: `python -m uvicorn main:app --reload`
3. Start the frontend (Electron/React).
4. Walk through the dashboard.

## 3. Important Notes

- **Mock Data Persistence**: Mock deals are saved to the SQlite database (`win_loss_deals` table). If you want to reset the data, delete `certify_intel.db` or the specific rows.

## 4. Final Verification Status

- **Backend**: Verified running (PID 19000) and listening on port 8000.
- **Mock Data**: Verified high-fidelity generation for HubSpot and SimilarWeb.
- **Documentation**: All architecture and planning docs archived to `/Documentation`.

**Ready for Demo.**
Launch the app at: `http://localhost:8000`

## 5. Troubleshooting

### White Screen / Loading Issues

If the dashboard refuses to load (White Screen):

1. **Check for Zombie Processes**: You may have multiple python servers fighting for port 8000.
2. **Fix**: Open Task Manager or Terminal and kill **all** `python.exe` processes, then restart:

    ```powershell
    taskkill /F /IM python.exe
    python -m uvicorn main:app --reload --port 8000
    ```

## 6. Live Data Refresh System

The "Refresh Data" button now performs **real live data collection** from multiple sources with full change tracking.

### Data Sources Integrated

| Source | Data Pulled | Cost |
|--------|-------------|------|
| SEC EDGAR | Public status, ticker, filings | Free |
| Clearbit Logo API | Company logos | Free |
| Google Custom Search | News mentions, product launches | 100/day free |
| Website Scraping + AI | Description, features, pricing | AI API costs |

### User Preferences Implemented

- **No auto AI calls on startup** - AI classification workflow commented out
- **Green AI buttons** - All AI-costing buttons use `.btn-ai` class with tooltip
- **Equal competitor processing** - `priority_order=False` (no threat-level prioritization)
- **Change logging** - All updates logged in `RefreshSnapshot` table with before/after values

### API Endpoints

- `GET /api/scrape/all` - Triggers live refresh for all competitors
- `GET /api/refresh/history` - Retrieves change log (supports `?competitor_id=X` filter)

## 7. High Priority Tasks Completed (2026-01-24)

### Task 1: Refresh History UI

Added collapsible "Refresh History" section to competitor detail modal:

- Toggle button shows/hides change log on demand
- Groups changes by refresh batch ID with timestamps
- Shows field name, old value (red strikethrough), new value (green)
- Scrollable container for long histories

**Files Modified:** `frontend/app_v2.js` (added 4 new functions)

### Task 2: Progress Indicator

Enhanced `triggerScrapeAll()` with visual progress overlay:

- Full-screen modal with progress bar animation
- Step-by-step status messages: "Initiating...", "Scraping...", "AI Extracting...", "Complete!"
- Cost warning reminder during refresh
- Clean removal on completion or error

### Task 3: API Verification

Tested both endpoints via command line:

- `/api/scrape/all` → Started refresh for 90 competitors ✓
- `/api/refresh/history` → Returns proper JSON structure ✓

## 8. Low Priority Enhancements (2026-01-24)

### User-Configurable Refresh Schedule

Added interactive scheduling controls to Settings page:

- Toggle switches for enabling/disabling weekly and daily refreshes
- Day of week dropdown (Sunday, Monday, Saturday) for weekly refresh
- Time input fields for setting exact refresh times
- Save button with localStorage + backend API persistence

**Files Modified:**

- `index.html` (lines 780-823): Enhanced Scheduler section
- `styles.css`: Added `.toggle-switch` CSS styling
- `app_v2.js`: Added `saveScheduleSettings()`, `loadScheduleSettings()`
- `main.py`: Added `/api/settings/schedule` GET/POST endpoints

### Notification Preferences

Added email and Slack alert configuration:

- Email alerts toggle with collapsible email input section
- Slack alerts toggle with webhook URL configuration
- High-threat only filter to limit notifications
- Visual show/hide panels based on toggle state

**Files Modified:**

- `index.html` (lines 825-879): Added Notification Preferences card
- `app_v2.js`: Added `saveNotificationSettings()`, `loadNotificationSettings()`
- `main.py`: Added `/api/settings/notifications` GET/POST endpoints

### Real-Time WebSocket Progress

Added WebSocket support for live refresh progress:

- `ConnectionManager` class to manage active connections
- `/ws/refresh-progress` WebSocket endpoint
- Broadcast method for sending updates to all connected clients

**Files Modified:** `main.py` (lines 3284-3316)

## 9. Deployment v4.0.0 (2026-01-24)

### GitHub Repository

Created new private repository with full project source code:

- **Repo:** `hicklax13/Project_Intel_v4`
- **Branch:** `master`
- **Status:** Synced with all latest changes (frontend v4, backend refresh system)

### Desktop Application Package

Built standalone Windows installer for v4.0.0:

- **File:** `Certify Intel Setup 4.0.0.exe`
- **Size:** ~760 MB
- **Locations Saved:**
  1. `C:\Users\conno\Desktop\Certify Intel Setup 4.0.0.exe`
  2. `C:\Users\conno\Downloads\Certify_Health_Intelv1\Project_Intel\Certify Intel Setup 4.0.0.exe`

### Version Highlights

- **Product Name:** `Certify Intel v4`
- **Description:** Competitive Intelligence Dashboard with Live Refresh
- **Electron Version:** 28.3.3

### Branding Update

Replaced generic "CI" placeholder with official **Certify Intel Logo**:

- **Source:** `desktop and browser icon.jpg`
- **Generated:** `icon.ico` (Windows) and `icon.png` (Linux/Splash)
- **Applied to:** Splash screen, Desktop shortcut, Taskbar icon
- **Status:** Integrated into v4.0.0 installer

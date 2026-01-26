# CERTIFY INTEL - ADVISOR PRESENTATION PREP
## January 26, 2026 - Tonight's Meeting

---

## API KEYS STATUS

### Currently Configured (in .env)
| Key | Status | Used For |
|-----|--------|----------|
| SECRET_KEY | ✅ Set | App security |
| OPENAI_API_KEY | ✅ Set | AI summaries, chat, analysis |
| GOOGLE_API_KEY | ✅ Set | Google Custom Search (Discovery) |
| GOOGLE_CX | ✅ Set | Search Engine ID |
| DATABASE_URL | ✅ Set | SQLite database |
| OPENAI_MODEL | ✅ Set | gpt-4.1 |

### Optional - Not Set (App works without these)
| Key | Status | Used For | How to Get |
|-----|--------|----------|------------|
| GOOGLE_AI_API_KEY | ⚠️ Empty | Gemini AI (hybrid mode) | https://aistudio.google.com/app/apikey |
| FIRECRAWL_API_KEY | ⚠️ Empty | Enhanced web scraping | https://www.firecrawl.dev/ |
| GNEWS_API_KEY | ⚠️ Empty | Extended news sources | https://gnews.io |
| MEDIASTACK_API_KEY | ⚠️ Empty | International news | https://mediastack.com |
| NEWSDATA_API_KEY | ⚠️ Empty | Tech/healthcare news | https://newsdata.io |

**Note:** For the demo, OpenAI is configured and will handle all AI tasks. Gemini (hybrid mode) is optional for cost savings on bulk tasks.

---

## CRITICAL PRE-MEETING CHECKLIST

### 🔴 PRIORITY 1: App Must Run (Do First!)
| # | Task | Status | Time Est |
|---|------|--------|----------|
| 1.1 | Start backend server: `cd backend && python main.py` | ⬜ | 1 min |
| 1.2 | Open http://localhost:8000 in browser | ⬜ | 1 min |
| 1.3 | Verify login page loads without errors | ⬜ | 1 min |
| 1.4 | Login with `admin@certifyhealth.com` / `certifyintel2024` | ⬜ | 1 min |
| 1.5 | Verify Dashboard loads with data | ⬜ | 1 min |

**If login fails, run password reset:**
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

## 🟡 PRIORITY 2: Manual Feature Testing (Do Second!)

### A. Dashboard Page Testing
| # | Feature | How to Test | Expected Result | Status |
|---|---------|-------------|-----------------|--------|
| A1 | Stats Cards Display | View top of dashboard | See Total, High, Medium, Low threat counts | ⬜ |
| A2 | Threat Distribution Chart | View pie chart | Chart renders with data | ⬜ |
| A3 | Pricing Models Chart | View bar chart | Chart renders with pricing data | ⬜ |
| A4 | Last Data Refresh | Check timestamp | Shows recent timestamp | ⬜ |
| A5 | AI Executive Summary | Wait for summary to load | Summary text appears | ⬜ |
| A6 | AI Summary Collapse | Click toggle button | Summary expands/collapses | ⬜ |
| A7 | AI Chat | Ask a question in chat | Get AI response | ⬜ |
| A8 | Edit AI Instructions | Click edit button | Modal opens with prompt editor | ⬜ |
| A9 | Save Custom Prompt | Create and save prompt | Prompt appears in dropdown | ⬜ |
| A10 | Refresh Data | Click refresh button | Progress bar shows, data updates | ⬜ |

### B. Competitors Page Testing
| # | Feature | How to Test | Expected Result | Status |
|---|---------|-------------|-----------------|--------|
| B1 | Competitor List | Navigate to Competitors | List of competitors shows | ⬜ |
| B2 | Grid/List Toggle | Click view toggle | View switches correctly | ⬜ |
| B3 | Search/Filter | Type in search box | Results filter | ⬜ |
| B4 | Add Competitor | Click Add button | Form opens | ⬜ |
| B5 | Edit Competitor | Click edit on card | Edit form opens with data | ⬜ |
| B6 | Delete Competitor | Click delete | Confirmation prompt, then delete | ⬜ |
| B7 | Competitor Details | Click competitor card | Details modal opens | ⬜ |
| B8 | Individual Refresh | Click refresh on card | Single competitor scrapes | ⬜ |
| B9 | Threat Level Badge | View cards | Badges show correct colors | ⬜ |
| B10 | Public/Private Badge | View cards | Stock ticker shows for public | ⬜ |

### C. Compare Page Testing
| # | Feature | How to Test | Expected Result | Status |
|---|---------|-------------|-----------------|--------|
| C1 | Select Competitors | Use dropdown to select 2-4 | Competitors selected | ⬜ |
| C2 | Side-by-Side View | View comparison | Data shows in columns | ⬜ |
| C3 | Feature Matrix | Scroll to features | Feature grid displays | ⬜ |
| C4 | Export PDF | Click export | PDF downloads | ⬜ |
| C5 | Export Excel | Click export | Excel downloads | ⬜ |

### D. Sales & Marketing Module Testing (NEW v5.0.7)
| # | Feature | How to Test | Expected Result | Status |
|---|---------|-------------|-----------------|--------|
| D1 | Navigate to Module | Click 🎯 Sales & Marketing | Page loads with 4 tabs | ⬜ |
| D2 | Dimension Scorecard | Click Dimensions tab | 9 dimensions display | ⬜ |
| D3 | Score a Dimension | Select competitor, set score 1-5 | Score saves | ⬜ |
| D4 | AI Dimension Suggest | Click AI suggest button | AI suggests scores | ⬜ |
| D5 | Generate Battlecard | Click Battlecards tab, generate | Battlecard renders | ⬜ |
| D6 | Export Battlecard PDF | Click PDF export | PDF downloads | ⬜ |
| D7 | Radar Chart Comparison | Click Comparison tab | Chart renders | ⬜ |
| D8 | Talking Points | Click Talking Points tab | Points list shows | ⬜ |
| D9 | Add Talking Point | Click add button | Form works | ⬜ |
| D10 | Dimension Widget | Go to Battlecards page | Widget shows on sidebar | ⬜ |

### E. News Feed Page Testing (NEW v5.0.4)
| # | Feature | How to Test | Expected Result | Status |
|---|---------|-------------|-----------------|--------|
| E1 | Navigate to News Feed | Click 📰 News Feed | Page loads | ⬜ |
| E2 | News Table | View table | Articles display | ⬜ |
| E3 | Filter by Competitor | Select competitor dropdown | Results filter | ⬜ |
| E4 | Filter by Date | Set date range | Results filter | ⬜ |
| E5 | Filter by Sentiment | Select sentiment | Results filter | ⬜ |
| E6 | Sentiment Badges | View table | Colored badges show | ⬜ |
| E7 | Stats Cards | View stats | Total, positive, neutral, negative | ⬜ |
| E8 | Pagination | Click page numbers | Data loads | ⬜ |
| E9 | Reset Filters | Click reset button | Filters clear | ⬜ |

### F. Analytics & Reports Testing
| # | Feature | How to Test | Expected Result | Status |
|---|---------|-------------|-----------------|--------|
| F1 | Market Positioning | Navigate to Analytics | Bubble chart shows | ⬜ |
| F2 | Win/Loss Tracking | View Win/Loss section | Deals display | ⬜ |
| F3 | Add Win/Loss Deal | Click add deal | Form works | ⬜ |
| F4 | Excel Export | Click export | Excel downloads | ⬜ |
| F5 | PDF Battlecards | Generate battlecard | PDF generates | ⬜ |

### G. Data Quality Page Testing
| # | Feature | How to Test | Expected Result | Status |
|---|---------|-------------|-----------------|--------|
| G1 | Completeness Score | View score | Percentage shows | ⬜ |
| G2 | Confidence Distribution | View chart | Doughnut chart renders | ⬜ |
| G3 | Source Type Breakdown | View cards | Source cards show | ⬜ |
| G4 | Field Coverage | View analysis | Coverage bars show | ⬜ |
| G5 | Quality Ranking | View table | Competitors ranked | ⬜ |
| G6 | Recalculate Scores | Click button | Scores recalculate | ⬜ |
| G7 | View Data Sources | Click Sources on card | Modal shows sources | ⬜ |

### H. Change Log Testing
| # | Feature | How to Test | Expected Result | Status |
|---|---------|-------------|-----------------|--------|
| H1 | Activity Timeline | Navigate to Change Log | Timeline shows | ⬜ |
| H2 | User Attribution | View entries | Username shows | ⬜ |
| H3 | Filter by Competitor | Select competitor | Results filter | ⬜ |
| H4 | Filter by Date | Set date range | Results filter | ⬜ |

### I. Settings Page Testing
| # | Feature | How to Test | Expected Result | Status |
|---|---------|-------------|-----------------|--------|
| I1 | Notification Preferences | Toggle notifications | Settings save | ⬜ |
| I2 | Schedule Settings | Change schedule | Settings save | ⬜ |
| I3 | AI Provider Status | View provider card | Shows OpenAI/Gemini status | ⬜ |

### J. Authentication Testing
| # | Feature | How to Test | Expected Result | Status |
|---|---------|-------------|-----------------|--------|
| J1 | Logout | Click logout | Returns to login page | ⬜ |
| J2 | Login Again | Enter credentials | Successfully logs in | ⬜ |
| J3 | Register New User | Click register, fill form | Account created | ⬜ |
| J4 | Login as New User | Login with new account | Dashboard loads | ⬜ |

### K. UI/UX Testing
| # | Feature | How to Test | Expected Result | Status |
|---|---------|-------------|-----------------|--------|
| K1 | Sidebar Navigation | Click each nav item | Pages load correctly | ⬜ |
| K2 | Sidebar Collapse | Click collapse button | Sidebar collapses to icons | ⬜ |
| K3 | Notification Bell | Click bell icon | Notifications dropdown | ⬜ |
| K4 | User Avatar | Click avatar | User menu dropdown | ⬜ |
| K5 | Date/Time Display | Check header | Shows correct format with EST | ⬜ |
| K6 | Mobile Responsiveness | Resize browser window | Layout adjusts | ⬜ |

---

## 🟢 PRIORITY 3: Issues to Fix Before Demo

### Known Warnings (Non-Breaking)
| # | Issue | Severity | Fix Required? |
|---|-------|----------|---------------|
| W1 | `google.generativeai` package deprecated | LOW | No - still works |
| W2 | Pydantic `orm_mode` deprecated | LOW | No - still works |

### Potential Issues to Check
| # | Issue | How to Check | If Broken, Fix |
|---|-------|--------------|----------------|
| P1 | Database has test data | Check competitor count | Add sample competitors if empty |
| P2 | API keys configured | Check .env file | Verify OPENAI_API_KEY present |
| P3 | Charts render | View Dashboard | May need competitor data |
| P4 | AI Summary generates | Wait on Dashboard | Check OpenAI key |

---

## 🔵 PRIORITY 4: Demo Script (For Tonight)

### Recommended Demo Flow (15-20 minutes)

**1. Introduction (2 min)**
- Show login page
- Explain: "Certify Intel tracks 30+ competitors in healthcare IT"
- Login to Dashboard

**2. Dashboard Overview (3 min)**
- Point out threat level stats (High/Medium/Low)
- Show threat distribution chart
- Highlight AI Executive Summary
- Demonstrate AI chat: "Which competitor has the best pricing?"

**3. Competitors Deep Dive (3 min)**
- Navigate to Competitors page
- Show competitor cards with data
- Click into one competitor for details
- Show confidence indicators on data

**4. Sales & Marketing Module (5 min) - KEY FEATURE
- Navigate to 🎯 Sales & Marketing
- Explain 9 competitive dimensions
- Show dimension scorecard
- Generate a battlecard
- Show radar chart comparison
- Export PDF battlecard

**5. News Feed (2 min)**
- Navigate to 📰 News Feed
- Show aggregated news from multiple sources
- Filter by competitor
- Point out sentiment analysis

**6. Data Quality (2 min)**
- Navigate to Data Quality
- Show confidence distribution
- Explain source triangulation
- Show data sources modal

**7. Q&A (5+ min)**

---

## 📋 SAMPLE DATA CHECK

Run this to verify you have enough data:
```bash
cd backend
python -c "
from database import SessionLocal, Competitor
db = SessionLocal()
competitors = db.query(Competitor).all()
print(f'Total competitors: {len(competitors)}')
for c in competitors[:5]:
    print(f'  - {c.name} (Threat: {c.threat_level})')
db.close()
"
```

If fewer than 5 competitors, add sample data:
```bash
cd backend
python -c "
from database import SessionLocal, Competitor
db = SessionLocal()
samples = [
    ('Phreesia', 'https://phreesia.com', 'HIGH', 'Patient intake & payments leader'),
    ('Clearwave', 'https://clearwave.com', 'MEDIUM', 'Self-service check-in kiosks'),
    ('Relatient', 'https://relatient.com', 'MEDIUM', 'Patient engagement platform'),
    ('Solutionreach', 'https://solutionreach.com', 'LOW', 'Patient communication'),
    ('Luma Health', 'https://lumahealth.io', 'HIGH', 'Patient success platform'),
]
for name, url, threat, desc in samples:
    if not db.query(Competitor).filter(Competitor.name == name).first():
        c = Competitor(name=name, website_url=url, threat_level=threat, description=desc)
        db.add(c)
        print(f'Added: {name}')
db.commit()
db.close()
"
```

---

## ⏰ TIMELINE FOR TODAY

| Time | Task | Duration |
|------|------|----------|
| NOW | Start app, verify login works | 10 min |
| +10 min | Test Dashboard features | 15 min |
| +25 min | Test Competitors page | 10 min |
| +35 min | Test Sales & Marketing Module | 15 min |
| +50 min | Test News Feed | 10 min |
| +60 min | Test remaining pages (Compare, Analytics, Data Quality, Change Log, Settings) | 20 min |
| +80 min | Fix any broken features found | 30 min |
| +110 min | Practice demo flow | 20 min |
| +130 min | Final check, prepare talking points | 10 min |
| **TOTAL** | | **~2.5 hours** |

---

## ✅ FINAL PRE-MEETING CHECKLIST

Before leaving for meeting:
- [ ] App is running at http://localhost:8000
- [ ] Login works
- [ ] Dashboard shows data
- [ ] AI Summary generates
- [ ] All charts render
- [ ] Sales & Marketing Module works
- [ ] News Feed loads
- [ ] Battlecard PDF exports
- [ ] Browser console has no critical errors (F12 → Console)
- [ ] Demo script practiced once

---

## 🚨 EMERGENCY CONTACTS

If something breaks:
1. Check browser console (F12) for JavaScript errors
2. Check terminal running `python main.py` for backend errors
3. Restart the server: `Ctrl+C` then `python main.py`
4. If database corrupted, restore from backup:
   ```bash
   cp certify_intel_backup_20260126_035133.db certify_intel.db
   ```

---

**Created**: January 26, 2026
**Purpose**: Advisor Presentation Prep
**Status**: READY FOR TESTING

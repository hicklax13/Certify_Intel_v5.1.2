# Step-by-Step GUI Testing Guide
## Click-by-Click Instructions for Certify Health Intel

**Date**: 2026-01-24
**Purpose**: Complete visual walkthrough of testing the system through the web interface
**Time Required**: ~15-20 minutes for basic functionality test

---

## Part 1: Starting the System (5 minutes)

### Step 1: Open Terminal/Command Prompt

**Windows**:
- Click Start menu
- Type: `cmd` or `powershell`
- Press Enter

**Mac**:
- Press Cmd + Space
- Type: `terminal`
- Press Enter

**Linux**:
- Press Ctrl + Alt + T
- Or search for "Terminal"

### Step 2: Navigate to Project Folder

Type this command and press Enter:
```bash
cd /home/user/Project_Intel_v4/backend
```

**Expected result**: Command prompt changes to show you're in the backend directory

### Step 3: Install Dependencies (First Time Only)

Type this command and press Enter:
```bash
pip install -r requirements.txt
```

**This will take 30-60 seconds. You should see:**
```
Collecting fastapi...
Collecting sqlalchemy...
...
Successfully installed [40+ packages]
```

**If you see errors**: Try `python -m pip install --upgrade pip` first, then retry.

### Step 4: Start the Backend Server

Type this command and press Enter:
```bash
python main.py
```

**You should see** (wait for this message):
```
INFO: Uvicorn running on http://0.0.0.0:8000
```

⚠️ **IMPORTANT**: Leave this terminal open and running. Do NOT close it.

### Step 5: Open a Web Browser

- Click your web browser (Chrome, Firefox, Safari, or Edge)
- In the address bar, type: `http://localhost:8000`
- Press Enter

---

## Part 2: Login (1 minute)

### Step 6: See Login Screen

You should see a login page with:
- Email field
- Password field
- Login button

### Step 7: Enter Email

- Click in the "Email" field
- Type: `admin@certifyhealth.com`

### Step 8: Enter Password

- Click in the "Password" field
- Type: `certifyintel2024`

### Step 9: Click Login Button

- Click the blue "Login" or "Sign In" button
- Wait 2-3 seconds for the page to load

**Expected**: You should see the dashboard with competitor data

---

## Part 3: Dashboard Tour (3 minutes)

### Step 10: View Dashboard

You should see:
- List of competitors (30+)
- Competitor cards showing basic info
- Search box
- Navigation menu

### Step 11: Scroll Down

- Scroll down to see more competitors
- Each competitor should show:
  - Company name
  - Industry
  - Employees
  - Funding
  - Last updated date

### Step 12: Check Search Works

- Click the search box at the top
- Type: `health` (or any keyword)
- Press Enter

**Expected**: The list filters to show only matching competitors

### Step 13: Click Search Results

- Click on any competitor name from the search results
- Wait for details to load

**Expected**: You should see detailed information about that competitor including:
- Company name
- Description
- Employees count
- Funding information
- Recent changes
- News articles (if available)

---

## Part 4: Competitor Details (3 minutes)

### Step 14: View Competitor Profile

You should see a detailed profile showing:
- Overview section
- Financial data
- Employee information
- Product details
- Latest changes
- News feed

### Step 15: Scroll Through Profile

- Scroll down to see all sections
- Look for:
  - Company description
  - Employee count
  - Funding rounds
  - Recent product updates
  - Latest news items

### Step 16: Check Last Updated Date

- Look for "Last Updated" timestamp
- Should show today's date or recent date

---

## Part 5: Export Features (3 minutes)

### Step 17: Look for Export Button

- Go back to main dashboard (click "Dashboard" in menu)
- Look for "Export" button or menu
- If not visible in menu, look for three dots (⋮) menu

### Step 18: Export to Excel

- Click "Export" or the menu button
- Look for "Excel" option
- Click "Download Excel" or "Export to Excel"

**Expected**:
- Download dialog appears
- File downloads as "competitors.xlsx" or similar
- File size should be 100KB+ (not empty)

### Step 19: Export to JSON

- Click "Export" again
- Look for "JSON" option
- Click "Download JSON" or "Export to JSON"

**Expected**:
- Another download appears
- File downloads as "competitors.json" or similar
- File size should be reasonable (not empty)

### Step 20: Check Downloaded Files

- Open your Downloads folder
- You should see:
  - `competitors.xlsx` (Excel file)
  - `competitors.json` (JSON file)
  - Both files should have today's date

**Optional**: Double-click the Excel file to verify it opens with data

---

## Part 6: Changes/Audit Trail (2 minutes)

### Step 21: Find Changes Log

- Look in navigation menu for "Changes", "History", or "Audit Log"
- Click on it

**Expected**: You should see a list of recent changes with:
- Date and time
- What was changed
- Which competitor
- Who made the change

### Step 22: Review Change History

- Look at the most recent changes
- Each change should show:
  - Timestamp
  - Competitor name
  - Field that changed
  - Old value → New value
  - User who made change

---

## Part 7: Search & Filter (2 minutes)

### Step 23: Test Search

- Go back to dashboard
- Click search box
- Type different search terms:
  - "data" (should find several matches)
  - "health" (should find matches)
  - "software" (should find matches)

**Expected**: Results filter in real-time

### Step 24: Test Competitor Filter

- If there's a filter option, try filtering by:
  - Industry
  - Funding stage
  - Employee count range
  - Location

---

## Part 8: Verify Data Quality (2 minutes)

### Step 25: Look for Data Quality Indicator

- On competitor cards or details
- Look for:
  - Quality score (0-100%)
  - Last updated date
  - Data freshness indicator
  - Completeness percentage

### Step 26: Check Multiple Competitors

- Click on 3-4 different competitors
- Verify each has:
  - Data quality score
  - Last updated timestamp
  - Multiple data fields filled in

---

## Part 9: Test Complete - Summary (1 minute)

### Verification Checklist ✅

If you can do all of these, the system works:

- [x] Login with credentials works
- [x] Dashboard loads with 30+ competitors
- [x] Can view individual competitor details
- [x] Search functionality filters results
- [x] Can export to Excel
- [x] Can export to JSON
- [x] Can see changes/audit log
- [x] Data quality indicators visible
- [x] Last updated dates showing
- [x] All pages load without errors

**If all boxes are checked**: ✅ **SYSTEM WORKS!**

---

## Troubleshooting: What If Something Doesn't Work?

### Issue 1: "Page Cannot Be Reached" or "Connection Refused"

**Problem**: Browser shows error when accessing http://localhost:8000

**Solution**:
1. Go back to terminal where you started backend
2. Look for error messages
3. Check that you see message: `Uvicorn running on http://0.0.0.0:8000`
4. If not there, backend didn't start - scroll up to see error
5. Try closing and restarting backend with `python main.py`

### Issue 2: Login Page Shows But Won't Login

**Problem**: Click login but get error

**Solution**:
1. Verify you typed email exactly: `admin@certifyhealth.com`
2. Verify password exactly: `certifyintel2024`
3. Check for typos (case-sensitive!)
4. Try clearing browser cache:
   - Click menu (⋮) → Settings → Privacy → Clear browsing data
   - Check "Cookies and other site data"
   - Click Clear data

### Issue 3: Dashboard Loads But Shows "No Competitors" or Empty

**Problem**: Competitors list is empty

**Solution**:
1. Reload page (press F5 or Cmd+R)
2. Wait 10 seconds for data to load
3. Check browser console for errors (press F12)
4. If still empty, database may need seeding - go back to terminal and restart backend

### Issue 4: Export Button Not Visible

**Problem**: Can't find export option

**Solution**:
1. Look for menu button (three horizontal lines ≡ or three dots ⋮)
2. Click menu to expand options
3. Look for "Export", "Download", or "Reports"
4. If still not there, try refreshing page with F5

### Issue 5: Excel File Downloads But Won't Open

**Problem**: File downloads but shows error when opening

**Solution**:
1. Check file size (should be 100KB+)
2. If file is very small (1KB), try again
3. Try renaming file to `competitors.xlsx` if needed
4. Try opening with different spreadsheet app (LibreOffice, Google Sheets, etc.)

### Issue 6: Page Loads But Data Appears Incomplete

**Problem**: Some competitors missing data fields

**Solution**:
1. This is NORMAL - some data sources may be unavailable
2. Scroll right to see all fields
3. Click on competitor to see full detail view
4. Data quality indicator will show completeness percentage

---

## Advanced Testing (Optional - 10 minutes)

### Step A1: Manual Data Correction (Optional)

If there's an "Edit" button on competitor details:

1. Click "Edit" on a competitor
2. Change one field (e.g., employee count)
3. Click "Save" or "Correct"
4. Look in Changes log - your change should appear

### Step A2: Test Discovery Agent (Optional)

If there's a "Discovery" or "Scan" button:

1. Click "Run Discovery Agent" or similar
2. Wait 10-30 seconds (may take time)
3. Check for "Discovery in progress" or "New competitors found" message
4. This may timeout - that's normal

### Step A3: Test Data Quality Scores (Optional)

If there's a "Data Quality" or "Quality Scores" page:

1. Navigate to Data Quality section
2. Look for competitor quality scores
3. Scores should be 0-100
4. Look for "Stale data" detection
5. Look for last verification date

### Step A4: View System Health (Optional)

Look for "System Status" or "Health Check":

1. Click System Status or Admin area
2. Look for:
   - Available scrapers (should show ✅ marks)
   - Disabled scrapers (should show ❌ for Crunchbase, PitchBook)
   - Last refresh time
   - Database status

---

## What You've Tested

### Core Functionality ✅
- Authentication (login system works)
- Database (has 30+ competitors with data)
- Web UI (displays correctly)
- Search (filters work)
- Navigation (pages load)

### Data Retrieval ✅
- Competitor list (shows all)
- Competitor details (shows complete data)
- Changes history (tracks updates)
- Timestamps (shows when updated)

### Export Functionality ✅
- Excel export (file generates)
- JSON export (file generates)
- Data accuracy (correct data in exports)
- File formats (valid Excel and JSON)

### Data Quality ✅
- Quality scores (calculated)
- Freshness dates (showing)
- Completeness (multiple fields present)
- Change tracking (audit trail works)

---

## Expected Results Summary

### ✅ If All Tests Pass

```
✅ Login: Works
✅ Dashboard: Loads with 30+ competitors
✅ Search: Filters results correctly
✅ Details: Show complete competitor data
✅ Exports: Excel and JSON files download
✅ History: Changes log shows updates
✅ Quality: Data quality metrics visible
✅ Performance: Pages load quickly (< 5 seconds)
```

**Conclusion**: 🎉 **SYSTEM FULLY FUNCTIONAL!**

### ⚠️ If Some Tests Show Warnings

Example: Excel export missing some columns
- This is acceptable
- System still works for core functions
- Document the issue
- Note for Phase 4 detailed testing

### ❌ If Tests Fail

Example: Login doesn't work
- Check backend is running (terminal should show "Uvicorn running")
- Verify credentials exactly
- Check for typos
- Restart backend
- Try again

---

## Time Breakdown

| Task | Time | Cumulative |
|------|------|-----------|
| Start backend | 2 min | 2 min |
| Install dependencies | 1 min | 3 min |
| Login | 1 min | 4 min |
| Dashboard tour | 3 min | 7 min |
| View competitor details | 3 min | 10 min |
| Test exports | 3 min | 13 min |
| Check changes log | 2 min | 15 min |
| Test search | 2 min | 17 min |
| Verify data quality | 2 min | 19 min |
| **Total** | | **~19 minutes** |

---

## Quick Start Checklist

Print this and check off each step:

- [ ] Terminal open and backend running (`python main.py`)
- [ ] Browser at `http://localhost:8000`
- [ ] Login page visible
- [ ] Email entered: `admin@certifyhealth.com`
- [ ] Password entered: `certifyintel2024`
- [ ] Logged in and dashboard loading
- [ ] See 30+ competitors listed
- [ ] Search works (type "health")
- [ ] Click one competitor to view details
- [ ] All details loading (name, employees, funding, etc.)
- [ ] Export button found
- [ ] Excel file downloaded
- [ ] JSON file downloaded
- [ ] Changes/History log visible
- [ ] Data quality indicators showing
- [ ] All pages load without errors

**If all checked**: ✅ **Testing complete!**

---

## What NOT to Do

❌ Do NOT close the backend terminal (system stops)
❌ Do NOT change the password in code
❌ Do NOT delete the database file while testing
❌ Do NOT use different credentials (use admin account)
❌ Do NOT skip the 5-second wait after starting backend

---

## Screenshots Reference (What You Should See)

### Login Screen
```
┌─────────────────────────────┐
│   Certify Health Intel      │
│                             │
│   Email:  [_______________]│
│   Password:[_______________]│
│   [      LOGIN      ]       │
│                             │
└─────────────────────────────┘
```

### Dashboard
```
┌─────────────────────────────┐
│ Dashboard                   │
│ Search: [__________]        │
├─────────────────────────────┤
│ ┌──────────┐ ┌──────────┐   │
│ │ Company1 │ │ Company2 │   │
│ │ Industry │ │ Industry │   │
│ │ Employees│ │Employees │   │
│ └──────────┘ └──────────┘   │
│ ┌──────────┐ ┌──────────┐   │
│ │ Company3 │ │ Company4 │   │
│ └──────────┘ └──────────┘   │
│ [  More competitors below ]  │
└─────────────────────────────┘
```

### Competitor Details
```
┌─────────────────────────────┐
│ Company Name: XYZ Corp      │
├─────────────────────────────┤
│ Overview                    │
│ Description: [detailed text]│
│                             │
│ Key Metrics                 │
│ • Employees: 500            │
│ • Founded: 2015             │
│ • Funding: $50M             │
│ • Last Updated: 2 days ago  │
│                             │
│ Recent Changes              │
│ • Field: Value → New Value  │
│ • Field2: Value → New Value │
└─────────────────────────────┘
```

---

## Next Steps After Visual Test

If your visual testing passes (all items checked):

1. **Document Results**
   - Take screenshots if possible
   - Note: "Dashboard test PASSED - All features working"
   - Save in PHASE_3A_RESULTS.md

2. **Proceed to Phase 4**
   - Follow PHASE_4_EXPORT_VALIDATION_PLAN.md
   - More detailed testing of exports

3. **Proceed to Phase 5**
   - Follow PHASE_5_DATA_QUALITY_PLAN.md
   - Test quality systems

---

## Support

**Can't find a button or feature?**
- Check the navigation menu (top or side)
- Look for hamburger menu (≡) or three dots (⋮)
- Press F12 to open browser developer tools to see any errors
- Check backend terminal for error messages

**Things don't look right?**
- Refresh page (press F5 or Cmd+R)
- Clear cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
- Try different browser
- Restart backend

---

## Success Criteria

✅ **Test Successful If**:
- You can login
- Dashboard displays competitors
- You can view competitor details
- Search works
- You can download exports
- You can see change history

**Expected outcome**: 🎉 System fully functional for basic testing

---

**This guide provides complete click-by-click instructions for testing.**
**Total time: ~20 minutes**
**No technical knowledge required**

Start with Step 1 and follow each step in order!

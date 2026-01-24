# Quick Start Testing Card
## Print This Page for Easy Reference

---

## STEP-BY-STEP: 5 MINUTES TO TEST

### STEP 1: Open Terminal
- Windows: Type `cmd` in search, press Enter
- Mac: Press Cmd + Space, type `terminal`, press Enter
- Linux: Press Ctrl + Alt + T

### STEP 2: Go to Project
```
cd /home/user/Project_Intel_v4/backend
```

### STEP 3: Install Dependencies (First Time Only)
```
pip install -r requirements.txt
```
Wait 30-60 seconds...

### STEP 4: Start Backend
```
python main.py
```
Wait for message: `Uvicorn running on http://0.0.0.0:8000`

⚠️ **KEEP THIS TERMINAL OPEN**

### STEP 5: Open Web Browser
Click your browser (Chrome, Firefox, Safari, Edge)

Type in address bar:
```
http://localhost:8000
```

Press Enter

---

## LOGIN (30 seconds)

### Step 6: Enter Email
- Click email field
- Type: `admin@certifyhealth.com`

### Step 7: Enter Password
- Click password field
- Type: `certifyintel2024`

### Step 8: Click Login
- Click blue LOGIN button
- Wait 2-3 seconds

---

## TEST THE SYSTEM (5 minutes)

### Test 1: Dashboard ✓
You should see 30+ competitor cards

**Pass**: ✅ Multiple competitors visible
**Fail**: ❌ Empty page or error

### Test 2: Search ✓
- Click search box
- Type: `health`
- Press Enter

**Pass**: ✅ List filters to show matching competitors
**Fail**: ❌ No results or search doesn't work

### Test 3: Competitor Details ✓
- Click any competitor name
- Wait 2-3 seconds

**Pass**: ✅ See detailed profile with info
**Fail**: ❌ Page doesn't load or blank

### Test 4: Excel Export ✓
- Look for "Export" button/menu
- Click "Export" or menu (⋮)
- Select "Excel" or "Download Excel"

**Pass**: ✅ File downloads (100KB+)
**Fail**: ❌ No file or file is empty

### Test 5: JSON Export ✓
- Click "Export" again
- Select "JSON" or "Download JSON"

**Pass**: ✅ File downloads (5KB+)
**Fail**: ❌ No file or file is empty

### Test 6: Changes Log ✓
- Look for "Changes", "History", or "Audit" in menu
- Click it

**Pass**: ✅ See list of recent changes with dates
**Fail**: ❌ Empty or page doesn't load

---

## RESULTS

Count your ✓ marks:

- 6/6 ✓ = **SYSTEM WORKS PERFECTLY** 🎉
- 5/6 ✓ = **SYSTEM WORKS (1 minor issue)** ✅
- 4/6 ✓ = **SYSTEM MOSTLY WORKS** ⚠️
- 3/6 or less = **NEEDS DEBUGGING** ❌

---

## IF SOMETHING FAILS

### "Page Cannot Be Reached"
→ Check backend terminal shows "Uvicorn running on http://0.0.0.0:8000"

### "Login Doesn't Work"
→ Check email: `admin@certifyhealth.com` (exact!)
→ Check password: `certifyintel2024` (exact!)

### "Dashboard Empty"
→ Reload page (press F5)
→ Wait 10 seconds
→ Restart backend

### "Export Button Missing"
→ Look for menu button (⋮ or ≡)
→ Click menu to see options

### "Dashboard Slow"
→ This is normal first time (database loading)
→ Wait longer or reload

---

## SUCCESSFUL TEST CHECKLIST

Print this and check each one:

- [ ] Terminal running with backend started
- [ ] Browser at http://localhost:8000
- [ ] Login page appears
- [ ] Logged in successfully
- [ ] See 30+ competitors on dashboard
- [ ] Search works (filters results)
- [ ] Click competitor shows details
- [ ] All competitor data visible
- [ ] Export button found
- [ ] Excel file downloaded
- [ ] JSON file downloaded
- [ ] Changes log visible
- [ ] No major errors seen

**All checked?** ✅ **TESTING PASSED!**

---

## CREDENTIALS (Write These Down)

Email: `admin@certifyhealth.com`

Password: `certifyintel2024`

---

## IMPORTANT REMINDERS

✅ DO: Keep backend terminal open and running
✅ DO: Wait for "Uvicorn running" message before opening browser
✅ DO: Wait 5 seconds after login page loads
✅ DO: Use exact credentials (copy-paste to be safe)

❌ DON'T: Close the backend terminal
❌ DON'T: Change passwords or code
❌ DON'T: Delete database files
❌ DON'T: Use different email/password

---

## QUICK FIXES

| Problem | Fix |
|---------|-----|
| Connection refused | Restart backend with `python main.py` |
| Login fails | Check email/password are EXACT |
| Empty dashboard | Reload page (F5), wait 10 sec |
| Export not found | Click menu button (⋮) |
| Page slow | First load is slower, be patient |
| Backend won't start | Reinstall: `pip install -r requirements.txt` |

---

## PHONE PHOTO TEST

Take a screenshot of each:
1. Login page with your credentials entered
2. Dashboard with competitor list
3. Competitor details page
4. Downloaded Excel file name
5. Downloaded JSON file name

This proves the system works!

---

## NEXT STEPS

✅ If test passes:
- Document results
- Proceed to Phase 4 detailed testing

⚠️ If minor issues:
- Note them
- Try the quick fixes above
- Proceed with testing

❌ If major failure:
- Check backend terminal for errors
- Restart from Step 1
- Verify credentials

---

## CONTACT POINTS

Can't figure something out?

See: `VISUAL_TESTING_GUIDE.md` (detailed version of this)
See: `QUICK_REFERENCE.md` (all commands)
See: `PHASE_3A_EXECUTION_SUMMARY.md` (for command-line testing)

---

## TIME ESTIMATE

- Install dependencies: 1 minute (first time only)
- Start backend: 1 minute
- Open browser & login: 1 minute
- Complete all 6 tests: 5 minutes
- **TOTAL: 8 minutes** ⏱️

---

**Ready? Start with STEP 1 above!**

🚀 Good luck! You've got this!

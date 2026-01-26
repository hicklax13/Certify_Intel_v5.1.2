# C-Suite Meeting Implementation Plan
## Target: January 26, 2026, 9:00 AM EST (Demo at 9:30 AM)
## Current Time: January 25, 2026, 9:11 PM EST

---

## Executive Summary

This plan addresses all outstanding tasks required before the C-Suite meeting:

1. **BUG FIX**: Dashboard threat level stats not displaying
2. **NEW FEATURE**: User-specific prompt management system
3. **NEW FEATURE**: Real-time AI summary progress bar
4. **CLEANUP**: Remove duplicate API endpoints in main.py

---

## Phase 1: Critical Bug Fix - Dashboard Stats (Priority: CRITICAL)

### Problem
The dashboard stat cards (Total Competitors, High/Medium/Low Threat) show "-" instead of actual values.

### Root Cause Analysis
- **Finding**: Duplicate `/api/dashboard/stats` endpoint in `main.py` (lines 1774 and 3499)
- **Impact**: FastAPI may be handling these inconsistently
- **Additional Issue**: Stats variable may be null when `updateStatsCards()` is called

### Solution
1. Remove duplicate endpoint at line 3499
2. Add null-safety check in frontend `updateStatsCards()` function
3. Add console logging for debugging

### Files to Modify
- `backend/main.py` - Remove duplicate endpoint
- `frontend/app_v2.js` - Add null safety

---

## Phase 2: User-Specific Prompt Management (Priority: HIGH)

### Requirements
- Users can create, save, edit, and delete their own prompts
- Prompts are private to each user account
- Users can select and load saved prompts
- Users can replace default Executive Summary prompt with their saved prompts

### Database Changes
Add new model `UserSavedPrompt`:
```python
class UserSavedPrompt(Base):
    __tablename__ = "user_saved_prompts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)  # User-friendly name
    prompt_type = Column(String, default="executive_summary")  # Type of prompt
    content = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)  # User's default for this type
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### API Endpoints
- `GET /api/user/prompts` - List user's saved prompts
- `POST /api/user/prompts` - Create new prompt
- `PUT /api/user/prompts/{id}` - Update prompt
- `DELETE /api/user/prompts/{id}` - Delete prompt
- `POST /api/user/prompts/{id}/set-default` - Set as default

### Frontend Changes
Update "Edit AI Instructions" modal to include:
- Dropdown to select from saved prompts
- "Save As New" button
- "Update Current" button
- "Delete" button
- "Load Default" button

### Files to Modify
- `backend/database.py` - Add UserSavedPrompt model
- `backend/main.py` - Add API endpoints
- `frontend/index.html` - Update modal HTML
- `frontend/prompt_manager.js` - Add CRUD functions
- `frontend/styles.css` - Add new styles

---

## Phase 3: AI Summary Progress Bar (Priority: HIGH)

### Requirements
- Real-time progress indicator during AI summary generation
- Show estimated time remaining
- Display current step (e.g., "Analyzing competitors...", "Generating insights...")

### Backend Changes
Add progress tracking endpoint:
- `GET /api/analytics/summary/progress` - Returns current progress state

Add progress state management:
```python
ai_summary_progress = {
    "active": False,
    "step": "",
    "progress": 0,
    "total_steps": 4,
    "started_at": None
}
```

### Frontend Changes
Add progress modal similar to data refresh:
- Circular or linear progress bar
- Step description text
- Percentage indicator
- Cancel button (optional)

### Files to Modify
- `backend/main.py` - Add progress tracking to summary endpoint
- `frontend/index.html` - Add progress modal HTML
- `frontend/app_v2.js` - Add progress polling and UI updates
- `frontend/styles.css` - Add progress bar styles

---

## Phase 4: Code Cleanup (Priority: MEDIUM)

### Issues to Fix
1. Remove duplicate `/api/dashboard/stats` endpoint (line 3499)
2. Remove/fix duplicate `/api/scrape/all` endpoint conflict (GET vs POST)
3. Remove duplicate model definitions

---

## Implementation Order

| # | Task | Est. Time | Priority |
|---|------|-----------|----------|
| 1 | Fix dashboard stats bug | 15 min | CRITICAL |
| 2 | Add UserSavedPrompt model | 10 min | HIGH |
| 3 | Add prompt CRUD API endpoints | 30 min | HIGH |
| 4 | Update prompt editor modal UI | 45 min | HIGH |
| 5 | Add AI summary progress backend | 20 min | HIGH |
| 6 | Add AI summary progress frontend | 30 min | HIGH |
| 7 | Test all features | 30 min | HIGH |
| 8 | Update documentation | 15 min | MEDIUM |

**Total Estimated Time: ~3.5 hours**

---

## Testing Checklist

### Dashboard Stats
- [ ] Stats cards show correct numbers on page load
- [ ] Stats update after data refresh
- [ ] No console errors

### Prompt Management
- [ ] Can create new prompt
- [ ] Can edit existing prompt
- [ ] Can delete prompt
- [ ] Can load saved prompt into editor
- [ ] Can set prompt as default
- [ ] Prompts are user-specific (not visible to other users)

### AI Summary Progress
- [ ] Progress bar appears when generating summary
- [ ] Progress updates in real-time
- [ ] Progress bar disappears when complete
- [ ] Summary displays correctly after generation

---

## Rollback Plan

If any feature causes issues:
1. Git revert to last stable commit
2. Focus on bug fixes only
3. Demo with existing functionality

---

## Success Criteria

1. Dashboard displays all stats correctly
2. Users can save and load their own prompts
3. AI summary generation shows real-time progress
4. No console errors or API failures
5. All features work for admin and regular users

---

Created: January 25, 2026, 9:15 PM EST
Author: Claude Opus 4.5

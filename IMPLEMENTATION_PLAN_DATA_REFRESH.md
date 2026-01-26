# Data Refresh Enhancement - Implementation Plan
## Live Progress Bar + AI Change Summary

**Created**: January 25, 2026, 10:30 PM EST
**Author**: Claude Opus 4.5
**Priority**: HIGH - C-Suite Meeting Prep

---

## Executive Summary

This plan addresses the user's requirements to:
1. Show a **live inline progress bar** on the Dashboard during data refresh (not a modal)
2. Provide **full transparency** into what data was refreshed, changed, and discovered
3. Generate an **AI-powered summary** of refresh changes using OpenAI

---

## Current State Analysis

### What Already Exists
| Component | Location | Status |
|-----------|----------|--------|
| Scrape progress tracking | `main.py:110-118` | Working - tracks `changes_detected`, `new_values_added` |
| Progress modal | `index.html:1018-1039` | Working - but displays as overlay modal |
| Change logging | `DataChangeHistory` table | Working - logs field-level changes |
| Activity logging | `ActivityLog` table | Working - logs user actions |
| Completion modal | `showRefreshCompleteModal()` | Basic - shows counts only |

### What's Missing
1. **Inline progress display** on Dashboard page (currently uses modal overlay)
2. **Detailed change breakdown** (which fields changed, old vs new values)
3. **AI summary of changes** (intelligent analysis of what the refresh discovered)
4. **Session-based refresh history** (view past refresh results)

---

## Phase 1: Inline Dashboard Progress Bar

### 1.1 Create Inline Progress Component

**File**: `frontend/index.html`

Add new inline progress section below the "Last Data Refresh" indicator:

```html
<!-- Data Refresh Progress (Inline) -->
<div id="inlineRefreshProgress" class="inline-refresh-progress" style="display: none;">
    <div class="refresh-progress-header">
        <div class="refresh-progress-title">
            <span class="refresh-icon spinning">🔄</span>
            <span>Refreshing Competitor Data...</span>
        </div>
        <span id="inlineProgressPercent" class="progress-percent">0%</span>
    </div>
    <div class="inline-progress-bar-container">
        <div id="inlineProgressBar" class="inline-progress-bar" style="width: 0%"></div>
    </div>
    <div class="refresh-progress-details">
        <span id="inlineProgressText">Starting...</span>
        <span id="inlineProgressCount">0 / 0 competitors</span>
    </div>
    <div id="inlineProgressLive" class="refresh-live-updates">
        <!-- Live updates will appear here -->
    </div>
</div>
```

### 1.2 CSS Styles for Inline Progress

**File**: `frontend/styles.css`

```css
/* Inline Refresh Progress */
.inline-refresh-progress {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border: 1px solid #7dd3fc;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
    animation: pulse-border 2s infinite;
}

@keyframes pulse-border {
    0%, 100% { border-color: #7dd3fc; }
    50% { border-color: #0ea5e9; }
}

.refresh-progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.refresh-progress-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
    color: #0369a1;
}

.refresh-icon.spinning {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.progress-percent {
    font-size: 24px;
    font-weight: 700;
    color: #0284c7;
}

.inline-progress-bar-container {
    height: 12px;
    background: #e0f2fe;
    border-radius: 6px;
    overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
}

.inline-progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #0ea5e9, #0284c7);
    border-radius: 6px;
    transition: width 0.3s ease;
}

.refresh-progress-details {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    font-size: 13px;
    color: #0369a1;
}

.refresh-live-updates {
    margin-top: 16px;
    max-height: 120px;
    overflow-y: auto;
    font-size: 12px;
}

.live-update-item {
    padding: 6px 10px;
    margin: 4px 0;
    background: white;
    border-radius: 6px;
    border-left: 3px solid #10b981;
    display: flex;
    align-items: center;
    gap: 8px;
}

.live-update-item.change {
    border-left-color: #f59e0b;
}

.live-update-item.new {
    border-left-color: #10b981;
}

.live-update-item.error {
    border-left-color: #ef4444;
}
```

### 1.3 JavaScript Updates

**File**: `frontend/app_v2.js`

Update `triggerScrapeAll()` to use inline progress instead of modal:

```javascript
async function triggerScrapeAll() {
    const btn = event?.target || document.querySelector('[onclick*="triggerScrapeAll"]');

    if (btn) {
        btn.classList.add('btn-loading');
        btn.disabled = true;
    }

    // Show inline progress (hide the data refresh indicator)
    showInlineRefreshProgress();

    try {
        const result = await fetchAPI('/api/scrape/all', { method: 'POST' });

        if (result && result.total) {
            pollInlineRefreshProgress(result.total);
        } else {
            hideInlineRefreshProgress();
            showToast('Error starting refresh', 'error');
        }
    } catch (e) {
        hideInlineRefreshProgress();
        showToast('Error: ' + e.message, 'error');
    } finally {
        if (btn) {
            btn.classList.remove('btn-loading');
            btn.disabled = false;
        }
    }
}

function showInlineRefreshProgress() {
    document.getElementById('dataRefreshIndicator').style.display = 'none';
    document.getElementById('inlineRefreshProgress').style.display = 'block';
    document.getElementById('inlineProgressBar').style.width = '0%';
    document.getElementById('inlineProgressPercent').textContent = '0%';
    document.getElementById('inlineProgressText').textContent = 'Starting...';
    document.getElementById('inlineProgressCount').textContent = '0 / 0 competitors';
    document.getElementById('inlineProgressLive').innerHTML = '';
}

function hideInlineRefreshProgress() {
    document.getElementById('inlineRefreshProgress').style.display = 'none';
    document.getElementById('dataRefreshIndicator').style.display = 'flex';
}

function updateInlineProgress(progress) {
    const percent = progress.total > 0 ? Math.round((progress.completed / progress.total) * 100) : 0;

    document.getElementById('inlineProgressBar').style.width = `${percent}%`;
    document.getElementById('inlineProgressPercent').textContent = `${percent}%`;
    document.getElementById('inlineProgressCount').textContent =
        `${progress.completed} / ${progress.total} competitors`;

    if (progress.current_competitor) {
        document.getElementById('inlineProgressText').textContent =
            `Scanning: ${progress.current_competitor}`;
    }

    // Update live feed with recent changes
    if (progress.recent_changes && progress.recent_changes.length > 0) {
        const liveEl = document.getElementById('inlineProgressLive');
        liveEl.innerHTML = progress.recent_changes.slice(-5).map(change => `
            <div class="live-update-item ${change.type}">
                <span class="change-icon">${change.type === 'new' ? '✨' : '📝'}</span>
                <span><strong>${change.competitor}</strong>: ${change.field} ${change.type === 'new' ? 'discovered' : 'updated'}</span>
            </div>
        `).join('');
    }
}
```

---

## Phase 2: Enhanced Backend Progress Tracking

### 2.1 Expand Progress Object

**File**: `backend/main.py`

Update the `scrape_progress` global to include detailed change tracking:

```python
# Enhanced progress tracker
scrape_progress = {
    "active": False,
    "total": 0,
    "completed": 0,
    "current_competitor": None,
    "competitors_done": [],
    "changes_detected": 0,
    "new_values_added": 0,
    "started_at": None,
    "recent_changes": [],  # NEW: Last 10 field-level changes
    "change_details": [],  # NEW: All changes for AI summary
    "errors": []           # NEW: Any errors encountered
}
```

### 2.2 Track Detailed Changes During Scrape

**File**: `backend/main.py`

Update `run_scrape_job_with_progress()` to populate `recent_changes`:

```python
async def run_scrape_job_with_progress(competitor_id: int, competitor_name: str):
    global scrape_progress

    # ... existing code ...

    # When a change is detected, add to recent_changes:
    change_entry = {
        "competitor": competitor_name,
        "field": field_name,
        "old_value": str(old_value)[:50] if old_value else None,
        "new_value": str(new_value)[:50] if new_value else None,
        "type": "new" if old_value is None else "change",
        "timestamp": datetime.utcnow().isoformat()
    }

    scrape_progress["recent_changes"].append(change_entry)
    scrape_progress["change_details"].append(change_entry)

    # Keep only last 10 in recent_changes for live display
    if len(scrape_progress["recent_changes"]) > 10:
        scrape_progress["recent_changes"] = scrape_progress["recent_changes"][-10:]
```

### 2.3 New Endpoint: Get Refresh Session Details

**File**: `backend/main.py`

```python
@app.get("/api/scrape/session")
async def get_scrape_session_details():
    """Get detailed information about the current or last refresh session."""
    return {
        "active": scrape_progress["active"],
        "total_competitors": scrape_progress["total"],
        "completed": scrape_progress["completed"],
        "changes_detected": scrape_progress["changes_detected"],
        "new_values_added": scrape_progress["new_values_added"],
        "change_details": scrape_progress["change_details"],
        "errors": scrape_progress["errors"],
        "started_at": scrape_progress.get("started_at"),
        "competitors_processed": scrape_progress["competitors_done"]
    }
```

---

## Phase 3: AI-Powered Refresh Summary

### 3.1 New Endpoint: Generate Refresh Summary

**File**: `backend/main.py`

```python
@app.post("/api/scrape/generate-summary")
async def generate_refresh_summary(db: Session = Depends(get_db)):
    """Use AI to generate a summary of the data refresh results."""

    if scrape_progress["active"]:
        return {"error": "Refresh still in progress"}

    if not scrape_progress["change_details"]:
        return {"summary": "No changes detected during the last refresh.", "type": "static"}

    # Check for OpenAI client
    try:
        from openai import OpenAI
        import os
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except Exception as e:
        return {"error": f"AI not available: {str(e)}"}

    # Prepare change data for AI
    changes_text = ""
    for change in scrape_progress["change_details"]:
        if change["type"] == "new":
            changes_text += f"- NEW: {change['competitor']} - {change['field']}: {change['new_value']}\n"
        else:
            changes_text += f"- CHANGED: {change['competitor']} - {change['field']}: '{change['old_value']}' → '{change['new_value']}'\n"

    # Generate AI summary
    prompt = f"""You are a competitive intelligence analyst. Summarize the following data refresh results in 3-4 sentences.
Focus on:
1. Most significant changes (pricing, threat levels, new features)
2. Any concerning trends
3. Recommended actions

Data Refresh Results:
- Competitors scanned: {scrape_progress['total']}
- Changes detected: {scrape_progress['changes_detected']}
- New data points: {scrape_progress['new_values_added']}

Detailed Changes:
{changes_text[:3000]}  # Limit to avoid token overflow

Provide a concise executive summary."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a competitive intelligence analyst providing brief, actionable summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )

        summary = response.choices[0].message.content

        # Log to activity
        log_activity(db, None, "system@certifyhealth.com", "ai_refresh_summary",
                    json.dumps({"summary_length": len(summary)}))

        return {
            "summary": summary,
            "type": "ai",
            "model": "gpt-4",
            "stats": {
                "competitors_scanned": scrape_progress["total"],
                "changes_detected": scrape_progress["changes_detected"],
                "new_values": scrape_progress["new_values_added"]
            }
        }

    except Exception as e:
        return {"error": str(e), "type": "error"}
```

### 3.2 Frontend: Refresh Complete with AI Summary

**File**: `frontend/index.html`

Update the refresh complete modal to include AI summary:

```html
<!-- Data Refresh Complete Modal (Enhanced) -->
<div id="refreshCompleteModal" class="modal-overlay" style="display: none;">
    <div class="modal complete-modal" style="max-width: 600px;">
        <div class="modal-header success-header">
            <span class="success-icon">✓</span>
            <h3>Data Refresh Complete!</h3>
        </div>
        <div class="modal-body">
            <div class="complete-stats">
                <div class="stat-row">
                    <span class="stat-label">Competitors Scanned</span>
                    <span class="stat-value" id="completeTotal">0</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Changes Detected</span>
                    <span class="stat-value" id="completeChanges">0</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">New Data Points</span>
                    <span class="stat-value" id="completeNewValues">0</span>
                </div>
            </div>

            <!-- AI Summary Section -->
            <div id="refreshAISummarySection" class="refresh-ai-summary">
                <div class="ai-summary-header-mini">
                    <span class="ai-icon">🤖</span>
                    <span>AI Analysis of Changes</span>
                </div>
                <div id="refreshAISummaryContent" class="ai-summary-content">
                    <span class="loading-text">Generating summary...</span>
                </div>
            </div>

            <!-- Change Details Accordion -->
            <div class="change-details-section">
                <button class="accordion-toggle" onclick="toggleChangeDetails()">
                    <span>📋 View Detailed Changes</span>
                    <span class="toggle-arrow">▼</span>
                </button>
                <div id="changeDetailsContent" class="change-details-content" style="display: none;">
                    <!-- Populated dynamically -->
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="viewChangeLog()">View Full Change Log</button>
            <button class="btn btn-primary" onclick="closeRefreshCompleteModal()">Done</button>
        </div>
    </div>
</div>
```

### 3.3 JavaScript: Fetch and Display AI Summary

**File**: `frontend/app_v2.js`

```javascript
async function showRefreshCompleteModal(progress) {
    const modal = document.getElementById('refreshCompleteModal');
    if (!modal) return;

    // Update stats
    document.getElementById('completeTotal').textContent = progress.total;
    document.getElementById('completeChanges').textContent = progress.changes_detected;
    document.getElementById('completeNewValues').textContent = progress.new_values_added;

    // Show modal
    modal.style.display = 'flex';

    // Fetch AI summary
    document.getElementById('refreshAISummaryContent').innerHTML =
        '<span class="loading-text">🤖 Analyzing changes...</span>';

    try {
        const summaryResult = await fetchAPI('/api/scrape/generate-summary', { method: 'POST' });

        if (summaryResult && summaryResult.summary) {
            document.getElementById('refreshAISummaryContent').innerHTML = `
                <p style="margin: 0; line-height: 1.6;">${summaryResult.summary}</p>
                <div class="summary-meta" style="margin-top: 8px; font-size: 11px; color: #94a3b8;">
                    Generated by ${summaryResult.model || 'AI'} • ${new Date().toLocaleTimeString()}
                </div>
            `;
        } else if (summaryResult.error) {
            document.getElementById('refreshAISummaryContent').innerHTML =
                `<p style="color: #94a3b8; font-style: italic;">Summary unavailable: ${summaryResult.error}</p>`;
        }
    } catch (e) {
        document.getElementById('refreshAISummaryContent').innerHTML =
            '<p style="color: #94a3b8; font-style: italic;">Could not generate AI summary.</p>';
    }

    // Populate change details
    await populateChangeDetails();
}

async function populateChangeDetails() {
    try {
        const session = await fetchAPI('/api/scrape/session');
        const detailsEl = document.getElementById('changeDetailsContent');

        if (session.change_details && session.change_details.length > 0) {
            detailsEl.innerHTML = session.change_details.map(change => `
                <div class="change-detail-item ${change.type}">
                    <div class="change-competitor">${change.competitor}</div>
                    <div class="change-field">${change.field}</div>
                    <div class="change-values">
                        ${change.old_value ? `<span class="old-value">${change.old_value}</span> →` : ''}
                        <span class="new-value">${change.new_value}</span>
                    </div>
                </div>
            `).join('');
        } else {
            detailsEl.innerHTML = '<p style="color: #94a3b8; padding: 12px;">No detailed changes recorded.</p>';
        }
    } catch (e) {
        console.error('Error loading change details:', e);
    }
}

function toggleChangeDetails() {
    const content = document.getElementById('changeDetailsContent');
    const arrow = document.querySelector('.toggle-arrow');

    if (content.style.display === 'none') {
        content.style.display = 'block';
        arrow.textContent = '▲';
    } else {
        content.style.display = 'none';
        arrow.textContent = '▼';
    }
}
```

---

## Phase 4: Refresh History & Logging

### 4.1 New Database Model: RefreshSession

**File**: `backend/database.py`

```python
class RefreshSession(Base):
    """Tracks each data refresh session with results."""
    __tablename__ = "refresh_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    competitors_scanned = Column(Integer, default=0)
    changes_detected = Column(Integer, default=0)
    new_values_added = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    ai_summary = Column(Text, nullable=True)
    status = Column(String, default="in_progress")  # in_progress, completed, failed
```

### 4.2 Persist Refresh Session

**File**: `backend/main.py`

```python
# At start of scrape/all:
refresh_session = RefreshSession(
    user_id=current_user.id if current_user else None,
    competitors_scanned=len(competitor_ids)
)
db.add(refresh_session)
db.commit()
scrape_progress["session_id"] = refresh_session.id

# At end of all scrapes:
session = db.query(RefreshSession).filter(RefreshSession.id == scrape_progress["session_id"]).first()
if session:
    session.completed_at = datetime.utcnow()
    session.changes_detected = scrape_progress["changes_detected"]
    session.new_values_added = scrape_progress["new_values_added"]
    session.status = "completed"
    db.commit()
```

### 4.3 View Refresh History Endpoint

**File**: `backend/main.py`

```python
@app.get("/api/refresh-history")
def get_refresh_history(limit: int = 10, db: Session = Depends(get_db)):
    """Get history of data refresh sessions."""
    sessions = db.query(RefreshSession).order_by(
        RefreshSession.started_at.desc()
    ).limit(limit).all()

    return [{
        "id": s.id,
        "started_at": s.started_at.isoformat() if s.started_at else None,
        "completed_at": s.completed_at.isoformat() if s.completed_at else None,
        "competitors_scanned": s.competitors_scanned,
        "changes_detected": s.changes_detected,
        "new_values_added": s.new_values_added,
        "status": s.status,
        "ai_summary": s.ai_summary
    } for s in sessions]
```

---

## Implementation Order

| Phase | Task | Priority | Est. Effort |
|-------|------|----------|-------------|
| 1.1 | Add inline progress HTML | HIGH | 15 min |
| 1.2 | Add inline progress CSS | HIGH | 15 min |
| 1.3 | Update JS for inline progress | HIGH | 30 min |
| 2.1 | Expand backend progress object | HIGH | 15 min |
| 2.2 | Track detailed changes | HIGH | 30 min |
| 2.3 | Add session details endpoint | MEDIUM | 15 min |
| 3.1 | Add AI summary endpoint | HIGH | 30 min |
| 3.2 | Update complete modal HTML | HIGH | 20 min |
| 3.3 | Add JS for AI summary | HIGH | 20 min |
| 4.1 | Add RefreshSession model | MEDIUM | 10 min |
| 4.2 | Persist sessions | MEDIUM | 20 min |
| 4.3 | Add history endpoint | LOW | 15 min |

**Total Estimated Effort**: ~4 hours

---

## Testing Checklist

### Phase 1: Inline Progress
- [ ] Inline progress bar appears when clicking "Refresh Data"
- [ ] Progress percentage updates in real-time
- [ ] Competitor count updates correctly
- [ ] Current competitor name displays
- [ ] Progress bar animates smoothly
- [ ] Hides correctly when complete

### Phase 2: Enhanced Tracking
- [ ] Recent changes appear in live feed
- [ ] Change details include old/new values
- [ ] Session endpoint returns full details

### Phase 3: AI Summary
- [ ] AI summary generates after refresh
- [ ] Summary appears in completion modal
- [ ] Handles missing API key gracefully
- [ ] Change details accordion works

### Phase 4: History
- [ ] Refresh sessions persist to database
- [ ] History endpoint returns past sessions
- [ ] AI summaries are stored

---

## Rollback Plan

If issues arise:
1. Revert to modal-based progress (already working)
2. Disable AI summary generation
3. Keep basic stats display

---

## Success Criteria

1. User can see live progress directly on Dashboard (no modal)
2. User knows exactly which competitors were scanned
3. User sees specific field-level changes (old → new)
4. AI provides actionable summary of refresh results
5. Refresh history is preserved for audit trail

---

**Document Version**: 1.0
**Last Updated**: January 25, 2026, 10:45 PM EST

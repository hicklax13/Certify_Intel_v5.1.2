---

## MASTER_TODO.md


Certify Intel - Master To Do List
IMPORTANT: This file should be updated by Claude agents after every task completion.
Always keep this list current and accurate.

Current Version: v5.0.1
Next Version: v5.0.2 (Gemini Hybrid Integration)
Active Tasks
ID	Task	Status	Assigned	Priority
5.0.1-023	Add inline progress HTML to Dashboard	pending	-	HIGH
5.0.1-024	Add inline progress CSS styles	pending	-	HIGH
5.0.1-025	Update JS for inline progress display	pending	-	HIGH
5.0.1-026	Expand backend scrape_progress object	pending	-	HIGH
5.0.1-027	Track field-level changes in scraper	pending	-	HIGH
5.0.1-028	Add /api/scrape/session endpoint	pending	-	MEDIUM
5.0.1-029	Add /api/scrape/generate-summary endpoint	pending	-	HIGH
5.0.1-030	Update refresh complete modal with AI summary	pending	-	HIGH
5.0.1-031	Add RefreshSession database model	pending	-	MEDIUM
5.0.1-032	Test full refresh flow end-to-end	pending	-	HIGH

v5.0.1 - Data Refresh Enhancement (IMPLEMENTATION_PLAN_DATA_REFRESH.md)
Goal: Replace modal-based refresh progress with inline Dashboard display + AI-powered change summary

Phase 1: Inline Progress Bar
ID	Task	Status	Details
5.0.1-023	Add inline progress HTML	pending	New component below "Last Data Refresh" indicator
5.0.1-024	Add inline progress CSS	pending	Animated progress bar, live update styling
5.0.1-025	Update JS for inline progress	pending	Replace modal functions with inline display

Phase 2: Enhanced Backend Tracking
ID	Task	Status	Details
5.0.1-026	Expand scrape_progress object	pending	Add recent_changes, change_details, errors arrays
5.0.1-027	Track field-level changes	pending	Record old/new values during scrape
5.0.1-028	Add /api/scrape/session endpoint	pending	Return full session details with changes

Phase 3: AI-Powered Summary
ID	Task	Status	Details
5.0.1-029	Add /api/scrape/generate-summary	pending	GPT-4 analysis of refresh changes
5.0.1-030	Update complete modal with AI	pending	Show AI summary + change details accordion

Phase 4: Refresh History
ID	Task	Status	Details
5.0.1-031	Add RefreshSession model	pending	New database table for session persistence
5.0.1-032	Test full flow	pending	End-to-end testing of all components
v5.0.2 - Gemini Hybrid AI Integration
Goal: Add Google Gemini as a secondary AI provider alongside OpenAI for cost savings and new features.

Estimated Savings: ~90% cost reduction on bulk tasks

Phase 1: Core Infrastructure (Required)
ID	Task	Status	Details
5.0.2-001	Add Gemini API dependencies	pending	Add google-generativeai to requirements.txt
5.0.2-002	Create Gemini provider module	pending	New file: backend/gemini_provider.py
5.0.2-003	Update .env.example with Gemini keys	pending	Add GOOGLE_AI_API_KEY, GOOGLE_AI_MODEL
5.0.2-004	Create AI router/dispatcher	pending	Route tasks to cheapest/best model
5.0.2-005	Update extractor.py for hybrid support	pending	Support both OpenAI and Gemini
5.0.2-006	Add fallback logic	pending	Switch providers on failure/rate-limit
5.0.2-007	Update CLAUDE.md with new config	pending	Document new environment variables
Phase 2: Existing Feature Migration (Optional)
ID	Task	Status	Details
5.0.2-008	Migrate executive summaries	pending	Option to use Gemini Flash
5.0.2-009	Migrate Discovery Agent	pending	Use Gemini for bulk web analysis
5.0.2-010	Migrate data extraction	pending	Hybrid extraction with cost optimization
5.0.2-011	Add model selection to UI	pending	Let users choose AI provider per task
Phase 3: New Gemini-Powered Features (Future)
ID	Task	Status	Details
5.0.2-012	Screenshot analysis	pending	Capture & analyze competitor websites visually
5.0.2-013	PDF/Document analysis	pending	Upload competitor whitepapers for insights
5.0.2-014	Video intelligence	pending	Analyze competitor demos/webinars
5.0.2-015	Real-time grounding	pending	Use Gemini's built-in web search
5.0.2-016	Bulk news processing	pending	Process 1000s of articles with Flash-Lite
Phase 4: Testing & Documentation
ID	Task	Status	Details
5.0.2-017	Unit tests for Gemini provider	pending	Test API calls, error handling
5.0.2-018	Integration tests	pending	Test hybrid routing logic
5.0.2-019	Cost comparison testing	pending	Verify savings vs OpenAI-only
5.0.2-020	Update README	pending	Document Gemini setup
5.0.2-021	Update .env.example	pending	Complete configuration guide
v5.0.2 Configuration Reference
# =============================================================================
# AI Provider Configuration (v5.0.2+)
# =============================================================================

# Provider: "openai", "google", or "hybrid" (recommended)
AI_PROVIDER=hybrid

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4.1-mini

# Google Gemini Configuration
GOOGLE_AI_API_KEY=your-gemini-api-key
GOOGLE_AI_MODEL=gemini-2.5-flash

# Hybrid Routing Rules (optional)
AI_BULK_TASKS=google          # Use Gemini for bulk processing
AI_QUALITY_TASKS=openai       # Use OpenAI for high-quality output
AI_FALLBACK_ENABLED=true      # Auto-switch on failure

Backlog (Future Versions)
v5.0.3 - Desktop App Fix
ID	Task	Status	Details
5.0.3-001	Fix .env path in installed app	pending	Resolve PyInstaller path issue
5.0.3-002	Test installed app end-to-end	pending	Verify desktop app works
5.0.3-003	Auto-updater implementation	pending	Push updates to installed apps
v5.1.0 - Cloud Deployment
ID	Task	Status	Details
5.1.0-001	Docker production config	pending	Production-ready Docker setup
5.1.0-002	Cloud deployment guide	pending	AWS/GCP/Azure instructions
5.1.0-003	CI/CD pipeline	pending	Automated testing & deployment
v5.2.0 - Team Features
ID	Task	Status	Details
5.2.0-001	Multi-user improvements	pending	Better team collaboration
5.2.0-002	Role-based dashboards	pending	Custom views per role
5.2.0-003	Shared annotations	pending	Team notes on competitors
Completed Tasks
v5.0.1 Session #5: CSS Fix & Data Refresh Planning (2026-01-25, 10:30 PM)
ID	Task	Completed	Details
5.0.1-033	Fix dashboard stats CSS visibility	2026-01-25	Scoped .stat-value white text to .complete-stats only
5.0.1-034	Fix refresh description text wrapping	2026-01-25	Changed max-width to white-space:nowrap
5.0.1-035	Create IMPLEMENTATION_PLAN_DATA_REFRESH.md	2026-01-25	4-phase plan for inline progress + AI summary

v5.0.1 Session #4: C-Suite Meeting Prep (2026-01-25, 9:11 PM)
ID	Task	Completed	Details
5.0.1-019	Fix dashboard stats display	2026-01-25	Removed duplicate endpoints, added null-safety
5.0.1-020	User-specific prompt management	2026-01-25	New UserSavedPrompt model, full CRUD API
5.0.1-021	AI summary progress bar	2026-01-25	Real-time 5-step progress modal
5.0.1-022	Code cleanup duplicate endpoints	2026-01-25	Removed redundant dashboard/stats, competitors

v5.0.1 UI/UX Session (2026-01-25)
ID	Task	Completed	Details
5.0.1-009	Fix admin login password hash	2026-01-25	Reset password to match SECRET_KEY
5.0.1-010	Update login page logo	2026-01-25	New centered app icon, removed checkered bg
5.0.1-011	Style secondary buttons	2026-01-25	Light gray (#C4CAD0) with shadows
5.0.1-012	Style user avatar button	2026-01-25	Navy blue (#122753) with blue glow
5.0.1-013	Style notification button	2026-01-25	Matching gray style, smaller size
5.0.1-014	Add prompt caching system	2026-01-25	Instant loading with DEFAULT_PROMPTS embedded
5.0.1-015	Update AI prompt for live data	2026-01-25	New prompt proves live data usage in demos
5.0.1-016	Enhance backend data for AI	2026-01-25	Full competitor details sent to AI
5.0.1-017	Add Last Data Refresh indicator	2026-01-25	Shows timestamp on dashboard
5.0.1-018	Add uvicorn startup to main.py	2026-01-25	python main.py now starts server

v5.0.1 (Previous Session)
ID	Task	Completed	Details
5.0.1-001	Rename repo to v5.0.1	2026-01-25	GitHub repo renamed
5.0.1-002	Add Google API keys to .env.example	2026-01-25	GOOGLE_API_KEY, GOOGLE_CX added
5.0.1-003	Update CLAUDE.md with full config	2026-01-25	Complete API key reference
5.0.1-004	Document launch options	2026-01-25	Local, Docker, Desktop options
5.0.1-005	Research OpenAI models (2026)	2026-01-25	Recommended gpt-4.1-mini
5.0.1-006	Research Gemini/Vertex AI	2026-01-25	94% cost savings identified
5.0.1-007	Create v5.0.2 Gemini Hybrid plan	2026-01-25	21 tasks across 4 phases
5.0.1-008	Successfully launch web version	2026-01-25	Running at localhost:8000
v2.0.1 (Previous)
ID	Task	Completed	Details
-	Desktop app build infrastructure	2026-01-25	PyInstaller + Electron setup
-	Fix .env loading from exe directory	2026-01-25	Modified main.py
-	Fix PIL missing module	2026-01-25	Updated certify_backend.spec
v2.0.0 (Previous)
ID	Task	Completed	Details
-	Remove paid API scrapers	2026-01-24	~737 lines deleted
-	Create test suite	2026-01-24	9 tests, all passing
-	Security audit	2026-01-24	JWT, SQL injection prevention
How to Use This File
For Claude Agents
Before starting work: Check "Active Tasks" for current priorities
When starting a task: Move task to "Active Tasks" with your session ID
When completing a task: Move to "Completed Tasks" with date
When blocked: Add notes to the task and mark as blocked
Task Status Values
pending - Not started
in_progress - Currently being worked on
blocked - Cannot proceed (add notes)
completed - Done (move to Completed section)
cancelled - No longer needed
Priority Levels
critical - Must be done immediately
high - Should be done this session
medium - Should be done soon
low - Nice to have
Last Updated: 2026-01-25 (10:45 PM EST)
Version: v5.0.1
Updated By: Claude Opus 4.5 (session: CSS Fix & Data Refresh Planning)

---

## Session End Summary (January 25, 2026, 10:45 PM)

### Changes Made This Session:
1. **CSS Fix** - Dashboard stat card numbers now visible (was white-on-white)
2. **CSS Fix** - Refresh description text stays on one line
3. **Planning** - Created comprehensive 4-phase Data Refresh Enhancement plan

### Files Modified:
- `frontend/styles.css` - Lines 661-666, 2962-2971
- `IMPLEMENTATION_PLAN_DATA_REFRESH.md` - New file
- `CLAUDE.md` - Session documentation
- `MASTER_TODO.md` - Task updates

### Next Session Should:
1. Start with Task 5.0.1-023 (inline progress HTML)
2. Follow IMPLEMENTATION_PLAN_DATA_REFRESH.md phases
3. Test each component before moving to next
4. Total estimated time: ~3.5 hours
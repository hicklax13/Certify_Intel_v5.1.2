# Certify Intel - Team Task Assignments

**Project:** Certify Intel
**Project Start:** January 5, 2026
**Minimal Working Prototype Due:** January 22, 2026
**Minimal Viable Product Due:** February 9, 2026

---

# Part 1: Team Roles & Responsibilities

---

## Product Development Lead

### Role Description

The Product Development Lead is responsible for building the backend "engine" that powers the competitive intelligence system. This includes the cloud infrastructure, web scraping automation, AI-powered data extraction, and connecting the backend to the Excel dashboard via Power Query. This role ensures that raw competitor data flows automatically from websites into the Excel dashboard without manual intervention.

### Primary Focus

- Building the automated data collection engine
- Integrating GPT-4 for intelligent data extraction
- Connecting backend to Excel dashboard
- Ensuring weekly automated refreshes work reliably

### Tasks

**Minimal Working Prototype Phase (January 5-22)**

- [ ] Create Excel template structure with all 32 data columns
- [ ] Define data schema and column naming conventions
- [ ] Support Data Lead with technical data formatting questions
- [ ] Ensure Excel file is structured for future Power Query connection

**Minimal Viable Product Phase (January 23 - February 9)**

- [ ] Set up cloud infrastructure (AWS or Azure)
- [ ] Deploy PostgreSQL database for competitor data storage
- [ ] Build Playwright web scraper for competitor websites
- [ ] Create FastAPI backend with REST endpoints
- [ ] Integrate OpenAI GPT-4 API for data extraction
- [ ] Build extraction prompts for each data category (pricing, features, etc.)
- [ ] Create Power Query connection from Excel to backend API
- [ ] Implement scheduled weekly scraping (Celery)
- [ ] Build email alert system for critical changes
- [ ] Write technical documentation for backend system
- [ ] Conduct backend testing and debugging

---

## Team Lead / Coordinator

### Role Description

The Team Lead serves as the project's primary coordinator and the main point of contact between the client, advisors, and team members. This role ensures workstreams are aligned, removes blockers, facilitates decision-making, and keeps the project on track. The Team Lead has the authority to help any team member and makes final approval decisions on deliverables.

### Primary Focus

- Cross-team coordination and communication
- Client and advisor relationship management
- Decision-making and approvals
- Ensuring deliverables meet quality standards

### Tasks

**Minimal Working Prototype Phase (January 5-22)**

- [ ] Kick off project with team alignment meeting
- [ ] Approve "middle market" definition and competitor criteria
- [ ] Review and prioritize initial competitor list
- [ ] Facilitate communication with client stakeholders
- [ ] Review and approve Minimal Working Prototype dashboard before delivery

**Minimal Viable Product Phase (January 23 - February 9)**

- [ ] Conduct weekly status check-in meetings (30 minutes each)
- [ ] Coordinate between team members when dependencies arise
- [ ] Communicate progress updates to client and advisors
- [ ] Review AI-generated insights for quality and relevance
- [ ] Resolve blockers and escalate issues as needed
- [ ] Attend Executive Presentation Workshop (January 27)
- [ ] Lead intensive weekend sessions (February 6-8)
- [ ] Conduct final Minimal Viable Product review and sign-off
- [ ] Lead final presentation to client (week of February 9)
- [ ] Facilitate handoff to summer team

---

## Research Lead

### Role Description

The Research Lead is responsible for all competitive research activities. This role maps the competitive landscape, identifies who qualifies as a competitor, understands what solutions target customers currently use instead of Certify Health, and finds reliable data sources for each data point. The Research Lead's work forms the foundation that the entire dashboard is built upon.

### Primary Focus

- Defining the competitive landscape
- Identifying and qualifying competitors
- Understanding target customer buying behavior
- Finding and validating data sources
- Matching Certify Health products to competitor solutions

### Tasks

**Minimal Working Prototype Phase (January 5-22)**

- [ ] Define criteria for what qualifies as a competitor
- [ ] Create competitor qualification framework (direct versus adjacent)
- [ ] Identify initial list of 40+ competitors
- [ ] Map competitors to Certify Health product categories (Intake, Verification, Payments, etc.)
- [ ] Gather website URLs and key pages for each competitor
- [ ] Research target customer segments and what they currently use
- [ ] Initial data collection for 15 priority competitors

**Minimal Viable Product Phase (January 23 - February 9)**

- [ ] Complete competitive landscape map
- [ ] Identify data sources for each of the 32 data points
- [ ] Document where to find pricing information per competitor
- [ ] Document where to find customer/logo information per competitor
- [ ] Research funding and valuation data (Crunchbase, news)
- [ ] Research hiring trends and employee counts (LinkedIn)
- [ ] Validate AI-extracted data for accuracy
- [ ] Monitor competitor news and announcements weekly
- [ ] Identify gaps in available data and document limitations
- [ ] Create research methodology documentation

---

## Data Lead

### Role Description

The Data Lead is responsible for building and maintaining the Excel dashboard. This role takes the research from the Research Lead and translates it into structured data points that populate the dashboard. The Data Lead owns the data model, KPI calculations, and ensures the dashboard accurately reflects the competitive intelligence gathered.

### Primary Focus

- Building the Excel dashboard structure
- Translating research into standardized data points
- Creating KPI formulas and calculations
- Ensuring data accuracy and consistency
- Managing data entry and updates

### Tasks

**Minimal Working Prototype Phase (January 5-22)**

- [ ] Build Excel workbook structure with all sheets
- [ ] Create data entry sheet with 32 columns
- [ ] Define data types and validation rules for each column
- [ ] Populate 10-15 competitors with research data
- [ ] Build initial pivot tables for data analysis
- [ ] Create dropdown lists for standardized fields (Threat Level, Status, etc.)

**Minimal Viable Product Phase (January 23 - February 9)**

- [ ] Expand competitor data to all 40+ companies
- [ ] Build pricing comparison matrix
- [ ] Build feature comparison matrix
- [ ] Create KPI formulas (growth rates, market share estimates, etc.)
- [ ] Build market segment analysis views
- [ ] Create conditional formatting rules for visual indicators
- [ ] Test Power Query data refresh with Product Development Lead
- [ ] Conduct data quality audit
- [ ] Fix data inconsistencies and errors
- [ ] Document data definitions and sources per column

---

## Delivery Lead

### Role Description

The Delivery Lead is responsible for the visual presentation and documentation of the dashboard. This role focuses on making the dashboard visually compelling, easy to understand, and presentation-ready. The Delivery Lead also documents how the dashboard works so future users can understand and maintain it.

### Primary Focus

- Dashboard layout and visual design
- Charts, graphs, and data visualizations
- User experience and navigation
- Documentation and user guides

### Tasks

**Minimal Working Prototype Phase (January 5-22)**

- [ ] Design overall dashboard layout and navigation
- [ ] Create color scheme and visual style guide
- [ ] Design chart templates (bar, pie, line charts)
- [ ] Build dashboard summary/overview sheet
- [ ] Apply professional formatting and branding

**Minimal Viable Product Phase (January 23 - February 9)**

- [ ] Create advanced visualizations (heatmaps, comparison charts)
- [ ] Design competitor profile view layout
- [ ] Build threat level visualization
- [ ] Create market segment breakdown charts
- [ ] Design change log / alert history view
- [ ] Write user guide documentation
- [ ] Create "How to Use" instructions sheet
- [ ] Document chart and graph mechanics
- [ ] Polish final dashboard visuals
- [ ] Prepare presentation materials for stakeholders
- [ ] Support preparation for Clinics Intensive Weekend (February 6-8)

---

# Part 2: Tasks by Implementation Order

The following is a logical sequence of all tasks, grouped by phase and ordered by dependencies.

---

## Minimal Working Prototype Phase: January 5-22 (Logical Order)

### Week 1 (January 5-11) — Foundation

| Order | Task | Role |
|-------|------|------|
| 1 | Kick off project with team alignment meeting | Team Lead / Coordinator |
| 2 | Define criteria for what qualifies as a competitor | Research Lead |
| 3 | Create competitor qualification framework | Research Lead |
| 4 | Approve "middle market" definition and competitor criteria | Team Lead / Coordinator |
| 5 | Create Excel template structure with all 32 data columns | Product Development Lead |
| 6 | Define data schema and column naming conventions | Product Development Lead |
| 7 | Design overall dashboard layout and navigation | Delivery Lead |
| 8 | Create color scheme and visual style guide | Delivery Lead |

### Week 2 (January 12-18) — Research & Data Structure

| Order | Task | Role |
|-------|------|------|
| 9 | Identify initial list of 40+ competitors | Research Lead |
| 10 | Map competitors to Certify Health product categories | Research Lead |
| 11 | Gather website URLs and key pages for each competitor | Research Lead |
| 12 | Build Excel workbook structure with all sheets | Data Lead |
| 13 | Create data entry sheet with 32 columns | Data Lead |
| 14 | Define data types and validation rules for each column | Data Lead |
| 15 | Create dropdown lists for standardized fields | Data Lead |
| 16 | Design chart templates | Delivery Lead |

### Week 3 (January 19-22) — Data Population & Minimal Working Prototype Delivery

| Order | Task | Role |
|-------|------|------|
| 17 | Research target customer segments | Research Lead |
| 18 | Initial data collection for 15 priority competitors | Research Lead |
| 19 | Populate 10-15 competitors with research data | Data Lead |
| 20 | Build initial pivot tables for data analysis | Data Lead |
| 21 | Support Data Lead with technical data formatting | Product Development Lead |
| 22 | Build dashboard summary/overview sheet | Delivery Lead |
| 23 | Review and prioritize initial competitor list | Team Lead / Coordinator |
| 24 | Ensure Excel file is structured for future Power Query | Product Development Lead |
| 25 | Apply professional formatting and branding | Delivery Lead |
| 26 | Facilitate communication with client stakeholders | Team Lead / Coordinator |
| 27 | Review and approve Minimal Working Prototype dashboard | Team Lead / Coordinator |

---

## Minimal Viable Product Phase: January 23 - February 9 (Logical Order)

### Week 4 (January 23-26) — Backend Foundation & Expanded Research

| Order | Task | Role |
|-------|------|------|
| 28 | Set up cloud infrastructure (AWS or Azure) | Product Development Lead |
| 29 | Deploy PostgreSQL database | Product Development Lead |
| 30 | Complete competitive landscape map | Research Lead |
| 31 | Identify data sources for each of the 32 data points | Research Lead |
| 32 | Document where to find pricing information per competitor | Research Lead |
| 33 | Build Playwright web scraper | Product Development Lead |
| 34 | Create FastAPI backend with REST endpoints | Product Development Lead |
| 35 | Expand competitor data to all 40+ companies | Data Lead |
| 36 | Conduct weekly status check-in | Team Lead / Coordinator |

### Week 5 (January 27 - February 2) — AI Integration & Analysis

| Order | Task | Role |
|-------|------|------|
| 37 | Integrate OpenAI GPT-4 API for data extraction | Product Development Lead |
| 38 | Build extraction prompts for each data category | Product Development Lead |
| 39 | Research funding and valuation data | Research Lead |
| 40 | Research hiring trends and employee counts | Research Lead |
| 41 | Build pricing comparison matrix | Data Lead |
| 42 | Build feature comparison matrix | Data Lead |
| 43 | Create KPI formulas | Data Lead |
| 44 | Validate AI-extracted data for accuracy | Research Lead |
| 45 | Create advanced visualizations | Delivery Lead |
| 46 | Design competitor profile view layout | Delivery Lead |
| 47 | Coordinate between team members | Team Lead / Coordinator |
| 48 | Attend Executive Presentation Workshop (January 27) | Team Lead / Coordinator |
| 49 | Conduct weekly status check-in | Team Lead / Coordinator |

### Week 6 (February 3-9) — Automation, Polish, Delivery

| Order | Task | Role |
|-------|------|------|
| 50 | Create Power Query connection from Excel to backend | Product Development Lead |
| 51 | Implement scheduled weekly scraping | Product Development Lead |
| 52 | Build email alert system for critical changes | Product Development Lead |
| 53 | Test Power Query data refresh | Data Lead |
| 54 | Monitor competitor news weekly | Research Lead |
| 55 | Create research methodology documentation | Research Lead |
| 56 | Conduct data quality audit | Data Lead |
| 57 | Fix data inconsistencies and errors | Data Lead |
| 58 | Document data definitions and sources | Data Lead |
| 59 | Build threat level visualization | Delivery Lead |
| 60 | Create market segment breakdown charts | Delivery Lead |
| 61 | Write user guide documentation | Delivery Lead |
| 62 | Create "How to Use" instructions sheet | Delivery Lead |
| 63 | Polish final dashboard visuals | Delivery Lead |
| 64 | Write technical documentation for backend | Product Development Lead |
| 65 | Conduct backend testing and debugging | Product Development Lead |
| 66 | Lead intensive weekend sessions (February 6-8) | Team Lead / Coordinator |
| 67 | Support Clinics Intensive Weekend | Delivery Lead |
| 68 | Review AI-generated insights | Team Lead / Coordinator |
| 69 | Conduct final Minimal Viable Product review and sign-off | Team Lead / Coordinator |
| 70 | Prepare presentation materials | Delivery Lead |
| 71 | Lead final presentation to client (week of February 9) | Team Lead / Coordinator |
| 72 | Facilitate handoff to summer team | Team Lead / Coordinator |

---

## Key Dates Summary

| Date | Event |
|------|-------|
| January 5, 2026 | Project Start / Team Onboarding |
| January 22, 2026 | Minimal Working Prototype Due |
| January 27, 2026 | Executive Presentation Workshop |
| February 6-8, 2026 | Clinics Intensive Weekend |
| Week of February 9, 2026 | Final Presentations / Minimal Viable Product Due |

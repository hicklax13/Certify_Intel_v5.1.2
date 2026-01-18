# Certify Intel - Data Schema Documentation

**Version:** 1.0 | **Last Updated:** January 17, 2026

---

## Overview

This document defines the 32 data columns used in the Certify Intel competitive intelligence dashboard. Each column is categorized, typed, and documented with expected sources and validation rules.

---

## Column Categories

| Category | Columns | Color Code |
|----------|---------|------------|
| Core | 1-7 | Blue (#2F5496) |
| Pricing | 8-10 | Green (#548235) |
| Product | 11-14 | Purple (#7030A0) |
| Market | 15-21 | Orange (#C65911) |
| Company | 22-28 | Navy (#305496) |
| Digital | 29-32 | Gold (#BF8F00) |

---

## Column Definitions

### Core Data (Columns 1-7)

| # | Column Name | Data Type | Required | Description |
|---|-------------|-----------|----------|-------------|
| 1 | Competitor Name | Text | Yes | Official company name |
| 2 | Website | URL | Yes | Primary company website (full URL) |
| 3 | Status | Dropdown | Yes | Active, Inactive, Acquired, Watch |
| 4 | Threat Level | Dropdown | Yes | High, Medium, Low, Watch |
| 5 | Last Updated | Date | Auto | Date of last data update (YYYY-MM-DD) |
| 6 | Notes | Text | No | Free-form notes and observations |
| 7 | Data Quality Score | Number | No | 1-100 confidence score on data accuracy |

**Status Values:**

- **Active:** Currently operating and selling
- **Inactive:** No longer operating
- **Acquired:** Purchased by another company
- **Watch:** New entrant or emerging competitor

**Threat Level Values:**

- **High:** Direct competitor, similar target market
- **Medium:** Adjacent competitor or partial overlap
- **Low:** Tangential or non-competing
- **Watch:** Monitor for potential threat changes

---

### Pricing Data (Columns 8-10)

| # | Column Name | Data Type | Required | Description |
|---|-------------|-----------|----------|-------------|
| 8 | Pricing Model | Dropdown | Yes | How the competitor charges |
| 9 | Base Price | Currency | Preferred | Starting price or typical cost |
| 10 | Price Unit | Text | Preferred | Unit of pricing (per user, per month, etc.) |

**Pricing Model Values:**

- Per User
- Per Provider
- Per Location
- Per Visit
- Flat Rate
- Tiered
- Custom
- Unknown

---

### Product Data (Columns 11-14)

| # | Column Name | Data Type | Required | Description |
|---|-------------|-----------|----------|-------------|
| 11 | Product Categories | Text | Yes | Semicolon-separated list of products (e.g., Intake; Payments; Scheduling) |
| 12 | Key Features | Text | Yes | Main capabilities and features |
| 13 | Integration Partners | Text | Preferred | EHR/PM systems they integrate with |
| 14 | Certifications | Text | Preferred | Security and compliance certifications (e.g., HIPAA; SOC2; HITRUST) |

**Standard Product Categories:**

- Patient Intake
- Insurance Verification
- Payments
- Scheduling
- Patient Portal
- Telehealth
- RCM (Revenue Cycle Management)
- PM (Practice Management)
- EHR (Electronic Health Record)

---

### Market Data (Columns 15-21)

| # | Column Name | Data Type | Required | Description |
|---|-------------|-----------|----------|-------------|
| 15 | Target Segments | Text | Yes | Customer segments they target (e.g., Health Systems; Specialty Practices) |
| 16 | Customer Size Focus | Dropdown | Yes | Practice size they target |
| 17 | Geographic Focus | Text | Preferred | Geographic markets (e.g., US National, CA only) |
| 18 | Customer Count | Text | Preferred | Estimated number of customers |
| 19 | Customer Acquisition Rate | Text | Preferred | How fast they're adding customers |
| 20 | Key Customers | Text | No | Notable customer names or references |
| 21 | G2 Rating | Number | Preferred | G2 Crowd rating (1.0-5.0) |

**Customer Size Focus Values:**

- Solo
- Small (1-15)
- Medium (15-50)
- Large (50+)
- Enterprise
- All Sizes

---

### Company Data (Columns 22-28)

| # | Column Name | Data Type | Required | Description |
|---|-------------|-----------|----------|-------------|
| 22 | Employee Count | Text | Preferred | Current headcount (e.g., 500+) |
| 23 | Employee Growth Rate | Text | No | Year-over-year growth (e.g., 20% YoY) |
| 24 | Year Founded | Number | Preferred | Year company was founded |
| 25 | Headquarters | Text | Preferred | City, State of HQ |
| 26 | Funding Total | Text | Preferred | Total funding raised (e.g., $50M+) |
| 27 | Latest Round | Text | No | Most recent funding round |
| 28 | PE/VC Backers | Text | No | Key investors or ownership |

---

### Digital Presence Data (Columns 29-32)

| # | Column Name | Data Type | Required | Description |
|---|-------------|-----------|----------|-------------|
| 29 | Website Traffic (Monthly) | Text | Preferred | Estimated monthly visits (e.g., 100K+) |
| 30 | Social Following | Text | No | Total social media following |
| 31 | Recent Product Launches | Text | No | Recent feature or product announcements |
| 32 | News Mentions (30d) | Number | No | Count of news mentions in last 30 days |

---

## Data Sources

| Data Category | Primary Sources |
|---------------|-----------------|
| Core | Company website, LinkedIn |
| Pricing | Pricing pages, sales calls, G2/Capterra |
| Product | Product pages, feature lists, documentation |
| Market | Case studies, press releases, LinkedIn |
| Company | LinkedIn, Crunchbase, press releases |
| Digital | SimilarWeb, social profiles, Google News |

---

## Validation Rules

### Required Fields

All competitors must have:

- Competitor Name
- Website
- Status
- Threat Level
- Product Categories
- Target Segments
- Customer Size Focus

### Format Standards

- URLs: Full URL with https://
- Dates: YYYY-MM-DD format
- Prices: Include currency symbol (e.g., $199)
- Lists: Semicolon-separated (e.g., Intake; Payments; Scheduling)
- Percentages: Include % symbol (e.g., 20% YoY)
- Counts: Use + for estimates (e.g., 1000+)

---

## Data Quality Scoring

| Score | Meaning |
|-------|---------|
| 90-100 | Verified from primary sources |
| 70-89 | Good data with some estimates |
| 50-69 | Partial data, needs validation |
| Below 50 | Significant data gaps |

---

## Change Tracking

All changes to competitor data should be logged in the Change Log sheet with:

- Date of change
- Competitor affected
- Type of change (Pricing, Feature, Funding, etc.)
- Previous value
- New value
- Source of update
- Severity (High, Medium, Low)

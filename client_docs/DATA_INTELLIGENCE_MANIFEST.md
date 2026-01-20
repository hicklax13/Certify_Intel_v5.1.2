# Certify Health Intel: Data Intelligence Manifest

This document defines the **scope, criteria, and metrics** currently used by the Certify Health Intelligence Engine.

## 1. Competitor Definition & Scope

The Autonomous Discovery Agent ("Certify Scout") qualifies a website as a "Competitor" only if it meets **ALL** of the following criteria (Logic: `discovery_agent.py`):

### A. Context Requirement (Must Match)

The website **MUST** contain at least one of these context markers:

- `healthcare`
- `medical`
- `hospital`
- `practice`

### B. Core Capabilities (Must Match)

The website **MUST** offer a product or service related to:

- **Patient Intake** / Digital Check-in
- **Revenue Cycle Management** (RCM)
- **Biometric Authentication** (Healthcare context)
- **Patient Engagement**

### C. Exclusion Criteria (Negative Filter)

The system **REJECTS** pages that appear to be:

- "Top 10" lists, Blogs, News Articles, Job Postings, Investment sites.
- Keywords excluded: `review`, `best`, `top 10`, `blog`, `article`, `career`, `salary`.

---

## 2. Data Dictionary: Scraped Metrics

The system scrapes and extracts the following **30+ data points** for each qualified competitor.

| Category | Metric | Definition / Extraction Prompt | Source |
| :--- | :--- | :--- | :--- |
| **Pricing** | `pricing_model` | How they charge (e.g., 'Per Visit', 'Subscription', 'Custom') | 🤖 AI Extraction |
| | `base_price` | Starting price point (e.g., '$199/month', '$0.10/check-in') | 🤖 AI Extraction |
| | `price_unit` | Unit for the price (e.g., 'provider/month') | 🤖 AI Extraction |
| **Product** | `product_categories` | Main product types (e.g., 'Patient Intake; Payments') | 🤖 AI Extraction |
| | `key_features` | List of specific capabilities (e.g., 'OCR Scanning, facial recognition') | 🤖 AI Extraction |
| | `integration_partners` | EHRs they integrate with (e.g., 'Epic, Cerner, Athena') | 🤖 AI Extraction |
| | `certifications` | Security/Compliance (e.g., 'HIPAA, SOC2, HITRUST') | 🤖 AI Extraction |
| | `recent_launches` | New features released recently | 🤖 AI Extraction |
| **Market** | `target_segments` | Core audience (e.g., 'Health Systems', 'Private Practice') | 🤖 AI Extraction |
| | `customer_size_focus` | Preferred practice size (Small, Medium, Enterprise) | 🤖 AI Extraction |
| | `geographic_focus` | Active regions (e.g., 'US', 'North America') | 🤖 AI Extraction |
| | `customer_count` | Total number of clients/providers | 🤖 AI Extraction |
| | `key_customers` | Names of notable health system clients | 🤖 AI Extraction |
| **Org** | `employee_count` | Total headcount | 🤖 AI Extraction / LinkedIn |
| | `year_founded` | Year established | 🤖 AI Extraction |
| | `headquarters` | Main office location | 🤖 AI Extraction |
| | `funding_total` | Total capital raised (e.g., '$50M') | 🤖 AI Extraction / Crunchbase |
| | `investors` | Key VC/PE backers | 🤖 AI Extraction |
| **Live** | `stock_price` | Real-time Share Price (if public) | 📈 Yahoo Finance |
| | `market_cap` | Total Market Capitalization | 📈 Yahoo Finance |
| | `stock_change` | Daily % Change | 📈 Yahoo Finance |
| **Signals** | `g2_rating` | Average User Review Score (0-5.0) | ⭐ G2 Scraper |
| | `threat_level` | Calculated Threat Score (High/Med/Low) | 🧠 Internal Algo |

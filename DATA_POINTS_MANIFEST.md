# Certify Intel - Data Collection Manifest

This document outlines every data point the system collects from various sources (Web Scraping, AI Extraction, and Real-Time APIs).

## 1. Stock Market Data (Real-Time via Yahoo Finance API)

*Applied automatically to Public Companies (e.g., Phreesia, CareCloud, Teladoc)*

- **Current Price** (Live market price)
- **Price Change ($)** (Day's movement)
- **Price Change (%)** (Day's percentage move)
- **Market Capitalization** (Total company value)
- **P/E Ratio** (Price-to-Earnings, valuation metric)
- **EPS** (Earnings Per Share)
- **Beta** (Volatility relative to market)
- **Volume** (Daily trading volume)
- **52-Week High**
- **52-Week Low**
- **Analyst Target Price** (Mean estimate)

## 2. Company Fundamentals (Web Scraped & AI Extracted)

*Extracted from Company "About" pages, LinkedIn, and Crunchbase*

- **Company Name**
- **Headquarters Location**
- **Year Founded**
- **Employee Count** (Range or specific)
- **Employee Growth Rate** (If available)
- **Funding Total** (Total capital raised)
- **Latest Funding Round** (Series A, B, IPO, etc.)
- **Investors/Backers** (VC/PE firms involved)

## 3. Product Intelligence (Web Scraped)

*Extracted from "Solutions" and "Platform" pages*

- **Product Categories** (e.g., Patient Intake, Telehealth, Billing)
- **Key Features** (Specific capabilities listed)
- **Integration Partners** (EHRs: Epic, Cerner, Athenahealth, etc.)
- **Certifications** (SOC2, HIPAA, HITRUST)

## 4. Pricing & Sales (Web Scraped)

*Extracted from "Pricing" pages*

- **Pricing Model** (Per Provider, Per Visit, Flat Fee)
- **Base Price** (Starting cost if public)
- **Price Unit** (Frequency of billing)

## 5. Market Strategy (Web Scraped)

- **Target Customer Segments** (Small Practices vs. Health Systems)
- **Customer Count** (Total active providers/practices)
- **Key Customers** (Case studies/Logos displayed)
- **Geographic Focus** (US-only, Global, etc.)

## 6. Digital Footprint (External Tools/Scraped)

- **G2 Rating** (User review score)
- **Website Traffic** (Monthly visits estimate)
- **Social Media Following** (LinkedIn/Twitter follower counts)
- **Recent Launches** (New features announced in blog)

## 7. News & Signals (Google News Scraper)

- **Recent Articles** (Titles, Snippets, URLs)
- **Sentiment** (Derived from article tone)

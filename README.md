# Certify Health Intel - Competitive Intelligence Dashboard

![Certify Intel Banner](frontend/logo.png)

## 📖 Overview

**Certify Health Intel** is a mission-critical competitive intelligence platform designed specifically for **Certify Health**. It provides a centralized, real-time dashboard to track, analyze, and counter competitors in the healthcare technology space.

The system aggregates data from multiple sources—public financial filings, web scrapers, and manual field intelligence—to provide a 360-degree view of the competitive landscape. It empowers the sales, product, and leadership teams with actionable insights to maintain Certify Health's market leadership.

## 🎯 Who Is This For?

- **Executive Leadership**: For high-level market summaries, threat analysis, and strategic planning.
- **Sales Team**: For instant access to "Battlecards," feature comparisons, and win/loss data to close more deals.
- **Product Management**: To identify feature gaps, monitor competitor releases, and guide the product roadmap.
- **Strategy & Ops**: To track market shifts, funding events, and M&A activity.

## ✨ Key Features

### 🔍 Real-Time Intelligence

- **Automated Tracking**: Monitors 30+ data points per competitor including pricing, customers, and employee growth.
- **AI Discovery Agent**: "Certify Scout" autonomously crawls the web to identify emerging threats and new market entrants.
- **Change Detection**: Alerts system that highlights significant changes in competitor messaging or pricing.

### 📊 Advanced Analytics

- **AI Executive Summary**: Generates weekly strategic briefings using GPT-4 analysis of all collected data.
- **Market Positioning Map**: Visualizes competitors by threat level, company size, and market focus.
- **Feature Gap Analysis**: Side-by-side product comparison matrices.

### 🛠️ Operational Tools

- **Battlecard Generator**: One-click PDF generation of sales battlecards.
- **Data Quality Engine**: Scores data freshness and completeness to ensure trust in the insights.
- **Multi-Platform Access**: Accessible via a responsive Web Dashboard or a standalone Desktop Application.

## 🏗️ Tech Stack & Architecture

This project is built with a modern, scalable architecture designed for performance and ease of deployment.

### **Backend (Python)**

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - High-performance async web framework.
- **Database**: **SQLite** (with SQLAlchemy ORM) - Lightweight and zero-config for easy deployment.
- **AI/ML**: **OpenAI GPT-4** Integration - For data extraction, summarization, and strategic analysis.
- **Scraping**: **Playwright** & **BeautifulSoup** - For robust web scraping and dynamic content handling.
- **Task Management**: **APScheduler** - For scheduling periodic background scraping jobs.
- **Reporting**: **ReportLab** - For programmatic PDF generation.

### **Frontend (Web)**

- **Core**: HTML5, Vanilla JavaScript (ES6+), CSS3.
- **Styling**: Custom CSS variables for a premium, dark-mode aesthetic (Glassmorphism design).
- **Visualization**: **Chart.js** - For interactive market maps and trend charts.
- **PWA**: Fully capable Progressive Web App with service workers.

### **DesktopWrapper**

- **Framework**: [Electron](https://www.electronjs.org/) - Wraps the web application for a native desktop experience.
- **Build Tools**: **electron-builder** - Generates `.exe` (Windows) and `.dmg` (macOS) installers.

## 📂 Project Structure

```
Project_Intel/
├── backend/                  # The Brain (Python API)
│   ├── main.py              # Application entry point
│   ├── database.py          # Data models & storage
│   ├── discovery_agent.py   # AI scraping logic
│   ├── analytics.py         # Data processing engine
│   └── [scrapers]           # Modular scraper scripts
├── frontend/                 # The Face (UI/UX)
│   ├── index.html           # Single Page Application
│   ├── app.js               # Client-side logic
│   └── styles.css           # Custom design system
├── desktop-app/              # The Wrapper (Electron)
│   ├── electron/            # Native integration
│   └── dist/                # Installers output
└── client_docs/              # Intelligence Library
    ├── [Project Plans]      # Strategic roadmaps
    ├── [Deliverables]       # Final reports
    └── [Templates]          # Excel dashboards
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.9+
- Node.js (for Desktop App only)
- OpenAI API Key (for AI features)

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Configure Environment
cp .env.example .env
# Edit .env with your keys:
# OPENAI_API_KEY=sk-...
# SMTP_PASSWORD=...

# Run Server
uvicorn main:app --reload --port 8000
```

### 2. Desktop App (Optional)

```bash
cd desktop-app
npm install
npm start
```

## 🛡️ Security & Privacy

- **Role-Based Access**: Multi-tier authentication (Admin, Analyst, Viewer).
- **Local-First Data**: All competitor data is stored in your local SQL database unless configured otherwise.
- **Audit Logs**: Full change history tracking for data integrity.

## 👥 Contributors

Developed for **Certify Health** by the Innovation Team.

- **Lead Developer**: Connor Hickey
- **Project Repository**: [GitHub - Project_Intel](https://github.com/hicklax13/Project_Intel)

---
*Confidential - For Internal Use Only*

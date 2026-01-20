# Certify Health Intel - Competitive Intelligence Dashboard

A modern competitive intelligence platform for healthcare technology companies. Track competitors, monitor market changes, and generate actionable insights powered by AI.

## 🚀 Features

- **Real-time Competitor Tracking**: Monitor pricing, features, funding, and market positioning
- **AI-Powered Discovery**: Automatically discover new competitors using OpenAI GPT
- **Change Log**: Track all competitor data changes with severity scoring
- **Analytics & Reports**: Generate executive briefings, battlecards, and comparison reports
- **Data Quality Dashboard**: Monitor data completeness and freshness
- **Desktop & Web App**: Run as standalone Electron app or web application

## 📁 Project Structure

```
Project_Intel/
├── backend/          # Python FastAPI backend
│   ├── main.py      # Main application entry point
│   ├── database.py  # SQLAlchemy models
│   ├── requirements.txt
│   ├── .env.example # Environment template
│   └── [scrapers]   # Data source integrations
├── frontend/         # HTML/CSS/JS frontend
│   ├── index.html   # Main dashboard
│   ├── login.html   # Authentication
│   ├── app.js       # Application logic
│   └── styles.css   # Styling
└── desktop-app/      # Electron wrapper (optional)
    ├── electron/
    └── package.json
```

## 🛠️ Installation & Setup

### Backend (Python)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key and SMTP settings
   ```

4. Run the backend:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Desktop App (Electron - Optional)

1. Navigate to the desktop-app directory:
   ```bash
   cd desktop-app
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the desktop app:
   ```bash
   npm start
   ```

4. Build installer:
   ```bash
   # Windows
   npm run build:win
   
   # macOS
   npm run build:mac
   ```

## 🌐 Access

- **Web App**: http://localhost:8000
- **Login**: Default credentials - admin@certifyhealth.com / admin123
- **API Docs**: http://localhost:8000/docs

## 📊 Key Endpoints

- `GET /api/competitors` - List all competitors
- `POST /api/competitors` - Add new competitor
- `GET /api/analytics/summary` - AI executive summary
- `GET /api/changes` - Recent competitor changes
- `POST /api/scrape` - Trigger data refresh

## 🔑 Required Configuration

Add these to your `.env` file:

- `OPENAI_API_KEY` - For AI-powered extraction and discovery
- `SMTP_*` - For email alerts (Gmail recommended)
- `SLACK_WEBHOOK_URL` - (Optional) For Slack notifications

## 📝 License

Proprietary - Certify Health Internal Use Only

## 👥 Team

Developed for Certify Health's competitive intelligence needs.

---

**GitHub Repository**: https://github.com/hicklax13/Project_Intel

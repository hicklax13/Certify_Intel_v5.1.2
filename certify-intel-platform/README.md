# Certify Intel Platform

AI-powered competitive intelligence platform for Certify Health.

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key
- (Optional) Bing Search API key

### Development Setup

1. **Clone and configure environment:**

   ```bash
   cd certify-intel-platform
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys
   ```

2. **Start all services:**

   ```bash
   cd docker
   docker-compose up -d
   ```

3. **Access the application:**
   - Frontend: <http://localhost:3000>
   - Backend API: <http://localhost:8000>
   - API Docs: <http://localhost:8000/docs>

### Local Development (without Docker)

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# Start PostgreSQL and Redis locally, then:
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
certify-intel-platform/
├── backend/
│   ├── app/
│   │   ├── api/        # FastAPI endpoints
│   │   ├── agents/     # AI agents (extraction, discovery, briefing)
│   │   ├── scrapers/   # Web scraping modules
│   │   ├── models/     # SQLAlchemy models
│   │   ├── schemas/    # Pydantic schemas
│   │   ├── services/   # Business logic
│   │   └── tasks/      # Celery async tasks
│   └── tests/
├── frontend/           # Next.js dashboard
├── docker/            # Docker configuration
└── docs/              # Documentation
```

## 🔑 Core Features

- **Competitor Discovery**: AI-powered identification of competitors
- **Web Scraping**: Playwright-based evidence collection
- **LLM Extraction**: Pricing, features, positioning extraction
- **Change Detection**: Semantic diff with impact assessment
- **Executive Briefings**: AI-generated weekly reports
- **Alert System**: Real-time notifications for important changes

## 📚 API Documentation

Once running, visit <http://localhost:8000/docs> for interactive API docs.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/competitors` | List competitors |
| POST | `/api/competitors` | Add competitor |
| GET | `/api/claims` | List extracted claims |
| GET | `/api/insights/dashboard` | Dashboard aggregations |
| GET | `/api/alerts` | List alerts |
| POST | `/api/insights/briefings/generate` | Generate briefing |

## 🛠️ Configuration

Environment variables (backend/.env):

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `OPENAI_API_KEY` | OpenAI API key |
| `BING_API_KEY` | Bing Search API key (optional) |

## 📄 License

Proprietary - Certify Health

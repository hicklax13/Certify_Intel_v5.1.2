# Certify Intel Platform - Backend

This is the FastAPI backend for the Certify Health competitive intelligence platform.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

## Project Structure

```
backend/
├── app/
│   ├── api/           # FastAPI route handlers
│   ├── agents/        # AI agent implementations
│   ├── scrapers/      # Data collection modules
│   ├── models/        # SQLAlchemy ORM models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── tasks/         # Celery async tasks
├── tests/
├── alembic/           # Database migrations
└── requirements.txt
```

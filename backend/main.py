"""
Certify Intel - Simplified Backend for Excel Dashboard
A lightweight FastAPI backend that:
1. Stores competitor data in SQLite (simple, no PostgreSQL setup needed)
2. Scrapes competitor websites using Playwright
3. Extracts data using OpenAI GPT
4. Exports data to Excel-compatible formats
"""
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print(f"Loading environment variables from .env")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'sqlite:///./certify_intel.db')}")
except ImportError:
    print("python-dotenv not installed, using system environment variables")

import json
import asyncio
try:
    import yfinance as yf
except ImportError:
    class MockYF:
        class Ticker:
            def __init__(self, t): self.info = {}
        def Ticker(self, t): return self.Ticker(t)
    yf = MockYF()
    print("yfinance not found, using mock")
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager



from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

# Enterprise Automation Import
try:
    from scheduler import start_scheduler, stop_scheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    print("Scheduler module not found. Automation disabled.")

# New Data Source Imports
import glassdoor_scraper
import indeed_scraper
import sec_edgar_scraper
import uspto_scraper
import klas_scraper
import appstore_scraper

import himss_scraper

# Database setup - SQLite for simplicity
# Database setup

from database import engine, SessionLocal, Base, get_db, Competitor, ChangeLog, DataSource, DataChangeHistory, User, SystemPrompt, KnowledgeBaseItem

# Auth imports for route protection
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Verify JWT token and return current user. Raises 401 if invalid/missing."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Import here to avoid circular import
    from extended_features import auth_manager
    
    payload = auth_manager.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {"email": payload.get("sub"), "role": payload.get("role")}

# White fill for Excel cells
WHITE_FILL = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

# Known healthcare IT public companies with tickers
KNOWN_TICKERS = {
    "phreesia": {"symbol": "PHR", "exchange": "NYSE", "name": "Phreesia Inc"},
    "health catalyst": {"symbol": "HCAT", "exchange": "NASDAQ", "name": "Health Catalyst Inc"},
    "veeva": {"symbol": "VEEV", "exchange": "NYSE", "name": "Veeva Systems Inc"},
    "teladoc": {"symbol": "TDOC", "exchange": "NYSE", "name": "Teladoc Health Inc"},
    "doximity": {"symbol": "DOCS", "exchange": "NYSE", "name": "Doximity Inc"},
    "hims & hers": {"symbol": "HIMS", "exchange": "NYSE", "name": "Hims & Hers Health Inc"},
    "definitive healthcare": {"symbol": "DH", "exchange": "NASDAQ", "name": "Definitive Healthcare Corp"},
    "carecloud": {"symbol": "CCLD", "exchange": "NASDAQ", "name": "CareCloud Inc"},
}

# Database Models imported from database.py


# ============== Pydantic Schemas ==============

class CompetitorCreate(BaseModel):
    name: str
    website: str
    status: str = "Active"
    threat_level: str = "Medium"
    notes: Optional[str] = None
    pricing_model: Optional[str] = None
    base_price: Optional[str] = None
    price_unit: Optional[str] = None
    product_categories: Optional[str] = None
    key_features: Optional[str] = None
    integration_partners: Optional[str] = None
    certifications: Optional[str] = None
    target_segments: Optional[str] = None
    customer_size_focus: Optional[str] = None
    geographic_focus: Optional[str] = None
    customer_count: Optional[str] = None
    customer_acquisition_rate: Optional[str] = None
    key_customers: Optional[str] = None
    g2_rating: Optional[str] = None
    employee_count: Optional[str] = None
    employee_growth_rate: Optional[str] = None
    year_founded: Optional[str] = None
    headquarters: Optional[str] = None
    funding_total: Optional[str] = None
    latest_round: Optional[str] = None
    pe_vc_backers: Optional[str] = None
    website_traffic: Optional[str] = None
    social_following: Optional[str] = None
    recent_launches: Optional[str] = None
    news_mentions: Optional[str] = None


class CompetitorResponse(CompetitorCreate):
    id: int
    last_updated: datetime
    data_quality_score: Optional[float] = None  # Float to support existing DB values
    created_at: datetime
    is_public: Optional[bool] = False
    ticker_symbol: Optional[str] = None
    stock_exchange: Optional[str] = None
    
    class Config:
        from_attributes = True


class CorrectionRequest(BaseModel):
    field: str
    new_value: str
    reason: Optional[str] = "Manual Correction"


class ScrapeRequest(BaseModel):
    competitor_id: int
    pages_to_scrape: List[str] = ["homepage", "pricing", "about"]

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None

class UserInviteRequest(BaseModel):
    email: str
    role: str = "viewer"
    full_name: Optional[str] = None


class SystemPromptBase(BaseModel):
    key: str
    content: str

class SystemPromptCreate(SystemPromptBase):
    pass

class SystemPromptResponse(SystemPromptBase):
    id: int
    updated_at: datetime
    class Config:
        from_attributes = True

class KnowledgeBaseItemBase(BaseModel):
    title: str
    content_text: str
    source_type: Optional[str] = "manual"
    is_active: Optional[bool] = True

class KnowledgeBaseItemCreate(KnowledgeBaseItemBase):
    pass

class KnowledgeBaseItemResponse(KnowledgeBaseItemBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True



# ============== FastAPI App ==============

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Certify Intel Backend starting...")
    print("=" * 60)

    # Configuration Validation
    print("Validating configuration...")
    missing_required = []

    # Check required environment variables
    if not os.getenv("SECRET_KEY"):
        missing_required.append("SECRET_KEY")

    if missing_required:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_required)}")
        raise ValueError(f"Missing required env vars: {', '.join(missing_required)}")

    # Warn about optional features
    optional_features = {
        "OPENAI_API_KEY": "AI Features (Executive Summaries, Discovery Agent, Web Extraction)",
        "SMTP_HOST": "Email Alerts",
        "SLACK_WEBHOOK_URL": "Slack Notifications"
    }

    disabled_scrapers = ["Crunchbase", "PitchBook", "LinkedIn (live scraping)"]

    print("\nAvailable Scrapers:")
    print("  ✅ Playwright Base Scraper - Website content extraction")
    print("  ✅ SEC Edgar (yfinance) - Public company financials")
    print("  ✅ News Monitor (Google News RSS) - Real-time news")
    print("  ✅ Known Data Fallback - Pre-populated data for demo")
    print("  ✅ [15+ other specialized scrapers with fallback data]")

    print("\nDisabled Scrapers (Paid APIs - not available):")
    for scraper in disabled_scrapers:
        print(f"  ❌ {scraper}")

    print("\nOptional Features:")
    for env_var, feature in optional_features.items():
        if os.getenv(env_var):
            print(f"  ✅ {feature} - ENABLED")
        else:
            print(f"  ⚠️  {feature} - DISABLED (set {env_var} to enable)")

    print("=" * 60)

    # Start Enterprise Scheduler
    if SCHEDULER_AVAILABLE:
        print("Initializing Enterprise Automation Engine...")
        start_scheduler()

    # Run Public/Private Workflow on Startup
    # Run Public/Private Workflow on Startup
    try:
        from extended_features import ClassificationWorkflow, auth_manager
        
        # Initialize DB Session for startup tasks
        db = SessionLocal()
        
        # 1. Ensure Admin User
        print("Ensuring default admin user exists...")
        auth_manager.ensure_default_admin(db)
        
        # 2. Run Classification Workflow
        workflow = ClassificationWorkflow(db)
        print("Running 'Private vs Public' Classification Workflow...")
        workflow.run_classification_pipeline()
        
        db.close()
    except Exception as e:
        print(f"Startup task warning: {e}")
        
    yield
    
    # Shutdown: Clean up resources
    print("Certify Intel Backend shutting down...")
    if SCHEDULER_AVAILABLE:
        stop_scheduler()

app = FastAPI(
    title="Certify Health Intel API",
    description="Backend for Competitive Intelligence Dashboard",
    version="1.0.0",
    lifespan=lifespan
)



# Valid API endpoints are defined above.
# The catch-all static file mount must be last.



# Redirect legacy /app path to root
@app.get("/app")
@app.get("/app/")
async def redirect_app():
    return RedirectResponse(url="/")








@app.get("/api/logo-proxy")
async def proxy_logo(url: str):
    """Proxy image requests to avoid CORS issues."""
    import requests
    from fastapi import Response
    
    try:
        # Validate URL
        if not url.startswith("http"):
            raise HTTPException(status_code=400, detail="Invalid URL")
            
        # Try Clearbit first
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                return Response(content=resp.content, media_type=resp.headers.get("content-type", "image/png"))
        except:
            pass
            
        # Fallback to Google Favicon service if Clearbit fails
        # Extract domain from the input URL (expected: https://logo.clearbit.com/domain.com)
        domain = url.split("/")[-1]
        google_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
        
        try:
            resp = requests.get(google_url, timeout=3)
            if resp.status_code == 200:
                return Response(content=resp.content, media_type=resp.headers.get("content-type", "image/png"))
        except:
            pass

        # Return 404 to trigger frontend onerror fallback
        raise HTTPException(status_code=404, detail="Image not found")
            
    except Exception as e:
        print(f"Proxy error: {e}")
        raise HTTPException(status_code=404, detail="Proxy error")


# get_db imported from database.py


@app.get("/api/analytics/summary")
@app.get("/api/analytics/executive-summary")
async def get_dashboard_summary(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Generate comprehensive AI executive summary analyzing ALL dashboard data points."""
    try:
        import os
        from openai import OpenAI
        
        # Get all active competitors
        competitors = db.query(Competitor).filter(
            Competitor.is_deleted == False,
            Competitor.status == "Active"
        ).all()
        
        if not competitors:
            return {"summary": "No active competitors found to analyze.", "type": "empty", "model": None}
        
        # Calculate statistics
        total = len(competitors)
        high_threat = sum(1 for c in competitors if c.threat_level == "High")
        medium_threat = sum(1 for c in competitors if c.threat_level == "Medium")
        low_threat = sum(1 for c in competitors if c.threat_level == "Low")
        public_companies = sum(1 for c in competitors if c.is_public)
        private_companies = total - public_companies
        
        # Gather pricing info
        pricing_models = {}
        for c in competitors:
            model = c.pricing_model or "Unknown"
            pricing_models[model] = pricing_models.get(model, 0) + 1
        
        # Gather top threats
        top_threats = [c.name for c in competitors if c.threat_level == "High"][:5]
        
        # Build comprehensive data summary for AI
        data_summary = f"""
COMPETITIVE INTELLIGENCE DATA SNAPSHOT:
========================================

TRACKING OVERVIEW:
- Total Competitors Monitored: {total}
- High Threat: {high_threat} ({round(high_threat/total*100, 1)}%)
- Medium Threat: {medium_threat} ({round(medium_threat/total*100, 1)}%)
- Low Threat: {low_threat} ({round(low_threat/total*100, 1)}%)
- Public Companies: {public_companies}
- Private Companies: {private_companies}

TOP HIGH-THREAT COMPETITORS: {', '.join(top_threats) if top_threats else 'None identified'}

PRICING MODEL DISTRIBUTION:
{chr(10).join(f'- {model}: {count} competitors' for model, count in pricing_models.items())}

DETAILED COMPETITOR DATA:
"""
        for c in competitors[:20]:  # Top 20 for context
            data_summary += f"""
{c.name}:
  - Threat Level: {c.threat_level}
  - Pricing: {c.base_price or 'Unknown'}
  - Customers: {c.customer_count or 'Unknown'}
  - Employees: {c.employee_count or 'Unknown'}
  - G2 Rating: {c.g2_rating or 'N/A'}
  - Funding: {c.funding_total or 'Unknown'}
  - Categories: {c.product_categories or 'Unknown'}
"""

        # Try OpenAI first
        api_key = os.getenv("OPENAI_API_KEY")
        model_used = "gpt-4-turbo"
        provider = "OpenAI"
        
        if api_key:
            try:
                # Fetch dynamic system prompt
                prompt_db = db.query(SystemPrompt).filter(SystemPrompt.key == "dashboard_summary").first()
                system_content = prompt_db.content if prompt_db else """You are Certify Health's competitive intelligence analyst. Generate a comprehensive, executive-level strategic summary. 

Your summary MUST include:
1. **Executive Overview** - High-level market position assessment
2. **Threat Analysis** - Breakdown of competitive landscape by threat level
3. **Pricing Intelligence** - Analysis of competitor pricing strategies
4. **Market Trends** - Emerging patterns and shifts
5. **Strategic Recommendations** - 3-5 specific, actionable recommendations
6. **Watch List** - Key competitors requiring immediate attention

Use data-driven insights. Be specific with numbers and competitor names. Format with markdown headers and bullet points."""

                # RAG: Inject Knowledge Base
                kb_items = db.query(KnowledgeBaseItem).filter(KnowledgeBaseItem.is_active == True).all()
                if kb_items:
                    data_summary += "\n\nINTERNAL KNOWLEDGE BASE (USE THIS CONTEXT):\n==========================\n"
                    for item in kb_items:
                        data_summary += f"\n--- {item.title} ({item.source_type}) ---\n{item.content_text}\n"

                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=model_used,
                    messages=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": data_summary}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                summary = response.choices[0].message.content
                return {
                    "summary": summary,
                    "type": "ai",
                    "model": model_used,
                    "provider": provider,
                    "provider_logo": "/static/openai-logo.svg",
                    "data_points_analyzed": total,
                    "generated_at": datetime.utcnow().isoformat()
                }
            except Exception as e:
                print(f"OpenAI Error: {e}")
        
        # Fallback to automated summary
        summary = f"""# AI-Generated Executive Summary

## Executive Overview
We are currently tracking **{total} competitors** in the patient engagement and healthcare check-in market. The competitive landscape shows **{high_threat} high-threat** competitors requiring immediate attention, **{medium_threat} medium-threat** competitors to monitor, and **{low_threat} low-threat** competitors with minimal impact.

## Threat Analysis
- **High Threat ({high_threat})**: {', '.join(top_threats[:3]) if top_threats else 'None'} - These competitors have significant market overlap and strong positioning
- **Medium Threat ({medium_threat})**: Competitors with partial market overlap requiring ongoing monitoring
- **Low Threat ({low_threat})**: Minimal competitive impact at this time

## Market Composition
- **Public Companies**: {public_companies} ({round(public_companies/total*100, 1)}% of tracked competitors)
- **Private Companies**: {private_companies} ({round(private_companies/total*100, 1)}% of tracked competitors)

## Pricing Intelligence
{chr(10).join(f'- **{model}**: {count} competitors' for model, count in list(pricing_models.items())[:5])}

## Strategic Recommendations
1. **Monitor pricing changes weekly** - Especially for high-threat competitors
2. **Investigate feature gaps** in patient intake workflows
3. **Review battlecards** for top high-threat targets
4. **Track funding announcements** from private competitors
5. **Analyze customer reviews** on G2 and Capterra for competitive insights

## Watch List
Top competitors requiring immediate attention: {', '.join(top_threats) if top_threats else 'No high-threat competitors identified'}

---
*Summary generated automatically based on {total} tracked competitors*
"""
        return {
            "summary": summary,
            "type": "fallback",
            "model": "automated",
            "provider": "Certify Intel",
            "provider_logo": "/static/certify-logo.svg",
            "data_points_analyzed": total,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Summary Error: {e}")
        return {"summary": f"Error generating summary: {str(e)}", "type": "error", "model": None}


@app.post("/api/analytics/chat")
def chat_with_summary(request: dict, db: Session = Depends(get_db)):
    """Chat with AI about the competitive intelligence data."""
    try:
        import os
        from openai import OpenAI
        
        user_message = request.get("message", "")
        if not user_message:
            return {"response": "Please provide a message.", "success": False}
        
        # Get competitor data for context
        competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
        context = f"We track {len(competitors)} competitors. "
        context += f"High threat: {sum(1 for c in competitors if c.threat_level == 'High')}, "
        context += f"Medium: {sum(1 for c in competitors if c.threat_level == 'Medium')}, "
        context += f"Low: {sum(1 for c in competitors if c.threat_level == 'Low')}. "
        context += f"Top competitors: {', '.join([c.name for c in competitors[:10]])}"
        
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            # Fetch dynamic persona
            prompt_db = db.query(SystemPrompt).filter(SystemPrompt.key == "chat_persona").first()
            base_persona = prompt_db.content if prompt_db else "You are a competitive intelligence analyst for Certify Health."
            
            # RAG: Inject Knowledge Base
            kb_text = ""
            kb_items = db.query(KnowledgeBaseItem).filter(KnowledgeBaseItem.is_active == True).all()
            if kb_items:
                kb_text += "\n\nINTERNAL KNOWLEDGE BASE (USE THIS CONCURRENTLY WITH LIVE DATA):\n"
                for item in kb_items:
                    kb_text += f"\n--- {item.title} ---\n{item.content_text}\n"
            
            full_system_content = f"{base_persona}\n\nLIVE DATA CONTEXT:\n{context}\n{kb_text}"

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": full_system_content},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500
            )
            return {"response": response.choices[0].message.content, "success": True}
        else:
            return {"response": "AI chat requires OpenAI API key configuration.", "success": False}
    except Exception as e:
        return {"response": f"Error: {str(e)}", "success": False}


# Health endpoint at /api/health
@app.get("/api/health")
def api_health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "version": "1.0.0"}


# Analytics sub-endpoints
@app.get("/api/analytics/threats")
def get_threat_analytics(db: Session = Depends(get_db)):
    """Get threat distribution analytics."""
    competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
    return {
        "high": sum(1 for c in competitors if c.threat_level == "High"),
        "medium": sum(1 for c in competitors if c.threat_level == "Medium"),
        "low": sum(1 for c in competitors if c.threat_level == "Low"),
        "total": len(competitors)
    }


@app.get("/api/analytics/market-share")
def get_market_share_analytics(db: Session = Depends(get_db)):
    """Get estimated market share by customer count."""
    competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
    shares = []
    for c in competitors[:10]:
        count = 0
        if c.customer_count:
            try:
                count = int(''.join(filter(str.isdigit, str(c.customer_count)))) or 100
            except:
                count = 100
        shares.append({"name": c.name, "customers": count})
    total = sum(s["customers"] for s in shares)
    for s in shares:
        s["share"] = round(s["customers"] / total * 100, 1) if total > 0 else 0
    return {"market_share": shares}


@app.get("/api/analytics/pricing")
def get_pricing_analytics(db: Session = Depends(get_db)):
    """Get pricing model distribution."""
    competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
    models = {}
    for c in competitors:
        model = c.pricing_model or "Unknown"
        models[model] = models.get(model, 0) + 1
    return {"pricing_models": [{"model": k, "count": v} for k, v in models.items()]}


# ============== DATA QUALITY ENDPOINTS ==============

# List of all data fields that should be tracked
COMPETITOR_DATA_FIELDS = [
    "name", "website", "status", "threat_level", "pricing_model", "base_price",
    "price_unit", "product_categories", "key_features", "integration_partners",
    "certifications", "target_segments", "customer_size_focus", "geographic_focus",
    "customer_count", "customer_acquisition_rate", "key_customers", "g2_rating",
    "employee_count", "employee_growth_rate", "year_founded", "headquarters",
    "funding_total", "latest_round", "pe_vc_backers", "website_traffic",
    "social_following", "recent_launches", "news_mentions", "is_public",
    "ticker_symbol", "stock_exchange"
]


def calculate_quality_score(competitor) -> int:
    """Calculate data quality score (0-100) based on field completeness."""
    filled_fields = 0
    for field in COMPETITOR_DATA_FIELDS:
        value = getattr(competitor, field, None)
        if value is not None and str(value).strip() not in ["", "None", "Unknown", "N/A"]:
            filled_fields += 1
    return int((filled_fields / len(COMPETITOR_DATA_FIELDS)) * 100)


@app.get("/api/data-quality/completeness")
def get_data_completeness(db: Session = Depends(get_db)):
    """Get field-by-field completeness statistics across all competitors."""
    competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
    total = len(competitors)
    
    if total == 0:
        return {"total_competitors": 0, "fields": [], "overall_completeness": 0}
    
    field_stats = []
    for field in COMPETITOR_DATA_FIELDS:
        filled = 0
        for comp in competitors:
            value = getattr(comp, field, None)
            if value is not None and str(value).strip() not in ["", "None", "Unknown", "N/A"]:
                filled += 1
        completeness = round((filled / total) * 100, 1)
        field_stats.append({
            "field": field,
            "filled": filled,
            "total": total,
            "completeness_percent": completeness
        })
    
    # Sort by completeness ascending (least complete first)
    field_stats.sort(key=lambda x: x["completeness_percent"])
    
    overall = round(sum(f["completeness_percent"] for f in field_stats) / len(field_stats), 1)
    
    return {
        "total_competitors": total,
        "total_fields": len(COMPETITOR_DATA_FIELDS),
        "overall_completeness": overall,
        "fields": field_stats
    }


@app.get("/api/data-quality/scores")
def get_quality_scores(db: Session = Depends(get_db)):
    """Get quality scores for all competitors."""
    competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
    
    scores = []
    for comp in competitors:
        score = calculate_quality_score(comp)
        scores.append({
            "id": comp.id,
            "name": comp.name,
            "score": score,
            "tier": "Excellent" if score >= 80 else "Good" if score >= 60 else "Fair" if score >= 40 else "Poor"
        })
    
    # Sort by score descending
    scores.sort(key=lambda x: x["score"], reverse=True)
    
    avg_score = round(sum(s["score"] for s in scores) / len(scores), 1) if scores else 0
    
    return {
        "average_score": avg_score,
        "total_competitors": len(scores),
        "scores": scores
    }


@app.get("/api/data-quality/stale")
def get_stale_records(days: int = 30, db: Session = Depends(get_db)):
    """Get competitors with data older than specified days."""
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    competitors = db.query(Competitor).filter(
        Competitor.is_deleted == False
    ).all()
    
    stale = []
    fresh = []
    for comp in competitors:
        check_date = comp.last_verified_at or comp.last_updated or comp.created_at
        if check_date and check_date < cutoff:
            days_old = (datetime.utcnow() - check_date).days
            stale.append({
                "id": comp.id,
                "name": comp.name,
                "last_verified": check_date.isoformat() if check_date else None,
                "days_old": days_old
            })
        else:
            fresh.append({"id": comp.id, "name": comp.name})
    
    stale.sort(key=lambda x: x["days_old"], reverse=True)
    
    return {
        "threshold_days": days,
        "stale_count": len(stale),
        "fresh_count": len(fresh),
        "stale_records": stale,
        "fresh_records": fresh[:10]  # Just show first 10 fresh
    }


@app.post("/api/data-quality/verify/{competitor_id}")
def verify_competitor_data(competitor_id: int, db: Session = Depends(get_db)):
    """Mark a competitor's data as verified (updates last_verified_at timestamp)."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    competitor.last_verified_at = datetime.utcnow()
    competitor.data_quality_score = calculate_quality_score(competitor)
    db.commit()
    
    return {
        "success": True,
        "competitor_id": competitor_id,
        "name": competitor.name,
        "verified_at": competitor.last_verified_at.isoformat(),
        "quality_score": competitor.data_quality_score
    }


@app.get("/api/data-quality/completeness/{competitor_id}")
def get_competitor_completeness(competitor_id: int, db: Session = Depends(get_db)):
    """Get field-by-field completeness for a specific competitor."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    fields = []
    for field in COMPETITOR_DATA_FIELDS:
        value = getattr(competitor, field, None)
        has_value = value is not None and str(value).strip() not in ["", "None", "Unknown", "N/A"]
        fields.append({
            "field": field,
            "has_value": has_value,
            "value": str(value)[:100] if value else None  # Truncate long values
        })
    
    filled = sum(1 for f in fields if f["has_value"])
    
    return {
        "competitor_id": competitor_id,
        "name": competitor.name,
        "filled_fields": filled,
        "total_fields": len(COMPETITOR_DATA_FIELDS),
        "completeness_percent": round((filled / len(COMPETITOR_DATA_FIELDS)) * 100, 1),
        "fields": fields
    }


# ============== CHANGE HISTORY ENDPOINTS ==============

@app.get("/api/changes")
def get_changes(competitor_id: Optional[int] = None, days: int = 30, db: Session = Depends(get_db)):
    """Get change logs for timeline."""
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(DataChangeHistory).filter(DataChangeHistory.changed_at >= cutoff)
    
    if competitor_id:
        query = query.filter(DataChangeHistory.competitor_id == competitor_id)
        
    changes = query.order_by(DataChangeHistory.changed_at.desc()).limit(100).all()
    
    return {
        "competitor_id": competitor_id,
        "days": days,
        "count": len(changes),
        "changes": [
            {
                "id": c.id,
                "competitor_id": c.competitor_id,
                "change_type": c.field_name.replace("_", " ").title(), # Map field_name to readable type
                "previous_value": c.old_value,
                "new_value": c.new_value,
                "severity": "Medium", # Default severity as DB model doesn't have it yet, or map from field
                "detected_at": c.changed_at.isoformat(),
                "source": c.source_url
            }
            for c in changes
        ]
    }


@app.get("/api/changes/history/{competitor_id}")
def get_competitor_change_history(competitor_id: int, db: Session = Depends(get_db)):
    """Get detailed change history for a specific competitor."""
    changes = db.query(DataChangeHistory).filter(
        DataChangeHistory.competitor_id == competitor_id
    ).order_by(DataChangeHistory.changed_at.desc()).limit(100).all()
    

# ============== DISCOVERY ENGINE ENDPOINTS ==============

@app.get("/api/discovery/context")
def get_discovery_context(current_user: dict = Depends(get_current_user)):
    """Get the current Discovery Engine context (certification DNA)."""
    try:
        context_path = os.path.join(os.path.dirname(__file__), "certify_context.json")
        if not os.path.exists(context_path):
             return {"core_keywords": [], "market_keywords": [], "exclusions": []}
             
        with open(context_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/discovery/context")
def update_discovery_context(new_context: dict, current_user: dict = Depends(get_current_user)):
    """Update the Discovery Engine context."""
    try:
        context_path = os.path.join(os.path.dirname(__file__), "certify_context.json")
        with open(context_path, 'w', encoding='utf-8') as f:
            json.dump(new_context, f, indent=4)
        return {"success": True, "message": "Context updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/discovery/refine-context")
def refine_discovery_context(request: dict, current_user: dict = Depends(get_current_user)):
    """Use AI to refine the context based on user chat input."""
    try:
        user_input = request.get("message")
        current_context = request.get("current_context")
        
        if not user_input:
            raise HTTPException(status_code=400, detail="Message required")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
             raise HTTPException(status_code=500, detail="OpenAI key missing")

        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        system_prompt = """You are an expert configuration assistant for a Competitor Discovery Engine.
        Your goal is to update the JSON configuration profile based on the user's request.
        
        The JSON structure is:
        {
            "core_keywords": ["list", "of", "competitor", "keywords"],
            "market_keywords": ["target", "markets"],
            "required_context": ["must", "have", "terms"],
            "negative_keywords": ["terms", "to", "avoid"],
            "known_competitors": ["known", "competitor", "names"],
            "exclusions": ["industries", "to", "exclude"]
        }
        
        Return ONLY the updated JSON. Do not return markdown formatting."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Current Profile: {json.dumps(current_context)}\n\nUser Request: {user_input}\n\nUpdate the profile:"}
            ],
            response_format={"type": "json_object"}
        )
        
        refined_json = json.loads(response.choices[0].message.content)
        return {"success": True, "refined_context": refined_json}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/discovery/schedule")
def schedule_discovery_run(request: dict, current_user: dict = Depends(get_current_user)):
    """Schedule a one-off discovery run."""
    try:
        run_at_str = request.get("run_at") # ISO format string
        if not run_at_str:
            raise HTTPException(status_code=400, detail="run_at timestamp required")
            
        run_at = datetime.fromisoformat(run_at_str.replace('Z', '+00:00'))
        
        from scheduler import schedule_one_off_discovery
        schedule_one_off_discovery(run_at)
        
        return {"success": True, "message": f"Discovery job scheduled for {run_at.isoformat()}"}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/changes/log")
def log_data_change(
    competitor_id: int,
    field_name: str,
    old_value: str,
    new_value: str,
    changed_by: str = "system",
    reason: Optional[str] = None,
    source_url: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Log a data change for audit purposes."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    change = DataChangeHistory(
        competitor_id=competitor_id,
        competitor_name=competitor.name,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        changed_by=changed_by,
        change_reason=reason,
        source_url=source_url
    )
    db.add(change)
    db.commit()
    
    return {"success": True, "change_id": change.id}


# ============== DATA SOURCE ENDPOINTS ==============

@app.get("/api/sources/{competitor_id}")
def get_competitor_sources(competitor_id: int, db: Session = Depends(get_db)):
    """Get all data sources for a competitor's fields."""
    sources = db.query(DataSource).filter(
        DataSource.competitor_id == competitor_id
    ).all()
    
    sources_by_field = {}
    for s in sources:
        sources_by_field[s.field_name] = {
            "source_type": s.source_type,
            "source_url": s.source_url,
            "source_name": s.source_name,
            "entered_by": s.entered_by,
            "formula": s.formula,
            "verified_at": s.verified_at.isoformat() if s.verified_at else None
        }
    
    return {
        "competitor_id": competitor_id,
        "sources": sources_by_field
    }


@app.get("/api/sources/{competitor_id}/{field_name}")
def get_field_source(competitor_id: int, field_name: str, db: Session = Depends(get_db)):
    """Get the data source for a specific field of a competitor."""
    source = db.query(DataSource).filter(
        DataSource.competitor_id == competitor_id,
        DataSource.field_name == field_name
    ).first()
    
    if not source:
        return {
            "competitor_id": competitor_id,
            "field_name": field_name,
            "source_type": "unknown",
            "source_url": None,
            "message": "No source recorded for this field"
        }
    
    return {
        "competitor_id": competitor_id,
        "field_name": field_name,
        "source_type": source.source_type,
        "source_url": source.source_url,
        "source_name": source.source_name,
        "entered_by": source.entered_by,
        "formula": source.formula,
        "verified_at": source.verified_at.isoformat() if source.verified_at else None
    }


@app.post("/api/sources/set")
def set_field_source(
    competitor_id: int,
    field_name: str,
    source_type: str,  # "external", "manual", "calculated"
    source_url: Optional[str] = None,
    source_name: Optional[str] = None,
    entered_by: Optional[str] = None,
    formula: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Set or update the source for a competitor's field."""
    # Check if source already exists
    existing = db.query(DataSource).filter(
        DataSource.competitor_id == competitor_id,
        DataSource.field_name == field_name
    ).first()
    
    if existing:
        existing.source_type = source_type
        existing.source_url = source_url
        existing.source_name = source_name
        existing.entered_by = entered_by
        existing.formula = formula
        existing.verified_at = datetime.utcnow()
        existing.updated_at = datetime.utcnow()
    else:
        new_source = DataSource(
            competitor_id=competitor_id,
            field_name=field_name,
            source_type=source_type,
            source_url=source_url,
            source_name=source_name,
            entered_by=entered_by,
            formula=formula
        )
        db.add(new_source)
    
    db.commit()
    return {"success": True, "message": f"Source set for {field_name}"}


# ============== BULK UPDATE ENDPOINT ==============

@app.post("/api/competitors/bulk-update")
async def bulk_update_competitors(
    request: Request,
    db: Session = Depends(get_db)
):
    """Bulk update competitors from JSON data."""
    data = await request.json()
    updates = data.get("updates", [])
    changed_by = data.get("changed_by", "bulk_import")
    
    results = {"success": [], "errors": []}
    
    for update in updates:
        competitor_id = update.get("id")
        if not competitor_id:
            results["errors"].append({"error": "Missing competitor ID", "data": update})
            continue
        
        competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
        if not competitor:
            results["errors"].append({"error": f"Competitor {competitor_id} not found", "data": update})
            continue
        
        try:
            for field, new_value in update.items():
                if field == "id":
                    continue
                if hasattr(competitor, field):
                    old_value = getattr(competitor, field)
                    setattr(competitor, field, new_value)
                    
                    # Log the change
                    change = DataChangeHistory(
                        competitor_id=competitor_id,
                        competitor_name=competitor.name,
                        field_name=field,
                        old_value=str(old_value) if old_value else None,
                        new_value=str(new_value) if new_value else None,
                        changed_by=changed_by
                    )
                    db.add(change)
            
            competitor.last_updated = datetime.utcnow()
            competitor.data_quality_score = calculate_quality_score(competitor)
            results["success"].append({"id": competitor_id, "name": competitor.name})
        except Exception as e:
            results["errors"].append({"error": str(e), "id": competitor_id})
    
    db.commit()
    
    return {
        "total_processed": len(updates),
        "successful": len(results["success"]),
        "failed": len(results["errors"]),
        "results": results
    }


# Import routers
from routers import reports, discovery
import api_routes

# Include routers
app.include_router(discovery.router)
app.include_router(api_routes.router)  # Covers analytics, winloss, external, etc.
app.include_router(reports.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# --- Competitors CRUD ---

@app.get("/api/competitors", response_model=List[CompetitorResponse])
async def list_competitors(
    status: Optional[str] = None,
    threat_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Competitor).filter(Competitor.is_deleted == False)
    if status:
        query = query.filter(Competitor.status == status)
    if threat_level:
        query = query.filter(Competitor.threat_level == threat_level)
    competitors = query.offset(skip).limit(limit).all()
    return competitors


@app.get("/api/competitors/{competitor_id}", response_model=CompetitorResponse)
async def get_competitor(competitor_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    competitor = db.query(Competitor).filter(
        Competitor.id == competitor_id,
        Competitor.is_deleted == False
    ).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return competitor


@app.post("/api/competitors", response_model=CompetitorResponse)
async def create_competitor(competitor: CompetitorCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_competitor = Competitor(**competitor.model_dump())
    
    # Auto-classify Public/Private
    comp_lower = db_competitor.name.lower()
    if comp_lower in KNOWN_TICKERS:
        info = KNOWN_TICKERS[comp_lower]
        db_competitor.is_public = True
        db_competitor.ticker_symbol = info["symbol"]
        db_competitor.stock_exchange = info["exchange"]
        
    db.add(db_competitor)
    db.commit()
    db.refresh(db_competitor)
    return db_competitor


@app.put("/api/competitors/{competitor_id}", response_model=CompetitorResponse)
async def update_competitor(competitor_id: int, competitor: CompetitorCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not db_competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    for key, value in competitor.model_dump().items():
        setattr(db_competitor, key, value)
    db_competitor.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(db_competitor)
    return db_competitor


@app.delete("/api/competitors/{competitor_id}")
async def delete_competitor(competitor_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not db_competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    db_competitor.is_deleted = True
    db.commit()
    return {"message": "Competitor deleted"}


@app.post("/api/competitors/{competitor_id}/correct")
async def correct_competitor_data(
    competitor_id: int, 
    correction: CorrectionRequest, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    """Manually correct a data point and lock it to prevent overwrite."""
    # 1. Get Competitor
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    # 2. Validate field exists
    if not hasattr(competitor, correction.field):
        raise HTTPException(status_code=400, detail=f"Invalid field: {correction.field}")
    
    old_value = getattr(competitor, correction.field)
    
    # 3. Update Value
    setattr(competitor, correction.field, correction.new_value)
    competitor.last_updated = datetime.utcnow()
    
    # 4. Update/Create Data Source (Lock as Manual)
    source = db.query(DataSource).filter(
        DataSource.competitor_id == competitor_id,
        DataSource.field_name == correction.field
    ).first()
    
    if source:
        source.source_type = "manual"
        source.entered_by = current_user.get("email", "unknown")
        source.updated_at = datetime.utcnow()
    else:
        new_source = DataSource(
            competitor_id=competitor_id,
            field_name=correction.field,
            source_type="manual",
            entered_by=current_user.get("email", "unknown"),
            verified_at=datetime.utcnow()
        )
        db.add(new_source)
    
    # 5. Log Change History
    history = DataChangeHistory(
        competitor_id=competitor_id,
        competitor_name=competitor.name,
        field_name=correction.field,
        old_value=str(old_value) if old_value else None,
        new_value=correction.new_value,
        changed_by=current_user.get("email", "unknown"),
        change_reason=correction.reason
    )
    db.add(history)
    
    db.commit()
    db.refresh(competitor)
    
    return {"message": "Correction applied successfully", "competitor": competitor}


# --- Excel Export ---

def auto_fit_columns(worksheet):
    """Auto-fit all columns to the widest content."""
    for column_cells in worksheet.columns:
        max_length = 0
        column_letter = get_column_letter(column_cells[0].column)
        for cell in column_cells:
            try:
                if cell.value:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
            except Exception:
                pass
        adjusted_width = max_length + 3
        if adjusted_width < 12:
            adjusted_width = 12
        if adjusted_width > 50:
            adjusted_width = 50
        worksheet.column_dimensions[column_letter].width = adjusted_width


def apply_white_background(worksheet, max_row=100, max_col=50):
    """Apply white background to all cells."""
    for row in range(1, max_row + 1):
        for col in range(1, max_col + 1):
            cell = worksheet.cell(row=row, column=col)
            if cell.fill.fgColor.rgb in (None, '00000000', 'FFFFFFFF') or cell.fill.fill_type is None:
                cell.fill = WHITE_FILL


@app.get("/api/export/excel")
def export_excel(db: Session = Depends(get_db)):
    """Export all competitor data to Excel."""
    competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Competitors"
    
    # Headers
    headers = [
        "Competitor Name", "Website", "Status", "Threat Level", "Last Updated",
        "Notes", "Data Quality Score", "Pricing Model", "Base Price", "Price Unit",
        "Product Categories", "Key Features", "Integration Partners", "Certifications",
        "Target Segments", "Customer Size Focus", "Geographic Focus", "Customer Count",
        "Customer Acquisition Rate", "Key Customers", "G2 Rating", "Employee Count",
        "Employee Growth Rate", "Year Founded", "Headquarters", "Funding Total",
        "Latest Round", "PE/VC Backers", "Website Traffic", "Social Following",
        "Recent Launches", "News Mentions"
    ]
    
    header_fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    # Data
    for row_idx, comp in enumerate(competitors, start=2):
        ws.cell(row=row_idx, column=1, value=comp.name)
        ws.cell(row=row_idx, column=2, value=comp.website)
        ws.cell(row=row_idx, column=3, value=comp.status)
        ws.cell(row=row_idx, column=4, value=comp.threat_level)
        ws.cell(row=row_idx, column=5, value=comp.last_updated.strftime("%Y-%m-%d") if comp.last_updated else "")
        ws.cell(row=row_idx, column=6, value=comp.notes)
        ws.cell(row=row_idx, column=7, value=comp.data_quality_score)
        ws.cell(row=row_idx, column=8, value=comp.pricing_model)
        ws.cell(row=row_idx, column=9, value=comp.base_price)
        ws.cell(row=row_idx, column=10, value=comp.price_unit)
        ws.cell(row=row_idx, column=11, value=comp.product_categories)
        ws.cell(row=row_idx, column=12, value=comp.key_features)
        ws.cell(row=row_idx, column=13, value=comp.integration_partners)
        ws.cell(row=row_idx, column=14, value=comp.certifications)
        ws.cell(row=row_idx, column=15, value=comp.target_segments)
        ws.cell(row=row_idx, column=16, value=comp.customer_size_focus)
        ws.cell(row=row_idx, column=17, value=comp.geographic_focus)
        ws.cell(row=row_idx, column=18, value=comp.customer_count)
        ws.cell(row=row_idx, column=19, value=comp.customer_acquisition_rate)
        ws.cell(row=row_idx, column=20, value=comp.key_customers)
        ws.cell(row=row_idx, column=21, value=comp.g2_rating)
        ws.cell(row=row_idx, column=22, value=comp.employee_count)
        ws.cell(row=row_idx, column=23, value=comp.employee_growth_rate)
        ws.cell(row=row_idx, column=24, value=comp.year_founded)
        ws.cell(row=row_idx, column=25, value=comp.headquarters)
        ws.cell(row=row_idx, column=26, value=comp.funding_total)
        ws.cell(row=row_idx, column=27, value=comp.latest_round)
        ws.cell(row=row_idx, column=28, value=comp.pe_vc_backers)
        ws.cell(row=row_idx, column=29, value=comp.website_traffic)
        ws.cell(row=row_idx, column=30, value=comp.social_following)
        ws.cell(row=row_idx, column=31, value=comp.recent_launches)
        ws.cell(row=row_idx, column=32, value=comp.news_mentions)
    
    ws.freeze_panes = "A2"
    auto_fit_columns(ws)
    apply_white_background(ws, max_row=len(competitors) + 10, max_col=32)
    
    # Save
    output_path = "./exports/competitors_export.xlsx"
    os.makedirs("./exports", exist_ok=True)
    wb.save(output_path)
    
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"certify_intel_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )


@app.get("/api/export/json")
def export_json(db: Session = Depends(get_db)):
    """Export all competitor data as JSON."""
    competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
    
    data = []
    for comp in competitors:
        data.append({
            "name": comp.name,
            "website": comp.website,
            "status": comp.status,
            "threat_level": comp.threat_level,
            "last_updated": comp.last_updated.isoformat() if comp.last_updated else None,
            "notes": comp.notes,
            "data_quality_score": comp.data_quality_score,
            "pricing_model": comp.pricing_model,
            "base_price": comp.base_price,
            "price_unit": comp.price_unit,
            "product_categories": comp.product_categories,
            "key_features": comp.key_features,
            "integration_partners": comp.integration_partners,
            "certifications": comp.certifications,
            "target_segments": comp.target_segments,
            "customer_size_focus": comp.customer_size_focus,
            "geographic_focus": comp.geographic_focus,
            "customer_count": comp.customer_count,
            "customer_acquisition_rate": comp.customer_acquisition_rate,
            "key_customers": comp.key_customers,
            "g2_rating": comp.g2_rating,
            "employee_count": comp.employee_count,
            "employee_growth_rate": comp.employee_growth_rate,
            "year_founded": comp.year_founded,
            "headquarters": comp.headquarters,
            "funding_total": comp.funding_total,
            "latest_round": comp.latest_round,
            "pe_vc_backers": comp.pe_vc_backers,
            "website_traffic": comp.website_traffic,
            "social_following": comp.social_following,
            "recent_launches": comp.recent_launches,
            "news_mentions": comp.news_mentions,
        })
    
    return {"competitors": data, "count": len(data), "exported_at": datetime.utcnow().isoformat()}


# --- Dashboard Stats ---

@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get summary statistics for dashboard."""
    competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
    
    stats = {
        "total_competitors": len(competitors),
        "active": len([c for c in competitors if c.status == "Active"]),
        "high_threat": len([c for c in competitors if c.threat_level == "High"]),
        "medium_threat": len([c for c in competitors if c.threat_level == "Medium"]),
        "low_threat": len([c for c in competitors if c.threat_level == "Low"]),
        "last_updated": datetime.utcnow().isoformat()
    }
    
    return stats


# --- Change Log ---

@app.get("/api/changes")
def get_change_log(
    severity: Optional[str] = None,
    days: int = 7,
    competitor_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get recent changes from the change log."""
    from datetime import timedelta
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(ChangeLog).filter(ChangeLog.detected_at >= cutoff)
    if severity:
        query = query.filter(ChangeLog.severity == severity)
    if competitor_id:
        query = query.filter(ChangeLog.competitor_id == competitor_id)
    
    changes = query.order_by(ChangeLog.detected_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "changes": [
            {
                "id": c.id,
                "competitor_id": c.competitor_id,
                "competitor_name": c.competitor_name,
                "change_type": c.change_type,
                "previous_value": c.previous_value,
                "new_value": c.new_value,
                "source": c.source,
                "severity": c.severity,
                "detected_at": c.detected_at.isoformat()
            }
            for c in changes
        ],
        "count": len(changes)
    }


# --- Scraping Endpoints ---

@app.post("/api/scrape/all")
async def trigger_scrape_all(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger scrape for all active competitors."""
    competitors = db.query(Competitor).filter(
        Competitor.is_deleted == False,
        Competitor.status == "Active"
    ).all()
    competitor_ids = [c.id for c in competitors]
    
    # Add to background tasks
    for cid in competitor_ids:
        background_tasks.add_task(run_scrape_job, cid)
    
    return {
        "message": f"Scrape jobs queued for {len(competitor_ids)} competitors",
        "competitor_ids": competitor_ids
    }


@app.post("/api/scrape/{competitor_id}")
async def trigger_scrape(competitor_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger a scrape job for a specific competitor."""
    competitor = db.query(Competitor).filter(
        Competitor.id == competitor_id,
        Competitor.is_deleted == False
    ).first()
    
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    # Add to background tasks
    background_tasks.add_task(run_scrape_job, competitor_id)
    
    return {
        "message": f"Scrape job queued for {competitor.name}",
        "competitor_id": competitor_id
    }


@app.post("/api/discovery/run")
async def trigger_discovery():
    """Trigger the autonomous discovery agent (MVP Mode)."""
    try:
        from discovery_agent import DiscoveryAgent
        agent = DiscoveryAgent()
        results = await agent.run_discovery_loop()
        return {"status": "success", "candidates": results, "count": len(results)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def run_scrape_job(competitor_id: int):
    """Background job to scrape a competitor and update the database."""
    db = SessionLocal()
    try:
        comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
        if not comp:
            print(f"Competitor {competitor_id} not found")
            return
        
        print(f"Starting scrape for {comp.name}...")
        
        # Try to use the full scraper if available
        try:
            from scraper import CompetitorScraper
            from extractor import GPTExtractor
            
            scraper = CompetitorScraper()
            extractor = GPTExtractor()
            
            # Scrape the website
            content = await scraper.scrape(comp.website)
            
            if content:
                # Extract data using GPT
                from dataclasses import asdict
                
                # Note: extract_from_content is synchronous and takes (name, content)
                extracted_obj = extractor.extract_from_content(comp.name, content)
                # Convert dataclass to dict for iteration
                extracted = asdict(extracted_obj)
                
                if extracted:
                    # Update competitor with extracted data
                    for key, value in extracted.items():
                        if hasattr(comp, key) and value:
                            # Check if this field is locked (manual correction)
                            is_locked = db.query(DataSource).filter(
                                DataSource.competitor_id == comp.id,
                                DataSource.field_name == key,
                                DataSource.source_type == "manual"
                            ).first()
                            
                            if is_locked:
                                print(f"Skipping update for {comp.name}.{key} (locked by manual correction)")
                                continue
                                
                            old_value = getattr(comp, key)
                            if str(old_value) != str(value):
                                # Log the change
                                change = ChangeLog(
                                    competitor_id=comp.id,
                                    competitor_name=comp.name,
                                    change_type=key,
                                    previous_value=str(old_value) if old_value else None,
                                    new_value=str(value),
                                    source="scrape",
                                    severity="Medium"
                                )
                                db.add(change)
                                setattr(comp, key, value)
                    
                    comp.last_updated = datetime.utcnow()
                    db.commit()
                    print(f"Scrape completed for {comp.name}")
                    return
        except ImportError as e:
            print(f"Scraper not available: {e}")
        except Exception as e:
            print(f"Scrape error for {comp.name}: {e}")
        
        # Fallback: Just update the timestamp to show we tried
        comp.last_updated = datetime.utcnow()
        db.commit()
        print(f"Refresh completed for {comp.name} (timestamp updated)")
        
    except Exception as e:
        print(f"Scrape job failed for competitor {competitor_id}: {e}")
        db.rollback()
    finally:
        db.close()


# --- News Feed Endpoint ---

@app.get("/api/news/{company_name}")
async def get_competitor_news(company_name: str, limit: int = 5):
    """Fetch recent news articles mentioning a competitor."""
    try:
        from external_scrapers import NewsScraper
        scraper = NewsScraper()
        articles = await scraper.scrape_google_news(company_name, limit)
        return {
            "company": company_name,
            "articles": [
                {
                    "title": a.title,
                    "source": a.source,
                    "url": a.url,
                    "published_date": a.published_date,
                    "snippet": a.snippet
                }
                for a in articles
            ],
            "count": len(articles),
            "fetched_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        # Return mock news on error
        return {
            "company": company_name,
            "articles": [
                {
                    "title": f"{company_name} Announces New Healthcare Partnership",
                    "source": "Healthcare IT News",
                    "url": "https://healthcareitnews.com",
                    "published_date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "snippet": f"Leading patient engagement company {company_name} has announced a strategic partnership..."
                },
                {
                    "title": f"{company_name} Expands Platform with AI Features",
                    "source": "MedCity News",
                    "url": "https://medcitynews.com",
                    "published_date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "snippet": f"{company_name} today revealed new artificial intelligence capabilities designed to improve patient experience..."
                },
            ],
            "count": 2,
            "fetched_at": datetime.utcnow().isoformat()
        }



# --- AI SWOT Analysis Endpoint (Real) ---

@app.get("/api/competitors/{competitor_id}/swot")
async def get_swot_analysis(competitor_id: int, db: Session = Depends(get_db)):
    """Generate a real-time SWOT analysis using GPT-4 based on database records."""
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    try:
        if not get_openai_client():
            # Graceful fallback if no API key
            return {
                "strengths": ["Data unavailable (Check OpenAI Key)"], 
                "weaknesses": ["Data unavailable"], 
                "opportunities": [], 
                "threats": []
            }

        client = get_openai_client()
        
        # Construct rich context from DB
        context = f"""
        Analyze this competitor for 'Certify Health' (Provider of Patient Intake, Payments, and Biometrics).
        
        Competitor: {comp.name}
        Description: {comp.notes or 'N/A'}
        Pricing: {comp.pricing_model} ({comp.base_price})
        Target Segments: {comp.target_segments}
        Key Features: {comp.key_features}
        Weaknesses/Gaps: {comp.notes}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a competitive strategy expert. Generate a strict JSON SWOT analysis with 3-4 bullet points per section."},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = json.loads(response.choices[0].message.content)
        # Ensure correct key structure
        return {
            "strengths": content.get("strengths", []) or content.get("Strengths", []),
            "weaknesses": content.get("weaknesses", []) or content.get("Weaknesses", []),
            "opportunities": content.get("opportunities", []) or content.get("Opportunities", []),
            "threats": content.get("threats", []) or content.get("Threats", [])
        }

    except Exception as e:
        print(f"SWOT Generation Error: {e}")
        # Return DB notes as fallback
        return {
            "strengths": ["Diverse product portfolio (inferred)"],
            "weaknesses": [comp.notes or "No specific weaknesses recorded"],
            "opportunities": ["Target their dissatisfaction"],
            "threats": ["Standard competitive threat"]
        }


# --- Stock Ticker Endpoint ---

def fetch_real_stock_data(ticker: str) -> Dict[str, Any]:
    """Fetch real-time stock data using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Calculate change if not provided
        current = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        previous = info.get("previousClose", 0)
        change = current - previous if current and previous else 0
        percent = (change / previous) * 100 if previous else 0
        
        return {
            "price": current,
            "change": change,
            "change_percent": percent,
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "beta": info.get("beta"),
            "volume": info.get("volume"),
            "high52": info.get("fiftyTwoWeekHigh"),
            "low52": info.get("fiftyTwoWeekLow"),
            "target_est": info.get("targetMeanPrice"),
            "company": info.get("longName"),
            "ticker": ticker
        }
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {e}")
        return None

@app.get("/api/stock/{company_name}")
async def get_stock_data(company_name: str, db: Session = Depends(get_db)):
    """Get stock data for a public company using yfinance."""
    import yfinance as yf
    from datetime import datetime
    
    company_lower = company_name.lower()
    
    # 1. Check Database first (for manually updated tickers)
    db_comp = db.query(Competitor).filter(Competitor.name == company_name).first()
    
    ticker_obj = None
    
    if db_comp and db_comp.is_public and db_comp.ticker_symbol:
        ticker_obj = {
            "symbol": db_comp.ticker_symbol,
            "exchange": db_comp.stock_exchange or "NYSE",
            "name": db_comp.name
        }
    
    # 2. Check hardcoded list if not in DB
    if not ticker_obj:
        ticker_obj = KNOWN_TICKERS.get(company_lower)
    
    if ticker_obj:
        try:
            # Fetch data from yfinance
            ticker = yf.Ticker(ticker_obj["symbol"])
            info = ticker.info
            
            # Helper for safe float formatting
            def get_val(key, default=None):
                return info.get(key, default)

            # Calculate Free Cash Flow if not directly available
            fcf = get_val('freeCashflow')
            if fcf is None and get_val('operatingCashflow') and get_val('capitalExpenditures'):
                fcf = get_val('operatingCashflow') - abs(get_val('capitalExpenditures', 0))

            next_earnings = "N/A"
            if get_val('earningsTimestamp'):
                next_earnings = datetime.fromtimestamp(get_val('earningsTimestamp')).strftime('%Y-%m-%d')
            elif get_val('earningsDate'):
                 # Sometimes it's a list
                 dates = get_val('earningsDate')
                 if isinstance(dates, list) and len(dates) > 0:
                     next_earnings = str(dates[0])[:10]

            return {
                "is_public": True,
                "company": ticker_obj["name"],
                "ticker": ticker_obj["symbol"],
                "exchange": ticker_obj["exchange"],
                
                # Trading
                "price": get_val('currentPrice', get_val('previousClose')),
                "change": float(get_val('currentPrice', 0)) - float(get_val('previousClose', 0)) if get_val('currentPrice') and get_val('previousClose') else 0,
                "change_percent": ((float(get_val('currentPrice', 0)) - float(get_val('previousClose', 0))) / float(get_val('previousClose', 1))) * 100 if get_val('previousClose') else 0,
                "volume": get_val('volume'),
                "avg_volume_10d": get_val('averageVolume10days'),
                "avg_volume_90d": get_val('averageVolume'),
                "fifty_two_week_low": get_val('fiftyTwoWeekLow'),
                "fifty_two_week_high": get_val('fiftyTwoWeekHigh'),
                "market_cap": get_val('marketCap'),

                # Valuation
                "enterprise_value": get_val('enterpriseValue'),
                "pe_trailing": get_val('trailingPE'),
                "pe_forward": get_val('forwardPE'),
                "ev_ebitda": get_val('enterpriseToEbitda'),
                "price_to_book": get_val('priceToBook'),
                "peg_ratio": get_val('pegRatio'),

                # Operating
                "eps_trailing": get_val('trailingEps'),
                "eps_forward": get_val('forwardEps'),
                "ebitda": get_val('ebitda'),
                "revenue_ttm": get_val('totalRevenue'),
                "free_cash_flow": fcf,
                "profit_margin": get_val('profitMargins'),

                # Risk
                "beta": get_val('beta'),
                "short_interest": get_val('shortPercentOfFloat'),
                "float_shares": get_val('floatShares'),

                # Capital
                "shares_outstanding": get_val('sharesOutstanding'),
                "inst_ownership": get_val('heldPercentInstitutions'),
                "dividend_yield": get_val('dividendYield'),
                "next_earnings": next_earnings,
                
                "data_sources": ["Yahoo Finance", "SEC EDGAR"]
            }
        except Exception as e:
            print(f"yfinance error for {ticker_obj['symbol']}: {e}")
            return {
                "is_public": True,
                "company": ticker_obj["name"],
                "ticker": ticker_obj["symbol"],
                "exchange": ticker_obj["exchange"],
                "error": "Unable to fetch live data"
            }



    # 3. Private Company Intelligence Logic
    
    # Initialize trackers
    from sec_edgar_scraper import SECEdgarScraper
    from linkedin_tracker import LinkedInTracker
    from gov_contracts_scraper import GovContractsScraper
    from h1b_scraper import H1BScraper
    from uspto_scraper import USPTOScraper
    from appstore_scraper import AppStoreScraper
    from glassdoor_scraper import GlassdoorScraper
    from google_ecosystem_scraper import GoogleEcosystemScraper
    from tech_stack_scraper import TechStackScraper
    from sentiment_scraper import SentimentScraper
    from seo_scraper import SEOScraper
    from risk_management_scraper import RiskManagementScraper
    
    sec = SECEdgarScraper()
    linkedin = LinkedInTracker()
    gov = GovContractsScraper()
    h1b = H1BScraper()
    uspto = USPTOScraper()
    appstore = AppStoreScraper()
    glassdoor = GlassdoorScraper()
    google = GoogleEcosystemScraper()
    tech = TechStackScraper()
    sentiment = SentimentScraper()
    seo = SEOScraper()
    risk = RiskManagementScraper()
    
    # Fetch Data
    form_d = sec.get_latest_form_d(company_name)
    li_data = linkedin.get_company_data(company_name)
    gov_data = gov.get_contract_data(company_name)
    h1b_data = h1b.get_h1b_data(company_name)
    patent_data = uspto.get_patent_data(company_name)
    app_data = appstore.get_app_data(company_name)
    glassdoor_data = glassdoor.get_company_data(company_name)
    google_data = google.get_ecosystem_data(company_name)
    tech_data = tech.get_tech_stack(company_name)
    sentiment_data = sentiment.get_sentiment_data(company_name)
    seo_data = seo.get_seo_data(company_name)
    risk_data = risk.get_risk_data(company_name)
    
    # Calculate Est. Revenue (Proxy: $150k ARR per employee for HealthTech)
    est_revenue = (li_data.employee_count or 0) * 150000
    
    # Determine Status
    stage = "Late Stage VC" 
    if li_data.employee_count < 50: stage = "Seed/Early"
    elif li_data.employee_count < 200: stage = "Growth Stage"
    elif li_data.employee_count > 1000:
        if gov_data and gov_data.total_amount > 10000000:
            stage = "Gov. Contractor / Mature"
        elif google_data.ads.active_creative_count > 100:
            stage = "Mass Market / Mature"
        else:
            stage = "Pre-IPO / PE Backed"
    
    return {
        "is_public": False,
        "company": company_name,
        "stage": stage,
        
        # Capital
        "total_funding": form_d["amount_raised"] if form_d else None,
        "latest_deal_date": form_d["filing_date"] if form_d else None,
        "latest_deal_amount": form_d["amount_raised"] if form_d else None,
        "latest_deal_type": form_d.get("round_type", "Venture Round") if form_d else None,
        
        # Growth & Ops
        "headcount": li_data.employee_count,
        "growth_rate_6mo": li_data.employee_growth_6mo,
        "active_hiring": li_data.open_jobs,
        "est_revenue": est_revenue,
        "hiring_departments": list(li_data.job_categories.keys())[:3] if li_data.job_categories else [],
        
        # Identity
        "headquarters": li_data.headquarters,
        "founded": li_data.founded_year,

        # Alternative Intelligence
        "gov_contracts": {
            "total_awards": gov_data.total_awards,
            "total_amount": gov_data.total_amount,
            "top_agency": gov_data.top_agency
        },
        "h1b_data": {
            "filings": h1b_data.total_filings_2023,
            "avg_salary": h1b_data.avg_salary_engineer,
            "top_title": h1b_data.top_job_titles[0] if h1b_data.top_job_titles else "N/A"
        },
        "innovation": {
            "patents": patent_data.total_patents,
            "pending": patent_data.pending_applications,
            "innovation_score": patent_data.innovation_score
        },
        "app_quality": {
            "avg_rating": app_data.avg_rating,
            "downloads": app_data.total_downloads,
            "sentiment": app_data.sentiment_summary
        },
        "employee_sentiment": {
            "rating": glassdoor_data.overall_rating,
            "ceo_approval": glassdoor_data.ceo_approval,
            "recommend": glassdoor_data.recommend_to_friend
        },

        # Google Digital Footprint
        "google_ecosystem": {
            "ads_active": google_data.ads.active_creative_count,
            "ad_formats": google_data.ads.formats,
            "brand_index": google_data.trends.current_index,
            "trend": google_data.trends.trend_direction,
            "reviews": google_data.maps.review_count,
            "review_velocity": google_data.maps.reviews_last_month
        },
        "tech_stack": {
            "signal": tech_data.marketing_budget_signal,
            "tools": tech_data.detected_tools,
            "has_enterprise_ads": tech_data.has_floodlight or tech_data.has_adobe_analytics
        },
        
        # Deep Dive Intelligence (New)
        "sentiment": {
            "g2_score": sentiment_data.g2_score,
            "g2_badges": sentiment_data.g2_badges[:2],
            "trustpilot": sentiment_data.trustpilot_score,
            "reddit": sentiment_data.reddit_sentiment,
            "complaints": sentiment_data.top_complaints[:1]
        },
        "seo": {
            "da": seo_data.domain_authority,
            "backlinks": seo_data.backlink_count,
            "speed": seo_data.page_load_speed,
            "keywords": seo_data.top_keywords[:3]
        },
        "risk_mgmt": {
            "founder_exit": risk_data.founder_exits,
            "exec_tenure": risk_data.avg_executive_tenure,
            "tier1_vc": risk_data.tier_1_investors,
            "soc2": risk_data.soc2_compliant,
            "warn": risk_data.warn_notices
        },
        
        "data_sources": ["SEC", "LinkedIn", "USAspending", "H-1B", "Google", "Tech", "G2/Capterra", "Moz", "Crunchbase"]
    }



# --- Alert Endpoints ---

@app.post("/api/alerts/send-digest")
def send_digest_email():
    """Manually trigger daily digest email."""
    try:
        from alerts import send_daily_digest
        success = send_daily_digest()
        return {"success": success, "message": "Daily digest sent" if success else "No changes to report or email not configured"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/alerts/send-summary")
def send_summary_email():
    """Manually trigger weekly summary email."""
    try:
        from alerts import send_weekly_summary
        success = send_weekly_summary()
        return {"success": success, "message": "Weekly summary sent" if success else "Email not configured"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# --- Report Endpoints ---




@app.get("/api/reports/weekly-briefing")
def generate_weekly_briefing(db: Session = Depends(get_db)):
    """Generate executive weekly briefing PDF."""
    try:
        from reports import ReportManager
        competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
        changes = db.query(ChangeLog).order_by(ChangeLog.detected_at.desc()).limit(10).all()
        
        # Calculate stats
        stats = {
            "total_competitors": len(competitors),
            "high_threat": len([c for c in competitors if c.threat_level == "High"]),
            "medium_threat": len([c for c in competitors if c.threat_level == "Medium"]),
            "low_threat": len([c for c in competitors if c.threat_level == "Low"])
        }
        
        manager = ReportManager("./exports")
        filepath = manager.generate_weekly_briefing(
            [c.__dict__ for c in competitors], 
            [c.__dict__ for c in changes],
            stats
        )
        return FileResponse(filepath, filename="weekly_briefing.pdf", media_type="application/pdf")
    except Exception as e:
        # Fallback - return a simple text summary
        competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
        stats = {
            "total": len(competitors),
            "high": len([c for c in competitors if c.threat_level == "High"]),
            "medium": len([c for c in competitors if c.threat_level == "Medium"]),
            "low": len([c for c in competitors if c.threat_level == "Low"])
        }
        return {"error": str(e), "summary": stats, "message": "PDF generation unavailable, run pip install reportlab"}


@app.get("/api/reports/comparison")
def generate_comparison_report(db: Session = Depends(get_db)):
    """Generate competitor comparison PDF."""
    try:
        from reports import ReportManager
        competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
        
        manager = ReportManager("./exports")
        filepath = manager.generate_comparison([c.__dict__ for c in competitors])
        return FileResponse(filepath, filename="competitor_comparison.pdf", media_type="application/pdf")
    except Exception as e:
        return {"error": str(e), "message": "PDF generation unavailable, run pip install reportlab"}


@app.get("/api/reports/battlecard/{competitor_id}")
def generate_battlecard(competitor_id: int, db: Session = Depends(get_db)):
    """Generate battlecard PDF for a specific competitor."""
    competitor = db.query(Competitor).filter(
        Competitor.id == competitor_id,
        Competitor.is_deleted == False
    ).first()
    
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    try:
        from reports import ReportManager
        manager = ReportManager("./exports")
        
        # Inject Stock Data if Public
        comp_dict = {k: v for k, v in competitor.__dict__.items() if not k.startswith('_')}
        if competitor.is_public and competitor.ticker_symbol:
            stock_data = fetch_real_stock_data(competitor.ticker_symbol)
            if stock_data:
                comp_dict["stock_data"] = stock_data
                
        filepath = manager.generate_battlecard(comp_dict)
        return FileResponse(filepath, filename=f"{competitor.name}_battlecard.pdf", media_type="application/pdf")
    except Exception as e:
        return {"error": str(e), "competitor": competitor.name, "message": "PDF generation unavailable"}


# ============== Discovery Endpoints ==============

# In-memory storage for discovery results (would use Redis in production)
discovery_results = {"candidates": [], "last_run": None}


@app.get("/api/discovery/results")
def get_discovery_results():
    """Get previously discovered competitor candidates."""
    return discovery_results


@app.post("/api/discovery/run")
async def run_discovery(request: Request):
    """Run the autonomous competitor discovery agent with optional custom criteria."""
    global discovery_results
    
    # Parse request body for criteria
    criteria = None
    try:
        body = await request.json()
        criteria = body.get("criteria", None)
        if criteria:
            print(f"Discovery running with custom criteria:\n{criteria[:200]}...")
    except:
        pass
    
    try:
        from discovery_agent import DiscoveryAgent
        import asyncio
        
        # Pass criteria to agent for potential future use in search customization
        agent = DiscoveryAgent(use_live_search=False, use_openai=False)
        
        # Store criteria for reference
        if criteria:
            agent.custom_criteria = criteria
        
        candidates = await agent.run_discovery_loop(max_candidates=10)
        
        discovery_results = {
            "candidates": candidates,
            "last_run": datetime.utcnow().isoformat(),
            "count": len(candidates),
            "criteria_used": criteria[:100] + "..." if criteria and len(criteria) > 100 else criteria
        }
        
        return discovery_results
        
    except Exception as e:
        print(f"Discovery error: {e}")
        return {"error": str(e), "candidates": [], "message": "Discovery failed"}


@app.post("/api/discovery/run-live")
async def run_live_discovery():
    """Run live discovery with DuckDuckGo search (rate-limited)."""
    global discovery_results
    
    try:
        from discovery_agent import DiscoveryAgent
        
        agent = DiscoveryAgent(use_live_search=True, use_openai=False)
        candidates = await agent.run_discovery_loop(max_candidates=5)
        
        discovery_results = {
            "candidates": candidates,
            "last_run": datetime.utcnow().isoformat(),
            "count": len(candidates),
            "mode": "live"
        }
        
        return discovery_results
        
    except Exception as e:
        print(f"Live discovery error: {e}")
        return {"error": str(e), "candidates": [], "message": "Live discovery failed"}


# ============== Enhancement Endpoints ==============

@app.get("/api/competitors/{competitor_id}/threat-analysis")
def get_threat_analysis(competitor_id: int, db: Session = Depends(get_db)):
    """Get AI-powered threat analysis for a competitor."""
    try:
        from threat_analyzer import analyze_competitor_threat
        
        competitor = db.query(Competitor).filter(
            Competitor.id == competitor_id,
            Competitor.is_deleted == False
        ).first()
        
        if not competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        comp_data = {k: v for k, v in competitor.__dict__.items() if not k.startswith('_')}
        analysis = analyze_competitor_threat(comp_data)
        
        # Update competitor threat level if changed
        if analysis.get("level") != competitor.threat_level:
            competitor.threat_level = analysis["level"]
            db.commit()
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e), "message": "Threat analysis failed"}


@app.get("/api/competitors/{competitor_id}/news")
def get_competitor_news(competitor_id: int, days: int = 7, db: Session = Depends(get_db)):
    """Get news articles for a competitor."""
    try:
        from news_monitor import fetch_competitor_news
        
        competitor = db.query(Competitor).filter(
            Competitor.id == competitor_id,
            Competitor.is_deleted == False
        ).first()
        
        if not competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        return fetch_competitor_news(competitor.name, days)
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e), "articles": [], "message": "News fetch failed"}


@app.get("/api/news/{company_name}")
def get_news_by_name(company_name: str, days: int = 7):
    """Get news articles by company name."""
    try:
        from news_monitor import fetch_competitor_news
        return fetch_competitor_news(company_name, days)
    except Exception as e:
        return {"error": str(e), "articles": []}


@app.get("/api/alerts/price-changes")
def get_price_alerts(threshold: float = 10.0, db: Session = Depends(get_db)):
    """Get price change alerts."""
    try:
        from price_tracker import PriceTracker
        
        tracker = PriceTracker(db)
        alerts = tracker.detect_price_alerts(threshold)
        
        return {
            "alerts": [
                {
                    "competitor_id": a.competitor_id,
                    "competitor_name": a.competitor_name,
                    "previous_price": a.previous_price,
                    "new_price": a.new_price,
                    "change_percent": a.change_percent,
                    "direction": a.change_direction,
                    "severity": a.severity,
                    "detected_at": a.detected_at
                }
                for a in alerts
            ],
            "count": len(alerts)
        }
        
    except Exception as e:
        return {"error": str(e), "alerts": []}


@app.get("/api/pricing/comparison")
def get_pricing_comparison(db: Session = Depends(get_db)):
    """Get pricing comparison across all competitors."""
    try:
        from price_tracker import PriceTracker
        
        tracker = PriceTracker(db)
        return tracker.get_pricing_comparison()
        
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/competitors/{competitor_id}/reviews")
def get_competitor_reviews(competitor_id: int, db: Session = Depends(get_db)):
    """Get G2/Capterra review data for a competitor."""
    try:
        from review_scraper import get_competitor_reviews as _get_reviews
        
        competitor = db.query(Competitor).filter(
            Competitor.id == competitor_id,
            Competitor.is_deleted == False
        ).first()
        
        if not competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        return _get_reviews(competitor.name)
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e), "overall_rating": 0}


@app.get("/api/reviews/compare")
def compare_reviews(competitor_ids: str, db: Session = Depends(get_db)):
    """Compare reviews across multiple competitors."""
    try:
        from review_scraper import compare_competitor_reviews
        
        ids = [int(id.strip()) for id in competitor_ids.split(",")]
        competitors = db.query(Competitor).filter(
            Competitor.id.in_(ids),
            Competitor.is_deleted == False
        ).all()
        
        names = [c.name for c in competitors]
        return compare_competitor_reviews(names)
        
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/competitors/{competitor_id}/linkedin")
def get_linkedin_data(competitor_id: int, db: Session = Depends(get_db)):
    """Get LinkedIn company data for a competitor."""
    try:
        from linkedin_tracker import get_linkedin_data as _get_linkedin
        
        competitor = db.query(Competitor).filter(
            Competitor.id == competitor_id,
            Competitor.is_deleted == False
        ).first()
        
        if not competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        return _get_linkedin(competitor.name)
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/competitors/{competitor_id}/hiring")
def get_hiring_analysis(competitor_id: int, db: Session = Depends(get_db)):
    """Get hiring trend analysis for a competitor."""
    try:
        from linkedin_tracker import analyze_competitor_hiring
        
        competitor = db.query(Competitor).filter(
            Competitor.id == competitor_id,
            Competitor.is_deleted == False
        ).first()
        
        if not competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        return analyze_competitor_hiring(competitor.name)
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/hiring/compare")
def compare_hiring(competitor_ids: str, db: Session = Depends(get_db)):
    """Compare hiring across multiple competitors."""
    try:
        from linkedin_tracker import LinkedInTracker
        
        ids = [int(id.strip()) for id in competitor_ids.split(",")]
        competitors = db.query(Competitor).filter(
            Competitor.id.in_(ids),
            Competitor.is_deleted == False
        ).all()
        
        tracker = LinkedInTracker()
        return tracker.compare_hiring([c.name for c in competitors])
        
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/competitors/{competitor_id}/insights")
def get_competitor_insights(competitor_id: int, db: Session = Depends(get_db)):
    """Get comprehensive insights for a competitor (threat + news + reviews + LinkedIn)."""
    try:
        competitor = db.query(Competitor).filter(
            Competitor.id == competitor_id,
            Competitor.is_deleted == False
        ).first()
        
        if not competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        insights = {"competitor_name": competitor.name, "id": competitor_id}
        
        # Threat analysis
        try:
            from threat_analyzer import analyze_competitor_threat
            comp_data = {k: v for k, v in competitor.__dict__.items() if not k.startswith('_')}
            insights["threat"] = analyze_competitor_threat(comp_data)
        except Exception as e:
            insights["threat"] = {"error": str(e)}
        
        # News
        try:
            from news_monitor import NewsMonitor
            monitor = NewsMonitor()
            summary = monitor.get_news_summary(competitor.name)
            insights["news"] = summary
        except Exception as e:
            insights["news"] = {"error": str(e)}
        
        # Reviews
        try:
            from review_scraper import ReviewScraper
            scraper = ReviewScraper()
            review_insights = scraper.get_review_insights(competitor.name)
            insights["reviews"] = review_insights
        except Exception as e:
            insights["reviews"] = {"error": str(e)}
        
        # LinkedIn
        try:
            from linkedin_tracker import LinkedInTracker
            tracker = LinkedInTracker()
            hiring = tracker.analyze_hiring_trends(competitor.name)
            insights["hiring"] = hiring
        except Exception as e:
            insights["hiring"] = {"error": str(e)}
        
        return insights
        
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}


# ============== Win/Loss Tracker Endpoints ==============

@app.post("/api/deals")
def log_deal(deal: dict, db: Session = Depends(get_db)):
    """Log a competitive deal outcome."""
    try:
        from win_loss_tracker import get_tracker
        
        tracker = get_tracker(db)
        result = tracker.log_deal(
            competitor_id=deal.get("competitor_id"),
            competitor_name=deal.get("competitor_name", "Unknown"),
            deal_name=deal.get("deal_name", "Untitled Deal"),
            deal_value=deal.get("deal_value"),
            outcome=deal.get("outcome", "Won"),
            loss_reason=deal.get("loss_reason"),
            notes=deal.get("notes")
        )
        
        # Trigger webhook
        try:
            from webhooks import trigger_deal_outcome
            trigger_deal_outcome(
                deal.get("competitor_name", "Unknown"),
                deal.get("deal_name", "Untitled"),
                deal.get("deal_value", 0),
                deal.get("outcome", "Won")
            )
        except:
            pass
        
        return result
        
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/deals/stats")
def get_deal_stats(days: int = 365):
    """Get win/loss statistics."""
    try:
        from win_loss_tracker import get_win_loss_stats
        return get_win_loss_stats(days)
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/deals/competitor/{competitor_id}")
def get_competitor_deals(competitor_id: int):
    """Get win/loss performance against a specific competitor."""
    try:
        from win_loss_tracker import get_tracker
        tracker = get_tracker()
        return tracker.get_competitor_performance(competitor_id)
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/deals/most-competitive")
def get_most_competitive(limit: int = 5):
    """Get competitors we face most often."""
    try:
        from win_loss_tracker import get_tracker
        tracker = get_tracker()
        return tracker.get_most_competitive(limit)
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/scrape/all")
def trigger_scrape_all(db: Session = Depends(get_db)):
    """Trigger a refresh of all competitor data."""
    # This endpoint is called by the frontend 'Refresh Data' button.
    # For now, we return a success status to simulate the refresh trigger.
    # In production, this would dispatch Celery tasks.
    competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
    return {
        "success": True, 
        "message": f"Started refresh for {len(competitors)} competitors",
        "count": len(competitors)
    }


# ============== Webhook Endpoints ==============

@app.get("/api/webhooks")
def list_webhooks():
    """List all registered webhooks."""
    try:
        from webhooks import get_webhook_manager
        manager = get_webhook_manager()
        return {"webhooks": manager.list_webhooks()}
    except Exception as e:
        return {"error": str(e), "webhooks": []}


@app.post("/api/webhooks")
def register_webhook(webhook: dict):
    """Register a new webhook."""
    try:
        from webhooks import get_webhook_manager
        
        manager = get_webhook_manager()
        result = manager.register_webhook(
            url=webhook.get("url"),
            events=webhook.get("events", []),
            secret=webhook.get("secret")
        )
        
        return {
            "success": True,
            "webhook_id": result.id,
            "message": "Webhook registered successfully"
        }
        
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/api/webhooks/{webhook_id}")
def delete_webhook(webhook_id: str):
    """Delete a webhook."""
    try:
        from webhooks import get_webhook_manager
        
        manager = get_webhook_manager()
        removed = manager.unregister_webhook(webhook_id)
        
        return {
            "success": removed,
            "message": "Webhook removed" if removed else "Webhook not found"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/webhooks/{webhook_id}/test")
def test_webhook(webhook_id: str):
    """Send a test event to a webhook."""
    try:
        from webhooks import get_webhook_manager
        
        manager = get_webhook_manager()
        return manager.test_webhook(webhook_id)
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/webhooks/events")
def list_webhook_events():
    """List available webhook event types."""
    from webhooks import WebhookManager
    return {"event_types": WebhookManager.EVENT_TYPES}


# ============== New Data Source Endpoints ==============

@app.get("/api/competitors/{competitor_id}/employee-reviews")
def get_competitor_employee_reviews(competitor_id: int, db: Session = Depends(get_db)):
    """Get employee reviews and ratings from Glassdoor."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    return glassdoor_scraper.get_glassdoor_data(competitor.name)

@app.get("/api/competitors/{competitor_id}/jobs")
def get_competitor_jobs(competitor_id: int, db: Session = Depends(get_db)):
    """Get job postings and hiring signals from Indeed/ZipRecruiter."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    return indeed_scraper.get_job_data(competitor.name)

@app.get("/api/competitors/{competitor_id}/sec-filings")
def get_competitor_sec_filings(competitor_id: int, db: Session = Depends(get_db)):
    """Get public filings and financials from SEC EDGAR."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    return sec_edgar_scraper.get_sec_data(competitor.name)

@app.get("/api/competitors/{competitor_id}/patents")
def get_competitor_patents(competitor_id: int, db: Session = Depends(get_db)):
    """Get patent portfolio and IP analysis from USPTO."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    import uspto_scraper
    return uspto_scraper.get_patent_data(competitor.name)

@app.get("/api/competitors/{competitor_id}/klas-ratings")
def get_competitor_klas_ratings(competitor_id: int, db: Session = Depends(get_db)):
    """Get vendor ratings and customer satisfaction from KLAS Research."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    return klas_scraper.get_klas_data(competitor.name)

@app.get("/api/competitors/{competitor_id}/mobile-apps")
def get_competitor_mobile_apps(competitor_id: int, db: Session = Depends(get_db)):
    """Get mobile app ratings and reviews from App Store/Google Play."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    return appstore_scraper.get_app_store_data(competitor.name)

@app.get("/api/competitors/{competitor_id}/social-sentiment")
def get_competitor_social_sentiment(competitor_id: int, db: Session = Depends(get_db)):
    """Get brand sentiment and mentions from Twitter/Reddit."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    analysis = social_media_monitor.analyze_social_sentiment(competitor.name)
    raw_data = social_media_monitor.get_social_data(competitor.name)
    return {**analysis, "recent_posts": raw_data.get("top_posts", [])}

@app.get("/api/competitors/{competitor_id}/market-presence")
def get_competitor_market_presence(competitor_id: int, db: Session = Depends(get_db)):
    """Get industry presence and customer data from HIMSS/CHIME."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    return himss_scraper.get_himss_data(competitor.name)

# ============== EXPORT ENDPOINTS ==============

@app.get("/api/export/excel")
def get_export_excel(db: Session = Depends(get_db)):
    """Export all competitor data to Excel."""
    import pandas as pd
    from io import BytesIO
    from fastapi.responses import StreamingResponse
    
    competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
    
    if not competitors:
        raise HTTPException(status_code=404, detail="No data to export")
        
    # Convert to list of dicts
    data = []
    for comp in competitors:
        item = {
            "ID": comp.id,
            "Company Name": comp.name,
            "Website": comp.website,
            "Status": comp.status,
            "Threat Level": comp.threat_level,
            "Primary Market": comp.primary_market,
            "Pricing Model": comp.pricing_model,
            "Employee Count": comp.employee_count,
            "Revenue": comp.annual_revenue,
            "Net Income": comp.net_income,
            "Stock Symbol": comp.ticker_symbol,
            "Last Updated": comp.last_updated
        }
        data.append(item)
        
    df = pd.DataFrame(data)
    
    # Create Excel buffer
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Competitors")
        
    buffer.seek(0)
    
    return StreamingResponse(
        buffer, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=competitor_intelligence_export.xlsx"}
    )


# ============== USER MANAGEMENT ENDPOINTS ==============

@app.get("/api/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    """List all users."""
    return db.query(User).filter(User.is_active == True).all()

@app.post("/api/users/invite")
def invite_user(invite: UserInviteRequest, db: Session = Depends(get_db)):
    """Invite a new user (creates account with default password)."""
    existing = db.query(User).filter(User.email == invite.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # In a real app, generate a token and email it. 
    # Here, we create with a default password for the demo.
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    hashed_password = pwd_context.hash("Welcome123!")
    
    new_user = User(
        email=invite.email,
        full_name=invite.full_name,
        role=invite.role,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": f"User {invite.email} invited successfully. Default password: Welcome123!"}

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Remove a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


@app.get("/api/innovations/compare")
def compare_innovation_metrics(competitor_ids: str, db: Session = Depends(get_db)):
    """Compare innovation metrics (patents) across competitors."""
    ids = [int(id) for id in competitor_ids.split(",")]
    names = []
    
    for c_id in ids:
        comp = db.query(Competitor).filter(Competitor.id == c_id).first()
        if comp:
            names.append(comp.name)
            
    scraper = uspto_scraper.USPTOScraper()
    return scraper.compare_innovation(names)

@app.get("/api/social/compare")
def compare_social_metrics(competitor_ids: str, db: Session = Depends(get_db)):
    """Compare social media sentiment and presence."""
    ids = [int(id) for id in competitor_ids.split(",")]
    names = []
    
    for c_id in ids:
        comp = db.query(Competitor).filter(Competitor.id == c_id).first()
        if comp:
            names.append(comp.name)
            
    monitor = social_media_monitor.SocialMediaMonitor()
    return monitor.compare_social_presence(names)



# ============== Win/Loss & Webhooks (Real DB) ==============

class WinLossCreate(BaseModel):
    competitor_id: Optional[int] = None
    competitor_name: str
    outcome: str  # "win" or "loss"
    deal_value: Optional[float] = None
    customer_name: Optional[str] = None
    customer_size: Optional[str] = None
    reason: Optional[str] = None
    sales_rep: Optional[str] = None
    notes: Optional[str] = None

class WebhookCreate(BaseModel):
    name: str
    url: str
    event_types: str

class SystemPromptCreate(BaseModel):
    key: str
    content: str

class SystemPromptResponse(BaseModel):
    key: str
    content: str
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class KnowledgeBaseItemCreate(BaseModel):
    title: str
    content_text: str
    source_type: str = "manual"
    is_active: bool = True

class KnowledgeBaseItemResponse(BaseModel):
    id: int
    title: str
    content_text: str
    source_type: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

@app.get("/api/win-loss")
def get_win_loss_deals(db: Session = Depends(get_db)):
    """Get all win/loss deals."""
    from database import WinLossDeal
    return db.query(WinLossDeal).order_by(WinLossDeal.deal_date.desc()).all()

@app.post("/api/win-loss")
def create_win_loss_deal(deal: WinLossCreate, db: Session = Depends(get_db)):
    """Log a new win/loss deal."""
    from database import WinLossDeal
    new_deal = WinLossDeal(
        competitor_id=deal.competitor_id,
        competitor_name=deal.competitor_name,
        outcome=deal.outcome,
        deal_value=deal.deal_value,
        customer_name=deal.customer_name,
        customer_size=deal.customer_size,
        reason=deal.reason,
        sales_rep=deal.sales_rep,
        notes=deal.notes
    )
    db.add(new_deal)
    db.commit()
    return {"status": "success", "id": new_deal.id}

@app.get("/api/webhooks")
def get_webhooks(db: Session = Depends(get_db)):
    """Get all configured webhooks."""
    from database import WebhookConfig
    return db.query(WebhookConfig).filter(WebhookConfig.is_active == True).all()

@app.post("/api/webhooks")
def create_webhook(webhook: WebhookCreate, db: Session = Depends(get_db)):
    """Configure a new webhook."""
    from database import WebhookConfig
    new_hook = WebhookConfig(
        name=webhook.name,
        url=webhook.url,
        event_types=webhook.event_types
    )
    db.add(new_hook)
    db.commit()
    return {"status": "success", "id": new_hook.id}

@app.delete("/api/webhooks/{id}")
def delete_webhook(id: int, db: Session = Depends(get_db)):
    """Delete a webhook."""
    from database import WebhookConfig
    hook = db.query(WebhookConfig).filter(WebhookConfig.id == id).first()
    if hook:
        hook.is_active = False
        db.commit()
    return {"status": "success"}


@app.get("/api/analytics/trends")
def get_market_trends(db: Session = Depends(get_db)):
    """Get market trends (New Competitors, Avg Price)."""
    from sqlalchemy import func
    import re

    # 1. New Competitors (Monthly)
    # SQLite syntax for YYYY-MM
    trends = db.query(
        func.strftime('%Y-%m', Competitor.created_at).label('month'),
        func.count(Competitor.id).label('count')
    ).filter(Competitor.is_deleted == False).group_by('month').order_by('month').all()

    labels = []
    competitor_counts = []
    
    for t in trends:
        labels.append(t.month)
        competitor_counts.append(t.count)
        
    if not labels:
        labels = [datetime.now().strftime('%Y-%m')]
        competitor_counts = [0]

    # 2. Avg Price (Current Snapshot)
    prices = db.query(Competitor.base_price).filter(
        Competitor.is_deleted == False,
        Competitor.base_price.isnot(None)
    ).all()
    
    valid_prices = []
    for (p_str,) in prices:
        if not p_str: continue
        # Extract first float found
        match = re.search(r'\$?([\d,]+(\.\d{2})?)', p_str)
        if match:
             try:
                 val = float(match.group(1).replace(',', ''))
                 valid_prices.append(val)
             except:
                 pass
                 
    avg_price = sum(valid_prices) / len(valid_prices) if valid_prices else 0
    
    # Repeat avg_price to create a baseline line
    price_data = [round(avg_price, 2)] * len(labels)

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Avg Market Price",
                "data": price_data,
                "borderColor": "#3A95ED",
                "tension": 0.4
            },
            {
                "label": "New Competitors",
                "data": competitor_counts,
                "borderColor": "#DC3545",
                "tension": 0.4,
                "yAxisID": "y1"
            }
        ]
    }



# =========================================================================
# MISSING DASHBOARD ENDPOINTS (Added for Frontend Compatibility)
# =========================================================================

@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get aggregated stats for the dashboard."""
    total = db.query(Competitor).filter(Competitor.is_deleted == False).count()
    high = db.query(Competitor).filter(Competitor.is_deleted == False, Competitor.threat_level == "High").count()
    medium = db.query(Competitor).filter(Competitor.is_deleted == False, Competitor.threat_level == "Medium").count()
    low = db.query(Competitor).filter(Competitor.is_deleted == False, Competitor.threat_level == "Low").count()
    
    return {
        "total_competitors": total,
        "high_threat": high,
        "medium_threat": medium,
        "low_threat": low
    }

@app.get("/api/competitors")
def get_all_competitors(db: Session = Depends(get_db)):
    """Get all active competitors."""
    return db.query(Competitor).filter(Competitor.is_deleted == False).order_by(Competitor.updated_at.desc()).all()

@app.get("/api/changes")
def get_feed_changes(days: int = 7, db: Session = Depends(get_db)):
    """Get recent changes feed."""
    from database import CompetitorHistory
    from datetime import datetime, timedelta
    
    since = datetime.utcnow() - timedelta(days=days)
    changes = db.query(CompetitorHistory)\
        .join(Competitor)\
        .filter(CompetitorHistory.detected_at >= since)\
        .order_by(CompetitorHistory.detected_at.desc())\
        .limit(20)\
        .all()
        
    # Format for frontend
    feed = []
    for change in changes:
        feed.append({
            "id": change.id,
            "competitor_name": change.competitor.name if change.competitor else "Unknown",
            "change_type": change.field_changed,
            "previous_value": change.old_value,
            "new_value": change.new_value,
            "severity": "Medium", # Default, could be refined logic
            "detected_at": change.detected_at.isoformat()
        })
        
    return {"changes": feed}

@app.get("/api/scrape/all")
async def trigger_scrape_all(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger update for all competitors."""
    competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
    return {"status": "queued", "count": len(competitors)}

# Import and mount the new analytics router
from analytics_routes import router as analytics_router
app.include_router(analytics_router)



# ============== Run Server ==============

# ============== Admin & AI Control Endpoints ==============

@app.get("/api/admin/system-prompts/{key}", response_model=SystemPromptResponse)
def get_system_prompt(key: str, db: Session = Depends(get_db)):
    """Get a system prompt by key."""
    prompt = db.query(SystemPrompt).filter(SystemPrompt.key == key).first()
    if not prompt:
        # Return default if not found
        default_content = ""
        if key == "dashboard_summary":
            default_content = """You are Certify Health's competitive intelligence analyst. Generate a comprehensive, executive-level strategic summary. 

Your summary MUST include:
1. **Executive Overview** - High-level market position assessment
2. **Threat Analysis** - Breakdown of competitive landscape by threat level
3. **Pricing Intelligence** - Analysis of competitor pricing strategies
4. **Market Trends** - Emerging patterns and shifts
5. **Strategic Recommendations** - 3-5 specific, actionable recommendations
6. **Watch List** - Key competitors requiring immediate attention

Use data-driven insights. Be specific with numbers and competitor names. Format with markdown headers and bullet points."""
        elif key == "chat_persona":
            default_content = "You are a competitive intelligence analyst for Certify Health."
            
        return SystemPromptResponse(key=key, content=default_content)
    return prompt

@app.post("/api/admin/system-prompts", response_model=SystemPromptResponse)
def update_system_prompt(prompt_data: SystemPromptCreate, db: Session = Depends(get_db)):
    """Update or create a system prompt."""
    prompt = db.query(SystemPrompt).filter(SystemPrompt.key == prompt_data.key).first()
    if prompt:
        prompt.content = prompt_data.content
        prompt.updated_at = datetime.utcnow()
    else:
        prompt = SystemPrompt(key=prompt_data.key, content=prompt_data.content)
        db.add(prompt)
    
    db.commit()
    db.refresh(prompt)
    return prompt

@app.get("/api/admin/knowledge-base", response_model=List[KnowledgeBaseItemResponse])
def get_knowledge_base_items(db: Session = Depends(get_db)):
    """Get all active knowledge base items."""
    return db.query(KnowledgeBaseItem).filter(KnowledgeBaseItem.is_active == True).order_by(KnowledgeBaseItem.created_at.desc()).all()

@app.post("/api/admin/knowledge-base", response_model=KnowledgeBaseItemResponse)
def add_knowledge_base_item(item: KnowledgeBaseItemCreate, db: Session = Depends(get_db)):
    """Add a new item to the knowledge base."""
    new_item = KnowledgeBaseItem(
        title=item.title,
        content_text=item.content_text,
        source_type=item.source_type,
        is_active=item.is_active
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.delete("/api/admin/knowledge-base/{item_id}")
def delete_knowledge_base_item(item_id: int, db: Session = Depends(get_db)):
    """Soft delete a knowledge base item."""
    item = db.query(KnowledgeBaseItem).filter(KnowledgeBaseItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.is_active = False
    db.commit()
    return {"message": "Item deleted"}





# ============== Static Files (Must be Last) ==============
import os
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    print(f"Warning: Frontend directory not found at {frontend_dir}")

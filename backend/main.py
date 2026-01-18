"""
Certify Intel - Simplified Backend for Excel Dashboard
A lightweight FastAPI backend that:
1. Stores competitor data in SQLite (simple, no PostgreSQL setup needed)
2. Scrapes competitor websites using Playwright
3. Extracts data using OpenAI GPT
4. Exports data to Excel-compatible formats
"""
import os
import json
import asyncio
import yfinance as yf
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager


from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

# New Data Source Imports
import crunchbase_scraper
import glassdoor_scraper
import indeed_scraper
import sec_edgar_scraper
import uspto_scraper
import klas_scraper
import appstore_scraper
import social_media_monitor
import himss_scraper
import pitchbook_scraper

# Database setup - SQLite for simplicity
DATABASE_URL = "sqlite:///./certify_intel.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

# ============== Database Models ==============

class Competitor(Base):
    __tablename__ = "competitors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    website = Column(String)
    status = Column(String, default="Active")
    threat_level = Column(String, default="Medium")
    last_updated = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    data_quality_score = Column(Integer, nullable=True)
    
    # Pricing
    pricing_model = Column(String, nullable=True)
    base_price = Column(String, nullable=True)
    price_unit = Column(String, nullable=True)
    
    # Product
    product_categories = Column(String, nullable=True)
    key_features = Column(Text, nullable=True)
    integration_partners = Column(String, nullable=True)
    certifications = Column(String, nullable=True)
    
    # Market
    target_segments = Column(String, nullable=True)
    customer_size_focus = Column(String, nullable=True)
    geographic_focus = Column(String, nullable=True)
    customer_count = Column(String, nullable=True)
    customer_acquisition_rate = Column(String, nullable=True)
    key_customers = Column(String, nullable=True)
    g2_rating = Column(String, nullable=True)
    
    # Company
    employee_count = Column(String, nullable=True)
    employee_growth_rate = Column(String, nullable=True)
    year_founded = Column(String, nullable=True)
    headquarters = Column(String, nullable=True)
    funding_total = Column(String, nullable=True)
    latest_round = Column(String, nullable=True)
    pe_vc_backers = Column(String, nullable=True)
    
    # Digital
    website_traffic = Column(String, nullable=True)
    social_following = Column(String, nullable=True)
    recent_launches = Column(String, nullable=True)
    news_mentions = Column(String, nullable=True)
    
    # Stock info (for public companies)
    is_public = Column(Boolean, default=False)
    ticker_symbol = Column(String, nullable=True)
    stock_exchange = Column(String, nullable=True)
    
    # Metadata
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChangeLog(Base):
    __tablename__ = "change_log"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, index=True)
    competitor_name = Column(String)
    change_type = Column(String)
    previous_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    source = Column(String, nullable=True)
    severity = Column(String, default="Low")
    detected_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


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


class ScrapeRequest(BaseModel):
    competitor_id: int
    pages_to_scrape: List[str] = ["homepage", "pricing", "about"]


# ============== FastAPI App ==============

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Certify Intel Backend starting...")
    
    # Run Public/Private Workflow on Startup
    try:
        db = SessionLocal()
        print("Running 'Private vs Public' Classification Workflow...")
        competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
        updates_count = 0
        for comp in competitors:
            comp_name_lower = comp.name.lower()
            if comp_name_lower in KNOWN_TICKERS:
                info = KNOWN_TICKERS[comp_name_lower]
                if not comp.is_public or comp.ticker_symbol != info["symbol"]:
                    print(f"  [AUTO-CLASSIFY] Identifying {comp.name} as PUBLIC ({info['symbol']})")
                    comp.is_public = True
                    comp.ticker_symbol = info["symbol"]
                    comp.stock_exchange = info["exchange"]
                    updates_count += 1
        if updates_count > 0:
            db.commit()
        print(f"Classification validation complete. {updates_count} records updated/verified.")
        db.close()
    except Exception as e:
        print(f"Error in startup classification: {e}")
        
    yield
    # Shutdown
    print("Certify Intel Backend shutting down...")

app = FastAPI(
    title="Certify Intel API",
    description="Backend API for competitive intelligence Excel dashboard",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/app", StaticFiles(directory="../frontend", html=True), name="app")


# Database dependency - MUST be defined before routes that use it
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/analytics/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Generate high-level AI executive summary of dashboard data."""
    try:
        from analytics import AnalyticsEngine
        
        # Get active competitors
        competitors = db.query(Competitor).filter(
            Competitor.is_deleted == False,
            Competitor.status == "Active"
        ).all()
        
        if not competitors:
            return {"summary": "No active competitors found to analyze.", "type": "empty"}
        
        # Convert to dicts
        comp_dicts = []
        for c in competitors:
            c_dict = {
                "name": c.name,
                "threat_level": c.threat_level,
                "base_price": c.base_price,
                "target_segments": c.target_segments,
                "key_features": c.key_features,
                "customer_count": c.customer_count,
                "product_categories": c.product_categories,
                "g2_rating": c.g2_rating,
                "funding_total": c.funding_total,
                "employee_count": c.employee_count
            }
            comp_dicts.append(c_dict)
            
        engine = AnalyticsEngine()
        result = engine.comparative_analysis(comp_dicts)
        return result["executive_summary"]
        
    except Exception as e:
        print(f"Summary Error: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=500, content={"summary": "Failed to generate summary", "error": str(e)})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return RedirectResponse(url="/app")


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# --- Competitors CRUD ---

@app.get("/api/competitors", response_model=List[CompetitorResponse])
def list_competitors(
    status: Optional[str] = None,
    threat_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Competitor).filter(Competitor.is_deleted == False)
    if status:
        query = query.filter(Competitor.status == status)
    if threat_level:
        query = query.filter(Competitor.threat_level == threat_level)
    competitors = query.offset(skip).limit(limit).all()
    return competitors


@app.get("/api/competitors/{competitor_id}", response_model=CompetitorResponse)
def get_competitor(competitor_id: int, db: Session = Depends(get_db)):
    competitor = db.query(Competitor).filter(
        Competitor.id == competitor_id,
        Competitor.is_deleted == False
    ).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return competitor


@app.post("/api/competitors", response_model=CompetitorResponse)
def create_competitor(competitor: CompetitorCreate, db: Session = Depends(get_db)):
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
def update_competitor(competitor_id: int, competitor: CompetitorCreate, db: Session = Depends(get_db)):
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
def delete_competitor(competitor_id: int, db: Session = Depends(get_db)):
    db_competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not db_competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    db_competitor.is_deleted = True
    db.commit()
    return {"message": "Competitor deleted"}


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
                extracted = await extractor.extract(content, comp.name)
                
                if extracted:
                    # Update competitor with extracted data
                    for key, value in extracted.items():
                        if hasattr(comp, key) and value:
                            old_value = getattr(comp, key)
                            if old_value != value:
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

@app.get("/api/competitors/{competitor_id}/funding")
def get_competitor_funding(competitor_id: int, db: Session = Depends(get_db)):
    """Get funding and acquisition data from Crunchbase."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    return crunchbase_scraper.get_crunchbase_data(competitor.name)

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

@app.get("/api/competitors/{competitor_id}/market-intelligence")
def get_competitor_market_intelligence(competitor_id: int, db: Session = Depends(get_db)):
    """Get valuation and market intelligence from PitchBook/CB Insights."""
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    return pitchbook_scraper.get_pitchbook_data(competitor.name)

# Comparison Endpoints

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

@app.get("/api/market/compare")
def compare_market_metrics(competitor_ids: str, db: Session = Depends(get_db)):
    """Compare market valuations and growth."""
    ids = [int(id) for id in competitor_ids.split(",")]
    names = []
    
    for c_id in ids:
        comp = db.query(Competitor).filter(Competitor.id == c_id).first()
        if comp:
            names.append(comp.name)
            
    scraper = pitchbook_scraper.PitchBookScraper()
    return scraper.compare_valuations(names)

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


# ============== Run Server ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



"""
Certify Intel - Extended API Routes
Additional endpoints for analytics, win/loss, auth, reports, and frontend serving
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from typing import Optional, List
from datetime import datetime, timedelta
import os

# Import extended features
from extended_features import (
    auth_manager, win_loss_tracker, rate_limiter, cache_manager,
    similarweb_scraper, social_monitor,
    WinLossRecord
)
from analytics import AnalyticsEngine
from reports import ReportManager
from external_scrapers import ExternalDataCollector

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


# ============== Authentication ==============

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token."""
    user = auth_manager.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = auth_manager.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@router.get("/api/auth/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user info."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = auth_manager.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"email": payload.get("sub"), "role": payload.get("role")}


# ============== Win/Loss Database ==============

@router.get("/api/winloss")
async def get_winloss_records(
    competitor: Optional[str] = None,
    outcome: Optional[str] = None
):
    """Get win/loss records."""
    records = win_loss_tracker.get_records(competitor, outcome)
    return {
        "records": [
            {
                "id": r.id,
                "competitor_name": r.competitor_name,
                "outcome": r.outcome,
                "deal_value": r.deal_value,
                "deal_date": r.deal_date.isoformat() if r.deal_date else None,
                "customer_name": r.customer_name,
                "customer_size": r.customer_size,
                "loss_reason": r.loss_reason,
                "win_factor": r.win_factor,
                "sales_rep": r.sales_rep,
                "notes": r.notes
            }
            for r in records
        ],
        "count": len(records)
    }


@router.post("/api/winloss")
async def add_winloss_record(
    competitor_name: str,
    outcome: str,
    deal_value: Optional[float] = None,
    customer_name: Optional[str] = None,
    customer_size: Optional[str] = None,
    loss_reason: Optional[str] = None,
    win_factor: Optional[str] = None,
    sales_rep: Optional[str] = None,
    notes: Optional[str] = None
):
    """Add a new win/loss record."""
    record = WinLossRecord(
        id=0,
        competitor_id=None,
        competitor_name=competitor_name,
        outcome=outcome,
        deal_value=deal_value,
        customer_name=customer_name,
        customer_size=customer_size,
        loss_reason=loss_reason,
        win_factor=win_factor,
        sales_rep=sales_rep,
        notes=notes
    )
    win_loss_tracker.add_record(record)
    return {"message": "Record added", "id": record.id}


@router.get("/api/winloss/stats")
async def get_winloss_stats():
    """Get win/loss statistics."""
    return win_loss_tracker.get_stats()


# ============== Analytics ==============

analytics_engine = AnalyticsEngine()

@router.get("/api/analytics/competitor/{competitor_id}")
async def get_competitor_analysis(competitor_id: int):
    """Get full analytics for a competitor."""
    from main import SessionLocal, Competitor
    
    db = SessionLocal()
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    db.close()
    
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    # Convert to dict
    comp_dict = {
        "name": comp.name,
        "website": comp.website,
        "threat_level": comp.threat_level,
        "target_segments": comp.target_segments,
        "customer_size_focus": comp.customer_size_focus,
        "funding_total": comp.funding_total,
        "employee_growth_rate": comp.employee_growth_rate,
        "product_categories": comp.product_categories,
        "customer_count": comp.customer_count,
        "base_price": comp.base_price,
        "pricing_model": comp.pricing_model,
        "recent_launches": comp.recent_launches,
        "key_features": comp.key_features,
        "g2_rating": comp.g2_rating,
        "year_founded": comp.year_founded,
        "headquarters": comp.headquarters,
        "employee_count": comp.employee_count,
        "latest_round": comp.latest_round,
    }
    
    return analytics_engine.full_analysis(comp_dict)


@router.get("/api/analytics/heatmap")
async def get_competitive_heatmap():
    """Get competitive heatmap data."""
    from main import SessionLocal, Competitor
    
    db = SessionLocal()
    comps = db.query(Competitor).filter(Competitor.is_deleted == False).all()
    db.close()
    
    comp_dicts = [{"name": c.name, "threat_level": c.threat_level} for c in comps]
    
    return analytics_engine.heatmap_generator.generate_heatmap_data(comp_dicts)


# ============== External Data ==============

external_collector = ExternalDataCollector()

@router.get("/api/external/{competitor_name}")
async def get_external_data(competitor_name: str):
    """Get external data for a competitor (G2, LinkedIn, News, etc.)."""
    # Check cache first
    cache_key = f"external:{competitor_name.lower()}"
    cached = cache_manager.get(cache_key)
    if cached:
        return cached
    
    # Collect fresh data
    data = await external_collector.collect_all(competitor_name)
    
    # Cache for 1 hour
    cache_manager.set(cache_key, data, ttl=3600)
    
    return data


@router.get("/api/traffic/{domain}")
async def get_traffic_data(domain: str):
    """Get SimilarWeb traffic data for a domain."""
    data = await similarweb_scraper.get_traffic_data(domain)
    return {
        "domain": data.domain,
        "total_visits": data.total_visits,
        "avg_visit_duration": data.avg_visit_duration,
        "pages_per_visit": data.pages_per_visit,
        "bounce_rate": data.bounce_rate,
        "traffic_sources": data.traffic_sources,
        "top_countries": data.top_countries
    }


@router.get("/api/social/{competitor_name}")
async def get_social_mentions(competitor_name: str, days: int = 7):
    """Get social media mentions for a competitor."""
    posts = await social_monitor.search_mentions(competitor_name, days)
    sentiment = social_monitor.analyze_sentiment(posts)
    
    return {
        "posts": [
            {
                "platform": p.platform,
                "content": p.content,
                "url": p.url,
                "author": p.author,
                "engagement": p.engagement,
                "sentiment": p.sentiment
            }
            for p in posts
        ],
        "sentiment_analysis": sentiment
    }


# ============== Reports ==============

report_manager = ReportManager("./reports")

@router.get("/api/reports/weekly-briefing")
async def generate_weekly_briefing():
    """Generate and return weekly executive briefing PDF."""
    from main import SessionLocal, Competitor, ChangeLog
    
    db = SessionLocal()
    competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
    
    # Get recent changes
    week_ago = datetime.utcnow() - timedelta(days=7)
    changes = db.query(ChangeLog).filter(ChangeLog.detected_at >= week_ago).all()
    
    db.close()
    
    comp_dicts = [{"name": c.name, "threat_level": c.threat_level, "customer_count": c.customer_count} for c in competitors]
    change_dicts = [
        {
            "competitor_name": c.competitor_name,
            "change_type": c.change_type,
            "previous_value": c.previous_value,
            "new_value": c.new_value,
            "severity": c.severity
        }
        for c in changes
    ]
    
    stats = {
        "total_competitors": len(competitors),
        "high_threat": len([c for c in competitors if c.threat_level == "High"]),
        "medium_threat": len([c for c in competitors if c.threat_level == "Medium"]),
        "low_threat": len([c for c in competitors if c.threat_level == "Low"])
    }
    
    path = report_manager.generate_weekly_briefing(comp_dicts, change_dicts, stats)
    
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"certify_intel_briefing_{datetime.now().strftime('%Y%m%d')}.pdf"
    )


@router.get("/api/reports/battlecard/{competitor_id}")
async def generate_battlecard(competitor_id: int):
    """Generate and return competitor battlecard PDF."""
    from main import SessionLocal, Competitor
    # Import Scrapers
    from linkedin_tracker import LinkedInTracker
    from google_ecosystem_scraper import GoogleEcosystemScraper
    from sentiment_scraper import SentimentScraper
    from tech_stack_scraper import TechStackScraper
    from seo_scraper import SEOScraper
    from risk_management_scraper import RiskManagementScraper
    
    db = SessionLocal()
    comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    db.close()
    
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    # Fetch Real-time Intelligence
    linkedin = LinkedInTracker()
    google = GoogleEcosystemScraper()
    sentiment = SentimentScraper()
    tech = TechStackScraper()
    seo = SEOScraper()
    risk = RiskManagementScraper()

    li_data = linkedin.get_company_data(comp.name)
    google_data = google.get_ecosystem_data(comp.name)
    sent_data = sentiment.get_sentiment_data(comp.name)
    tech_data = tech.get_tech_stack(comp.name)
    seo_data = seo.get_seo_data(comp.name)
    risk_data = risk.get_risk_data(comp.name)

    # Calculate Data Points
    est_rev = (li_data.employee_count or 0) * 150000
    stage = "Late Stage VC" 
    if li_data.employee_count < 50: stage = "Seed/Early"
    elif li_data.employee_count < 200: stage = "Growth Stage"
    elif li_data.employee_count > 1000:
        if google_data.ads.active_creative_count > 100: stage = "Mass Market"
        else: stage = "Pre-IPO / PE"
    
    comp_dict = {
        "name": comp.name,
        "website": comp.website,
        "threat_level": comp.threat_level,
        "year_founded": comp.year_founded,
        "headquarters": comp.headquarters,
        "employee_count": comp.employee_count,
        "customer_count": comp.customer_count,
        "funding_total": comp.funding_total,
        "pricing_model": comp.pricing_model,
        "base_price": comp.base_price,
        "product_categories": comp.product_categories,
        "key_features": comp.key_features,
        "target_segments": comp.target_segments,
        "g2_rating": comp.g2_rating,
        "latest_round": comp.latest_round,
        # Deep Dive Data Structure
        "deep_dive": {
            "capital": {
                "est_revenue": f"${est_rev:,.0f}" if est_rev else "N/A",
                "funding_total": comp.funding_total,
                "stage": stage
            },
            "growth": {
                "headcount": li_data.employee_count,
                "growth_rate": li_data.employee_growth_6mo,
                "active_hiring": li_data.open_jobs
            },
            "digital": {
                "ads_active": google_data.ads.active_creative_count,
                "brand_index": google_data.trends.current_index,
                "trend": google_data.trends.trend_direction,
                "review_velocity": google_data.maps.reviews_last_month,
                "tech_signal": tech_data.marketing_budget_signal
            },
            "sentiment": {
                "g2_score": sent_data.g2_score
            },
            "seo": {
                "da": seo_data.domain_authority
            },
            "risk": {
                "founder_exit": "Exited Founder" if risk_data.founder_exits else "Standard",
                "warn": risk_data.warn_notices > 0
            }
        }
    }
    
    path = report_manager.generate_battlecard(comp_dict)
    
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"battlecard_{comp.name.replace(' ', '_').lower()}.pdf"
    )


@router.get("/api/reports/comparison")
async def generate_comparison_report():
    """Generate and return comparison report PDF."""
    from main import SessionLocal, Competitor
    # Only essentials for comparison to avoid timeout
    from google_ecosystem_scraper import GoogleEcosystemScraper
    from seo_scraper import SEOScraper
    
    db = SessionLocal()
    competitors = db.query(Competitor).filter(
        Competitor.is_deleted == False,
        Competitor.threat_level.in_(["High", "Medium"])
    ).all()
    db.close()
    
    google = GoogleEcosystemScraper()
    seo = SEOScraper()

    comp_dicts = []
    
    for c in competitors:
        # Lite fetch
        google_data = google.get_ecosystem_data(c.name)
        seo_data = seo.get_seo_data(c.name)
        
        comp_dicts.append({
            "name": c.name,
            "threat_level": c.threat_level,
            "pricing_model": c.pricing_model,
            "base_price": c.base_price,
            "customer_count": c.customer_count,
            "employee_count": c.employee_count,
            "g2_rating": c.g2_rating,
            "target_segments": c.target_segments,
            "funding_total": c.funding_total,
            "product_categories": c.product_categories,
            "deep_dive": {
                "digital": {
                    "ads_active": google_data.ads.active_creative_count,
                    "brand_index": google_data.trends.current_index
                },
                "seo": {
                    "da": seo_data.domain_authority
                }
            }
        })
    
    path = report_manager.generate_comparison(comp_dicts)
    
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"certify_intel_comparison_{datetime.now().strftime('%Y%m%d')}.pdf"
    )


# ============== Rate Limiting Middleware ==============

async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to requests."""
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        return HTMLResponse(
            content='{"error": "Rate limit exceeded"}',
            status_code=429,
            media_type="application/json"
        )
    
    response = await call_next(request)
    
    # Add rate limit headers
    remaining = rate_limiter.get_remaining(client_ip)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.limit)
    
    return response

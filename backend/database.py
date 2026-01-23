from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database setup - SQLite for simplicity
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./certify_intel.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
    
    # Market Vertical Tracking (aligned with Certify Health's 11 markets)
    primary_market = Column(String, nullable=True)  # hospitals, ambulatory, behavioral, etc.
    markets_served = Column(String, nullable=True)  # Semicolon-separated: "hospitals;ambulatory;telehealth"
    market_focus_score = Column(Integer, nullable=True)  # 0-100 overlap with Certify markets
    
    # Product Overlap Tracking (aligned with Certify Health's 7 products)
    has_pxp = Column(Boolean, default=False)  # Patient Experience Platform
    has_pms = Column(Boolean, default=False)  # Practice Management System
    has_rcm = Column(Boolean, default=False)  # Revenue Cycle Management
    has_patient_mgmt = Column(Boolean, default=False)  # Patient Management / EHR
    has_payments = Column(Boolean, default=False)  # CERTIFY Pay equivalent
    has_biometric = Column(Boolean, default=False)  # FaceCheck equivalent
    has_interoperability = Column(Boolean, default=False)  # EHR integrations
    product_overlap_score = Column(Integer, nullable=True)  # 0-100 overlap with Certify products
    
    # Enhanced Analytics Fields
    telehealth_capabilities = Column(Boolean, default=False)
    ai_features = Column(String, nullable=True)  # "ai scribe;chatbot;analytics"
    mobile_app_available = Column(Boolean, default=False)
    hipaa_compliant = Column(Boolean, default=True)
    ehr_integrations = Column(String, nullable=True)  # "Epic;Cerner;Athena"
    
    # ===========================================
    # FREE API DATA SOURCES
    # ===========================================
    
    # Clearbit Logo API (free unlimited)
    logo_url = Column(String, nullable=True)  # https://logo.clearbit.com/domain.com
    
    # SEC EDGAR API (free unlimited - public companies only)
    sec_cik = Column(String, nullable=True)  # SEC Central Index Key
    annual_revenue = Column(String, nullable=True)  # From 10-K filing
    net_income = Column(String, nullable=True)  # From 10-K filing
    sec_employee_count = Column(String, nullable=True)  # From 10-K filing
    fiscal_year_end = Column(String, nullable=True)  # e.g., "January 31"
    recent_sec_filings = Column(String, nullable=True)  # JSON: recent 8-K, 10-Q filings
    sec_risk_factors = Column(String, nullable=True)  # Competition section from 10-K
    
    # Hunter.io API (free 25/month)
    email_pattern = Column(String, nullable=True)  # "{first}.{last}@company.com"
    key_contacts = Column(String, nullable=True)  # JSON: executive emails
    hunter_email_count = Column(Integer, nullable=True)  # Total emails found
    
    # Google Custom Search API (free 100/day)
    last_google_search = Column(DateTime, nullable=True)  # Rate limiting
    
    # Metadata
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_verified_at = Column(DateTime, nullable=True)  # For freshness tracking


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


class DataSource(Base):
    """Tracks the source of each data point for every competitor field."""
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, index=True)
    field_name = Column(String, index=True)  # e.g., "pricing_model", "funding_total"
    source_type = Column(String)  # "external", "manual", "calculated"
    source_url = Column(String, nullable=True)  # URL for external sources
    entered_by = Column(String, nullable=True)  # Username for manual entries
    formula = Column(Text, nullable=True)  # Formula string for calculated values
    source_name = Column(String, nullable=True)  # e.g., "Crunchbase", "Company Website"
    verified_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataChangeHistory(Base):
    """Detailed audit log of all data changes with user attribution."""
    __tablename__ = "data_change_history"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, index=True)
    competitor_name = Column(String)
    field_name = Column(String, index=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_by = Column(String)  # Username who made the change
    change_reason = Column(String, nullable=True)
    source_url = Column(String, nullable=True)  # Where the new data came from
    changed_at = Column(DateTime, default=datetime.utcnow, index=True)


class User(Base):
    """User model for authentication and RBAC."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    role = Column(String, default="viewer")  # viewer, analyst, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)



class SystemPrompt(Base):
    """Dynamic system prompts for AI generation."""
    __tablename__ = "system_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)  # e.g., "dashboard_summary", "chat_persona"
    content = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgeBaseItem(Base):
    """Internal documents and text for RAG."""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content_text = Column(Text, nullable=False)   # Extracted text from PDF/Doc
    source_type = Column(String, default="manual") # manual, upload, integration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    key = Column(String, primary_key=True, index=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)


class WinLossDeal(Base):
    """Record of a competitive deal (win or loss)."""
    __tablename__ = "win_loss_deals"
    
    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, index=True)
    competitor_name = Column(String)
    outcome = Column(String)  # "win" or "loss"
    deal_value = Column(Float, nullable=True)
    deal_date = Column(DateTime, default=datetime.utcnow)
    customer_name = Column(String, nullable=True)
    customer_size = Column(String, nullable=True)
    reason = Column(String, nullable=True)  # "loss_reason" or "win_factor"
    sales_rep = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class WebhookConfig(Base):
    """Configuration for outbound webhooks."""
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    url = Column(String)
    event_types = Column(String)  # JSON-encoded list of events or comma-separated
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

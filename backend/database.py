from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import sys

# Database setup - SQLite for simplicity
# PyInstaller Fix (v5.0.3): Ensure database is created next to executable, not in temp folder
def _get_database_url():
    """Get database URL with PyInstaller awareness."""
    # First check if explicitly set (by __main__.py or user)
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    # If running as PyInstaller bundle, use exe directory
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        db_path = os.path.join(exe_dir, 'certify_intel.db')
        return f'sqlite:///{db_path}'

    # Default for development
    return "sqlite:///./certify_intel.db"

DATABASE_URL = _get_database_url()
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
    # SALES & MARKETING MODULE: 9 COMPETITIVE DIMENSIONS (v5.0.7)
    # ===========================================
    # Each dimension has: score (1-5), evidence (text), updated (datetime)

    # Dimension 1: Product Modules & Packaging
    dim_product_packaging_score = Column(Integer, nullable=True)  # 1-5 (1=Major Weakness, 5=Major Strength)
    dim_product_packaging_evidence = Column(Text, nullable=True)
    dim_product_packaging_updated = Column(DateTime, nullable=True)

    # Dimension 2: Interoperability & Integration Depth
    dim_integration_depth_score = Column(Integer, nullable=True)  # 1-5
    dim_integration_depth_evidence = Column(Text, nullable=True)
    dim_integration_depth_updated = Column(DateTime, nullable=True)

    # Dimension 3: Customer Support & Service Model
    dim_support_service_score = Column(Integer, nullable=True)  # 1-5
    dim_support_service_evidence = Column(Text, nullable=True)
    dim_support_service_updated = Column(DateTime, nullable=True)

    # Dimension 4: Retention & Product Stickiness
    dim_retention_stickiness_score = Column(Integer, nullable=True)  # 1-5
    dim_retention_stickiness_evidence = Column(Text, nullable=True)
    dim_retention_stickiness_updated = Column(DateTime, nullable=True)

    # Dimension 5: User Adoption & Ease of Use
    dim_user_adoption_score = Column(Integer, nullable=True)  # 1-5
    dim_user_adoption_evidence = Column(Text, nullable=True)
    dim_user_adoption_updated = Column(DateTime, nullable=True)

    # Dimension 6: Implementation Effort & Time to Value
    dim_implementation_ttv_score = Column(Integer, nullable=True)  # 1-5
    dim_implementation_ttv_evidence = Column(Text, nullable=True)
    dim_implementation_ttv_updated = Column(DateTime, nullable=True)

    # Dimension 7: Reliability & Enterprise Readiness
    dim_reliability_enterprise_score = Column(Integer, nullable=True)  # 1-5
    dim_reliability_enterprise_evidence = Column(Text, nullable=True)
    dim_reliability_enterprise_updated = Column(DateTime, nullable=True)

    # Dimension 8: Pricing Model & Commercial Flexibility
    dim_pricing_flexibility_score = Column(Integer, nullable=True)  # 1-5
    dim_pricing_flexibility_evidence = Column(Text, nullable=True)
    dim_pricing_flexibility_updated = Column(DateTime, nullable=True)

    # Dimension 9: Reporting & Analytics Capability
    dim_reporting_analytics_score = Column(Integer, nullable=True)  # 1-5
    dim_reporting_analytics_evidence = Column(Text, nullable=True)
    dim_reporting_analytics_updated = Column(DateTime, nullable=True)

    # Aggregate Dimension Scores
    dim_overall_score = Column(Float, nullable=True)  # Average of all 9 dimensions
    dim_sales_priority = Column(String, nullable=True)  # High/Medium/Low based on threat + dimensions

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
    """Enhanced source tracking for every data point with confidence scoring."""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), index=True)
    field_name = Column(String, index=True)  # e.g., "customer_count", "base_price"

    # Value tracking
    current_value = Column(String, nullable=True)
    previous_value = Column(String, nullable=True)

    # Source attribution
    source_type = Column(String)  # "website_scrape", "sec_filing", "manual", "api", "news"
    source_url = Column(String, nullable=True)
    source_name = Column(String, nullable=True)  # "Company Website", "SEC 10-K 2025", "KLAS Report"
    extraction_method = Column(String, nullable=True)  # "gpt_extraction", "structured_api", "manual_entry"
    extracted_at = Column(DateTime, default=datetime.utcnow)

    # Confidence scoring (Admiralty Code)
    source_reliability = Column(String, nullable=True)  # A-F scale (A=completely reliable, F=unknown)
    information_credibility = Column(Integer, nullable=True)  # 1-6 scale (1=confirmed, 6=cannot be judged)
    confidence_score = Column(Integer, nullable=True)  # 0-100 composite score
    confidence_level = Column(String, nullable=True)  # "high", "moderate", "low"

    # Verification tracking
    is_verified = Column(Boolean, default=False)
    verified_by = Column(String, nullable=True)  # "triangulation", "manual", "sec_filing"
    verification_date = Column(DateTime, nullable=True)
    corroborating_sources = Column(Integer, default=0)  # Number of sources that agree

    # Temporal relevance
    data_as_of_date = Column(DateTime, nullable=True)  # When the data was true (not when extracted)
    staleness_days = Column(Integer, default=0)

    # Legacy fields for backwards compatibility
    entered_by = Column(String, nullable=True)  # Username for manual entries
    formula = Column(Text, nullable=True)  # Formula string for calculated values
    verified_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CompetitorProduct(Base):
    """Individual product/solution offered by a competitor."""
    __tablename__ = "competitor_products"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), index=True)

    # Product identification
    product_name = Column(String)  # e.g., "Phreesia Intake", "Athena Collector"
    product_category = Column(String)  # e.g., "Patient Intake", "RCM", "EHR"
    product_subcategory = Column(String, nullable=True)  # e.g., "Self-Service Kiosk"

    # Product details
    description = Column(Text, nullable=True)
    key_features = Column(Text, nullable=True)  # JSON array
    target_segment = Column(String, nullable=True)  # "SMB", "Mid-Market", "Enterprise"

    # Competitive positioning
    is_primary_product = Column(Boolean, default=False)  # Main revenue driver
    market_position = Column(String, nullable=True)  # "Leader", "Challenger", "Niche"

    # Metadata
    launched_date = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)

    # Relationships
    pricing_tiers = relationship("ProductPricingTier", back_populates="product")
    created_at = Column(DateTime, default=datetime.utcnow)


class ProductPricingTier(Base):
    """Pricing tier for a specific product."""
    __tablename__ = "product_pricing_tiers"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("competitor_products.id"), index=True)

    # Tier identification
    tier_name = Column(String)  # e.g., "Basic", "Professional", "Enterprise"
    tier_position = Column(Integer, nullable=True)  # 1, 2, 3... for ordering

    # Pricing structure (based on healthcare SaaS models)
    pricing_model = Column(String)  # "per_visit", "per_provider", "per_location", "subscription", "percentage_collections", "custom"

    # Price details
    base_price = Column(Float, nullable=True)  # Numeric value
    price_currency = Column(String, default="USD")
    price_unit = Column(String, nullable=True)  # "visit", "provider/month", "location/month"
    price_display = Column(String, nullable=True)  # Original display: "$3.00/visit", "Contact Sales"

    # For percentage-based pricing (RCM)
    percentage_rate = Column(Float, nullable=True)  # e.g., 4.5 for 4.5%
    percentage_basis = Column(String, nullable=True)  # "collections", "charges", "net_revenue"

    # Tier limitations
    min_volume = Column(String, nullable=True)  # "100 visits/month"
    max_volume = Column(String, nullable=True)  # "Unlimited"
    included_features = Column(Text, nullable=True)  # JSON array
    excluded_features = Column(Text, nullable=True)  # JSON array

    # Contract terms
    contract_length = Column(String, nullable=True)  # "Monthly", "Annual", "3-year"
    setup_fee = Column(Float, nullable=True)
    implementation_cost = Column(String, nullable=True)  # "Included", "$5,000", "Custom"

    # Data quality
    price_verified = Column(Boolean, default=False)
    price_source = Column(String, nullable=True)  # "website", "sales_quote", "customer_intel"
    confidence_score = Column(Integer, nullable=True)
    last_verified = Column(DateTime, nullable=True)

    # Relationships
    product = relationship("CompetitorProduct", back_populates="pricing_tiers")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProductFeatureMatrix(Base):
    """Feature comparison matrix across products."""
    __tablename__ = "product_feature_matrix"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("competitor_products.id"), index=True)

    feature_category = Column(String)  # "Patient Intake", "Payments", "Integration"
    feature_name = Column(String)  # "Digital Check-In", "Apple Pay Support"
    feature_status = Column(String)  # "included", "add_on", "not_available", "coming_soon"
    feature_tier = Column(String, nullable=True)  # Which tier includes this

    notes = Column(Text, nullable=True)
    source_url = Column(String, nullable=True)
    last_verified = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CustomerCountEstimate(Base):
    """Detailed customer count tracking with verification."""
    __tablename__ = "customer_count_estimates"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), index=True)

    # The estimate
    count_value = Column(Integer, nullable=True)  # Numeric: 3000
    count_display = Column(String, nullable=True)  # Display: "3,000+" or "3,000-5,000"
    count_type = Column(String, nullable=True)  # "exact", "minimum", "range", "estimate"

    # What is being counted (CRITICAL CONTEXT)
    count_unit = Column(String, nullable=True)  # "healthcare_organizations", "providers", "locations", "users", "lives_covered"
    count_definition = Column(Text, nullable=True)  # "Number of distinct hospital/clinic customers"

    # Segment breakdown (if available)
    segment_breakdown = Column(Text, nullable=True)  # JSON: {"hospitals": 500, "ambulatory": 2500}

    # Verification
    is_verified = Column(Boolean, default=False)
    verification_method = Column(String, nullable=True)  # "sec_filing", "triangulation", "sales_intel"
    verification_date = Column(DateTime, nullable=True)

    # Source tracking
    primary_source = Column(String, nullable=True)  # "website", "sec_10k", "press_release"
    primary_source_url = Column(String, nullable=True)
    primary_source_date = Column(DateTime, nullable=True)

    # Multi-source data
    all_sources = Column(Text, nullable=True)  # JSON array of all source claims
    source_agreement_score = Column(Float, nullable=True)  # 0-1, how much sources agree

    # Confidence
    confidence_score = Column(Integer, nullable=True)  # 0-100
    confidence_level = Column(String, nullable=True)  # "high", "moderate", "low"
    confidence_notes = Column(Text, nullable=True)

    # Historical tracking
    as_of_date = Column(DateTime, nullable=True)  # When this count was valid
    previous_count = Column(Integer, nullable=True)
    growth_rate = Column(Float, nullable=True)  # YoY growth %

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
    """Dynamic system prompts for AI generation. user_id=NULL means global prompt."""
    __tablename__ = "system_prompts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # NULL = global prompt
    key = Column(String, index=True)  # e.g., "dashboard_summary", "chat_persona"
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
    """Record of a competitive deal (win or loss). Each user tracks their own deals."""
    __tablename__ = "win_loss_deals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Owner of this deal record
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


class UserSettings(Base):
    """Personal settings for each user (notification preferences, schedules, etc.)."""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    setting_key = Column(String, index=True)  # e.g., "notifications", "schedule", "display_preferences"
    setting_value = Column(Text, nullable=False)  # JSON-encoded value
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityLog(Base):
    """Logs all user activities including data refreshes, logins, etc. Shared across all users."""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user_email = Column(String, index=True)  # Store email for easy display
    action_type = Column(String, index=True)  # "data_refresh", "login", "competitor_update", etc.
    action_details = Column(Text, nullable=True)  # JSON-encoded details
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class UserSavedPrompt(Base):
    """User-specific saved prompts for AI generation. Each user can save multiple named prompts."""
    __tablename__ = "user_saved_prompts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)  # User-friendly name for the prompt
    prompt_type = Column(String, default="executive_summary")  # "executive_summary", "chat_persona", etc.
    content = Column(Text, nullable=False)  # The actual prompt content
    is_default = Column(Boolean, default=False)  # If true, this is the user's default for this type
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RefreshSession(Base):
    """Phase 4: Task 5.0.1-031 - Tracks each data refresh session with results for audit trail."""
    __tablename__ = "refresh_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    competitors_scanned = Column(Integer, default=0)
    changes_detected = Column(Integer, default=0)
    new_values_added = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    ai_summary = Column(Text, nullable=True)  # Store the AI-generated summary
    change_details = Column(Text, nullable=True)  # JSON-encoded change details
    status = Column(String, default="in_progress")  # in_progress, completed, failed


# ===========================================
# SALES & MARKETING MODULE TABLES (v5.0.7)
# ===========================================

class CompetitorDimensionHistory(Base):
    """Track dimension score changes over time for audit trail and trend analysis."""
    __tablename__ = "competitor_dimension_history"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), index=True)
    dimension_id = Column(String, index=True)  # e.g., "product_packaging", "integration_depth"
    old_score = Column(Integer, nullable=True)  # Previous score (null if first entry)
    new_score = Column(Integer)  # New score (1-5)
    evidence = Column(Text, nullable=True)  # Supporting evidence for the score change
    source = Column(String, default="manual")  # "manual", "ai", "news", "review"
    confidence = Column(String, nullable=True)  # "low", "medium", "high"
    changed_by = Column(String)  # User email or "system"
    changed_at = Column(DateTime, default=datetime.utcnow, index=True)


class Battlecard(Base):
    """Generated battlecards for competitors - stored for quick retrieval and versioning."""
    __tablename__ = "battlecards"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), index=True)
    title = Column(String)  # e.g., "Epic Systems Full Battlecard"
    content = Column(Text)  # JSON or Markdown content
    battlecard_type = Column(String)  # "full", "quick", "objection_handler"
    focus_dimensions = Column(String, nullable=True)  # JSON array of dimension IDs
    deal_context = Column(Text, nullable=True)  # Optional deal-specific context
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(String)  # User email or "ai"
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    pdf_path = Column(String, nullable=True)  # Path to exported PDF
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TalkingPoint(Base):
    """Dimension-specific talking points for sales conversations."""
    __tablename__ = "talking_points"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), index=True)
    dimension_id = Column(String, index=True)  # e.g., "product_packaging"
    point_type = Column(String, index=True)  # "strength", "weakness", "objection", "counter"
    content = Column(Text)  # The talking point text
    context = Column(Text, nullable=True)  # When to use this talking point
    effectiveness_score = Column(Integer, nullable=True)  # From win/loss feedback (1-5)
    usage_count = Column(Integer, default=0)  # How many times this point was used
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)  # User email or "ai"
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class DimensionNewsTag(Base):
    """Link news articles to competitive dimensions for dimension-aware news filtering."""
    __tablename__ = "dimension_news_tags"

    id = Column(Integer, primary_key=True, index=True)
    news_url = Column(String, index=True)  # URL of the news article
    news_title = Column(String)  # Title for display
    news_snippet = Column(Text, nullable=True)  # Brief excerpt
    competitor_id = Column(Integer, ForeignKey("competitors.id"), index=True)
    dimension_id = Column(String, index=True)  # e.g., "product_packaging"
    relevance_score = Column(Float)  # 0-1 confidence that article relates to dimension
    sentiment = Column(String, nullable=True)  # "positive", "negative", "neutral"
    tagged_at = Column(DateTime, default=datetime.utcnow, index=True)
    tagged_by = Column(String)  # "ai" or user email
    is_validated = Column(Boolean, default=False)  # User validated the tag


# ===========================================
# TEAM FEATURES (v5.2.0)
# ===========================================

class Team(Base):
    """Team model for grouping users and enabling team collaboration."""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Team settings
    default_dashboard_layout = Column(String, default="standard")  # standard, compact, detailed
    notification_settings = Column(Text, nullable=True)  # JSON-encoded team notification preferences


class TeamMembership(Base):
    """Association table linking users to teams with roles."""
    __tablename__ = "team_memberships"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    role = Column(String, default="member")  # owner, admin, member
    joined_at = Column(DateTime, default=datetime.utcnow)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class CompetitorAnnotation(Base):
    """Shared annotations/notes on competitors visible to team members."""
    __tablename__ = "competitor_annotations"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True, index=True)  # NULL = personal note

    # Annotation content
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    annotation_type = Column(String, default="note")  # note, insight, warning, opportunity, action_item
    priority = Column(String, default="normal")  # low, normal, high, critical

    # Visibility
    is_public = Column(Boolean, default=True)  # Visible to all team members
    is_pinned = Column(Boolean, default=False)  # Pinned to top of annotations

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Context (optional - link to specific field or dimension)
    field_name = Column(String, nullable=True)  # e.g., "pricing", "customer_count"
    dimension_id = Column(String, nullable=True)  # e.g., "product_packaging"


class AnnotationReply(Base):
    """Replies to annotations for threaded discussions."""
    __tablename__ = "annotation_replies"

    id = Column(Integer, primary_key=True, index=True)
    annotation_id = Column(Integer, ForeignKey("competitor_annotations.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DashboardConfiguration(Base):
    """Role-based dashboard configurations and user customizations."""
    __tablename__ = "dashboard_configurations"

    id = Column(Integer, primary_key=True, index=True)
    config_type = Column(String, index=True)  # "role", "user", "team"
    config_key = Column(String, index=True)  # role name, user_id, or team_id

    # Layout settings
    layout = Column(String, default="standard")  # standard, compact, detailed, custom
    widgets = Column(Text, nullable=True)  # JSON: enabled widgets and their positions

    # Display preferences
    default_threat_filter = Column(String, nullable=True)  # "all", "high", "medium", "low"
    default_sort = Column(String, default="threat_level")
    items_per_page = Column(Integer, default=10)

    # Feature visibility (role-based permissions)
    can_view_analytics = Column(Boolean, default=True)
    can_view_financials = Column(Boolean, default=True)
    can_edit_competitors = Column(Boolean, default=False)
    can_manage_users = Column(Boolean, default=False)
    can_export_data = Column(Boolean, default=True)
    can_trigger_refresh = Column(Boolean, default=False)

    # Quick access
    pinned_competitors = Column(Text, nullable=True)  # JSON array of competitor IDs
    favorite_reports = Column(Text, nullable=True)  # JSON array of report configurations

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeamActivity(Base):
    """Track team-level activities for collaboration awareness."""
    __tablename__ = "team_activities"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user_email = Column(String)
    activity_type = Column(String, index=True)  # "annotation", "update", "export", "insight"
    activity_details = Column(Text, nullable=True)  # JSON details
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class NewsArticleCache(Base):
    """
    Cache for fetched news articles (v5.0.8).

    Stores news articles to reduce API calls and improve load times.
    Articles are automatically refreshed by the background scheduler.
    """
    __tablename__ = "news_article_cache"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), index=True)
    competitor_name = Column(String, index=True)

    # Article data
    title = Column(String)
    url = Column(String, index=True)  # Dedupe key
    source = Column(String)  # e.g., "TechCrunch", "Reuters"
    source_type = Column(String)  # google_news, sec_edgar, gnews, mediastack, newsdata
    published_at = Column(DateTime, index=True)
    snippet = Column(Text, nullable=True)

    # Analysis
    sentiment = Column(String)  # positive, neutral, negative
    event_type = Column(String, nullable=True)  # funding, acquisition, product_launch, partnership, leadership
    is_major_event = Column(Boolean, default=False)

    # Dimension tags (v5.0.8)
    dimension_tags = Column(Text, nullable=True)  # JSON: [{"dimension": "pricing_flexibility", "confidence": 0.8}]

    # Metadata
    fetched_at = Column(DateTime, default=datetime.utcnow)
    cache_expires_at = Column(DateTime, index=True)  # Auto-refresh after this time

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

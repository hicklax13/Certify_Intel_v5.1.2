# Data Quality & Intelligence Enhancement Plan
## Solving Customer Count, Pricing, and Source Attribution Gaps

**Created**: January 25, 2026, 11:30 PM EST
**Author**: Claude Opus 4.5
**Status**: AWAITING APPROVAL
**Priority**: HIGH - Foundational Data Integrity

---

## Executive Summary

This plan addresses critical gaps identified in Certify Intel's competitive data collection system:

| Gap | Current State | Target State |
|-----|---------------|--------------|
| **Customer Counts** | Unverified marketing claims ("3000+") | Multi-source triangulated estimates with confidence scores |
| **Pricing Data** | Single price point, unclear product | Product-specific pricing matrix with tier breakdowns |
| **Source Attribution** | No tracking of where data originated | Full provenance chain with timestamps and reliability ratings |
| **Data Verification** | GPT extraction from websites only | Multi-source triangulation with automated cross-validation |
| **Product Specificity** | Company-level metrics | Product-line level competitive analysis |

**Research Foundation**: This plan is based on industry best practices from [Contify](https://www.contify.com/resources/blog/best-competitive-intelligence-tools/), [KLAS Research](https://klasresearch.com/klas-model), [Gartner](https://www.gartner.com/reviews/market/competitive-and-market-intelligence-tools), [Definitive Healthcare](https://www.definitivehc.com/), and academic frameworks for [data triangulation](https://www.evalacademy.com/articles/part-1-what-is-data-triangulation-in-evaluation) and [intelligence confidence scoring](https://en.wikipedia.org/wiki/Analytic_confidence).

---

## Phase 1: Source Attribution & Confidence Scoring
### Priority: CRITICAL | Effort: 2-3 days

**Objective**: Track where every data point comes from and how reliable it is.

### 1.1 Database Schema Changes

**New Table: `DataSource`** (enhance existing)

```python
class DataSource(Base):
    """Enhanced source tracking for every data point."""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"))
    field_name = Column(String, index=True)  # e.g., "customer_count", "base_price"

    # Value tracking
    current_value = Column(String)
    previous_value = Column(String, nullable=True)

    # Source attribution (NEW)
    source_type = Column(String)  # "website_scrape", "sec_filing", "manual", "api", "news"
    source_url = Column(String, nullable=True)
    source_name = Column(String, nullable=True)  # "Company Website", "SEC 10-K 2025", "KLAS Report"
    extraction_method = Column(String)  # "gpt_extraction", "structured_api", "manual_entry"
    extracted_at = Column(DateTime, default=datetime.utcnow)

    # Confidence scoring (NEW) - Based on Admiralty Code
    source_reliability = Column(String)  # A-F scale (A=completely reliable, F=unknown)
    information_credibility = Column(Integer)  # 1-6 scale (1=confirmed, 6=cannot be judged)
    confidence_score = Column(Integer)  # 0-100 composite score
    confidence_level = Column(String)  # "high", "moderate", "low" (National Intelligence Council standard)

    # Verification tracking (NEW)
    is_verified = Column(Boolean, default=False)
    verified_by = Column(String, nullable=True)  # "triangulation", "manual", "sec_filing"
    verification_date = Column(DateTime, nullable=True)
    corroborating_sources = Column(Integer, default=0)  # Number of sources that agree

    # Temporal relevance
    data_as_of_date = Column(DateTime, nullable=True)  # When the data was true (not when extracted)
    staleness_days = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 1.2 Confidence Scoring Algorithm

Based on [intelligence community standards](https://www.cisecurity.org/ms-isac/services/words-of-estimative-probability-analytic-confidences-and-structured-analytic-techniques):

```python
def calculate_confidence_score(
    source_type: str,
    source_reliability: str,  # A-F
    information_credibility: int,  # 1-6
    corroborating_sources: int,
    data_age_days: int
) -> dict:
    """
    Calculate composite confidence score using Admiralty Code framework.

    Returns:
        {
            "score": 0-100,
            "level": "high" | "moderate" | "low",
            "explanation": "Based on..."
        }
    """

    # Source reliability weights (A=50, B=40, C=30, D=20, E=10, F=5)
    reliability_scores = {"A": 50, "B": 40, "C": 30, "D": 20, "E": 10, "F": 5}
    reliability_score = reliability_scores.get(source_reliability, 5)

    # Information credibility weights (1=30, 2=25, 3=20, 4=15, 5=10, 6=5)
    credibility_scores = {1: 30, 2: 25, 3: 20, 4: 15, 5: 10, 6: 5}
    credibility_score = credibility_scores.get(information_credibility, 5)

    # Corroboration bonus (max 15 points)
    corroboration_bonus = min(corroborating_sources * 5, 15)

    # Freshness penalty (lose 1 point per 30 days, max -15)
    freshness_penalty = min(data_age_days // 30, 15)

    # Source type bonus
    source_bonuses = {
        "sec_filing": 10,      # Legally required disclosures
        "api_verified": 8,     # Structured data from official APIs
        "klas_report": 8,      # Industry analyst reports
        "manual_verified": 5,  # Human-verified
        "website_scrape": 0,   # Marketing content
        "news_article": -2,    # May be outdated/inaccurate
    }
    source_bonus = source_bonuses.get(source_type, 0)

    # Calculate composite score
    raw_score = reliability_score + credibility_score + corroboration_bonus + source_bonus - freshness_penalty
    final_score = max(0, min(100, raw_score))

    # Determine confidence level
    if final_score >= 70:
        level = "high"
        explanation = "Based on high-quality, corroborated information from reliable sources"
    elif final_score >= 40:
        level = "moderate"
        explanation = "Based on credible information, but limited corroboration or source reliability"
    else:
        level = "low"
        explanation = "Based on unverified claims or sources with limited reliability history"

    return {
        "score": final_score,
        "level": level,
        "explanation": explanation
    }
```

### 1.3 Source Type Definitions

| Source Type | Reliability | Description | Example |
|-------------|-------------|-------------|---------|
| `sec_filing` | A (Completely Reliable) | Legally mandated disclosures | 10-K employee count |
| `api_verified` | A-B | Official API data | G2 API, LinkedIn API |
| `klas_report` | B (Usually Reliable) | Industry analyst research | KLAS vendor ratings |
| `definitive_hc` | B | Healthcare market data | Hospital customer lists |
| `manual_verified` | B-C | Human-verified entry | Sales team confirmation |
| `website_scrape` | C-D (Fairly/Unreliable) | Marketing website content | Pricing page |
| `news_article` | C-D | Press releases, news | Funding announcements |
| `linkedin_estimate` | D | Employee count estimate | LinkedIn profile count |
| `crunchbase` | D | Startup database | Funding, employee range |
| `unknown` | F | Source not documented | Legacy data |

### 1.4 API Endpoints

```python
# New endpoints for source attribution

@app.get("/api/competitors/{competitor_id}/data-sources")
async def get_competitor_data_sources(competitor_id: int, db: Session = Depends(get_db)):
    """Get all data sources and confidence scores for a competitor."""
    sources = db.query(DataSource).filter(
        DataSource.competitor_id == competitor_id
    ).order_by(DataSource.field_name).all()

    return [{
        "field": s.field_name,
        "value": s.current_value,
        "source_type": s.source_type,
        "source_name": s.source_name,
        "source_url": s.source_url,
        "confidence": {
            "score": s.confidence_score,
            "level": s.confidence_level,
            "corroborating_sources": s.corroborating_sources
        },
        "extracted_at": s.extracted_at.isoformat() if s.extracted_at else None,
        "is_verified": s.is_verified
    } for s in sources]

@app.get("/api/data-quality/low-confidence")
async def get_low_confidence_data(threshold: int = 40, db: Session = Depends(get_db)):
    """Get all data points below confidence threshold for review."""
    sources = db.query(DataSource).filter(
        DataSource.confidence_score < threshold
    ).order_by(DataSource.confidence_score).all()

    return sources
```

---

## Phase 2: Multi-Source Data Triangulation
### Priority: HIGH | Effort: 3-4 days

**Objective**: Verify data by cross-referencing multiple independent sources.

Based on [data triangulation best practices](https://www.kingsresearch.com/blog/data-triangulation-in-market-research/), we implement automated cross-validation.

### 2.1 Triangulation Engine

```python
class DataTriangulator:
    """
    Cross-reference data from multiple sources to verify accuracy.

    Methodology:
    1. Collect same data point from multiple sources
    2. Compare values for consistency
    3. Flag discrepancies for human review
    4. Calculate confidence based on agreement
    """

    async def triangulate_customer_count(
        self,
        competitor_id: int,
        competitor_name: str,
        website: str
    ) -> dict:
        """
        Verify customer count using multiple sources.

        Sources used:
        1. Company website (marketing claims)
        2. SEC filings (if public)
        3. LinkedIn employee count (proxy metric)
        4. News/press releases
        5. G2 Crowd reviews count
        6. Case studies/customer logos
        """

        results = {}

        # Source 1: Website scrape (existing)
        website_count = await self.scrape_website_customer_count(website)
        results["website_claim"] = {
            "value": website_count,
            "source_type": "website_scrape",
            "reliability": "D",  # Marketing claims
            "credibility": 4     # Plausible but unverified
        }

        # Source 2: SEC filings (for public companies)
        sec_count = await self.fetch_sec_customer_count(competitor_name)
        if sec_count:
            results["sec_filing"] = {
                "value": sec_count,
                "source_type": "sec_filing",
                "reliability": "A",  # Legally required
                "credibility": 1     # Confirmed
            }

        # Source 3: LinkedIn employee count (proxy)
        linkedin_count = await self.fetch_linkedin_employee_count(competitor_name)
        if linkedin_count:
            # Estimate customer count from employee count using industry ratios
            estimated_customers = self.estimate_customers_from_employees(
                linkedin_count,
                industry="healthcare_saas"
            )
            results["linkedin_proxy"] = {
                "value": f"{estimated_customers} (estimated from {linkedin_count} employees)",
                "source_type": "linkedin_estimate",
                "reliability": "C",
                "credibility": 3
            }

        # Source 4: G2 Crowd review count
        g2_data = await self.fetch_g2_data(competitor_name)
        if g2_data:
            results["g2_reviews"] = {
                "value": f"{g2_data['review_count']} reviews",
                "source_type": "api_verified",
                "reliability": "B",
                "credibility": 2
            }

        # Source 5: News mentions
        news_mentions = await self.search_customer_mentions_news(competitor_name)
        if news_mentions:
            results["news_mentions"] = {
                "value": news_mentions,
                "source_type": "news_article",
                "reliability": "C",
                "credibility": 3
            }

        # Calculate triangulated result
        return self.calculate_triangulated_value(results, "customer_count")

    def calculate_triangulated_value(self, sources: dict, field_name: str) -> dict:
        """
        Determine most reliable value and overall confidence.

        Rules:
        1. If SEC filing exists, use that (highest authority)
        2. If 3+ sources agree within 20%, high confidence
        3. If sources disagree significantly, flag for review
        """

        # Priority order for authoritative sources
        authority_order = ["sec_filing", "api_verified", "klas_report", "manual_verified"]

        # Check for authoritative source
        for auth_source in authority_order:
            if auth_source in sources:
                return {
                    "best_value": sources[auth_source]["value"],
                    "confidence_level": "high",
                    "source_used": auth_source,
                    "all_sources": sources,
                    "discrepancy_flag": False
                }

        # Otherwise, look for consensus
        values = [s["value"] for s in sources.values() if s["value"]]

        if len(values) >= 3:
            # Check for consensus (values within 20% of median)
            # ... consensus logic
            pass

        # If no consensus, return most reliable with flag
        return {
            "best_value": sources.get("website_claim", {}).get("value"),
            "confidence_level": "low",
            "source_used": "website_scrape",
            "all_sources": sources,
            "discrepancy_flag": True,
            "review_reason": "No authoritative source; values not corroborated"
        }
```

### 2.2 Data Source Integrations

| Source | API/Method | Data Points | Cost | Reliability |
|--------|-----------|-------------|------|-------------|
| **SEC EDGAR** | Free API | Employee count, revenue, customer mentions in filings | Free | A |
| **LinkedIn** | LinkedIn API / Scraping | Employee count, growth rate, job postings | Paid/$99+/mo | C |
| **G2 Crowd** | [G2 API](https://data.g2.com/api/docs) | Ratings, review counts, feature scores | Paid | B |
| **Crunchbase** | Crunchbase API | Funding, employee range, acquisitions | $99+/mo | C |
| **Definitive Healthcare** | [DH API](https://www.definitivehc.com/data-products) | Hospital customers, physician data | Enterprise | A |
| **KLAS Research** | Manual / Reports | Healthcare IT ratings, customer satisfaction | $5K+/year | A |
| **Google News** | Custom Search API | Press releases, funding announcements | Existing | C |
| **Glassdoor** | Scraping | Employee count, reviews | Existing | C |

### 2.3 Verification Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA VERIFICATION FLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. INITIAL SCRAPE                                              │
│     └── Website content → GPT extraction → Raw value            │
│                                                                  │
│  2. MULTI-SOURCE COLLECTION                                     │
│     ├── SEC EDGAR check (if public)                             │
│     ├── LinkedIn employee lookup                                │
│     ├── G2/Capterra reviews                                     │
│     ├── News/press search                                       │
│     └── Crunchbase data                                         │
│                                                                  │
│  3. TRIANGULATION                                               │
│     └── Compare all sources → Calculate consensus               │
│                                                                  │
│  4. CONFIDENCE SCORING                                          │
│     └── Apply Admiralty Code → Generate score (0-100)           │
│                                                                  │
│  5. HUMAN REVIEW (if needed)                                    │
│     └── Flag discrepancies → Queue for analyst review           │
│                                                                  │
│  6. PERSIST WITH PROVENANCE                                     │
│     └── Store value + all sources + confidence + timestamp      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 3: Product-Specific Pricing Structure
### Priority: HIGH | Effort: 2-3 days

**Objective**: Track pricing at the product/tier level, not just company level.

Based on [healthcare SaaS pricing research](https://www.getmonetizely.com/articles/testing-healthcare-saas-pricing-strategies-maximizing-value-while-meeting-industry-needs):

### 3.1 Database Schema - Product & Pricing Models

```python
class CompetitorProduct(Base):
    """Individual product/solution offered by a competitor."""
    __tablename__ = "competitor_products"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"))

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


class ProductPricingTier(Base):
    """Pricing tier for a specific product."""
    __tablename__ = "product_pricing_tiers"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("competitor_products.id"))

    # Tier identification
    tier_name = Column(String)  # e.g., "Basic", "Professional", "Enterprise"
    tier_position = Column(Integer)  # 1, 2, 3... for ordering

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


class ProductFeatureMatrix(Base):
    """Feature comparison matrix across products."""
    __tablename__ = "product_feature_matrix"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("competitor_products.id"))

    feature_category = Column(String)  # "Patient Intake", "Payments", "Integration"
    feature_name = Column(String)  # "Digital Check-In", "Apple Pay Support"
    feature_status = Column(String)  # "included", "add_on", "not_available", "coming_soon"
    feature_tier = Column(String, nullable=True)  # Which tier includes this

    notes = Column(Text, nullable=True)
    source_url = Column(String, nullable=True)
    last_verified = Column(DateTime, nullable=True)
```

### 3.2 Healthcare-Specific Pricing Model Types

Based on [industry research](https://www.optimantra.com/blog/emr-pricing-models-explained-flat-fee-per-provider-per-encounter-and-more/):

| Pricing Model | Description | Common In | Example |
|---------------|-------------|-----------|---------|
| `per_visit` | Charge per patient encounter | Patient Intake, Payments | $3.00/visit |
| `per_provider` | Monthly fee per provider | PM, EHR | $400/provider/month |
| `per_location` | Fee per practice location | Multi-site solutions | $1,500/location/month |
| `subscription_flat` | Fixed monthly fee | SMB tools | $299/month |
| `subscription_tiered` | Tiered by features/volume | All | $99-$499/month |
| `percentage_collections` | % of collected revenue | RCM, Billing | 4-8% of collections |
| `percentage_charges` | % of billed charges | RCM | 2-4% of charges |
| `per_bed` | Hospital capacity pricing | Enterprise EHR | $15,000/bed |
| `per_member` | Per covered life | Payer solutions | $0.50 PMPM |
| `custom_enterprise` | Negotiated pricing | Enterprise | Contact Sales |

### 3.3 Product-Level API Endpoints

```python
@app.get("/api/competitors/{competitor_id}/products")
async def get_competitor_products(competitor_id: int, db: Session = Depends(get_db)):
    """Get all products and pricing for a competitor."""
    products = db.query(CompetitorProduct).filter(
        CompetitorProduct.competitor_id == competitor_id
    ).all()

    return [{
        "id": p.id,
        "name": p.product_name,
        "category": p.product_category,
        "is_primary": p.is_primary_product,
        "pricing_tiers": [{
            "tier_name": t.tier_name,
            "pricing_model": t.pricing_model,
            "price_display": t.price_display,
            "price_unit": t.price_unit,
            "confidence_score": t.confidence_score
        } for t in p.pricing_tiers]
    } for p in products]

@app.get("/api/pricing/compare")
async def compare_pricing(
    category: str,  # e.g., "Patient Intake"
    pricing_model: str = None,  # e.g., "per_visit"
    db: Session = Depends(get_db)
):
    """Compare pricing across competitors for a product category."""
    query = db.query(ProductPricingTier).join(CompetitorProduct).filter(
        CompetitorProduct.product_category == category
    )

    if pricing_model:
        query = query.filter(ProductPricingTier.pricing_model == pricing_model)

    tiers = query.all()

    return [{
        "competitor": t.product.competitor.name,
        "product": t.product.product_name,
        "tier": t.tier_name,
        "price": t.price_display,
        "model": t.pricing_model,
        "confidence": t.confidence_score
    } for t in tiers]
```

---

## Phase 4: Customer Count Verification System
### Priority: HIGH | Effort: 2-3 days

**Objective**: Replace vague "3000+" claims with verified, contextualized counts.

### 4.1 Customer Count Data Model

```python
class CustomerCountEstimate(Base):
    """Detailed customer count tracking with verification."""
    __tablename__ = "customer_count_estimates"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"))

    # The estimate
    count_value = Column(Integer, nullable=True)  # Numeric: 3000
    count_display = Column(String)  # Display: "3,000+" or "3,000-5,000"
    count_type = Column(String)  # "exact", "minimum", "range", "estimate"

    # What is being counted (CRITICAL CONTEXT)
    count_unit = Column(String)  # "healthcare_organizations", "providers", "locations", "users", "lives_covered"
    count_definition = Column(Text, nullable=True)  # "Number of distinct hospital/clinic customers"

    # Segment breakdown (if available)
    segment_breakdown = Column(Text, nullable=True)  # JSON: {"hospitals": 500, "ambulatory": 2500}

    # Verification
    is_verified = Column(Boolean, default=False)
    verification_method = Column(String, nullable=True)  # "sec_filing", "triangulation", "sales_intel"
    verification_date = Column(DateTime, nullable=True)

    # Source tracking
    primary_source = Column(String)  # "website", "sec_10k", "press_release"
    primary_source_url = Column(String, nullable=True)
    primary_source_date = Column(DateTime, nullable=True)

    # Multi-source data
    all_sources = Column(Text, nullable=True)  # JSON array of all source claims
    source_agreement_score = Column(Float, nullable=True)  # 0-1, how much sources agree

    # Confidence
    confidence_score = Column(Integer)  # 0-100
    confidence_level = Column(String)  # "high", "moderate", "low"
    confidence_notes = Column(Text, nullable=True)

    # Historical tracking
    as_of_date = Column(DateTime)  # When this count was valid
    previous_count = Column(Integer, nullable=True)
    growth_rate = Column(Float, nullable=True)  # YoY growth %

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
```

### 4.2 Customer Count Verification Methods

| Method | Data Source | Reliability | What It Provides |
|--------|------------|-------------|------------------|
| **SEC 10-K Analysis** | SEC EDGAR | A (Confirmed) | Employee count, revenue per customer proxy |
| **Logo Counting** | Website case studies | C (Some verification) | Minimum customer count from visible logos |
| **LinkedIn Analysis** | LinkedIn | C (Proxy) | Employee count → estimated customers |
| **G2/Capterra Reviews** | Review platforms | B (Verified users) | Review count as customer proxy |
| **Press Release Mining** | News | C (Claims) | Announced customer milestones |
| **Job Posting Analysis** | Indeed/LinkedIn | C (Proxy) | Growth indicators |
| **Definitive Healthcare** | DH API | A (Verified) | Actual hospital/practice customers |

### 4.3 Customer Count Contextualization

**Problem**: "3000+ customers" is meaningless without context.

**Solution**: Always capture and display:

```
┌────────────────────────────────────────────────────────────────┐
│  PHREESIA CUSTOMER COUNT                                       │
├────────────────────────────────────────────────────────────────┤
│  Count: 3,500+ healthcare organizations                        │
│  Unit: Distinct healthcare provider organizations              │
│  As of: January 2026 (SEC 10-K filing)                         │
│                                                                │
│  Breakdown:                                                    │
│  ├── Health Systems: ~200                                      │
│  ├── Physician Practices: ~3,000                               │
│  └── Other (Labs, Imaging): ~300                               │
│                                                                │
│  Confidence: HIGH (92/100)                                     │
│  ├── SEC filing confirms "over 3,000 provider organizations"   │
│  ├── Website claims "3,500+ healthcare organizations"          │
│  └── G2 shows 1,200+ reviews (supports large customer base)    │
│                                                                │
│  Trend: +15% YoY growth                                        │
└────────────────────────────────────────────────────────────────┘
```

---

## Phase 5: Enhanced Scraper with Source Tracking
### Priority: MEDIUM | Effort: 2 days

**Objective**: Update existing scrapers to capture and store source metadata.

### 5.1 Extractor Updates

```python
@dataclass
class ExtractedDataWithSource:
    """Enhanced extraction result with full provenance."""

    # Existing fields
    pricing_model: str = None
    base_price: str = None
    customer_count: str = None
    # ... other fields ...

    # NEW: Source metadata for each field
    field_sources: dict = field(default_factory=dict)
    # Structure: {
    #     "customer_count": {
    #         "value": "3000+",
    #         "source_url": "https://phreesia.com/about",
    #         "source_page": "about",
    #         "extraction_context": "Found in text: 'Trusted by 3,000+ healthcare organizations'",
    #         "confidence": 65
    #     }
    # }

    # NEW: Extraction metadata
    extraction_timestamp: datetime = None
    extraction_model: str = None  # "gpt-4o-mini"
    total_pages_scraped: int = 0
    extraction_warnings: list = field(default_factory=list)


class EnhancedGPTExtractor:
    """GPT extractor with source tracking."""

    def extract_with_sources(
        self,
        competitor_name: str,
        page_contents: dict  # {"homepage": content, "pricing": content, ...}
    ) -> ExtractedDataWithSource:
        """
        Extract data and track which page each data point came from.
        """

        result = ExtractedDataWithSource()
        result.extraction_timestamp = datetime.utcnow()
        result.extraction_model = "gpt-4o-mini"
        result.total_pages_scraped = len(page_contents)

        for page_type, content in page_contents.items():
            # Extract with page-specific prompt
            extracted = self._extract_page(competitor_name, page_type, content)

            # Merge results, tracking source for each field
            for field_name, value in extracted.items():
                if value and not getattr(result, field_name, None):
                    setattr(result, field_name, value)
                    result.field_sources[field_name] = {
                        "value": value,
                        "source_page": page_type,
                        "source_url": f"{competitor_website}/{page_type}",
                        "extraction_context": self._get_context_snippet(content, value),
                        "confidence": self._estimate_confidence(page_type, field_name)
                    }

        return result

    def _estimate_confidence(self, page_type: str, field_name: str) -> int:
        """Estimate extraction confidence based on page type and field."""

        # Pricing from pricing page = higher confidence
        if field_name in ["base_price", "pricing_model"] and page_type == "pricing":
            return 75

        # Customer count from about page = moderate
        if field_name == "customer_count" and page_type in ["about", "customers"]:
            return 60

        # Generic extraction = lower confidence
        return 40
```

### 5.2 Scrape Job Updates

```python
async def run_enhanced_scrape_job(
    competitor_id: int,
    competitor_name: str,
    website: str,
    db: Session
):
    """
    Enhanced scrape with full source tracking.
    """

    # 1. Scrape all relevant pages
    pages_to_scrape = ["homepage", "pricing", "about", "customers", "features"]
    page_contents = {}

    for page in pages_to_scrape:
        try:
            content = await scraper.scrape_page(website, page)
            if content:
                page_contents[page] = content
        except Exception as e:
            log_scrape_error(competitor_id, page, str(e))

    # 2. Extract with source tracking
    extractor = EnhancedGPTExtractor()
    extracted = extractor.extract_with_sources(competitor_name, page_contents)

    # 3. Store each field with its source
    for field_name, source_info in extracted.field_sources.items():
        # Create/update DataSource record
        data_source = DataSource(
            competitor_id=competitor_id,
            field_name=field_name,
            current_value=source_info["value"],
            source_type="website_scrape",
            source_url=source_info["source_url"],
            source_name=f"{competitor_name} Website - {source_info['source_page']}",
            extraction_method="gpt_extraction",
            extracted_at=extracted.extraction_timestamp,
            source_reliability="D",  # Website = fairly unreliable
            information_credibility=4,  # Plausible
            confidence_score=source_info["confidence"],
            confidence_level="low" if source_info["confidence"] < 50 else "moderate"
        )
        db.add(data_source)

    # 4. Trigger triangulation for key fields
    triangulator = DataTriangulator()
    for key_field in ["customer_count", "base_price", "employee_count"]:
        if key_field in extracted.field_sources:
            await triangulator.verify_field(
                competitor_id,
                key_field,
                extracted.field_sources[key_field]["value"]
            )

    db.commit()
```

---

## Phase 6: UI Enhancements
### Priority: MEDIUM | Effort: 2 days

**Objective**: Display confidence scores and source attribution in the UI.

### 6.1 Competitor Table Enhancements

```html
<!-- Enhanced competitor row with confidence indicators -->
<tr class="competitor-row">
    <td class="competitor-name">
        <img src="${comp.logo_url}" class="competitor-logo">
        <div>
            <strong>${comp.name}</strong>
            <span class="website-link">${comp.website}</span>
        </div>
    </td>

    <td class="threat-level">
        <span class="badge badge-${comp.threat_level}">${comp.threat_level}</span>
    </td>

    <!-- ENHANCED: Customer count with confidence -->
    <td class="customer-count">
        <div class="data-with-confidence">
            <span class="value">${comp.customer_count || 'Unknown'}</span>
            <span class="confidence-indicator confidence-${comp.customer_count_confidence}"
                  title="Confidence: ${comp.customer_count_confidence_score}/100 - ${comp.customer_count_source}">
                ${getConfidenceIcon(comp.customer_count_confidence)}
            </span>
        </div>
        <span class="data-context">${comp.customer_count_unit || ''}</span>
    </td>

    <!-- ENHANCED: Pricing with confidence -->
    <td class="pricing">
        <div class="data-with-confidence">
            <span class="value">${comp.base_price || 'Custom'}</span>
            <span class="confidence-indicator confidence-${comp.pricing_confidence}"
                  title="Confidence: ${comp.pricing_confidence_score}/100 - ${comp.pricing_source}">
                ${getConfidenceIcon(comp.pricing_confidence)}
            </span>
        </div>
        <span class="data-context">${comp.pricing_model || ''}</span>
    </td>

    <td class="last-updated">${formatDate(comp.updated_at)}</td>

    <td class="actions">
        <button onclick="viewCompetitor(${comp.id})">View</button>
        <button onclick="viewDataSources(${comp.id})" class="btn-secondary">
            📋 Sources
        </button>
    </td>
</tr>
```

### 6.2 Confidence Indicator Styles

```css
/* Confidence indicators */
.confidence-indicator {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    font-size: 12px;
    cursor: help;
    margin-left: 6px;
}

.confidence-high {
    background: #10b981;
    color: white;
}

.confidence-moderate {
    background: #f59e0b;
    color: white;
}

.confidence-low {
    background: #ef4444;
    color: white;
}

.data-context {
    display: block;
    font-size: 11px;
    color: #64748b;
    margin-top: 2px;
}

/* Data source popup */
.data-source-popup {
    position: absolute;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    max-width: 300px;
    z-index: 100;
}

.source-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    border-bottom: 1px solid #f1f5f9;
}

.source-item:last-child {
    border-bottom: none;
}

.source-type-badge {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 4px;
    background: #f1f5f9;
}
```

### 6.3 Data Sources Modal

```javascript
async function viewDataSources(competitorId) {
    const sources = await fetchAPI(`/api/competitors/${competitorId}/data-sources`);

    const modal = document.getElementById('dataSourcesModal');
    const content = document.getElementById('dataSourcesContent');

    content.innerHTML = `
        <div class="sources-header">
            <h3>Data Source Attribution</h3>
            <p class="sources-description">
                Every data point is tracked with its source and confidence level.
            </p>
        </div>

        <div class="sources-table">
            <table>
                <thead>
                    <tr>
                        <th>Field</th>
                        <th>Value</th>
                        <th>Source</th>
                        <th>Confidence</th>
                        <th>Last Updated</th>
                    </tr>
                </thead>
                <tbody>
                    ${sources.map(s => `
                        <tr class="source-row">
                            <td class="field-name">${formatFieldName(s.field)}</td>
                            <td class="field-value">${s.value || '-'}</td>
                            <td class="source-info">
                                <span class="source-type-badge">${s.source_type}</span>
                                ${s.source_url ? `<a href="${s.source_url}" target="_blank">🔗</a>` : ''}
                            </td>
                            <td class="confidence">
                                <div class="confidence-bar">
                                    <div class="confidence-fill confidence-${s.confidence.level}"
                                         style="width: ${s.confidence.score}%"></div>
                                </div>
                                <span class="confidence-score">${s.confidence.score}/100</span>
                            </td>
                            <td class="updated-at">${formatDate(s.extracted_at)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>

        <div class="sources-legend">
            <h4>Confidence Levels</h4>
            <div class="legend-items">
                <span class="legend-item">
                    <span class="dot confidence-high"></span>
                    High (70-100): Verified from authoritative sources
                </span>
                <span class="legend-item">
                    <span class="dot confidence-moderate"></span>
                    Moderate (40-69): Credible but not fully verified
                </span>
                <span class="legend-item">
                    <span class="dot confidence-low"></span>
                    Low (0-39): Unverified marketing claims
                </span>
            </div>
        </div>
    `;

    modal.style.display = 'flex';
}
```

---

## Phase 7: Data Quality Dashboard
### Priority: LOW | Effort: 1-2 days

**Objective**: Provide visibility into overall data quality and gaps.

### 7.1 Quality Metrics API

```python
@app.get("/api/data-quality/overview")
async def get_data_quality_overview(db: Session = Depends(get_db)):
    """Get overall data quality metrics."""

    total_competitors = db.query(Competitor).filter(Competitor.is_active == True).count()

    # Confidence distribution
    sources = db.query(DataSource).all()
    high_confidence = len([s for s in sources if s.confidence_score >= 70])
    moderate_confidence = len([s for s in sources if 40 <= s.confidence_score < 70])
    low_confidence = len([s for s in sources if s.confidence_score < 40])

    # Verification stats
    verified_count = len([s for s in sources if s.is_verified])

    # Staleness
    stale_threshold = datetime.utcnow() - timedelta(days=90)
    stale_count = len([s for s in sources if s.extracted_at < stale_threshold])

    # Field coverage
    key_fields = ["customer_count", "base_price", "pricing_model", "employee_count"]
    field_coverage = {}
    for field in key_fields:
        populated = db.query(DataSource).filter(
            DataSource.field_name == field,
            DataSource.current_value.isnot(None)
        ).count()
        field_coverage[field] = {
            "populated": populated,
            "total": total_competitors,
            "percentage": round((populated / total_competitors) * 100, 1) if total_competitors > 0 else 0
        }

    return {
        "total_competitors": total_competitors,
        "total_data_points": len(sources),
        "confidence_distribution": {
            "high": high_confidence,
            "moderate": moderate_confidence,
            "low": low_confidence
        },
        "verification_rate": round((verified_count / len(sources)) * 100, 1) if sources else 0,
        "staleness_rate": round((stale_count / len(sources)) * 100, 1) if sources else 0,
        "field_coverage": field_coverage,
        "needs_attention": {
            "low_confidence_count": low_confidence,
            "stale_count": stale_count,
            "unverified_count": len(sources) - verified_count
        }
    }
```

---

## Implementation Timeline

| Phase | Description | Effort | Dependencies |
|-------|-------------|--------|--------------|
| **Phase 1** | Source Attribution & Confidence Scoring | 2-3 days | None |
| **Phase 2** | Multi-Source Data Triangulation | 3-4 days | Phase 1 |
| **Phase 3** | Product-Specific Pricing Structure | 2-3 days | Phase 1 |
| **Phase 4** | Customer Count Verification System | 2-3 days | Phase 1, 2 |
| **Phase 5** | Enhanced Scraper with Source Tracking | 2 days | Phase 1 |
| **Phase 6** | UI Enhancements | 2 days | Phase 1-5 |
| **Phase 7** | Data Quality Dashboard | 1-2 days | Phase 1-6 |

**Total Estimated Effort**: 14-19 days

---

## External API Costs (Optional Integrations)

| Service | Purpose | Estimated Cost | Priority |
|---------|---------|----------------|----------|
| G2 API | Review data, ratings | $500-2000/mo | Medium |
| LinkedIn API | Employee counts | $99-500/mo | Medium |
| Crunchbase API | Funding, employee ranges | $99-500/mo | Low |
| Definitive Healthcare | Hospital customer data | $5,000+/year | High (if budget allows) |
| KLAS Research | Healthcare IT ratings | $5,000+/year | High (if budget allows) |

**Note**: Phase 1-6 can be implemented without additional API costs using existing free sources (SEC EDGAR, website scraping, news search).

---

## Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| Data points with source attribution | 0% | 100% |
| Data points with confidence scores | 0% | 100% |
| High-confidence data points | Unknown | >40% |
| Customer counts with context (unit defined) | 0% | 100% |
| Pricing with product/tier specification | 0% | >80% |
| Data verified by multiple sources | 0% | >30% |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| External APIs become unavailable | All external sources are optional; core system works with website scraping |
| GPT extraction accuracy decreases | Confidence scoring will flag low-quality extractions for review |
| Triangulation finds conflicting data | Human review queue for discrepancies |
| Performance impact from additional data | Indexed database fields; lazy loading in UI |

---

## Research Sources

This plan is based on research from:

- [Contify - Best Competitive Intelligence Tools](https://www.contify.com/resources/blog/best-competitive-intelligence-tools/)
- [Ibbaka - B2B SaaS Pricing Predictions 2026](https://www.ibbaka.com/ibbaka-market-blog/b2b-saas-and-agentic-ai-pricing-predictions-for-2026)
- [Monetizely - Competitive Pricing Intelligence](https://www.getmonetizely.com/articles/competitive-pricing-intelligence-staying-ahead-of-market-changes)
- [Eval Academy - Data Triangulation](https://www.evalacademy.com/articles/part-1-what-is-data-triangulation-in-evaluation)
- [Kings Research - Data Triangulation in Market Research](https://www.kingsresearch.com/blog/data-triangulation-in-market-research)
- [Wikipedia - Intelligence Source Reliability (Admiralty Code)](https://en.wikipedia.org/wiki/Intelligence_source_and_information_reliability)
- [Wikipedia - Analytic Confidence](https://en.wikipedia.org/wiki/Analytic_confidence)
- [KLAS Research - Healthcare IT Data Model](https://klasresearch.com/klas-model)
- [Definitive Healthcare - Market Intelligence](https://www.definitivehc.com/use-case/market-intelligence)
- [G2 API Documentation](https://data.g2.com/api/docs)
- [Coresignal - Finding Employee Counts](https://coresignal.com/blog/how-to-find-number-of-employees-in-a-company/)
- [Monetizely - Healthcare SaaS Pricing](https://www.getmonetizely.com/articles/testing-healthcare-saas-pricing-strategies-maximizing-value-while-meeting-industry-needs)
- [OptiMantra - EMR Pricing Models](https://www.optimantra.com/blog/emr-pricing-models-explained-flat-fee-per-provider-per-encounter-and-more)
- [Product School - Competitor Analysis](https://productschool.com/blog/skills/product-manager-competitive-analysis)
- [Thrv - Competitive Analysis Matrix](https://www.thrv.com/glossary/competitive-analysis-matrix)

---

**Document Version**: 1.5
**Status**: PHASE 5 COMPLETE
**Next Step**: Begin Phase 6 (UI Enhancements)

---

## Implementation Progress

| Phase | Status | Completed |
|-------|--------|-----------|
| Phase 1: Source Attribution & Confidence Scoring | ✅ COMPLETE | Jan 26, 2026 |
| Phase 2: Multi-Source Data Triangulation | ✅ COMPLETE | Jan 26, 2026 |
| Phase 3: Product-Specific Pricing Structure | ✅ COMPLETE | Jan 26, 2026 |
| Phase 4: Customer Count Verification System | ✅ COMPLETE | Jan 26, 2026 |
| Phase 5: Enhanced Scraper with Source Tracking | ✅ COMPLETE | Jan 26, 2026 |
| Phase 6: UI Enhancements | 🟡 PENDING | - |
| Phase 7: Data Quality Dashboard | 🟡 PENDING | - |


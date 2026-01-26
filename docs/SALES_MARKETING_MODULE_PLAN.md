# Sales & Marketing Module Implementation Plan

**Certify Intel v5.0.7 Integration**

---

## ✅ IMPLEMENTATION STATUS: COMPLETE

**Completed**: January 26, 2026
**All 26 tasks across 5 phases have been implemented.**

This module implements the CMO's "Competitive Evaluation Dimensions for Healthcare AI Software" document, which requested structured dimension variables for the application and its underlying LLM to organize competitor findings and surface motion-specific insights for sales and marketing execution.

### Files Created
| File | Lines | Description |
|------|-------|-------------|
| `backend/sales_marketing_module.py` | ~600 | Core module logic, DimensionID, DIMENSION_METADATA |
| `backend/dimension_analyzer.py` | ~450 | AI dimension classification and scoring |
| `backend/battlecard_generator.py` | ~650 | Dynamic battlecard generation engine |
| `backend/routers/sales_marketing.py` | ~700 | FastAPI router with 30+ endpoints |
| `frontend/sales_marketing.js` | ~1,100 | Module JavaScript functions |
| `backend/tests/test_sales_marketing.py` | ~300 | End-to-end test suite |

### Files Modified
| File | Changes |
|------|---------|
| `backend/database.py` | Added 29 dimension fields + 4 new tables |
| `backend/main.py` | Included sales_marketing router |
| `backend/news_monitor.py` | Added dimension tagging integration |
| `backend/win_loss_tracker.py` | Added dimension correlation tracking |
| `backend/reports.py` | Added DimensionBattlecardPDFGenerator |
| `frontend/index.html` | Added sidebar item + page section |
| `frontend/app_v2.js` | Added module initialization |
| `frontend/styles.css` | Added ~400 lines of module styles |

---

## Executive Summary

This plan outlines the implementation of a Sales & Marketing Module as a new integrated component within the existing Certify Intel application. The module adds 9 Competitive Evaluation Dimensions as structured data fields, enabling the AI to organize competitor findings and surface actionable insights for sales deal execution and marketing campaigns.

**Key Principle**: This is an additive module, not a transformation. All new features integrate with and extend the existing codebase.

## Research Foundation

Based on deep research into competitive intelligence platforms (Klue, Crayon), sales enablement best practices, and healthcare vendor evaluation criteria:

| Best Practice | Implementation Approach |
|--------------|------------------------|
| AI-powered battlecards that update dynamically | Auto-generate battlecards from dimension scores + news feed |
| Structured dimension scoring (1-5 scale) | 9 dimensions with numeric scores + evidence text |
| Living competitive content vs static PDFs | Real-time dimension updates from news/data sources |
| Deal-specific competitive guidance | Dimension-based talking points and objection handlers |
| Win/Loss analysis tied to dimensions | Link existing Win/Loss tracker to dimension performance |

## Module Architecture

### Integration Points with Existing Codebase

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXISTING CERTIFY INTEL                        │
├─────────────────────────────────────────────────────────────────┤
│  frontend/                                                       │
│  ├── index.html          ← Add "Sales & Marketing" sidebar item │
│  ├── app_v2.js           ← Add module JavaScript functions      │
│  └── styles.css          ← Add module-specific styles           │
│                                                                  │
│  backend/                                                        │
│  ├── database.py         ← Add dimension fields to Competitor   │
│  ├── main.py             ← Add module API endpoints             │
│  ├── analytics.py        ← Extend with dimension analytics      │
│  ├── reports.py          ← Add battlecard PDF generation        │
│  ├── win_loss_tracker.py ← Link deals to dimensions             │
│  └── news_monitor.py     ← Tag articles by dimension            │
├─────────────────────────────────────────────────────────────────┤
│                    NEW MODULE FILES                              │
├─────────────────────────────────────────────────────────────────┤
│  backend/                                                        │
│  ├── sales_marketing_module.py    ← Core module logic           │
│  ├── dimension_analyzer.py        ← AI dimension classification │
│  ├── battlecard_generator.py      ← Dynamic battlecard engine   │
│  └── routers/sales_marketing.py   ← FastAPI router              │
│                                                                  │
│  frontend/                                                       │
│  └── sales_marketing.js           ← Module-specific JS          │
└─────────────────────────────────────────────────────────────────┘
```

## The 9 Competitive Evaluation Dimensions

### Dimension Schema

| # | Dimension ID | Display Name | What to Track | Deal Impact |
|---|--------------|--------------|---------------|-------------|
| 1 | product_packaging | Product Modules & Packaging | Bundled vs modular, suite lock-in, module gaps | Buyers reject forced bundles |
| 2 | integration_depth | Interoperability & Integration | EHR/EMR integrations, API maturity, workflow embed | Integration = key differentiator |
| 3 | support_service | Customer Support & Service | Responsiveness, implementation partnership, services depth | Support drives outcomes > features |
| 4 | retention_stickiness | Retention & Product Stickiness | Renewal strength, switching costs, operational embed | Sticky products persist |
| 5 | user_adoption | User Adoption & Ease of Use | Workflow fit, training burden, sustained usage | Adoption = value realization |
| 6 | implementation_ttv | Implementation & Time to Value | Deployment timelines, go-live consistency | Faster TTV wins deals |
| 7 | reliability_enterprise | Reliability & Enterprise Readiness | Uptime, scalability, operational maturity | Enterprise needs stability |
| 8 | pricing_flexibility | Pricing Model & Commercial Flexibility | Transparency, modularity, hidden costs | Commercial structure = buyer confidence |
| 9 | reporting_analytics | Reporting & Analytics Capability | Dashboards, module performance, data export | Buyers need self-service data |

### Scoring Model

Each dimension has:
- **Score**: 1-5 numeric rating (1=Major Weakness, 5=Major Strength)
- **Evidence**: Text field with supporting facts, sources, dates
- **Last Updated**: Timestamp of last assessment
- **Source**: Manual, AI-inferred, or News-derived
- **Confidence**: Low, Medium, High

---

## Phase 1: Database Schema Extension

### New Fields for Competitor Model

**File**: `backend/database.py`

```python
# ============== Sales & Marketing Module: Competitive Dimensions ==============

# Dimension 1: Product Modules & Packaging
dim_product_packaging_score = Column(Integer, nullable=True)  # 1-5
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

# Aggregate Scores
dim_overall_score = Column(Float, nullable=True)  # Average of all dimensions
dim_sales_priority = Column(String, nullable=True)  # High/Medium/Low
```

### New Tables

**File**: `backend/database.py`

```python
class CompetitorDimensionHistory(Base):
    """Track dimension score changes over time"""
    __tablename__ = "competitor_dimension_history"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"))
    dimension_id = Column(String)  # e.g., "product_packaging"
    old_score = Column(Integer, nullable=True)
    new_score = Column(Integer)
    evidence = Column(Text)
    source = Column(String)  # manual, ai, news
    changed_by = Column(String)  # user email or "system"
    changed_at = Column(DateTime, default=datetime.utcnow)


class Battlecard(Base):
    """Generated battlecards for competitors"""
    __tablename__ = "battlecards"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"))
    title = Column(String)
    content = Column(Text)  # JSON or Markdown
    battlecard_type = Column(String)  # full, quick, objection_handler
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(String)  # user or "ai"
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)


class TalkingPoint(Base):
    """Dimension-specific talking points for sales"""
    __tablename__ = "talking_points"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"))
    dimension_id = Column(String)
    point_type = Column(String)  # strength, weakness, objection, counter
    content = Column(Text)
    effectiveness_score = Column(Integer, nullable=True)  # From win/loss feedback
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)


class DimensionNewsTag(Base):
    """Link news articles to dimensions"""
    __tablename__ = "dimension_news_tags"

    id = Column(Integer, primary_key=True, index=True)
    news_url = Column(String)
    news_title = Column(String)
    competitor_id = Column(Integer, ForeignKey("competitors.id"))
    dimension_id = Column(String)
    relevance_score = Column(Float)  # 0-1 confidence
    tagged_at = Column(DateTime, default=datetime.utcnow)
    tagged_by = Column(String)  # ai or user email
```

---

## Phase 2: Backend Module Implementation

### Core Module File

**File**: `backend/sales_marketing_module.py` (NEW)

```python
"""
Certify Intel - Sales & Marketing Module
Core logic for competitive dimension management and sales enablement.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class DimensionID(str, Enum):
    PRODUCT_PACKAGING = "product_packaging"
    INTEGRATION_DEPTH = "integration_depth"
    SUPPORT_SERVICE = "support_service"
    RETENTION_STICKINESS = "retention_stickiness"
    USER_ADOPTION = "user_adoption"
    IMPLEMENTATION_TTV = "implementation_ttv"
    RELIABILITY_ENTERPRISE = "reliability_enterprise"
    PRICING_FLEXIBILITY = "pricing_flexibility"
    REPORTING_ANALYTICS = "reporting_analytics"

DIMENSION_METADATA = {
    DimensionID.PRODUCT_PACKAGING: {
        "name": "Product Modules & Packaging",
        "description": "Modular vs bundled purchasing, module gaps, suite lock-in",
        "deal_impact": "Buyers often reject forced bundles and overbuy risk",
        "keywords": ["bundle", "module", "package", "suite", "pricing tier", "add-on"],
        "review_signals": ["forced to buy", "only needed", "too many features", "nickel and dime"]
    },
    DimensionID.INTEGRATION_DEPTH: {
        "name": "Interoperability & Integration Depth",
        "description": "Number and depth of EHR/EMR integrations, API maturity, workflow embed",
        "deal_impact": "Broad, proven integration coverage reduces friction and becomes a standalone differentiator",
        "keywords": ["integration", "API", "EHR", "EMR", "Epic", "Cerner", "interoperability", "HL7", "FHIR"],
        "review_signals": ["integrates with", "connects to", "API", "data sync", "workflow"]
    },
    DimensionID.SUPPORT_SERVICE: {
        "name": "Customer Support & Service Model",
        "description": "Responsiveness, implementation partnership, services depth",
        "deal_impact": "Support quality often drives outcomes more than features",
        "keywords": ["support", "service", "help desk", "customer success", "account manager", "response time"],
        "review_signals": ["support team", "responsive", "helpful", "slow to respond", "ticket"]
    },
    DimensionID.RETENTION_STICKINESS: {
        "name": "Retention & Product Stickiness",
        "description": "Renewal strength, switching costs, embedded operational value",
        "deal_impact": "Sticky products persist because they deliver durable value",
        "keywords": ["retention", "churn", "renewal", "switching cost", "contract", "lock-in"],
        "review_signals": ["hard to leave", "switching", "contract", "renewal", "years using"]
    },
    DimensionID.USER_ADOPTION: {
        "name": "User Adoption & Ease of Use",
        "description": "Workflow fit, training burden, sustained usage evidence",
        "deal_impact": "Adoption determines whether value materializes",
        "keywords": ["adoption", "ease of use", "user-friendly", "training", "onboarding", "intuitive"],
        "review_signals": ["easy to use", "intuitive", "learning curve", "training", "staff adoption"]
    },
    DimensionID.IMPLEMENTATION_TTV: {
        "name": "Implementation Effort & Time to Value",
        "description": "Deployment timelines, services requirements, go-live consistency",
        "deal_impact": "Strong implementation creates faster time-to-value",
        "keywords": ["implementation", "deployment", "go-live", "timeline", "onboarding", "setup"],
        "review_signals": ["implementation", "go-live", "weeks", "months", "delayed", "on time"]
    },
    DimensionID.RELIABILITY_ENTERPRISE: {
        "name": "Reliability & Enterprise Readiness",
        "description": "Uptime, operational consistency, scalability, maturity at enterprise volume",
        "deal_impact": "Operational systems require dependable performance at scale",
        "keywords": ["uptime", "reliability", "scalability", "enterprise", "downtime", "outage", "performance"],
        "review_signals": ["downtime", "reliable", "crashes", "slow", "enterprise", "scale"]
    },
    DimensionID.PRICING_FLEXIBILITY: {
        "name": "Pricing Model & Commercial Flexibility",
        "description": "Pricing transparency, modularity, hidden cost drivers",
        "deal_impact": "Commercial structure shapes buyer confidence and ROI",
        "keywords": ["pricing", "cost", "fee", "contract", "transparent", "hidden", "ROI"],
        "review_signals": ["expensive", "affordable", "hidden fees", "pricing", "cost", "value"]
    },
    DimensionID.REPORTING_ANALYTICS: {
        "name": "Reporting & Analytics Capability",
        "description": "Operational dashboards, module-level performance visibility, exportable data",
        "deal_impact": "Buyers need surfaced data for ongoing performance improvement",
        "keywords": ["reporting", "analytics", "dashboard", "metrics", "data", "export", "insights"],
        "review_signals": ["reports", "dashboard", "analytics", "metrics", "visibility", "data"]
    }
}

@dataclass
class DimensionScore:
    dimension_id: str
    score: int  # 1-5
    evidence: str
    source: str  # manual, ai, news
    confidence: str  # low, medium, high
    updated_at: datetime

@dataclass
class CompetitorDimensionProfile:
    competitor_id: int
    competitor_name: str
    dimensions: Dict[str, DimensionScore]
    overall_score: float
    strengths: List[str]  # dimension_ids where score >= 4
    weaknesses: List[str]  # dimension_ids where score <= 2
    sales_priority: str  # high, medium, low

class SalesMarketingModule:
    """Core module for sales and marketing competitive intelligence."""

    def __init__(self, db_session):
        self.db = db_session

    def get_dimension_profile(self, competitor_id: int) -> CompetitorDimensionProfile:
        """Get complete dimension profile for a competitor."""
        pass  # Implementation

    def update_dimension_score(
        self,
        competitor_id: int,
        dimension_id: str,
        score: int,
        evidence: str,
        user_email: str
    ) -> bool:
        """Update a dimension score with audit trail."""
        pass  # Implementation

    def get_dimension_comparison(
        self,
        competitor_ids: List[int]
    ) -> Dict[str, Any]:
        """Compare multiple competitors across all dimensions."""
        pass  # Implementation

    def get_sales_talking_points(
        self,
        competitor_id: int,
        focus_dimensions: Optional[List[str]] = None
    ) -> List[Dict]:
        """Get talking points for sales conversations."""
        pass  # Implementation

    def calculate_overall_score(self, competitor_id: int) -> float:
        """Calculate weighted overall dimension score."""
        pass  # Implementation
```

### AI Dimension Analyzer

**File**: `backend/dimension_analyzer.py` (NEW)

```python
"""
AI-powered dimension classification and scoring.
Analyzes news, reviews, and competitor data to infer dimension scores.
"""

from typing import Dict, List, Tuple, Optional
from sales_marketing_module import DIMENSION_METADATA, DimensionID
import os

class DimensionAnalyzer:
    """
    Analyzes text content to classify by dimension and infer scores.
    Uses existing OpenAI integration from main.py.
    """

    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1")

    def classify_article_dimension(
        self,
        title: str,
        snippet: str,
        competitor_name: str
    ) -> List[Tuple[str, float]]:
        """
        Classify which dimensions a news article relates to.
        Returns list of (dimension_id, confidence) tuples.
        """
        pass  # Implementation using OpenAI

    def analyze_review_dimensions(
        self,
        review_text: str,
        review_rating: float,
        competitor_name: str
    ) -> Dict[str, int]:
        """
        Extract dimension signals from a customer review.
        Returns dict of dimension_id -> inferred score (1-5).
        """
        pass  # Implementation

    def generate_dimension_evidence(
        self,
        competitor_name: str,
        dimension_id: str,
        sources: List[Dict]  # news, reviews, etc.
    ) -> str:
        """
        Generate evidence summary for a dimension from multiple sources.
        """
        pass  # Implementation

    def suggest_dimension_scores(
        self,
        competitor_id: int,
        competitor_name: str
    ) -> Dict[str, Dict]:
        """
        AI-suggested dimension scores based on all available data.
        Returns dict with score, evidence, confidence for each dimension.
        """
        pass  # Implementation
```

### Battlecard Generator

**File**: `backend/battlecard_generator.py` (NEW)

```python
"""
Dynamic battlecard generation engine.
Creates sales-ready competitive battlecards from dimension data.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sales_marketing_module import DIMENSION_METADATA

class BattlecardGenerator:
    """
    Generates dynamic battlecards that update with dimension changes.
    Integrates with existing reports.py for PDF export.
    """

    BATTLECARD_TEMPLATES = {
        "full": {
            "sections": [
                "quick_facts",
                "dimension_scorecard",
                "strengths_weaknesses",
                "key_differentiators",
                "common_objections",
                "counter_positioning",
                "win_themes",
                "red_flags",
                "recent_news"
            ]
        },
        "quick": {
            "sections": [
                "quick_facts",
                "top_3_differentiators",
                "killer_questions",
                "one_liner"
            ]
        },
        "objection_handler": {
            "sections": [
                "common_objections",
                "counter_responses",
                "proof_points"
            ]
        }
    }

    def __init__(self, db_session):
        self.db = db_session

    def generate_battlecard(
        self,
        competitor_id: int,
        battlecard_type: str = "full",
        focus_dimensions: Optional[List[str]] = None,
        deal_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a battlecard for a competitor.

        Args:
            competitor_id: Target competitor
            battlecard_type: full, quick, or objection_handler
            focus_dimensions: Optional list to emphasize
            deal_context: Optional deal-specific context for personalization
        """
        pass  # Implementation

    def generate_dimension_scorecard(
        self,
        competitor_id: int,
        include_certify_comparison: bool = True
    ) -> Dict[str, Any]:
        """Generate visual dimension scorecard section."""
        pass  # Implementation

    def generate_objection_handlers(
        self,
        competitor_id: int
    ) -> List[Dict]:
        """Generate dimension-based objection handlers."""
        pass  # Implementation

    def export_to_pdf(
        self,
        battlecard_id: int
    ) -> bytes:
        """Export battlecard to PDF using existing reports.py."""
        pass  # Implementation integrating with backend/reports.py
```

### FastAPI Router

**File**: `backend/routers/sales_marketing.py` (NEW)

```python
"""
Sales & Marketing Module API Routes
Integrates with existing FastAPI app in main.py
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/sales-marketing", tags=["Sales & Marketing"])

# ============== Pydantic Models ==============

class DimensionScoreUpdate(BaseModel):
    dimension_id: str
    score: int  # 1-5
    evidence: str

class BattlecardRequest(BaseModel):
    competitor_id: int
    battlecard_type: str = "full"
    focus_dimensions: Optional[List[str]] = None
    deal_context: Optional[str] = None

class TalkingPointCreate(BaseModel):
    competitor_id: int
    dimension_id: str
    point_type: str  # strength, weakness, objection, counter
    content: str

# ============== Dimension Endpoints ==============

@router.get("/dimensions")
async def list_dimensions():
    """Get all 9 competitive dimensions with metadata."""
    pass

@router.get("/competitors/{competitor_id}/dimensions")
async def get_competitor_dimensions(competitor_id: int):
    """Get dimension profile for a competitor."""
    pass

@router.put("/competitors/{competitor_id}/dimensions/{dimension_id}")
async def update_dimension_score(
    competitor_id: int,
    dimension_id: str,
    update: DimensionScoreUpdate
):
    """Update a dimension score with evidence."""
    pass

@router.get("/competitors/{competitor_id}/dimensions/history")
async def get_dimension_history(competitor_id: int):
    """Get dimension score change history."""
    pass

@router.post("/competitors/{competitor_id}/dimensions/ai-suggest")
async def ai_suggest_dimensions(competitor_id: int):
    """Get AI-suggested dimension scores."""
    pass

# ============== Battlecard Endpoints ==============

@router.post("/battlecards/generate")
async def generate_battlecard(request: BattlecardRequest):
    """Generate a new battlecard."""
    pass

@router.get("/battlecards/{battlecard_id}")
async def get_battlecard(battlecard_id: int):
    """Get a specific battlecard."""
    pass

@router.get("/competitors/{competitor_id}/battlecards")
async def list_competitor_battlecards(competitor_id: int):
    """List all battlecards for a competitor."""
    pass

@router.get("/battlecards/{battlecard_id}/pdf")
async def export_battlecard_pdf(battlecard_id: int):
    """Export battlecard as PDF."""
    pass

# ============== Comparison Endpoints ==============

@router.post("/compare/dimensions")
async def compare_dimensions(competitor_ids: List[int]):
    """Compare multiple competitors across all dimensions."""
    pass

@router.get("/compare/{competitor_id}/vs-certify")
async def compare_vs_certify(competitor_id: int):
    """Compare competitor dimensions against Certify Health."""
    pass

# ============== Talking Points Endpoints ==============

@router.get("/competitors/{competitor_id}/talking-points")
async def get_talking_points(
    competitor_id: int,
    dimension_id: Optional[str] = None,
    point_type: Optional[str] = None
):
    """Get talking points for sales conversations."""
    pass

@router.post("/talking-points")
async def create_talking_point(point: TalkingPointCreate):
    """Create a new talking point."""
    pass

# ============== News Dimension Tagging ==============

@router.get("/news/by-dimension/{dimension_id}")
async def get_news_by_dimension(
    dimension_id: str,
    competitor_id: Optional[int] = None,
    days: int = 30
):
    """Get news articles tagged with a specific dimension."""
    pass

@router.post("/news/tag-dimension")
async def tag_news_dimension(
    news_url: str,
    competitor_id: int,
    dimension_id: str
):
    """Manually tag a news article with a dimension."""
    pass

# ============== Analytics Endpoints ==============

@router.get("/analytics/dimension-trends")
async def get_dimension_trends(
    competitor_id: Optional[int] = None,
    days: int = 90
):
    """Get dimension score trends over time."""
    pass

@router.get("/analytics/win-loss-by-dimension")
async def get_win_loss_by_dimension():
    """Analyze win/loss correlation with dimensions."""
    pass
```

---

## Phase 3: Frontend Implementation

### Sidebar Integration

**File**: `frontend/index.html`

Add after existing sidebar items:

```html
<a href="#" class="nav-item" onclick="showPage('salesmarketing')">
    <span class="nav-icon">🎯</span>
    <span class="nav-text">Sales & Marketing</span>
</a>
```

### Main Page Section

**File**: `frontend/index.html`

```html
<!-- Sales & Marketing Module Page -->
<section id="salesmarketingPage" class="page" style="display:none;">
    <div class="page-header">
        <h2>🎯 Sales & Marketing Module</h2>
        <p class="page-description">Competitive dimensions, battlecards, and sales enablement tools</p>
    </div>

    <!-- Sub-navigation Tabs -->
    <div class="module-tabs">
        <button class="tab-btn active" onclick="showSalesMarketingTab('dimensions')">
            📊 Dimension Scorecard
        </button>
        <button class="tab-btn" onclick="showSalesMarketingTab('battlecards')">
            ⚔️ Battlecards
        </button>
        <button class="tab-btn" onclick="showSalesMarketingTab('comparison')">
            📈 Competitor Comparison
        </button>
        <button class="tab-btn" onclick="showSalesMarketingTab('talkingpoints')">
            💬 Talking Points
        </button>
    </div>

    <!-- Tab Content: Dimension Scorecard -->
    <div id="dimensionsTab" class="tab-content active">
        <!-- Competitor Selector -->
        <div class="filter-bar">
            <select id="dimensionCompetitorSelect" onchange="loadCompetitorDimensions()">
                <option value="">-- Select Competitor --</option>
            </select>
            <button class="btn-secondary" onclick="aiSuggestDimensions()">
                🤖 AI Suggest Scores
            </button>
        </div>

        <!-- Dimension Grid -->
        <div id="dimensionGrid" class="dimension-grid">
            <!-- Populated by JavaScript -->
        </div>
    </div>

    <!-- Tab Content: Battlecards -->
    <div id="battlecardsTab" class="tab-content" style="display:none;">
        <div class="filter-bar">
            <select id="battlecardCompetitorSelect">
                <option value="">-- Select Competitor --</option>
            </select>
            <select id="battlecardType">
                <option value="full">Full Battlecard</option>
                <option value="quick">Quick Reference</option>
                <option value="objection_handler">Objection Handler</option>
            </select>
            <button class="btn-primary" onclick="generateBattlecard()">
                ⚔️ Generate Battlecard
            </button>
        </div>
        <div id="battlecardContent" class="battlecard-container">
            <!-- Generated battlecard appears here -->
        </div>
    </div>

    <!-- Tab Content: Competitor Comparison -->
    <div id="comparisonTab" class="tab-content" style="display:none;">
        <div class="filter-bar">
            <select id="compareCompetitor1"></select>
            <span style="margin: 0 10px;">vs</span>
            <select id="compareCompetitor2"></select>
            <button class="btn-primary" onclick="loadDimensionComparison()">
                Compare
            </button>
        </div>
        <div id="comparisonChart" class="comparison-container">
            <!-- Radar chart comparison -->
        </div>
    </div>

    <!-- Tab Content: Talking Points -->
    <div id="talkingpointsTab" class="tab-content" style="display:none;">
        <div class="filter-bar">
            <select id="talkingPointsCompetitor"></select>
            <select id="talkingPointsDimension">
                <option value="">All Dimensions</option>
            </select>
            <select id="talkingPointsType">
                <option value="">All Types</option>
                <option value="strength">Strengths</option>
                <option value="weakness">Weaknesses</option>
                <option value="objection">Objections</option>
                <option value="counter">Counter-Points</option>
            </select>
        </div>
        <div id="talkingPointsList" class="talking-points-container">
            <!-- Talking points list -->
        </div>
    </div>
</section>
```

### JavaScript Module

**File**: `frontend/sales_marketing.js` (NEW)

```javascript
/**
 * Sales & Marketing Module JavaScript
 * Integrates with existing app_v2.js
 */

// ============== Constants ==============

const DIMENSIONS = [
    { id: 'product_packaging', name: 'Product Modules & Packaging', icon: '📦' },
    { id: 'integration_depth', name: 'Interoperability & Integration', icon: '🔗' },
    { id: 'support_service', name: 'Customer Support & Service', icon: '🎧' },
    { id: 'retention_stickiness', name: 'Retention & Stickiness', icon: '🔒' },
    { id: 'user_adoption', name: 'User Adoption & Ease of Use', icon: '👥' },
    { id: 'implementation_ttv', name: 'Implementation & Time to Value', icon: '⏱️' },
    { id: 'reliability_enterprise', name: 'Reliability & Enterprise Readiness', icon: '🏢' },
    { id: 'pricing_flexibility', name: 'Pricing & Commercial Flexibility', icon: '💰' },
    { id: 'reporting_analytics', name: 'Reporting & Analytics', icon: '📊' }
];

// ============== Tab Navigation ==============

function showSalesMarketingTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName + 'Tab').style.display = 'block';
    event.target.classList.add('active');
}

// ============== Dimension Scorecard ==============

async function loadCompetitorDimensions() {
    const competitorId = document.getElementById('dimensionCompetitorSelect').value;
    if (!competitorId) return;

    const data = await fetchAPI(`/api/sales-marketing/competitors/${competitorId}/dimensions`);
    renderDimensionGrid(data);
}

function renderDimensionGrid(data) {
    const grid = document.getElementById('dimensionGrid');
    grid.innerHTML = DIMENSIONS.map(dim => {
        const dimData = data.dimensions[dim.id] || {};
        const score = dimData.score || 0;
        return `
            <div class="dimension-card" data-dimension="${dim.id}">
                <div class="dimension-header">
                    <span class="dimension-icon">${dim.icon}</span>
                    <span class="dimension-name">${dim.name}</span>
                </div>
                <div class="dimension-score">
                    ${renderScoreSelector(dim.id, score)}
                </div>
                <div class="dimension-evidence">
                    <textarea placeholder="Evidence and sources..."
                              id="evidence-${dim.id}">${dimData.evidence || ''}</textarea>
                </div>
                <div class="dimension-meta">
                    ${dimData.updated_at ? `Updated: ${formatDate(dimData.updated_at)}` : 'Not scored yet'}
                </div>
                <button class="btn-small" onclick="saveDimensionScore('${dim.id}')">
                    Save
                </button>
            </div>
        `;
    }).join('');
}

function renderScoreSelector(dimensionId, currentScore) {
    return [1, 2, 3, 4, 5].map(score => `
        <button class="score-btn ${score === currentScore ? 'active' : ''}"
                onclick="selectScore('${dimensionId}', ${score})"
                title="${getScoreLabel(score)}">
            ${score}
        </button>
    `).join('');
}

function getScoreLabel(score) {
    const labels = {
        1: 'Major Weakness',
        2: 'Weakness',
        3: 'Neutral',
        4: 'Strength',
        5: 'Major Strength'
    };
    return labels[score];
}

async function saveDimensionScore(dimensionId) {
    const competitorId = document.getElementById('dimensionCompetitorSelect').value;
    const scoreBtn = document.querySelector(`[data-dimension="${dimensionId}"] .score-btn.active`);
    const evidence = document.getElementById(`evidence-${dimensionId}`).value;

    if (!scoreBtn) {
        showNotification('Please select a score', 'error');
        return;
    }

    await fetchAPI(`/api/sales-marketing/competitors/${competitorId}/dimensions/${dimensionId}`, {
        method: 'PUT',
        body: JSON.stringify({
            dimension_id: dimensionId,
            score: parseInt(scoreBtn.textContent),
            evidence: evidence
        })
    });

    showNotification('Dimension score saved', 'success');
}

// ============== Battlecard Generation ==============

async function generateBattlecard() {
    const competitorId = document.getElementById('battlecardCompetitorSelect').value;
    const battlecardType = document.getElementById('battlecardType').value;

    if (!competitorId) {
        showNotification('Please select a competitor', 'error');
        return;
    }

    const container = document.getElementById('battlecardContent');
    container.innerHTML = '<div class="loading">Generating battlecard...</div>';

    const data = await fetchAPI('/api/sales-marketing/battlecards/generate', {
        method: 'POST',
        body: JSON.stringify({
            competitor_id: parseInt(competitorId),
            battlecard_type: battlecardType
        })
    });

    renderBattlecard(data);
}

function renderBattlecard(data) {
    const container = document.getElementById('battlecardContent');
    container.innerHTML = `
        <div class="battlecard">
            <div class="battlecard-header">
                <h3>${data.competitor_name} Battlecard</h3>
                <button class="btn-secondary" onclick="exportBattlecardPDF(${data.id})">
                    📄 Export PDF
                </button>
            </div>
            <div class="battlecard-body">
                ${data.content}
            </div>
        </div>
    `;
}

// ============== Comparison Chart ==============

async function loadDimensionComparison() {
    const competitor1 = document.getElementById('compareCompetitor1').value;
    const competitor2 = document.getElementById('compareCompetitor2').value;

    if (!competitor1 || !competitor2) {
        showNotification('Please select two competitors', 'error');
        return;
    }

    const data = await fetchAPI('/api/sales-marketing/compare/dimensions', {
        method: 'POST',
        body: JSON.stringify({ competitor_ids: [parseInt(competitor1), parseInt(competitor2)] })
    });

    renderComparisonRadarChart(data);
}

function renderComparisonRadarChart(data) {
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: DIMENSIONS.map(d => d.name),
            datasets: data.competitors.map((comp, i) => ({
                label: comp.name,
                data: DIMENSIONS.map(d => comp.dimensions[d.id]?.score || 0),
                borderColor: i === 0 ? '#2F5496' : '#22c55e',
                backgroundColor: i === 0 ? 'rgba(47, 84, 150, 0.2)' : 'rgba(34, 197, 94, 0.2)'
            }))
        },
        options: {
            scales: {
                r: {
                    min: 0,
                    max: 5,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

// ============== Initialize ==============

function initSalesMarketingModule() {
    const selects = [
        'dimensionCompetitorSelect',
        'battlecardCompetitorSelect',
        'compareCompetitor1',
        'compareCompetitor2',
        'talkingPointsCompetitor'
    ];

    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            select.innerHTML = '<option value="">-- Select Competitor --</option>' +
                competitors.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        }
    });

    const dimSelect = document.getElementById('talkingPointsDimension');
    if (dimSelect) {
        dimSelect.innerHTML = '<option value="">All Dimensions</option>' +
            DIMENSIONS.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
    }
}
```

---

## Phase 4: Integration with Existing Features

### News Feed Integration

**File**: `backend/news_monitor.py`

Add dimension tagging to article processing:

```python
def _tag_article_dimensions(self, article: NewsArticle, competitor_name: str) -> List[str]:
    """Tag article with relevant competitive dimensions."""
    from dimension_analyzer import DimensionAnalyzer

    analyzer = DimensionAnalyzer()
    dimension_tags = analyzer.classify_article_dimension(
        article.title,
        article.snippet,
        competitor_name
    )

    return [dim_id for dim_id, confidence in dimension_tags if confidence > 0.6]
```

### Win/Loss Tracker Integration

**File**: `backend/win_loss_tracker.py`

Add dimension correlation:

```python
def analyze_dimension_impact(self, competitor_id: int) -> Dict[str, Any]:
    """Analyze which dimensions correlate with wins/losses."""
    # Link deal outcomes to dimension scores at time of deal
    pass
```

---

## Phase 5: AI Enhancement

### Dimension Auto-Scoring from Reviews

Integrate with existing `review_scraper.py`:

```python
def score_dimensions_from_reviews(self, competitor_id: int) -> Dict[str, int]:
    """Analyze G2/Capterra reviews to infer dimension scores."""
    from review_scraper import ReviewScraper
    from dimension_analyzer import DimensionAnalyzer

    scraper = ReviewScraper()
    analyzer = DimensionAnalyzer()

    reviews = scraper.fetch_reviews(competitor_name)
    dimension_scores = {}

    for review in reviews:
        review_dimensions = analyzer.analyze_review_dimensions(
            review.text,
            review.rating,
            competitor_name
        )
        # Aggregate scores

    return dimension_scores
```

### Auto-Update Dimensions from News

```python
def update_dimensions_from_news(self, competitor_id: int):
    """Update dimension evidence from recent news articles."""
    from news_monitor import fetch_competitor_news
    from dimension_analyzer import DimensionAnalyzer

    news = fetch_competitor_news(competitor_name, days=30)
    analyzer = DimensionAnalyzer()

    for article in news['articles']:
        dimensions = analyzer.classify_article_dimension(
            article['title'],
            article['snippet'],
            competitor_name
        )

        for dim_id, confidence in dimensions:
            if confidence > 0.7:
                # Append to dimension evidence
                pass
```

---

## File Summary

### New Files to Create (7)

| File | Purpose |
|------|---------|
| `backend/sales_marketing_module.py` | Core module logic |
| `backend/dimension_analyzer.py` | AI dimension classification |
| `backend/battlecard_generator.py` | Dynamic battlecard engine |
| `backend/routers/sales_marketing.py` | FastAPI router (30+ endpoints) |
| `frontend/sales_marketing.js` | Module JavaScript |
| `frontend/sales_marketing.css` | Module styles |
| `docs/SALES_MARKETING_MODULE_PLAN.md` | This documentation |

### Existing Files to Modify (8)

| File | Changes |
|------|---------|
| `backend/database.py` | Add 27 dimension fields + 4 new tables |
| `backend/main.py` | Include sales_marketing router |
| `backend/news_monitor.py` | Add dimension tagging |
| `backend/win_loss_tracker.py` | Add dimension correlation |
| `backend/reports.py` | Add battlecard PDF export |
| `frontend/index.html` | Add sidebar + page section |
| `frontend/app_v2.js` | Add module initialization |
| `frontend/styles.css` | Add module styles |

---

## Implementation Timeline

| Phase | Tasks | Effort |
|-------|-------|--------|
| Phase 1 | Database schema extension | 2 hours |
| Phase 2 | Backend module files | 6 hours |
| Phase 3 | Frontend implementation | 4 hours |
| Phase 4 | Integration with existing features | 3 hours |
| Phase 5 | AI enhancement | 4 hours |
| Testing | End-to-end testing | 3 hours |
| **Total** | | **~22 hours** |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Dimension coverage | 100% of competitors scored on 9 dimensions |
| Battlecard generation time | < 10 seconds |
| AI dimension accuracy | > 75% agreement with manual scoring |
| Sales team adoption | 80% of reps using battlecards weekly |
| Win rate improvement | Measurable via Win/Loss correlation |

---

## Research Sources

- Klue Competitive Intelligence Platform
- Crayon vs Klue Comparison
- AI Battlecard Generation
- Sales Enablement Best Practices 2026
- Vendor Scorecard Templates
- B2B Sales Intelligence Guide

---

*Created: January 26, 2026*
*Version: v5.0.7 Planning Document*

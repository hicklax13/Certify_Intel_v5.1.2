"""
Pydantic schemas for API request/response validation.
"""
import uuid
from datetime import datetime
from typing import Optional, List, Any, Dict

from pydantic import BaseModel, Field, HttpUrl, ConfigDict


# ============================================================================
# Competitor Schemas
# ============================================================================

class CompetitorBase(BaseModel):
    """Base competitor schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    company_url: Optional[str] = None
    description: Optional[str] = None
    threat_level: str = Field(default="watch", pattern="^(high|medium|low|watch)$")
    vertical: Optional[str] = Field(None, max_length=100)
    segment: Optional[str] = Field(None, max_length=100)


class CompetitorCreate(CompetitorBase):
    """Schema for creating a new competitor."""
    discovery_method: Optional[str] = "manual"
    discovery_reasoning: Optional[str] = None


class CompetitorUpdate(BaseModel):
    """Schema for updating a competitor."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    company_url: Optional[str] = None
    description: Optional[str] = None
    threat_level: Optional[str] = Field(None, pattern="^(high|medium|low|watch)$")
    vertical: Optional[str] = Field(None, max_length=100)
    segment: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, pattern="^(active|inactive|archived)$")
    validation_notes: Optional[str] = None


class CompetitorResponse(CompetitorBase):
    """Schema for competitor API responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    discovery_method: Optional[str] = None
    discovery_reasoning: Optional[str] = None
    validated_by: str = "auto"
    status: str = "active"
    created_at: datetime
    updated_at: datetime
    last_scraped_at: Optional[datetime] = None


class CompetitorListResponse(BaseModel):
    """Paginated list of competitors."""
    items: List[CompetitorResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================================
# Evidence Schemas
# ============================================================================

class EvidenceBase(BaseModel):
    """Base evidence schema."""
    source_type: str = Field(..., pattern="^(website|news|review|job_posting|sec_filing|social)$")
    source_url: str
    source_name: Optional[str] = None
    title: Optional[str] = None


class EvidenceCreate(EvidenceBase):
    """Schema for creating evidence."""
    competitor_id: uuid.UUID
    content_text: Optional[str] = None
    content_html: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EvidenceResponse(EvidenceBase):
    """Schema for evidence API responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    competitor_id: uuid.UUID
    content_hash: str
    http_status: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    status: str
    fetched_at: datetime
    published_at: Optional[datetime] = None


# ============================================================================
# Claim Schemas
# ============================================================================

class ClaimBase(BaseModel):
    """Base claim schema."""
    claim_type: str = Field(..., pattern="^(pricing|feature|positioning|sentiment|company_health|executive|integration)$")
    claim_subtype: Optional[str] = None
    claim_data: Dict[str, Any]


class ClaimCreate(ClaimBase):
    """Schema for creating a claim."""
    competitor_id: uuid.UUID
    evidence_id: Optional[uuid.UUID] = None
    evidence_quote: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    extraction_reasoning: Optional[str] = None


class ClaimUpdate(BaseModel):
    """Schema for updating a claim."""
    claim_data: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    status: Optional[str] = Field(None, pattern="^(active|superseded|review_required|rejected)$")
    validation_notes: Optional[str] = None
    validated_by: Optional[str] = None


class ClaimResponse(ClaimBase):
    """Schema for claim API responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    competitor_id: uuid.UUID
    evidence_id: Optional[uuid.UUID] = None
    evidence_quote: Optional[str] = None
    extraction_model: Optional[str] = None
    extraction_reasoning: Optional[str] = None
    confidence: float
    validated_by: str
    validation_notes: Optional[str] = None
    status: str
    valid_from: datetime
    valid_to: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Change Event Schemas
# ============================================================================

class ChangeEventResponse(BaseModel):
    """Schema for change event API responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    competitor_id: uuid.UUID
    change_type: str
    severity: str
    previous_claim_id: Optional[uuid.UUID] = None
    new_claim_id: Optional[uuid.UUID] = None
    change_summary: str
    impact_assessment: Optional[str] = None
    recommended_action: Optional[str] = None
    status: str
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    detected_at: datetime


# ============================================================================
# Alert Schemas
# ============================================================================

class AlertResponse(BaseModel):
    """Schema for alert API responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    change_event_id: Optional[uuid.UUID] = None
    alert_type: str
    priority: str
    title: str
    body: str
    delivery_channel: str
    delivered_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime


class AlertAcknowledge(BaseModel):
    """Schema for acknowledging an alert."""
    acknowledged_by: str


# ============================================================================
# Briefing Schemas
# ============================================================================

class BriefingResponse(BaseModel):
    """Schema for briefing API responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    period_start: datetime
    period_end: datetime
    briefing_type: str
    title: str
    executive_summary: str
    content_markdown: str
    content_html: Optional[str] = None
    competitors_covered: Optional[List[uuid.UUID]] = None
    key_insights_count: int
    threats_count: int
    opportunities_count: int
    delivered_at: Optional[datetime] = None
    feedback_score: Optional[int] = None
    generated_at: datetime


class BriefingRequest(BaseModel):
    """Schema for requesting a new briefing."""
    period_start: datetime
    period_end: datetime
    briefing_type: str = "ad_hoc"
    competitor_ids: Optional[List[uuid.UUID]] = None


# ============================================================================
# Insight Schemas
# ============================================================================

class InsightResponse(BaseModel):
    """Generic insight response."""
    insight_type: str
    title: str
    summary: str
    details: Optional[str] = None
    severity: str = "info"
    competitor_id: Optional[uuid.UUID] = None
    competitor_name: Optional[str] = None
    recommended_action: Optional[str] = None
    supporting_data: Optional[Dict[str, Any]] = None
    generated_at: datetime


class InsightListResponse(BaseModel):
    """List of insights."""
    items: List[InsightResponse]
    total: int

"""
SQLAlchemy ORM models for the Certify Intel Platform.
"""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Text, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.core.database import Base


class Competitor(Base):
    """
    Represents a competitor company being tracked.
    """
    __tablename__ = "competitors"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    company_url: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Classification
    threat_level: Mapped[str] = mapped_column(String(20), default="watch")  # high, medium, low, watch
    vertical: Mapped[Optional[str]] = mapped_column(String(100))
    segment: Mapped[Optional[str]] = mapped_column(String(100))  # enterprise, mid-market, smb
    
    # Discovery metadata
    discovery_method: Mapped[Optional[str]] = mapped_column(String(50))
    discovery_reasoning: Mapped[Optional[str]] = mapped_column(Text)
    discovery_query: Mapped[Optional[str]] = mapped_column(Text)
    
    # Validation
    validated_by: Mapped[str] = mapped_column(String(50), default="auto")  # auto, human
    validation_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, inactive, archived
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    evidence: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="competitor", cascade="all, delete-orphan")
    claims: Mapped[List["Claim"]] = relationship("Claim", back_populates="competitor", cascade="all, delete-orphan")
    change_events: Mapped[List["ChangeEvent"]] = relationship("ChangeEvent", back_populates="competitor", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_competitors_domain", "domain"),
        Index("ix_competitors_threat_level", "threat_level"),
        Index("ix_competitors_status", "status"),
    )


class Evidence(Base):
    """
    Raw evidence collected from various sources (websites, news, reviews, etc.).
    """
    __tablename__ = "evidence"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("competitors.id"), nullable=False)
    
    # Source information
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # website, news, review, job_posting, sec_filing
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_name: Mapped[Optional[str]] = mapped_column(String(255))  # e.g., "G2", "LinkedIn Jobs"
    
    # Content
    title: Mapped[Optional[str]] = mapped_column(Text)
    content_text: Mapped[Optional[str]] = mapped_column(Text)
    content_html: Mapped[Optional[str]] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)  # Flexible storage for source-specific data
    http_status: Mapped[Optional[int]] = mapped_column()
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, superseded, failed
    
    # Timestamps
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)  # For news articles
    
    # Relationships
    competitor: Mapped["Competitor"] = relationship("Competitor", back_populates="evidence")
    claims: Mapped[List["Claim"]] = relationship("Claim", back_populates="evidence")
    
    __table_args__ = (
        Index("ix_evidence_competitor_id", "competitor_id"),
        Index("ix_evidence_source_type", "source_type"),
        Index("ix_evidence_fetched_at", "fetched_at"),
        Index("ix_evidence_content_hash", "content_hash"),
    )


class Claim(Base):
    """
    Extracted and validated claims about competitors (pricing, features, positioning, etc.).
    """
    __tablename__ = "claims"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("competitors.id"), nullable=False)
    evidence_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("evidence.id"))
    
    # Claim type
    claim_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pricing, feature, positioning, sentiment, company_health, executive
    claim_subtype: Mapped[Optional[str]] = mapped_column(String(50))  # e.g., for pricing: per_user, flat, etc.
    
    # Extracted data (structured)
    claim_data: Mapped[dict] = mapped_column(JSONB, nullable=False)  # Type-specific structured data
    
    # Evidence trail
    evidence_quote: Mapped[Optional[str]] = mapped_column(Text)  # Exact quote supporting the claim
    span_start: Mapped[Optional[int]] = mapped_column()  # Character offset in source
    span_end: Mapped[Optional[int]] = mapped_column()
    
    # AI extraction metadata
    extraction_model: Mapped[Optional[str]] = mapped_column(String(50))
    extraction_reasoning: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Validation
    validated_by: Mapped[str] = mapped_column(String(50), default="auto")  # auto, human
    validation_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Status and versioning
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, superseded, review_required, rejected
    superseded_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("claims.id"))
    
    # Validity period
    valid_from: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    competitor: Mapped["Competitor"] = relationship("Competitor", back_populates="claims")
    evidence: Mapped[Optional["Evidence"]] = relationship("Evidence", back_populates="claims")
    
    __table_args__ = (
        Index("ix_claims_competitor_id", "competitor_id"),
        Index("ix_claims_claim_type", "claim_type"),
        Index("ix_claims_status", "status"),
        Index("ix_claims_created_at", "created_at"),
    )


class ClaimEmbedding(Base):
    """
    Vector embeddings for semantic search and similarity.
    """
    __tablename__ = "claim_embeddings"
    
    claim_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("claims.id"), primary_key=True)
    embedding: Mapped[list] = mapped_column(Vector(1536))  # OpenAI text-embedding-3-large dimension
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ChangeEvent(Base):
    """
    Detected changes in competitor data.
    """
    __tablename__ = "change_events"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("competitors.id"), nullable=False)
    
    # Change details
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pricing_change, feature_added, positioning_shift, etc.
    severity: Mapped[str] = mapped_column(String(20), default="medium")  # high, medium, low, info
    
    # Related claims
    previous_claim_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("claims.id"))
    new_claim_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("claims.id"))
    
    # AI-generated analysis
    change_summary: Mapped[str] = mapped_column(Text, nullable=False)
    impact_assessment: Mapped[Optional[str]] = mapped_column(Text)
    recommended_action: Mapped[Optional[str]] = mapped_column(Text)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="open")  # open, acknowledged, resolved
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(100))
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Timestamps
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    competitor: Mapped["Competitor"] = relationship("Competitor", back_populates="change_events")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="change_event", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_change_events_competitor_id", "competitor_id"),
        Index("ix_change_events_change_type", "change_type"),
        Index("ix_change_events_severity", "severity"),
        Index("ix_change_events_detected_at", "detected_at"),
    )


class Alert(Base):
    """
    Notifications sent to users about important changes.
    """
    __tablename__ = "alerts"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    change_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("change_events.id"))
    
    # Alert content
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)  # threat, opportunity, info
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # critical, high, medium, low
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Delivery
    delivery_channel: Mapped[str] = mapped_column(String(50), default="dashboard")  # dashboard, email, slack
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Acknowledgement
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(100))
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    change_event: Mapped[Optional["ChangeEvent"]] = relationship("ChangeEvent", back_populates="alerts")
    
    __table_args__ = (
        Index("ix_alerts_alert_type", "alert_type"),
        Index("ix_alerts_priority", "priority"),
        Index("ix_alerts_created_at", "created_at"),
    )


class Briefing(Base):
    """
    AI-generated executive briefings.
    """
    __tablename__ = "briefings"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Period covered
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    briefing_type: Mapped[str] = mapped_column(String(50), default="weekly")  # weekly, monthly, ad_hoc
    
    # Content
    title: Mapped[str] = mapped_column(Text, nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[Optional[str]] = mapped_column(Text)
    
    # Metadata
    competitors_covered: Mapped[Optional[list]] = mapped_column(JSONB)  # List of competitor IDs
    key_insights_count: Mapped[int] = mapped_column(default=0)
    threats_count: Mapped[int] = mapped_column(default=0)
    opportunities_count: Mapped[int] = mapped_column(default=0)
    
    # Delivery
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    delivered_to: Mapped[Optional[list]] = mapped_column(JSONB)  # List of email addresses
    
    # Feedback
    feedback_score: Mapped[Optional[int]] = mapped_column()  # 1-5 rating
    feedback_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_briefings_period", "period_start", "period_end"),
        Index("ix_briefings_type", "briefing_type"),
        Index("ix_briefings_generated_at", "generated_at"),
    )

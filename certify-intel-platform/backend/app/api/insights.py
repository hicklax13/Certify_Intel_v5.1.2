"""
Insights API endpoints.
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Competitor, Claim, ChangeEvent, Briefing
from app.schemas import InsightResponse, InsightListResponse, BriefingResponse, BriefingRequest

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_insights(
    db: AsyncSession = Depends(get_db),
):
    """
    Get aggregated insights for the main dashboard.
    """
    # Count competitors by threat level
    threat_counts = {}
    for level in ["high", "medium", "low", "watch"]:
        count = await db.scalar(
            select(func.count()).select_from(Competitor).where(
                Competitor.threat_level == level,
                Competitor.status == "active"
            )
        )
        threat_counts[level] = count or 0
    
    # Count recent changes (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_changes = await db.scalar(
        select(func.count()).select_from(ChangeEvent).where(
            ChangeEvent.detected_at >= week_ago
        )
    )
    
    # Count claims by type
    claim_counts = {}
    for claim_type in ["pricing", "feature", "positioning", "sentiment"]:
        count = await db.scalar(
            select(func.count()).select_from(Claim).where(
                Claim.claim_type == claim_type,
                Claim.status == "active"
            )
        )
        claim_counts[claim_type] = count or 0
    
    # Get open high-severity events
    high_severity_open = await db.scalar(
        select(func.count()).select_from(ChangeEvent).where(
            ChangeEvent.severity == "high",
            ChangeEvent.status == "open"
        )
    )
    
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "competitors": {
            "total": sum(threat_counts.values()),
            "by_threat_level": threat_counts,
        },
        "changes": {
            "last_7_days": recent_changes or 0,
            "high_severity_open": high_severity_open or 0,
        },
        "claims": {
            "total": sum(claim_counts.values()),
            "by_type": claim_counts,
        },
    }


@router.get("/threats", response_model=InsightListResponse)
async def get_threat_insights(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    """
    Get recent threat-related insights.
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    # Get high/medium severity change events
    result = await db.execute(
        select(ChangeEvent).where(
            ChangeEvent.detected_at >= since,
            ChangeEvent.severity.in_(["high", "medium"]),
        ).order_by(ChangeEvent.detected_at.desc()).limit(20)
    )
    events = result.scalars().all()
    
    insights = []
    for event in events:
        # Get competitor name
        comp_result = await db.execute(
            select(Competitor).where(Competitor.id == event.competitor_id)
        )
        competitor = comp_result.scalar_one_or_none()
        
        insights.append(InsightResponse(
            insight_type="threat",
            title=f"{event.change_type.replace('_', ' ').title()} Detected",
            summary=event.change_summary,
            details=event.impact_assessment,
            severity=event.severity,
            competitor_id=event.competitor_id,
            competitor_name=competitor.name if competitor else "Unknown",
            recommended_action=event.recommended_action,
            generated_at=event.detected_at,
        ))
    
    return InsightListResponse(items=insights, total=len(insights))


@router.get("/opportunities", response_model=InsightListResponse)
async def get_opportunity_insights(
    db: AsyncSession = Depends(get_db),
):
    """
    Get opportunity insights (competitor weaknesses, market gaps).
    """
    # This would typically use AI analysis - placeholder implementation
    # In production, this would query pre-generated opportunity insights
    
    return InsightListResponse(items=[], total=0)


@router.get("/briefings", response_model=List[BriefingResponse])
async def list_briefings(
    briefing_type: Optional[str] = Query(None, pattern="^(weekly|monthly|ad_hoc)$"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    List executive briefings.
    """
    query = select(Briefing)
    
    if briefing_type:
        query = query.where(Briefing.briefing_type == briefing_type)
    
    query = query.order_by(Briefing.generated_at.desc()).limit(limit)
    
    result = await db.execute(query)
    briefings = result.scalars().all()
    
    return [BriefingResponse.model_validate(b) for b in briefings]


@router.get("/briefings/{briefing_id}", response_model=BriefingResponse)
async def get_briefing(
    briefing_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific briefing by ID.
    """
    result = await db.execute(
        select(Briefing).where(Briefing.id == briefing_id)
    )
    briefing = result.scalar_one_or_none()
    
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")
    
    return BriefingResponse.model_validate(briefing)


@router.post("/briefings/generate", status_code=202)
async def generate_briefing(
    request: BriefingRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger generation of a new executive briefing.
    Returns immediately; generation happens asynchronously.
    """
    # TODO: Queue briefing generation task with Celery
    # from app.tasks.briefings import generate_briefing_task
    # task = generate_briefing_task.delay(
    #     request.period_start.isoformat(),
    #     request.period_end.isoformat(),
    #     request.briefing_type,
    #     [str(id) for id in request.competitor_ids] if request.competitor_ids else None
    # )
    
    return {
        "message": "Briefing generation queued",
        "period_start": request.period_start.isoformat(),
        "period_end": request.period_end.isoformat(),
        "briefing_type": request.briefing_type,
        "status": "pending",
    }

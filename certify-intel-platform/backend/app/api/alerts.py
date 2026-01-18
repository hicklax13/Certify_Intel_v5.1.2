"""
Alerts API endpoints.
"""
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Alert, ChangeEvent
from app.schemas import AlertResponse, AlertAcknowledge

router = APIRouter()


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    priority: Optional[str] = Query(None, pattern="^(critical|high|medium|low)$"),
    alert_type: Optional[str] = Query(None, pattern="^(threat|opportunity|info)$"),
    acknowledged: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    List alerts with optional filtering.
    """
    query = select(Alert)
    
    if priority:
        query = query.where(Alert.priority == priority)
    if alert_type:
        query = query.where(Alert.alert_type == alert_type)
    if acknowledged is not None:
        if acknowledged:
            query = query.where(Alert.acknowledged_at.isnot(None))
        else:
            query = query.where(Alert.acknowledged_at.is_(None))
    
    query = query.order_by(Alert.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return [AlertResponse.model_validate(a) for a in alerts]


@router.get("/unread/count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
):
    """
    Get count of unacknowledged alerts by priority.
    """
    from sqlalchemy import func
    
    counts = {}
    for priority in ["critical", "high", "medium", "low"]:
        count = await db.scalar(
            select(func.count()).select_from(Alert).where(
                Alert.priority == priority,
                Alert.acknowledged_at.is_(None)
            )
        )
        counts[priority] = count or 0
    
    return {
        "total": sum(counts.values()),
        "by_priority": counts,
    }


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single alert by ID.
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertResponse.model_validate(alert)


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: uuid.UUID,
    data: AlertAcknowledge,
    db: AsyncSession = Depends(get_db),
):
    """
    Acknowledge an alert.
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.acknowledged_at:
        raise HTTPException(status_code=400, detail="Alert already acknowledged")
    
    alert.acknowledged_by = data.acknowledged_by
    alert.acknowledged_at = datetime.utcnow()
    
    # Also acknowledge the related change event if exists
    if alert.change_event_id:
        event_result = await db.execute(
            select(ChangeEvent).where(ChangeEvent.id == alert.change_event_id)
        )
        event = event_result.scalar_one_or_none()
        if event and event.status == "open":
            event.status = "acknowledged"
            event.acknowledged_by = data.acknowledged_by
            event.acknowledged_at = datetime.utcnow()
    
    await db.flush()
    await db.refresh(alert)
    
    return AlertResponse.model_validate(alert)


@router.post("/acknowledge-all", status_code=200)
async def acknowledge_all_alerts(
    data: AlertAcknowledge,
    priority: Optional[str] = Query(None, pattern="^(critical|high|medium|low)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Acknowledge all unacknowledged alerts, optionally filtered by priority.
    """
    query = select(Alert).where(Alert.acknowledged_at.is_(None))
    
    if priority:
        query = query.where(Alert.priority == priority)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    now = datetime.utcnow()
    count = 0
    for alert in alerts:
        alert.acknowledged_by = data.acknowledged_by
        alert.acknowledged_at = now
        count += 1
    
    await db.flush()
    
    return {
        "message": f"Acknowledged {count} alerts",
        "count": count,
    }

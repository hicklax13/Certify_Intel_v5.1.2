"""
Competitor API endpoints.
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Competitor
from app.schemas import (
    CompetitorCreate,
    CompetitorUpdate,
    CompetitorResponse,
    CompetitorListResponse,
)

router = APIRouter()


@router.get("", response_model=CompetitorListResponse)
async def list_competitors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    threat_level: Optional[str] = Query(None, pattern="^(high|medium|low|watch)$"),
    status: Optional[str] = Query(None, pattern="^(active|inactive|archived)$"),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all competitors with pagination and filtering.
    """
    query = select(Competitor)
    
    # Apply filters
    if threat_level:
        query = query.where(Competitor.threat_level == threat_level)
    if status:
        query = query.where(Competitor.status == status)
    else:
        query = query.where(Competitor.status == "active")
    if search:
        query = query.where(
            Competitor.name.ilike(f"%{search}%") | 
            Competitor.domain.ilike(f"%{search}%")
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Competitor.name)
    
    result = await db.execute(query)
    competitors = result.scalars().all()
    
    return CompetitorListResponse(
        items=[CompetitorResponse.model_validate(c) for c in competitors],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{competitor_id}", response_model=CompetitorResponse)
async def get_competitor(
    competitor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single competitor by ID.
    """
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    competitor = result.scalar_one_or_none()
    
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    return CompetitorResponse.model_validate(competitor)


@router.post("", response_model=CompetitorResponse, status_code=201)
async def create_competitor(
    data: CompetitorCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new competitor.
    """
    # Check for duplicate domain
    if data.domain:
        existing = await db.execute(
            select(Competitor).where(Competitor.domain == data.domain)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=409, 
                detail=f"Competitor with domain '{data.domain}' already exists"
            )
    
    competitor = Competitor(**data.model_dump())
    db.add(competitor)
    await db.flush()
    await db.refresh(competitor)
    
    return CompetitorResponse.model_validate(competitor)


@router.patch("/{competitor_id}", response_model=CompetitorResponse)
async def update_competitor(
    competitor_id: uuid.UUID,
    data: CompetitorUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing competitor.
    """
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    competitor = result.scalar_one_or_none()
    
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(competitor, field, value)
    
    await db.flush()
    await db.refresh(competitor)
    
    return CompetitorResponse.model_validate(competitor)


@router.delete("/{competitor_id}", status_code=204)
async def delete_competitor(
    competitor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a competitor (soft delete by setting status to archived).
    """
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    competitor = result.scalar_one_or_none()
    
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    competitor.status = "archived"
    await db.flush()
    
    return None


@router.post("/{competitor_id}/scrape", status_code=202)
async def trigger_scrape(
    competitor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a scrape job for a specific competitor.
    Returns immediately; scraping happens asynchronously.
    """
    result = await db.execute(
        select(Competitor).where(Competitor.id == competitor_id)
    )
    competitor = result.scalar_one_or_none()
    
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    # TODO: Queue scrape task with Celery
    # from app.tasks.scraping import scrape_competitor
    # scrape_competitor.delay(str(competitor_id))
    
    return {
        "message": "Scrape job queued",
        "competitor_id": str(competitor_id),
        "status": "pending",
    }

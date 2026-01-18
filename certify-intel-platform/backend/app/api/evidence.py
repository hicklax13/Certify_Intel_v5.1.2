"""
Evidence API endpoints.
"""
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Evidence, Competitor
from app.schemas import EvidenceCreate, EvidenceResponse

router = APIRouter()


@router.get("", response_model=List[EvidenceResponse])
async def list_evidence(
    competitor_id: Optional[uuid.UUID] = None,
    source_type: Optional[str] = Query(None, pattern="^(website|news|review|job_posting|sec_filing|social)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    List evidence with optional filtering.
    """
    query = select(Evidence).where(Evidence.status == "active")
    
    if competitor_id:
        query = query.where(Evidence.competitor_id == competitor_id)
    if source_type:
        query = query.where(Evidence.source_type == source_type)
    
    query = query.order_by(Evidence.fetched_at.desc())
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    evidence_list = result.scalars().all()
    
    return [EvidenceResponse.model_validate(e) for e in evidence_list]


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single evidence record by ID.
    """
    result = await db.execute(
        select(Evidence).where(Evidence.id == evidence_id)
    )
    evidence = result.scalar_one_or_none()
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return EvidenceResponse.model_validate(evidence)


@router.get("/{evidence_id}/content")
async def get_evidence_content(
    evidence_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the full content of an evidence record.
    """
    result = await db.execute(
        select(Evidence).where(Evidence.id == evidence_id)
    )
    evidence = result.scalar_one_or_none()
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return {
        "id": str(evidence.id),
        "source_url": evidence.source_url,
        "content_text": evidence.content_text,
        "content_html": evidence.content_html,
        "fetched_at": evidence.fetched_at.isoformat(),
    }

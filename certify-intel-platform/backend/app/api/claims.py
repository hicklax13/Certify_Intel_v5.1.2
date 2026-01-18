"""
Claims API endpoints.
"""
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Claim
from app.schemas import ClaimCreate, ClaimUpdate, ClaimResponse

router = APIRouter()


@router.get("", response_model=List[ClaimResponse])
async def list_claims(
    competitor_id: Optional[uuid.UUID] = None,
    claim_type: Optional[str] = Query(None, pattern="^(pricing|feature|positioning|sentiment|company_health|executive|integration)$"),
    status: Optional[str] = Query(None, pattern="^(active|superseded|review_required|rejected)$"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    List claims with optional filtering.
    """
    query = select(Claim)
    
    if competitor_id:
        query = query.where(Claim.competitor_id == competitor_id)
    if claim_type:
        query = query.where(Claim.claim_type == claim_type)
    if status:
        query = query.where(Claim.status == status)
    else:
        query = query.where(Claim.status == "active")
    if min_confidence is not None:
        query = query.where(Claim.confidence >= min_confidence)
    
    query = query.order_by(Claim.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    claims = result.scalars().all()
    
    return [ClaimResponse.model_validate(c) for c in claims]


@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single claim by ID.
    """
    result = await db.execute(
        select(Claim).where(Claim.id == claim_id)
    )
    claim = result.scalar_one_or_none()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    return ClaimResponse.model_validate(claim)


@router.post("", response_model=ClaimResponse, status_code=201)
async def create_claim(
    data: ClaimCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new claim manually.
    """
    claim = Claim(
        **data.model_dump(),
        extraction_model="manual",
        validated_by="manual",
    )
    db.add(claim)
    await db.flush()
    await db.refresh(claim)
    
    return ClaimResponse.model_validate(claim)


@router.patch("/{claim_id}", response_model=ClaimResponse)
async def update_claim(
    claim_id: uuid.UUID,
    data: ClaimUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a claim (e.g., human validation).
    """
    result = await db.execute(
        select(Claim).where(Claim.id == claim_id)
    )
    claim = result.scalar_one_or_none()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(claim, field, value)
    
    await db.flush()
    await db.refresh(claim)
    
    return ClaimResponse.model_validate(claim)


@router.get("/compare/{claim_type}")
async def compare_claims(
    claim_type: str,
    competitor_ids: Optional[str] = Query(None, description="Comma-separated competitor UUIDs"),
    db: AsyncSession = Depends(get_db),
):
    """
    Compare claims across competitors (e.g., pricing comparison).
    """
    query = select(Claim).where(
        Claim.claim_type == claim_type,
        Claim.status == "active",
    )
    
    if competitor_ids:
        ids = [uuid.UUID(id.strip()) for id in competitor_ids.split(",")]
        query = query.where(Claim.competitor_id.in_(ids))
    
    query = query.order_by(Claim.competitor_id, Claim.confidence.desc())
    
    result = await db.execute(query)
    claims = result.scalars().all()
    
    # Group by competitor
    comparison = {}
    for claim in claims:
        comp_id = str(claim.competitor_id)
        if comp_id not in comparison:
            comparison[comp_id] = []
        comparison[comp_id].append(ClaimResponse.model_validate(claim).model_dump())
    
    return {
        "claim_type": claim_type,
        "comparison": comparison,
        "total_claims": len(claims),
        "competitors_count": len(comparison),
    }

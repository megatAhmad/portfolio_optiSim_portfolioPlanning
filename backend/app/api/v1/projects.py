"""
Projects API Routes

Manages investment opportunities (projects) with CRUD operations,
attributes, metrics, and outcomes.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import structlog

from app.models.base import get_async_session
from app.models.project import Opportunity, OpportunityAttribute, OpportunityMetricTimeSeries, Outcome
from app.schemas.project import (
    OpportunityCreate,
    OpportunityRead,
    OpportunityUpdate,
    OpportunityWithOutcomes,
    OutcomeCreate,
    OutcomeRead,
    OutcomeUpdate,
)

logger = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Opportunities (Projects)
# ---------------------------------------------------------------------------


@router.post("/", response_model=OpportunityRead, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opportunity: OpportunityCreate,
    session: AsyncSession = Depends(get_async_session),
) -> Opportunity:
    """
    Create a new investment opportunity (project).

    - **name**: Unique project name
    - **type**: Project type (EXPLORATION, DEVELOPMENT, PRODUCTION, INFRASTRUCTURE, DECOMMISSIONING, RENEWABLE)
    - **business_unit**: Business unit or region
    - **location**: Geographic location
    - **description**: Optional detailed description
    """
    # Check for duplicate name
    stmt = select(Opportunity).where(Opportunity.name == opportunity.name)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Opportunity with name '{opportunity.name}' already exists",
        )

    db_opportunity = Opportunity(**opportunity.model_dump())
    session.add(db_opportunity)
    await session.commit()
    await session.refresh(db_opportunity)

    logger.info(
        "opportunity_created",
        opportunity_id=str(db_opportunity.id),
        name=db_opportunity.name,
        type=db_opportunity.type,
    )

    return db_opportunity


@router.get("/", response_model=List[OpportunityRead])
async def list_opportunities(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    type: Optional[str] = Query(None, description="Filter by project type"),
    business_unit: Optional[str] = Query(None, description="Filter by business unit"),
    session: AsyncSession = Depends(get_async_session),
) -> List[Opportunity]:
    """
    List all opportunities with optional filtering.

    Supports pagination and filtering by type and business unit.
    """
    stmt = select(Opportunity)

    if type:
        stmt = stmt.where(Opportunity.type == type)
    if business_unit:
        stmt = stmt.where(Opportunity.business_unit == business_unit)

    stmt = stmt.offset(skip).limit(limit).order_by(Opportunity.name)

    result = await session.execute(stmt)
    opportunities = result.scalars().all()

    return list(opportunities)


@router.get("/{opportunity_id}", response_model=OpportunityWithOutcomes)
async def get_opportunity(
    opportunity_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> Opportunity:
    """
    Get a specific opportunity by ID with all outcomes.
    """
    stmt = (
        select(Opportunity)
        .where(Opportunity.id == opportunity_id)
        .options(selectinload(Opportunity.outcomes))
    )

    result = await session.execute(stmt)
    opportunity = result.scalar_one_or_none()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found",
        )

    return opportunity


@router.patch("/{opportunity_id}", response_model=OpportunityRead)
async def update_opportunity(
    opportunity_id: UUID,
    opportunity_update: OpportunityUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> Opportunity:
    """
    Update an existing opportunity (partial update).
    """
    stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
    result = await session.execute(stmt)
    db_opportunity = result.scalar_one_or_none()

    if not db_opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found",
        )

    # Update only provided fields
    update_data = opportunity_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_opportunity, field, value)

    await session.commit()
    await session.refresh(db_opportunity)

    logger.info(
        "opportunity_updated",
        opportunity_id=str(db_opportunity.id),
        updated_fields=list(update_data.keys()),
    )

    return db_opportunity


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Delete an opportunity and all associated data (outcomes, metrics, attributes).

    **Warning**: This is a destructive operation and cannot be undone.
    """
    stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
    result = await session.execute(stmt)
    db_opportunity = result.scalar_one_or_none()

    if not db_opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found",
        )

    await session.delete(db_opportunity)
    await session.commit()

    logger.info("opportunity_deleted", opportunity_id=str(opportunity_id))


# ---------------------------------------------------------------------------
# Outcomes (Probabilistic Scenarios)
# ---------------------------------------------------------------------------


@router.post("/{opportunity_id}/outcomes", response_model=OutcomeRead, status_code=status.HTTP_201_CREATED)
async def create_outcome(
    opportunity_id: UUID,
    outcome: OutcomeCreate,
    session: AsyncSession = Depends(get_async_session),
) -> Outcome:
    """
    Create a new outcome for an opportunity.

    Outcomes represent probabilistic scenarios (e.g., Base, Optimistic, Pessimistic).
    Weights across all outcomes for an opportunity must sum to 1.0.
    """
    # Verify opportunity exists
    stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
    result = await session.execute(stmt)
    opportunity = result.scalar_one_or_none()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found",
        )

    # Create outcome
    db_outcome = Outcome(
        **outcome.model_dump(),
        opportunity_id=opportunity_id,
    )
    session.add(db_outcome)
    await session.commit()
    await session.refresh(db_outcome)

    logger.info(
        "outcome_created",
        outcome_id=str(db_outcome.id),
        opportunity_id=str(opportunity_id),
        weight=db_outcome.weight,
    )

    return db_outcome


@router.get("/{opportunity_id}/outcomes", response_model=List[OutcomeRead])
async def list_outcomes(
    opportunity_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> List[Outcome]:
    """
    List all outcomes for a specific opportunity.
    """
    stmt = (
        select(Outcome)
        .where(Outcome.opportunity_id == opportunity_id)
        .order_by(Outcome.weight.desc())
    )

    result = await session.execute(stmt)
    outcomes = result.scalars().all()

    return list(outcomes)


@router.patch("/{opportunity_id}/outcomes/{outcome_id}", response_model=OutcomeRead)
async def update_outcome(
    opportunity_id: UUID,
    outcome_id: UUID,
    outcome_update: OutcomeUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> Outcome:
    """
    Update an existing outcome.
    """
    stmt = (
        select(Outcome)
        .where(Outcome.id == outcome_id, Outcome.opportunity_id == opportunity_id)
    )
    result = await session.execute(stmt)
    db_outcome = result.scalar_one_or_none()

    if not db_outcome:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outcome {outcome_id} not found for opportunity {opportunity_id}",
        )

    # Update only provided fields
    update_data = outcome_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_outcome, field, value)

    await session.commit()
    await session.refresh(db_outcome)

    logger.info(
        "outcome_updated",
        outcome_id=str(outcome_id),
        updated_fields=list(update_data.keys()),
    )

    return db_outcome


@router.delete("/{opportunity_id}/outcomes/{outcome_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outcome(
    opportunity_id: UUID,
    outcome_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Delete an outcome.
    """
    stmt = (
        select(Outcome)
        .where(Outcome.id == outcome_id, Outcome.opportunity_id == opportunity_id)
    )
    result = await session.execute(stmt)
    db_outcome = result.scalar_one_or_none()

    if not db_outcome:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outcome {outcome_id} not found for opportunity {opportunity_id}",
        )

    await session.delete(db_outcome)
    await session.commit()

    logger.info("outcome_deleted", outcome_id=str(outcome_id))

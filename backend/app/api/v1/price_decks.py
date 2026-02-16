"""
Price Decks and Master Data API Routes

Manages commodity price forecasts and shared parameter sets (Master Data)
that apply to multiple projects via attribute matching.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.base import get_async_session
from app.models.price_deck import PriceDeck, MasterDataSet, MasterDataMetric
from app.schemas.common import PriceDeckCreate, PriceDeckRead, MasterDataSetCreate, MasterDataSetRead

logger = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Price Decks
# ---------------------------------------------------------------------------


@router.post("/", response_model=PriceDeckRead, status_code=status.HTTP_201_CREATED)
async def create_price_deck(
    price_deck: PriceDeckCreate,
    session: AsyncSession = Depends(get_async_session),
) -> PriceDeck:
    """
    Create a new price deck.

    A price deck contains commodity price forecasts over the planning horizon:
    - Oil (Brent, WTI, Dubai)
    - Natural gas (Henry Hub, TTF, JKM)
    - NGL (propane, butane, ethane)
    - Power/electricity
    - Carbon credits

    Multiple price scenarios can be created (Base, High, Low) for sensitivity analysis.
    """
    db_price_deck = PriceDeck(**price_deck.model_dump())
    session.add(db_price_deck)
    await session.commit()
    await session.refresh(db_price_deck)

    logger.info(
        "price_deck_created",
        price_deck_id=str(db_price_deck.id),
        name=db_price_deck.name,
    )

    return db_price_deck


@router.get("/", response_model=List[PriceDeckRead])
async def list_price_decks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_async_session),
) -> List[PriceDeck]:
    """
    List all price decks.
    """
    stmt = select(PriceDeck).offset(skip).limit(limit).order_by(PriceDeck.name)
    result = await session.execute(stmt)
    price_decks = result.scalars().all()

    return list(price_decks)


@router.get("/{price_deck_id}", response_model=PriceDeckRead)
async def get_price_deck(
    price_deck_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> PriceDeck:
    """
    Get a specific price deck by ID.
    """
    stmt = select(PriceDeck).where(PriceDeck.id == price_deck_id)
    result = await session.execute(stmt)
    price_deck = result.scalar_one_or_none()

    if not price_deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Price deck {price_deck_id} not found",
        )

    return price_deck


@router.delete("/{price_deck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_price_deck(
    price_deck_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Delete a price deck.
    """
    stmt = select(PriceDeck).where(PriceDeck.id == price_deck_id)
    result = await session.execute(stmt)
    db_price_deck = result.scalar_one_or_none()

    if not db_price_deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Price deck {price_deck_id} not found",
        )

    await session.delete(db_price_deck)
    await session.commit()

    logger.info("price_deck_deleted", price_deck_id=str(price_deck_id))


# ---------------------------------------------------------------------------
# Master Data Sets
# ---------------------------------------------------------------------------


@router.post("/master-data", response_model=MasterDataSetRead, status_code=status.HTTP_201_CREATED)
async def create_master_data_set(
    master_data: MasterDataSetCreate,
    session: AsyncSession = Depends(get_async_session),
) -> MasterDataSet:
    """
    Create a new Master Data Set.

    Master Data Sets are shared parameter collections that apply to multiple
    projects based on attribute matching. Examples:
    - "Gulf Coast Fiscal Regime" → applies to all projects with region="Gulf Coast"
    - "High Price Scenario" → commodity prices for sensitivity analysis
    - "Aggressive Drilling Schedule" → drilling parameters for development projects
    """
    db_master_data = MasterDataSet(**master_data.model_dump())
    session.add(db_master_data)
    await session.commit()
    await session.refresh(db_master_data)

    logger.info(
        "master_data_set_created",
        master_data_id=str(db_master_data.id),
        name=db_master_data.name,
        category=db_master_data.category,
    )

    return db_master_data


@router.get("/master-data", response_model=List[MasterDataSetRead])
async def list_master_data_sets(
    category: str = Query(None, description="Filter by category"),
    session: AsyncSession = Depends(get_async_session),
) -> List[MasterDataSet]:
    """
    List all Master Data Sets with optional category filtering.
    """
    stmt = select(MasterDataSet)

    if category:
        stmt = stmt.where(MasterDataSet.category == category)

    stmt = stmt.order_by(MasterDataSet.category, MasterDataSet.name)
    result = await session.execute(stmt)
    master_data_sets = result.scalars().all()

    return list(master_data_sets)


@router.delete("/master-data/{master_data_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_master_data_set(
    master_data_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Delete a Master Data Set.
    """
    stmt = select(MasterDataSet).where(MasterDataSet.id == master_data_id)
    result = await session.execute(stmt)
    db_master_data = result.scalar_one_or_none()

    if not db_master_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Master Data Set {master_data_id} not found",
        )

    await session.delete(db_master_data)
    await session.commit()

    logger.info("master_data_set_deleted", master_data_id=str(master_data_id))

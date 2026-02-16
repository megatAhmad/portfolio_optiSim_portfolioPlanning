"""
Scenarios API Routes

Manages optimization scenarios with inputs, results, and lifecycle operations.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import structlog

from app.models.base import get_async_session
from app.models.scenario import Scenario, ScenarioInput, ScenarioResult
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioRead,
    ScenarioUpdate,
    ScenarioWithDetails,
)

logger = structlog.get_logger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------


@router.post("/", response_model=ScenarioRead, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    scenario: ScenarioCreate,
    session: AsyncSession = Depends(get_async_session),
) -> Scenario:
    """
    Create a new optimization scenario.

    A scenario defines:
    - Which projects are considered (universe)
    - Objective function (NPV, IRR, production, emissions, custom)
    - Constraints (CAPEX limits, production targets, resource constraints)
    - Planning horizon and time periods
    - Solver settings (solver type, time limit, MIP gap)
    """
    db_scenario = Scenario(**scenario.model_dump())
    session.add(db_scenario)
    await session.commit()
    await session.refresh(db_scenario)

    logger.info(
        "scenario_created",
        scenario_id=str(db_scenario.id),
        name=db_scenario.name,
        objective=db_scenario.objective_function,
    )

    return db_scenario


@router.get("/", response_model=List[ScenarioRead])
async def list_scenarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by status"),
    session: AsyncSession = Depends(get_async_session),
) -> List[Scenario]:
    """
    List all scenarios with optional filtering.

    Statuses:
    - DRAFT: Being configured
    - QUEUED: Submitted for optimization
    - RUNNING: Currently optimizing
    - COMPLETED: Successfully optimized
    - FAILED: Optimization failed
    - CANCELLED: User cancelled
    """
    stmt = select(Scenario)

    if status:
        stmt = stmt.where(Scenario.status == status)

    stmt = stmt.offset(skip).limit(limit).order_by(Scenario.created_at.desc())

    result = await session.execute(stmt)
    scenarios = result.scalars().all()

    return list(scenarios)


@router.get("/{scenario_id}", response_model=ScenarioWithDetails)
async def get_scenario(
    scenario_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> Scenario:
    """
    Get a specific scenario with inputs and results.
    """
    stmt = (
        select(Scenario)
        .where(Scenario.id == scenario_id)
        .options(
            selectinload(Scenario.inputs),
            selectinload(Scenario.results),
        )
    )

    result = await session.execute(stmt)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found",
        )

    return scenario


@router.patch("/{scenario_id}", response_model=ScenarioRead)
async def update_scenario(
    scenario_id: UUID,
    scenario_update: ScenarioUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> Scenario:
    """
    Update an existing scenario.

    Only DRAFT scenarios can be updated. To modify a COMPLETED scenario,
    clone it first.
    """
    stmt = select(Scenario).where(Scenario.id == scenario_id)
    result = await session.execute(stmt)
    db_scenario = result.scalar_one_or_none()

    if not db_scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found",
        )

    if db_scenario.status not in ["DRAFT", "FAILED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update scenario in {db_scenario.status} status. Only DRAFT or FAILED scenarios can be updated.",
        )

    # Update only provided fields
    update_data = scenario_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_scenario, field, value)

    await session.commit()
    await session.refresh(db_scenario)

    logger.info(
        "scenario_updated",
        scenario_id=str(scenario_id),
        updated_fields=list(update_data.keys()),
    )

    return db_scenario


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    scenario_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Delete a scenario and all associated results.

    **Warning**: This is a destructive operation and cannot be undone.
    """
    stmt = select(Scenario).where(Scenario.id == scenario_id)
    result = await session.execute(stmt)
    db_scenario = result.scalar_one_or_none()

    if not db_scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found",
        )

    if db_scenario.status == "RUNNING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a running scenario. Cancel it first.",
        )

    await session.delete(db_scenario)
    await session.commit()

    logger.info("scenario_deleted", scenario_id=str(scenario_id))


# ---------------------------------------------------------------------------
# Scenario Lifecycle Operations
# ---------------------------------------------------------------------------


@router.post("/{scenario_id}/clone", response_model=ScenarioRead, status_code=status.HTTP_201_CREATED)
async def clone_scenario(
    scenario_id: UUID,
    new_name: str = Query(..., description="Name for the cloned scenario"),
    session: AsyncSession = Depends(get_async_session),
) -> Scenario:
    """
    Clone an existing scenario with a new name.

    Copies all inputs and configuration, but not results.
    Useful for sensitivity analysis and what-if scenarios.
    """
    stmt = (
        select(Scenario)
        .where(Scenario.id == scenario_id)
        .options(selectinload(Scenario.inputs))
    )
    result = await session.execute(stmt)
    source_scenario = result.scalar_one_or_none()

    if not source_scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found",
        )

    # Create new scenario with copied data
    new_scenario = Scenario(
        name=new_name,
        description=f"Cloned from: {source_scenario.name}",
        objective_function=source_scenario.objective_function,
        planning_horizon_years=source_scenario.planning_horizon_years,
        discount_rate=source_scenario.discount_rate,
        optimization_method=source_scenario.optimization_method,
        optimization_settings=source_scenario.optimization_settings,
        status="DRAFT",
    )

    session.add(new_scenario)
    await session.flush()

    # Copy inputs
    for inp in source_scenario.inputs:
        new_input = ScenarioInput(
            scenario_id=new_scenario.id,
            input_type=inp.input_type,
            input_data=inp.input_data,
        )
        session.add(new_input)

    await session.commit()
    await session.refresh(new_scenario)

    logger.info(
        "scenario_cloned",
        source_id=str(scenario_id),
        new_id=str(new_scenario.id),
        new_name=new_name,
    )

    return new_scenario


@router.post("/{scenario_id}/cancel", response_model=ScenarioRead)
async def cancel_scenario(
    scenario_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> Scenario:
    """
    Cancel a running or queued optimization.

    This will signal the Celery task to terminate.
    """
    stmt = select(Scenario).where(Scenario.id == scenario_id)
    result = await session.execute(stmt)
    db_scenario = result.scalar_one_or_none()

    if not db_scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found",
        )

    if db_scenario.status not in ["QUEUED", "RUNNING"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel scenario in {db_scenario.status} status",
        )

    # TODO: Send cancellation signal to Celery task
    # from app.tasks.optimization_tasks import cancel_optimization
    # cancel_optimization.apply_async(args=[str(scenario_id)])

    db_scenario.status = "CANCELLED"
    await session.commit()
    await session.refresh(db_scenario)

    logger.info("scenario_cancelled", scenario_id=str(scenario_id))

    return db_scenario

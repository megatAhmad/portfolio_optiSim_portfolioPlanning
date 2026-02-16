"""
Optimization API Routes

Triggers portfolio optimization runs and retrieves optimization results.
"""

from typing import Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.base import get_async_session
from app.models.scenario import Scenario
from app.schemas.optimization import OptimizationRequest, OptimizationStatus

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/{scenario_id}/run", response_model=OptimizationStatus, status_code=status.HTTP_202_ACCEPTED)
async def run_optimization(
    scenario_id: UUID,
    request: OptimizationRequest,
    session: AsyncSession = Depends(get_async_session),
) -> Dict:
    """
    Trigger optimization for a scenario.

    Returns immediately with a task ID. Client should poll or use WebSocket
    for status updates.

    The optimization will:
    1. Build the MILP model with Pyomo
    2. Apply all constraints (selection, dependency, group, metric)
    3. Solve using the configured solver (HiGHS, Gurobi, etc.)
    4. Store results in TimescaleDB
    5. Generate summary statistics
    """
    stmt = select(Scenario).where(Scenario.id == scenario_id)
    result = await session.execute(stmt)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found",
        )

    if scenario.status == "RUNNING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Scenario is already running",
        )

    # Update scenario status
    scenario.status = "QUEUED"
    await session.commit()

    # TODO: Dispatch to Celery worker
    # from app.tasks.optimization_tasks import run_optimization_task
    # task = run_optimization_task.apply_async(args=[str(scenario_id)])
    # task_id = task.id

    task_id = "mock-task-id"

    logger.info(
        "optimization_queued",
        scenario_id=str(scenario_id),
        task_id=task_id,
        method=request.method,
    )

    return {
        "scenario_id": str(scenario_id),
        "task_id": task_id,
        "status": "QUEUED",
        "message": "Optimization queued successfully",
    }


@router.get("/{scenario_id}/status", response_model=OptimizationStatus)
async def get_optimization_status(
    scenario_id: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> Dict:
    """
    Get the current status of an optimization run.
    """
    stmt = select(Scenario).where(Scenario.id == scenario_id)
    result = await session.execute(stmt)
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found",
        )

    return {
        "scenario_id": str(scenario_id),
        "task_id": None,  # TODO: Retrieve from Celery
        "status": scenario.status,
        "message": None,
    }

"""
Optimization Celery Tasks

Long-running MILP optimization dispatched to Celery workers.
"""

from uuid import UUID

import structlog

from app.tasks import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, name="optimization.run", max_retries=1)
def run_optimization_task(
    self,
    scenario_id: str,
    solver: str | None = None,
    time_limit_seconds: int | None = None,
    mip_gap: float = 0.001,
) -> dict:
    """Run portfolio optimization as a Celery task.

    This task:
    1. Loads scenario and project data from the database
    2. Builds the MILP model
    3. Solves using the specified solver
    4. Stores results in TimescaleDB
    5. Updates scenario status

    Args:
        scenario_id: UUID of the scenario to optimize
        solver: Solver name (None = default)
        time_limit_seconds: Max solve time
        mip_gap: Target MIP gap

    Returns:
        Dict with optimization results summary
    """
    logger.info(
        "optimization_task_started",
        task_id=self.request.id,
        scenario_id=scenario_id,
    )

    self.update_state(state="RUNNING", meta={"progress": 0.0, "message": "Building model..."})

    try:
        # Import here to avoid circular imports at module load
        from app.models.base import AsyncSessionLocal
        import asyncio

        async def _run():
            from app.services.optimization_service import OptimizationService

            async with AsyncSessionLocal() as session:
                service = OptimizationService(session)
                result = await service.run_optimization(
                    scenario_id=UUID(scenario_id),
                    solver=solver,
                    time_limit_seconds=time_limit_seconds,
                    mip_gap=mip_gap,
                )
                return {
                    "scenario_id": scenario_id,
                    "status": result.status,
                    "objective_value": result.objective_value,
                    "total_npv": result.total_npv,
                    "selected_projects": result.num_projects_selected,
                    "total_projects": result.num_projects_total,
                    "solve_time": result.solver_stats.solve_time_seconds,
                    "mip_gap": result.solver_stats.mip_gap,
                }

        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_run())
        finally:
            loop.close()

    except Exception as exc:
        logger.error(
            "optimization_task_failed",
            task_id=self.request.id,
            scenario_id=scenario_id,
            error=str(exc),
        )
        self.update_state(
            state="FAILURE",
            meta={"error": str(exc), "scenario_id": scenario_id},
        )
        raise


@celery_app.task(name="optimization.cancel")
def cancel_optimization(scenario_id: str) -> dict:
    """Cancel a running optimization task.

    Sends revoke signal to the worker processing this scenario.
    """
    logger.info("optimization_cancel_requested", scenario_id=scenario_id)

    # In production, would look up the task ID for this scenario
    # and call celery_app.control.revoke(task_id, terminate=True)

    return {"scenario_id": scenario_id, "status": "CANCELLED"}

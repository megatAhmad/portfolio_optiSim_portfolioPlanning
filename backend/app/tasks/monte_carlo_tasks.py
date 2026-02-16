"""
Monte Carlo Simulation Celery Tasks

Long-running Monte Carlo simulations dispatched to Celery workers.
"""

import structlog

from app.tasks import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, name="analytics.monte_carlo", max_retries=1)
def run_monte_carlo_task(
    self,
    scenario_id: str,
    num_simulations: int = 1000,
    seed: int | None = None,
) -> dict:
    """Run Monte Carlo simulation as a Celery task.

    Args:
        scenario_id: UUID of the scenario
        num_simulations: Number of simulation iterations
        seed: Random seed for reproducibility

    Returns:
        Dict with simulation results summary
    """
    logger.info(
        "monte_carlo_task_started",
        task_id=self.request.id,
        scenario_id=scenario_id,
        num_simulations=num_simulations,
    )

    self.update_state(state="RUNNING", meta={"progress": 0.0})

    try:
        from app.services.analytics_service import AnalyticsService

        service = AnalyticsService()

        # TODO: Load actual project NPVs and uncertainties from scenario results
        result = service.run_monte_carlo(
            base_npv=0.0,
            project_npvs={},
            uncertainties={},
            num_simulations=num_simulations,
            seed=seed,
        )

        return {
            "scenario_id": scenario_id,
            "num_simulations": result.num_simulations,
            "mean_npv": result.mean_npv,
            "std_npv": result.std_npv,
            "p10": result.p10,
            "p50": result.p50,
            "p90": result.p90,
            "prob_positive": result.prob_positive,
        }

    except Exception as exc:
        logger.error(
            "monte_carlo_task_failed",
            task_id=self.request.id,
            scenario_id=scenario_id,
            error=str(exc),
        )
        raise

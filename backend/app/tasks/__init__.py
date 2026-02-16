"""Celery async task modules.

Long-running operations dispatched to Celery workers:
- optimization_tasks: MILP optimization runs
- monte_carlo_tasks: Monte Carlo simulations
- report_tasks: Excel, PowerPoint, PDF report generation
"""

from celery import Celery

from app.config import settings

# Create Celery app
celery_app = Celery(
    "portfolio_optisim",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=1800,  # 30 min soft limit
    worker_prefetch_multiplier=1,  # Fair distribution for long tasks
    task_acks_late=True,  # Acknowledge after completion (reliability)
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])

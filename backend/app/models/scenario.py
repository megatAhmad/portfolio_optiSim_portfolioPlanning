"""ORM models for scenarios and scenario comparisons."""

from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseModel


class Scenario(BaseModel, Base):
    """
    A portfolio optimisation scenario containing inputs, configuration, and results.

    Maps to the ``scenarios`` table.

    Lifecycle: draft -> running -> completed | failed

    The ``inputs`` JSONB column stores the full scenario configuration:
    ``{price_deck_id, constraints, objective, project_availability,
    optimization_settings (including solver field)}``.

    The ``results`` JSONB column stores the optimisation output once complete:
    ``{optimal_portfolio, solver_stats, temporal_results}``.
    """

    __tablename__ = "scenarios"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="User ID or email of the scenario creator",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        server_default="draft",
        nullable=False,
        comment="draft, running, completed, failed",
    )
    inputs: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment=(
            "Scenario configuration: price_deck_id, constraints, objective, "
            "project_availability, optimization_settings (solver, time_limit, "
            "mip_gap, use_hybrid_optimization, temporal_aggregation, "
            "lazy_constraints)"
        ),
    )
    results: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment=(
            "Optimisation results: optimal_portfolio (selected_projects, "
            "objective_value, metrics), solver_stats, temporal_results"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Scenario(id={self.id!r}, name={self.name!r}, "
            f"status={self.status!r})>"
        )


class ScenarioComparison(BaseModel, Base):
    """
    A named set of scenarios grouped together for side-by-side comparison.

    Maps to the ``scenario_comparisons`` table.

    The ``scenario_ids`` JSONB column stores a list of scenario UUIDs to compare.
    """

    __tablename__ = "scenario_comparisons"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scenario_ids: Mapped[Optional[list[Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of scenario UUIDs to compare",
    )

    def __repr__(self) -> str:
        return (
            f"<ScenarioComparison(id={self.id!r}, name={self.name!r})>"
        )

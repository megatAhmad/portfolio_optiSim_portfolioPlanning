"""ORM model for optimisation results stored in a TimescaleDB hypertable."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Integer, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class OptimizationResult(Base):
    """
    Per-(scenario, opportunity, year) optimisation output row.

    Maps to the ``optimization_results`` **TimescaleDB hypertable**.

    This table stores the full time-series output of an optimisation run.
    Dashboard queries use continuous aggregates built on top of this table
    for fast retrieval (e.g. total CAPEX / revenue / production per scenario
    per year).

    Composite primary key: ``(scenario_id, opportunity_id, year)``.

    Indexes (defined in migration, not on the ORM model):
      - ``idx_scenario_project_year ON (scenario_id, opportunity_id, year)``
      - ``idx_scenario_selected ON (scenario_id, is_selected)``
    """

    __tablename__ = "optimization_results"

    # ------------------------------------------------------------------
    # Composite primary key
    # ------------------------------------------------------------------
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )
    year: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Selection metadata
    # ------------------------------------------------------------------
    is_selected: Mapped[Optional[bool]] = mapped_column(nullable=True)
    start_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    working_interest: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 4),
        nullable=True,
    )
    instances: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ------------------------------------------------------------------
    # Financial metrics
    # ------------------------------------------------------------------
    revenue: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False,
    )
    opex: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False,
    )
    capex: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False,
    )
    production: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=Decimal("0"),
        server_default="0",
        nullable=False,
    )
    cashflow: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )
    emissions: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Timestamp
    # ------------------------------------------------------------------
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<OptimizationResult("
            f"scenario_id={self.scenario_id!r}, "
            f"opportunity_id={self.opportunity_id!r}, "
            f"year={self.year!r}, "
            f"is_selected={self.is_selected!r})>"
        )

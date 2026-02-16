"""ORM model for metric expressions (PlanningSpace-compatible formula system)."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseModel


class MetricExpression(BaseModel, Base):
    """
    A computed metric definition with PlanningSpace-compatible formula syntax.

    Maps to the ``metric_expressions`` table.

    Each expression defines how a metric is evaluated across the planning horizon:
      - ``formula_fyf`` — First Year Formula (t=0; cannot reference prior time)
      - ``formula_pt``  — Prior Time reference expression (value at t-1)
      - ``formula_ct``  — Current Time formula (t>0; may reference PT and current metrics)
      - ``formula_total`` — Aggregation formula across all years (e.g. SUM)
      - ``formula_total_disc`` — Discounted aggregation (NPV calculation)

    The ``level`` column controls aggregation scope:
      - ``'O'`` — Outcome level
      - ``'P'`` — Project / Opportunity level
      - ``'S'`` — Scenario level (portfolio-wide)

    The ``dependencies`` JSONB column stores an auto-extracted list of metric names
    referenced by this expression's formulas, used for topological sort evaluation.

    Built-in functions supported in formulas:
      Total(), TotalDisc(), IF(), MAX(), MIN(), SUM(), GetCumulative()
    """

    __tablename__ = "metric_expressions"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    metric_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Input, Computed, or Master Data",
    )
    metric_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Formula columns — PlanningSpace FYF / PT / CT pattern
    formula_fyf: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="First Year Formula — evaluated at t=0 only",
    )
    formula_pt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Prior Time expression — provides the value at t-1 for CT formulas",
    )
    formula_ct: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Current Time formula — evaluated at t>0; may reference PT",
    )
    formula_total: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Total aggregation formula across all time periods",
    )
    formula_total_disc: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Discounted total aggregation formula (NPV-style)",
    )

    # Aggregation level
    level: Mapped[str] = mapped_column(
        String(1),
        default="S",
        server_default="S",
        nullable=False,
        comment="Aggregation level: O=Outcome, P=Project, S=Scenario",
    )

    # Filtering
    attribute_filter: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Filter expression on opportunity attributes",
    )
    characteristic_filter: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Filter expression on opportunity characteristics",
    )

    # Flags
    is_fixture: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="True if this expression references Master Data via fixture linkage",
    )
    is_indicator: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="True if this metric is a display-only indicator (not used in optimization)",
    )
    is_hidden: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="True if this metric should be hidden from default views",
    )
    scale_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Metric name to scale results by (e.g. working interest)",
    )

    # Dependency tracking (auto-extracted from formulas)
    dependencies: Mapped[Optional[list[Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of metric names referenced in formulas (for topological sort)",
    )

    def __repr__(self) -> str:
        return (
            f"<MetricExpression(id={self.id!r}, "
            f"metric_name={self.metric_name!r}, "
            f"metric_type={self.metric_type!r}, "
            f"level={self.level!r})>"
        )

"""ORM models for selection constraints and metric constraints."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel

if TYPE_CHECKING:
    from app.models.project import Opportunity


class SelectionConstraint(BaseModel, Base):
    """
    Per-opportunity selection rules governing how a project may enter the portfolio.

    Maps to the ``selection_constraints`` table.

    Controls:
      - Integer vs. continuous selection (``is_integer``)
      - Working interest bounds (``total_wi_min`` / ``total_wi_max``)
      - Instance limits (``total_instances_min`` / ``total_instances_max``)
      - Year-by-year timing windows (``yearly_constraints`` JSONB)
    """

    __tablename__ = "selection_constraints"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_integer: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    total_wi_min: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        default=Decimal("0"),
        server_default="0",
        nullable=False,
        comment="Minimum total working interest (0.0 to 1.0+)",
    )
    total_wi_max: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        default=Decimal("1"),
        server_default="1",
        nullable=False,
        comment="Maximum total working interest (0.0 to 1.0+)",
    )
    total_instances_min: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )
    total_instances_max: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
        nullable=False,
    )
    yearly_constraints: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="[{year: int, min: int, max: int}, ...] — per-year timing windows",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    opportunity: Mapped[Opportunity] = relationship(
        "Opportunity",
        back_populates="selection_constraints",
    )

    def __repr__(self) -> str:
        return (
            f"<SelectionConstraint(id={self.id!r}, "
            f"opportunity_id={self.opportunity_id!r}, "
            f"is_integer={self.is_integer!r})>"
        )


class MetricConstraint(BaseModel, Base):
    """
    Portfolio-level limit on any computed metric.

    Maps to the ``metric_constraints`` table.

    Supports both hard enforcement (infeasible if violated) and soft enforcement
    (penalty added to objective via slack variables).

    Examples:
      - Annual CAPEX <= $1B (hard, Max)
      - Production >= 397,000 boe/d (soft, Min, penalty_weight=10.0)
      - Cumulative emissions <= 50 Mt CO2e (hard, Max)
    """

    __tablename__ = "metric_constraints"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_enforced: Mapped[bool] = mapped_column(default=True, nullable=False)
    constraint_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Min, Max, Range, Equal",
    )
    is_soft: Mapped[bool] = mapped_column(default=False, nullable=False)
    penalty_weight: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Weight applied to slack variable in objective (soft constraints only)",
    )
    penalty_magnitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        nullable=True,
        comment="Normalisation magnitude for the penalty term (soft constraints only)",
    )
    default_limit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2),
        nullable=True,
        comment="Default constraint limit applied to all years unless overridden",
    )
    yearly_limits: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment='Per-year limit overrides, e.g. {"0": 1000, "1": 1000, ...}',
    )

    def __repr__(self) -> str:
        return (
            f"<MetricConstraint(id={self.id!r}, "
            f"metric_name={self.metric_name!r}, "
            f"constraint_type={self.constraint_type!r}, "
            f"is_soft={self.is_soft!r})>"
        )

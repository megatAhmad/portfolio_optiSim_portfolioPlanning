"""ORM models for projects (opportunities), outcomes, and input metrics."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel

if TYPE_CHECKING:
    from app.models.constraint import SelectionConstraint
    from app.models.dependency import GroupMember


class Opportunity(BaseModel, Base):
    """
    An investment project / asset (PlanningSpace "Opportunity").

    Maps to the ``opportunities`` table.
    Examples: upstream oil field, gas development, solar farm, decommissioning project.
    """

    __tablename__ = "opportunities"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="upstream_oil, upstream_gas, midstream, renewable_solar, "
        "renewable_wind, decommissioning, etc.",
    )
    business_unit: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    location_lat: Mapped[Optional[float]] = mapped_column(nullable=True)
    location_lon: Mapped[Optional[float]] = mapped_column(nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    outcomes: Mapped[list[Outcome]] = relationship(
        "Outcome",
        back_populates="opportunity",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    metrics: Mapped[list[OpportunityMetric]] = relationship(
        "OpportunityMetric",
        back_populates="opportunity",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    attributes: Mapped[Optional[OpportunityAttribute]] = relationship(
        "OpportunityAttribute",
        back_populates="opportunity",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    selection_constraints: Mapped[list[SelectionConstraint]] = relationship(
        "SelectionConstraint",
        back_populates="opportunity",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    group_memberships: Mapped[list[GroupMember]] = relationship(
        "GroupMember",
        back_populates="opportunity",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Opportunity(id={self.id!r}, name={self.name!r}, type={self.type!r})>"


class Outcome(BaseModel, Base):
    """
    A probabilistic scenario for an opportunity (e.g. Base / Optimistic / Pessimistic).

    Maps to the ``outcomes`` table.
    Outcome weights within a single opportunity must sum to 1.0.
    """

    __tablename__ = "outcomes"
    __table_args__ = (
        CheckConstraint(
            "probability >= 0 AND probability <= 1",
            name="valid_probability",
        ),
    )

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Base, Optimistic, Pessimistic",
    )
    probability: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
        comment="0.0000 to 1.0000 — weights per opportunity must sum to 1.0",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    opportunity: Mapped[Opportunity] = relationship(
        "Opportunity",
        back_populates="outcomes",
    )
    metrics: Mapped[list[OpportunityMetric]] = relationship(
        "OpportunityMetric",
        back_populates="outcome",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Outcome(id={self.id!r}, name={self.name!r}, "
            f"probability={self.probability!r})>"
        )


class OpportunityMetric(BaseModel, Base):
    """
    Input time-series data for a given opportunity-outcome-metric combination.

    Maps to the ``opportunity_metrics`` table.
    The ``time_series_data`` column stores a JSONB list of ``{year: int, value: float}``
    entries (PlanningSpace wide-format rows are normalised into this long format on import).
    """

    __tablename__ = "opportunity_metrics"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
    )
    outcome_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("outcomes.id", ondelete="CASCADE"),
        nullable=False,
    )
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    time_series_data: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        comment='[{year: int, value: float}, ...]',
    )
    imported_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    opportunity: Mapped[Opportunity] = relationship(
        "Opportunity",
        back_populates="metrics",
    )
    outcome: Mapped[Outcome] = relationship(
        "Outcome",
        back_populates="metrics",
    )

    def __repr__(self) -> str:
        return (
            f"<OpportunityMetric(id={self.id!r}, metric_name={self.metric_name!r})>"
        )


class OpportunityAttribute(Base):
    """
    Flexible attribute system for categorising opportunities.

    Maps to the ``opportunity_attributes`` table.
    Supports PlanningSpace "fixture" records (Master Data assignment), standard
    petroleum attributes, and arbitrary custom key-value attributes.
    """

    __tablename__ = "opportunity_attributes"

    # ------------------------------------------------------------------
    # Columns — single-row-per-opportunity (PK is the FK)
    # ------------------------------------------------------------------
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    is_fixture: Mapped[bool] = mapped_column(default=False, nullable=False)
    area: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    onshore_offshore: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )
    reserve_category: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )
    business_unit: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    price_scenario: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    custom_attributes: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    hierarchy: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    opportunity: Mapped[Opportunity] = relationship(
        "Opportunity",
        back_populates="attributes",
    )

    def __repr__(self) -> str:
        return (
            f"<OpportunityAttribute(opportunity_id={self.opportunity_id!r}, "
            f"is_fixture={self.is_fixture!r})>"
        )

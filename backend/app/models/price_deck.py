"""ORM models for Master Data Sets and Master Data Metrics (price decks, tolls, taxes)."""

from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel


class MasterDataSet(BaseModel, Base):
    """
    A named set of shared time-series parameters applied to multiple opportunities
    via attribute-based matching.

    Maps to the ``master_data_sets`` table.

    Examples:
      - "High Price" price deck (category=price_scenario, applicable_to_value=High)
      - "North Tolls" toll schedule (category=toll_scenario, applicable_to_value=North)

    Opportunities are linked to a Master Data Set when their corresponding
    attribute value matches ``applicable_to_value`` for the given
    ``applicable_to_attribute``.
    """

    __tablename__ = "master_data_sets"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="price_scenario, toll_scenario, tax_scenario",
    )
    applicable_to_attribute: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Attribute name used for matching (e.g. price_scenario)",
    )
    applicable_to_value: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Attribute value used for matching (e.g. High, Base, Low)",
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    metrics: Mapped[list[MasterDataMetric]] = relationship(
        "MasterDataMetric",
        back_populates="master_data_set",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<MasterDataSet(id={self.id!r}, name={self.name!r}, "
            f"category={self.category!r})>"
        )


class MasterDataMetric(BaseModel, Base):
    """
    A single time-series metric within a Master Data Set.

    Maps to the ``master_data_metrics`` table.

    The ``time_series_data`` JSONB column stores yearly values, e.g.:
    ``[{year: 0, value: 75.0}, {year: 1, value: 78.5}, ...]``

    For stochastic Master Data, ``is_stochastic=True`` and
    ``distribution_params`` contains distribution specification
    (e.g. ``{type: "gbm", mu: 0.02, sigma: 0.15}``).
    """

    __tablename__ = "master_data_metrics"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    master_data_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("master_data_sets.id", ondelete="CASCADE"),
        nullable=False,
    )
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    time_series_data: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="[{year: int, value: float}, ...]",
    )
    is_stochastic: Mapped[bool] = mapped_column(default=False, nullable=False)
    distribution_params: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Distribution parameters for stochastic metrics, e.g. {type, mu, sigma}",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    master_data_set: Mapped[MasterDataSet] = relationship(
        "MasterDataSet",
        back_populates="metrics",
    )

    def __repr__(self) -> str:
        return (
            f"<MasterDataMetric(id={self.id!r}, "
            f"metric_name={self.metric_name!r})>"
        )

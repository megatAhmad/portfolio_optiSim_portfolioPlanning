"""ORM models for project interdependencies, selection groups, and group members."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel

if TYPE_CHECKING:
    from app.models.project import Opportunity


class SelectionDependency(BaseModel, Base):
    """
    A directed dependency between two opportunities.

    Maps to the ``selection_dependencies`` table.

    Examples:
      - "Project A *Must* start *Before* Project B with a 2-year offset"
      - "Project C *Must Not* coexist with Project D" (mutual exclusivity)

    Converted to Pyomo MILP constraints during optimization via
    ``constraint_generators.py``.
    """

    __tablename__ = "selection_dependencies"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    independent_opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
    )
    dependent_opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
    )
    must_or_must_not: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Must or Must Not",
    )
    time_offset: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Time offset in years between independent and dependent opportunity",
    )
    timing_relation: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Before, After, or During",
    )
    need_instances: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="Instance ratio numerator (e.g. 'N' in N:M ratio)",
    )
    each_instances: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="Instance ratio denominator (e.g. 'M' in N:M ratio)",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    independent_opportunity: Mapped[Opportunity] = relationship(
        "Opportunity",
        foreign_keys=[independent_opportunity_id],
        lazy="selectin",
    )
    dependent_opportunity: Mapped[Opportunity] = relationship(
        "Opportunity",
        foreign_keys=[dependent_opportunity_id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<SelectionDependency(id={self.id!r}, "
            f"{self.independent_opportunity_id!r} "
            f"{self.must_or_must_not!r} "
            f"{self.dependent_opportunity_id!r})>"
        )


class SelectionGroup(BaseModel, Base):
    """
    A named group of opportunities with collective selection constraints.

    Maps to the ``selection_groups`` table.

    Group types:
      - **Exclusive** — at most 1 member can be selected
      - **Inclusive** — all or nothing (select all members or none)
      - **AtLeastN** — at least N members must be selected
      - **AtMostN** — at most N members can be selected
      - **ExactlyN** — exactly N members must be selected
    """

    __tablename__ = "selection_groups"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    group_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Exclusive, Inclusive, AtLeastN, AtMostN, ExactlyN",
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    total_instances_min: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    total_instances_max: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    yearly_constraints: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="[{year: int, min: int, max: int}, ...]",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    members: Mapped[list[GroupMember]] = relationship(
        "GroupMember",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<SelectionGroup(id={self.id!r}, name={self.name!r}, "
            f"group_type={self.group_type!r})>"
        )


class GroupMember(Base):
    """
    M:N join between ``SelectionGroup`` and ``Opportunity``.

    Maps to the ``group_members`` table.
    Composite primary key: ``(group_id, opportunity_id)``.
    """

    __tablename__ = "group_members"

    # ------------------------------------------------------------------
    # Columns (composite PK)
    # ------------------------------------------------------------------
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("selection_groups.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    is_disabled: Mapped[bool] = mapped_column(default=False, nullable=False)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    group: Mapped[SelectionGroup] = relationship(
        "SelectionGroup",
        back_populates="members",
    )
    opportunity: Mapped[Opportunity] = relationship(
        "Opportunity",
        back_populates="group_memberships",
    )

    def __repr__(self) -> str:
        return (
            f"<GroupMember(group_id={self.group_id!r}, "
            f"opportunity_id={self.opportunity_id!r})>"
        )

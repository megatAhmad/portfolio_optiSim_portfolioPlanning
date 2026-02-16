"""ORM model for platform users."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseModel


class User(BaseModel, Base):
    """
    A platform user with role-based access control.

    Maps to the ``users`` table.

    Roles:
      - **admin** — full system access, user management
      - **manager** — create/approve scenarios, manage projects
      - **analyst** — create/run scenarios, view all data (default)
      - **viewer** — read-only access to dashboards and reports

    Authentication supports both local password auth (``hashed_password``)
    and SSO via SAML 2.0 (``sso_provider`` + ``sso_id``).
    """

    __tablename__ = "users"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20),
        default="analyst",
        server_default="analyst",
        nullable=False,
        comment="admin, manager, analyst, viewer",
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Local authentication
    hashed_password: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # SSO authentication (SAML 2.0 — Okta, Azure AD)
    sso_provider: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="SSO provider name (e.g. okta, azure_ad)",
    )
    sso_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="External SSO identifier",
    )

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id!r}, email={self.email!r}, "
            f"role={self.role!r})>"
        )

"""Application configuration via pydantic-settings.

All settings are loaded from environment variables (or a .env file).
Defaults are provided for local development; production deployments
must override via environment variables or secrets management.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SolverChoice(str, Enum):
    """Supported MILP solvers.

    Open-source solvers are available out of the box.
    Commercial solvers require separate license installation.
    """

    HIGHS = "highs"
    GLPK = "glpk"
    CBC = "cbc"
    GUROBI = "gurobi"
    CPLEX = "cplex"
    ORTOOLS = "ortools"


class LogLevel(str, Enum):
    """Supported log levels for structlog."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All fields use UPPER_SNAKE_CASE env var names by default.
    Prefix: none (bare env var names). Override with env_prefix if needed.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    APP_NAME: str = "Portfolio OptiSim"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: LogLevel = LogLevel.INFO

    # -------------------------------------------------------------------------
    # API
    # -------------------------------------------------------------------------
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins. Set to ['*'] only in development.",
    )

    # -------------------------------------------------------------------------
    # Security
    # -------------------------------------------------------------------------
    SECRET_KEY: str = Field(
        default="CHANGE-ME-in-production-use-openssl-rand-hex-64",
        description="Secret key for JWT signing. Must be overridden in production.",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # -------------------------------------------------------------------------
    # Database (PostgreSQL + TimescaleDB)
    # -------------------------------------------------------------------------
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "portfolio"
    DATABASE_PASSWORD: str = "portfolio"
    DATABASE_NAME: str = "portfolio_optisim"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> str:
        """Async database URL for SQLAlchemy (asyncpg driver)."""
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for Alembic migrations (psycopg2 driver)."""
        return (
            f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    DATABASE_POOL_SIZE: int = Field(default=20, ge=1, le=100)
    DATABASE_MAX_OVERFLOW: int = Field(default=10, ge=0, le=50)
    DATABASE_POOL_TIMEOUT: int = Field(default=30, ge=5)
    DATABASE_ECHO: bool = False

    # -------------------------------------------------------------------------
    # Redis
    # -------------------------------------------------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = Field(default=20, ge=1)

    # -------------------------------------------------------------------------
    # Celery Task Queue
    # -------------------------------------------------------------------------
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_SOFT_TIME_LIMIT: int = Field(
        default=1800,
        description="Soft time limit for Celery tasks in seconds (30 min).",
    )
    CELERY_TASK_HARD_TIME_LIMIT: int = Field(
        default=3600,
        description="Hard time limit for Celery tasks in seconds (60 min).",
    )

    # -------------------------------------------------------------------------
    # Optimization Engine
    # -------------------------------------------------------------------------
    DEFAULT_SOLVER: SolverChoice = Field(
        default=SolverChoice.HIGHS,
        description=(
            "Default MILP solver. Users can override per scenario. "
            "Options: highs (recommended), glpk, cbc, gurobi, cplex, ortools."
        ),
    )
    MIP_GAP: float = Field(
        default=0.001,
        ge=0.0,
        le=1.0,
        description="MIP optimality gap tolerance (0.001 = 0.1% = 99.9% optimal).",
    )
    MAX_SOLVE_TIME_SECONDS: int = Field(
        default=300,
        ge=10,
        le=86400,
        description="Maximum solver wall-clock time in seconds (default 5 min).",
    )
    PLANNING_HORIZON: int = Field(
        default=30,
        ge=1,
        le=50,
        description="Planning horizon in years for portfolio optimization.",
    )
    MAX_PROJECTS: int = Field(
        default=2000,
        ge=1,
        description="Maximum number of projects per portfolio.",
    )

    # -------------------------------------------------------------------------
    # Monte Carlo
    # -------------------------------------------------------------------------
    MONTE_CARLO_DEFAULT_SCENARIOS: int = Field(
        default=1000,
        ge=100,
        le=100000,
        description="Default number of Monte Carlo simulation scenarios.",
    )

    # -------------------------------------------------------------------------
    # File Storage
    # -------------------------------------------------------------------------
    UPLOAD_DIR: str = "/tmp/portfolio_optisim/uploads"
    EXPORT_DIR: str = "/tmp/portfolio_optisim/exports"
    MAX_UPLOAD_SIZE_MB: int = Field(default=100, ge=1)

    # -------------------------------------------------------------------------
    # External Services (S3 / Blob Storage)
    # -------------------------------------------------------------------------
    S3_BUCKET_NAME: str = ""
    S3_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""


# Singleton settings instance - import this throughout the application
settings = Settings()

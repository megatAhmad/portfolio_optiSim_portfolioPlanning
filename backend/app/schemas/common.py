"""Common Pydantic schemas used across all API endpoints.

Provides generic pagination, error response, task response, and time-series
value schemas that are referenced by domain-specific schema modules.
"""

from __future__ import annotations

import math
import uuid
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Metadata for paginated list responses."""

    total: int = Field(..., description="Total number of items matching the query")
    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    per_page: int = Field(..., ge=1, le=1000, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")

    @classmethod
    def build(cls, *, total: int, page: int, per_page: int) -> PaginationMeta:
        """Construct pagination metadata from query results."""
        return cls(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=max(1, math.ceil(total / per_page)) if total > 0 else 0,
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper.

    Usage::

        PaginatedResponse[OpportunityResponse](
            data=[...],
            meta=PaginationMeta(total=42, page=1, per_page=20, total_pages=3),
        )
    """

    data: list[T]
    meta: PaginationMeta


class ErrorDetail(BaseModel):
    """Structured error detail returned in API error responses."""

    code: str = Field(..., description="Machine-readable error code (e.g. OPTIMIZATION_INFEASIBLE)")
    message: str = Field(..., description="Human-readable error description")
    details: dict[str, object] | None = Field(
        default=None,
        description="Optional additional context for debugging",
    )


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    error: ErrorDetail


class TaskResponse(BaseModel):
    """Response returned when a long-running task is dispatched asynchronously."""

    task_id: str = Field(..., description="Unique identifier for the background task")
    status: str = Field(
        default="pending",
        description="Initial task status (pending, running, completed, failed)",
    )
    message: str = Field(
        default="Task submitted successfully",
        description="Human-readable status message",
    )


class TimeSeriesValue(BaseModel):
    """A single year-value pair within a time-series array."""

    model_config = ConfigDict(from_attributes=True)

    year: int = Field(..., description="Year index (0-based relative to planning horizon start)")
    value: float = Field(..., description="Metric value for this year")


# ---------------------------------------------------------------------------
# Price Decks
# ---------------------------------------------------------------------------


class PriceDeckCreate(BaseModel):
    """Request body for creating a price deck."""

    name: str = Field(..., min_length=1, max_length=255, description="Price deck name (e.g., 'Base Case 2025')")
    description: str | None = Field(default=None, description="Optional description")
    effective_date: datetime = Field(..., description="Date this price deck becomes effective")
    prices: dict[str, list[TimeSeriesValue]] = Field(
        ...,
        description="Commodity prices indexed by commodity name (e.g., 'oil_brent', 'gas_henry_hub')",
    )


class PriceDeckRead(BaseModel):
    """Response schema for price deck."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    effective_date: datetime
    prices: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Master Data Sets
# ---------------------------------------------------------------------------


class MasterDataSetCreate(BaseModel):
    """Request body for creating a Master Data Set."""

    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., max_length=100, description="Category (e.g., 'Fiscal Regime', 'Price Scenario')")
    description: str | None = Field(default=None)
    applicability_filter: dict[str, Any] | None = Field(
        default=None,
        description="Attribute matching rules for auto-applying to projects",
    )
    metrics: dict[str, list[TimeSeriesValue]] = Field(
        ...,
        description="Named time-series parameters in this data set",
    )


class MasterDataSetRead(BaseModel):
    """Response schema for Master Data Set."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    category: str
    description: str | None = None
    applicability_filter: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

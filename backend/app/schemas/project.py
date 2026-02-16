"""Pydantic schemas for Opportunities (projects), Outcomes, Metrics, and Attributes."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import TimeSeriesValue


# ---------------------------------------------------------------------------
# Opportunity (Project)
# ---------------------------------------------------------------------------


class OpportunityCreate(BaseModel):
    """Request body for creating a new opportunity / investment project."""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    type: str | None = Field(
        default=None,
        max_length=50,
        description="Project type (upstream_oil, upstream_gas, renewable_solar, etc.)",
    )
    business_unit: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    location_lat: float | None = Field(default=None, ge=-90, le=90)
    location_lon: float | None = Field(default=None, ge=-180, le=180)


class OpportunityUpdate(BaseModel):
    """Request body for updating an existing opportunity. All fields optional."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    type: str | None = Field(default=None, max_length=50)
    business_unit: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    location_lat: float | None = Field(default=None, ge=-90, le=90)
    location_lon: float | None = Field(default=None, ge=-180, le=180)


class OpportunityResponse(BaseModel):
    """Serialised representation of an opportunity (list views)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: str | None = None
    business_unit: str | None = None
    country: str | None = None
    created_at: datetime
    updated_at: datetime


class OutcomeResponse(BaseModel):
    """Serialised representation of an outcome."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    opportunity_id: uuid.UUID
    name: str
    probability: float


class MetricTimeSeriesResponse(BaseModel):
    """Serialised representation of an input time-series metric."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    metric_name: str
    unit: str | None = None
    time_series_data: list[TimeSeriesValue] | list[dict[str, Any]] | None = None


class OpportunityDetail(OpportunityResponse):
    """Extended opportunity response including child relationships.

    Used for single-entity detail views (``GET /projects/{id}``).
    """

    outcomes: list[OutcomeResponse] = Field(default_factory=list)
    metrics: list[MetricTimeSeriesResponse] = Field(default_factory=list)
    attributes: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Outcome
# ---------------------------------------------------------------------------


class OutcomeCreate(BaseModel):
    """Request body for adding an outcome to an opportunity."""

    opportunity_id: uuid.UUID = Field(..., description="Parent opportunity ID")
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Outcome name (e.g. Base, Optimistic, Pessimistic)",
    )
    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probability weight (all outcomes per opportunity must sum to 1.0)",
    )


# ---------------------------------------------------------------------------
# Metric Time Series
# ---------------------------------------------------------------------------


class MetricTimeSeriesCreate(BaseModel):
    """Request body for adding a time-series metric to an opportunity-outcome pair."""

    opportunity_id: uuid.UUID
    outcome_id: uuid.UUID
    metric_name: str = Field(..., min_length=1, max_length=255)
    unit: str = Field(..., max_length=50, description="Engineering / financial unit (e.g. $M, bbl/d)")
    time_series_data: list[TimeSeriesValue] = Field(
        ...,
        min_length=1,
        description="Array of {year, value} pairs",
    )


# ---------------------------------------------------------------------------
# Attributes
# ---------------------------------------------------------------------------


class AttributeUpdate(BaseModel):
    """Request body for updating opportunity attributes (fixture, classification, custom)."""

    is_fixture: bool = False
    area: str | None = None
    onshore_offshore: str | None = None
    reserve_category: str | None = None
    business_unit: str | None = None
    price_scenario: str | None = None
    custom_attributes: dict[str, Any] | None = None

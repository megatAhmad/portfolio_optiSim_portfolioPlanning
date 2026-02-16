"""Pydantic schemas for Dependencies, Groups, Constraints, Master Data, Expressions, and Import."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import TimeSeriesValue


# ---------------------------------------------------------------------------
# Selection Dependencies (between projects)
# ---------------------------------------------------------------------------


class DependencyCreate(BaseModel):
    """Request body for creating a directed dependency between two opportunities."""

    independent_opportunity_id: uuid.UUID = Field(
        ...,
        description="The prerequisite / independent opportunity ID",
    )
    dependent_opportunity_id: uuid.UUID = Field(
        ...,
        description="The dependent opportunity ID",
    )
    must_or_must_not: str = Field(
        ...,
        description="Must (prerequisite) or Must Not (mutual exclusivity)",
    )
    time_offset: int = Field(
        default=0,
        ge=0,
        description="Time offset in years between independent and dependent",
    )
    timing_relation: str = Field(
        default="Before",
        description="Timing relation: Before, After, or During",
    )


class DependencyResponse(BaseModel):
    """Serialised representation of a selection dependency."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    independent_opportunity_id: uuid.UUID
    dependent_opportunity_id: uuid.UUID
    must_or_must_not: str
    time_offset: int
    timing_relation: str | None = None
    is_active: bool = True
    created_at: datetime


# ---------------------------------------------------------------------------
# Selection Groups
# ---------------------------------------------------------------------------


class SelectionGroupCreate(BaseModel):
    """Request body for creating a named selection group of opportunities."""

    name: str = Field(..., min_length=1, max_length=255)
    group_type: str = Field(
        ...,
        description="Group type: Exclusive, Inclusive, AtLeastN, AtMostN, ExactlyN",
    )
    member_ids: list[uuid.UUID] = Field(
        ...,
        min_length=1,
        description="List of opportunity IDs to include in this group",
    )


class GroupMemberResponse(BaseModel):
    """Serialised group member entry."""

    model_config = ConfigDict(from_attributes=True)

    opportunity_id: uuid.UUID
    is_disabled: bool = False


class SelectionGroupResponse(BaseModel):
    """Serialised representation of a selection group."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    group_type: str
    members: list[GroupMemberResponse] = Field(default_factory=list)
    is_active: bool = True


# ---------------------------------------------------------------------------
# Selection Constraints (per-project)
# ---------------------------------------------------------------------------


class SelectionConstraintCreate(BaseModel):
    """Request body for creating per-project selection rules."""

    opportunity_id: uuid.UUID
    is_integer: bool = Field(
        default=True,
        description="True for binary (0/1) selection; False for continuous WI",
    )
    total_wi_min: float = Field(
        default=0.0,
        ge=0.0,
        description="Minimum total working interest",
    )
    total_wi_max: float = Field(
        default=1.0,
        ge=0.0,
        description="Maximum total working interest",
    )
    total_instances_min: int = Field(default=0, ge=0)
    total_instances_max: int = Field(default=1, ge=0)
    yearly_constraints: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Per-year timing windows [{year, min, max}, ...]",
    )


class SelectionConstraintResponse(BaseModel):
    """Serialised representation of a selection constraint."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    opportunity_id: uuid.UUID
    is_integer: bool
    total_wi_min: float
    total_wi_max: float
    total_instances_min: int
    total_instances_max: int
    yearly_constraints: list[dict[str, Any]] | None = None
    is_active: bool = True


# ---------------------------------------------------------------------------
# Metric Constraints (portfolio-level)
# ---------------------------------------------------------------------------


class MetricConstraintCreate(BaseModel):
    """Request body for creating a portfolio-level metric constraint."""

    metric_name: str = Field(..., min_length=1, max_length=255)
    unit: str = Field(..., max_length=50)
    constraint_type: str = Field(
        ...,
        description="Constraint type: Min, Max, Range, Equal",
    )
    is_soft: bool = Field(
        default=False,
        description="True for soft constraint with penalty; False for hard enforcement",
    )
    penalty_weight: float | None = Field(
        default=None,
        description="Weight for soft constraint penalty in objective (soft only)",
    )
    penalty_magnitude: float | None = Field(
        default=None,
        description="Normalisation magnitude for penalty term (soft only)",
    )
    default_limit: float | None = Field(
        default=None,
        description="Default limit applied to all years unless overridden",
    )
    yearly_limits: dict[int, float] = Field(
        default_factory=dict,
        description="Per-year limit overrides {year: limit}",
    )


class MetricConstraintResponse(BaseModel):
    """Serialised representation of a metric constraint."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    metric_name: str
    unit: str | None = None
    constraint_type: str
    is_soft: bool
    penalty_weight: float | None = None
    penalty_magnitude: float | None = None
    default_limit: float | None = None
    yearly_limits: dict[str, Any] | None = None
    is_enforced: bool = True


# ---------------------------------------------------------------------------
# Master Data Sets
# ---------------------------------------------------------------------------


class MasterDataSetCreate(BaseModel):
    """Request body for creating a Master Data Set (e.g. price deck, toll schedule)."""

    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(
        ...,
        max_length=100,
        description="Category (price_scenario, toll_scenario, tax_scenario)",
    )
    applicable_to_attribute: str = Field(
        ...,
        max_length=100,
        description="Attribute name for opportunity matching (e.g. price_scenario)",
    )
    applicable_to_value: str = Field(
        ...,
        max_length=100,
        description="Attribute value for opportunity matching (e.g. High, Base, Low)",
    )


class MasterDataSetResponse(BaseModel):
    """Serialised representation of a Master Data Set."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    category: str | None = None
    applicable_to_attribute: str | None = None
    applicable_to_value: str | None = None
    is_active: bool = True


class MasterDataSetDetail(MasterDataSetResponse):
    """Extended Master Data Set response including child metrics."""

    metrics: list[MasterDataMetricResponse] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Master Data Metrics
# ---------------------------------------------------------------------------


class MasterDataMetricCreate(BaseModel):
    """Request body for adding a metric to a Master Data Set."""

    master_data_set_id: uuid.UUID
    metric_name: str = Field(..., min_length=1, max_length=255)
    unit: str = Field(..., max_length=50)
    time_series_data: list[TimeSeriesValue] = Field(
        ...,
        min_length=1,
        description="Array of {year, value} pairs",
    )
    is_stochastic: bool = Field(
        default=False,
        description="True if this metric follows a stochastic distribution",
    )


class MasterDataMetricResponse(BaseModel):
    """Serialised representation of a Master Data metric."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    metric_name: str
    unit: str | None = None
    time_series_data: list[TimeSeriesValue] | list[dict[str, Any]] | None = None
    is_stochastic: bool = False


# ---------------------------------------------------------------------------
# Expressions (Computed Metrics)
# ---------------------------------------------------------------------------


class ExpressionCreate(BaseModel):
    """Request body for creating a computed metric expression."""

    metric_type: str = Field(
        ...,
        description="Type: Input, Master Data, or Computed",
    )
    metric_name: str = Field(..., min_length=1, max_length=255)
    unit: str = Field(..., max_length=50)
    formula_fyf: str | None = Field(
        default=None,
        description="First Year Formula (t=0, no PT references)",
    )
    formula_ct: str | None = Field(
        default=None,
        description="Current Time formula (t>0, may reference PT)",
    )
    formula_total: str | None = Field(
        default=None,
        description="Total aggregation formula (e.g. Total([Revenue]))",
    )
    formula_total_disc: str | None = Field(
        default=None,
        description="Discounted total formula (e.g. TotalDisc([Cash Flow], 0.10))",
    )
    level: str = Field(
        default="S",
        description="Aggregation level: O (Outcome), P (Project), S (Scenario)",
    )


class ExpressionResponse(BaseModel):
    """Serialised representation of a metric expression."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    metric_type: str
    metric_name: str
    unit: str | None = None
    formula_fyf: str | None = None
    formula_ct: str | None = None
    formula_total: str | None = None
    formula_total_disc: str | None = None
    level: str = "S"


# ---------------------------------------------------------------------------
# Data Import
# ---------------------------------------------------------------------------


class ImportRequest(BaseModel):
    """Metadata accompanying a file upload for project import."""

    file_type: str = Field(
        ...,
        description="File format: excel or csv",
    )


class ImportResponse(BaseModel):
    """Summary of a completed data import operation."""

    opportunities_count: int = Field(..., description="Number of opportunities imported")
    outcomes_count: int = Field(..., description="Number of outcomes imported")
    metrics_count: int = Field(..., description="Number of metric time-series imported")
    errors: list[str] = Field(
        default_factory=list,
        description="Import validation errors (rows skipped)",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal import warnings",
    )


# ---------------------------------------------------------------------------
# Solver Detection
# ---------------------------------------------------------------------------


class SolverInfo(BaseModel):
    """Information about an available MILP solver."""

    name: str
    is_available: bool
    license_type: str = Field(..., description="open_source or commercial")
    description: str = ""


# ---------------------------------------------------------------------------
# Sensitivity Analysis
# ---------------------------------------------------------------------------


class SensitivityRequest(BaseModel):
    """Request body for running a sensitivity analysis."""

    scenario_id: uuid.UUID
    parameters: list[str] = Field(
        ...,
        min_length=1,
        description="List of parameter names to vary",
    )
    variation_pct: float = Field(
        default=0.1,
        ge=0.01,
        le=1.0,
        description="Variation range as a fraction (0.1 = +/-10%)",
    )


# ---------------------------------------------------------------------------
# Monte Carlo
# ---------------------------------------------------------------------------


class MonteCarloRequest(BaseModel):
    """Request body for running a Monte Carlo simulation."""

    scenario_id: uuid.UUID
    num_scenarios: int = Field(
        default=1000,
        ge=100,
        le=100000,
        description="Number of simulation scenarios",
    )
    seed: int | None = Field(
        default=None,
        description="Random seed for reproducibility",
    )


class RiskMetricsResponse(BaseModel):
    """Risk metrics computed from Monte Carlo simulation results."""

    scenario_id: uuid.UUID
    var_95: float = Field(..., description="Value at Risk at 95% confidence level ($M)")
    var_99: float = Field(..., description="Value at Risk at 99% confidence level ($M)")
    cvar_95: float = Field(
        ...,
        description="Conditional Value at Risk at 95% ($M) -- expected loss in worst 5%",
    )
    cvar_99: float = Field(
        ...,
        description="Conditional Value at Risk at 99% ($M) -- expected loss in worst 1%",
    )
    mean_npv: float = Field(..., description="Mean NPV across all simulation scenarios ($M)")
    std_npv: float = Field(..., description="Standard deviation of NPV ($M)")
    p10: float = Field(..., description="P10 NPV (10% probability of exceeding)")
    p50: float = Field(..., description="P50 NPV (median)")
    p90: float = Field(..., description="P90 NPV (90% probability of exceeding)")


# ---------------------------------------------------------------------------
# Dependency Graph Visualization
# ---------------------------------------------------------------------------


class GraphNode(BaseModel):
    """A node in the dependency graph visualization."""

    id: str
    label: str
    type: str | None = None
    group: str | None = None


class GraphEdge(BaseModel):
    """An edge in the dependency graph visualization."""

    source: str
    target: str
    relation: str
    time_offset: int = 0


class DependencyGraphResponse(BaseModel):
    """Dependency graph data formatted for frontend visualization (D3.js / React Flow)."""

    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    has_cycles: bool = False


class CycleCheckResponse(BaseModel):
    """Result of a cycle detection check on the dependency graph."""

    has_cycles: bool
    cycles: list[list[str]] = Field(
        default_factory=list,
        description="List of cycles, each cycle is a list of opportunity IDs",
    )


# ---------------------------------------------------------------------------
# Optimization Execution
# ---------------------------------------------------------------------------


class OptimizationRequest(BaseModel):
    """Request body for triggering an optimization run."""

    method: str = Field(
        default="DETERMINISTIC",
        description="Optimization method: DETERMINISTIC, STOCHASTIC, MULTI_OBJECTIVE",
    )
    solver: str | None = Field(
        default=None,
        description="Solver to use (highs, gurobi, cplex, etc.). If not specified, uses default from config.",
    )
    time_limit_seconds: int | None = Field(
        default=None,
        ge=1,
        le=3600,
        description="Maximum solve time in seconds",
    )
    mip_gap: float | None = Field(
        default=0.001,
        ge=0.0,
        le=0.1,
        description="Target MIP gap (0.001 = 0.1% = 99.9% optimal)",
    )


class OptimizationStatus(BaseModel):
    """Response schema for optimization status."""

    scenario_id: str
    task_id: str | None = None
    status: str = Field(..., description="Status: DRAFT, QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED")
    message: str | None = None
    progress: float | None = Field(default=None, ge=0.0, le=1.0, description="Progress fraction (0.0 to 1.0)")
    solve_time_seconds: float | None = None
    mip_gap: float | None = None
    objective_value: float | None = None

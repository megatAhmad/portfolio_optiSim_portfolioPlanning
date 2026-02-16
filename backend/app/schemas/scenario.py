"""Pydantic schemas for Scenarios, Optimization Settings, and Results."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Optimization Settings (embedded in ScenarioCreate)
# ---------------------------------------------------------------------------


class OptimizationSettings(BaseModel):
    """Per-scenario solver and optimizer configuration."""

    solver: str = Field(
        default="highs",
        description="MILP solver to use (highs, glpk, cbc, gurobi, cplex, ortools)",
    )
    time_limit_seconds: int = Field(
        default=300,
        ge=10,
        le=86400,
        description="Maximum solver wall-clock time in seconds",
    )
    mip_gap: float = Field(
        default=0.001,
        ge=0.0,
        le=1.0,
        description="MIP optimality gap tolerance (0.001 = 0.1%)",
    )
    use_hybrid_optimization: bool = Field(
        default=True,
        description="Pre-compute standalone NPV for independent projects",
    )
    temporal_aggregation: str = Field(
        default="annual",
        description="Time-period resolution (annual, biennial, quinquennial)",
    )


# ---------------------------------------------------------------------------
# Scenario Objective
# ---------------------------------------------------------------------------


class ScenarioObjective(BaseModel):
    """Objective function specification for portfolio optimization."""

    type: str = Field(
        ...,
        description="Objective type: maximize_npv, maximize_npv_per_capex, multi_objective",
    )
    weights: dict[str, float] | None = Field(
        default=None,
        description="Metric weights for multi-objective optimization",
    )


# ---------------------------------------------------------------------------
# Scenario Constraints (input-level schema, stored in JSONB)
# ---------------------------------------------------------------------------


class ScenarioConstraintInput(BaseModel):
    """A constraint definition attached to a scenario at creation time.

    The ``type`` field identifies the constraint kind (e.g. ``metric_max``,
    ``capex_annual``, ``production_min``) and ``parameters`` carries the
    type-specific configuration.
    """

    type: str = Field(..., description="Constraint type identifier")
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Type-specific constraint parameters",
    )


# ---------------------------------------------------------------------------
# Scenario CRUD
# ---------------------------------------------------------------------------


class ScenarioCreate(BaseModel):
    """Request body for creating a new portfolio optimization scenario."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price_deck_id: uuid.UUID | None = Field(
        default=None,
        description="Master Data Set ID to use as the price deck",
    )
    constraints: list[ScenarioConstraintInput] = Field(
        default_factory=list,
        description="List of constraint definitions for this scenario",
    )
    objective: ScenarioObjective = Field(
        ...,
        description="Objective function specification",
    )
    project_ids: list[uuid.UUID] | None = Field(
        default=None,
        description="Subset of opportunity IDs to include (None = all)",
    )
    optimization_settings: OptimizationSettings = Field(
        default_factory=OptimizationSettings,
    )


class ScenarioUpdate(BaseModel):
    """Request body for updating scenario metadata. Only name and description are mutable."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class ScenarioResponse(BaseModel):
    """Serialised scenario for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    status: str
    created_by: str | None = None
    created_at: datetime


class ScenarioDetail(ScenarioResponse):
    """Extended scenario response including full inputs and results."""

    inputs: dict[str, Any] | None = None
    results: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Solver Statistics
# ---------------------------------------------------------------------------


class SolverStats(BaseModel):
    """Statistics returned by the solver after an optimization run."""

    solver_name: str = Field(..., description="Name of the solver used")
    status: str = Field(..., description="Solver termination status (optimal, infeasible, timeout, etc.)")
    objective_value: float | None = Field(
        default=None,
        description="Best objective value found (None if infeasible)",
    )
    solve_time_seconds: float = Field(..., description="Wall-clock solver time")
    mip_gap: float = Field(
        ...,
        description="Achieved MIP gap (0.0 = proven optimal)",
    )
    iterations: int = Field(..., description="Total solver iterations (simplex or barrier)")
    num_variables: int = Field(..., description="Number of decision variables in the model")
    num_constraints: int = Field(..., description="Number of constraints in the model")
    precomputed_projects: int = Field(
        ...,
        description="Number of independent projects solved via pre-computation",
    )
    optimization_method: str = Field(
        ...,
        description="Method used (deterministic_milp, sddp, multi_objective, etc.)",
    )


# ---------------------------------------------------------------------------
# Optimization Result
# ---------------------------------------------------------------------------


class OptimizationResultResponse(BaseModel):
    """Top-level optimization result returned after a successful solve."""

    selected_projects: list[dict[str, Any]] = Field(
        ...,
        description="List of selected projects with timing, WI, and per-project metrics",
    )
    objective_value: float = Field(
        ...,
        description="Optimal objective function value ($M)",
    )
    metrics: dict[str, Any] = Field(
        ...,
        description="Portfolio-level aggregate metrics (total_npv, total_capex, etc.)",
    )
    solver_stats: SolverStats


# ---------------------------------------------------------------------------
# Scenario Comparison
# ---------------------------------------------------------------------------


class ScenarioCompareRequest(BaseModel):
    """Request body for comparing multiple scenarios side by side."""

    scenario_ids: list[uuid.UUID] = Field(
        ...,
        min_length=2,
        description="List of scenario IDs to compare (minimum 2)",
    )

"""
MILP Builder - Pyomo ConcreteModel construction for portfolio optimization

Builds the Mixed Integer Linear Programming (MILP) model that represents
the portfolio optimization problem:

  maximize sum(NPV[p] * select[p]) - penalty_terms
  subject to:
    - Selection constraints (per-project)
    - Dependency constraints (between projects)
    - Group constraints (collective)
    - Metric constraints (portfolio-level)
    - Temporal state evolution (debt, production, emissions)
    - Working interest bounds
    - Budget / CAPEX limits

The model uses explicit temporal state variables (NOT recursion) as specified
in CLAUDE.md Key Architectural Decision #1.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from pyomo.environ import (
    Binary,
    ConcreteModel,
    Constraint,
    NonNegativeReals,
    Objective,
    RangeSet,
    Reals,
    Set as PyomoSet,
    Var,
    maximize,
    minimize,
    value,
)
import structlog

from app.optimization.constraint_generators import (
    MetricConstraintData,
    SelectionConstraintData,
    SelectionDependencyData,
    SelectionGroupData,
    add_all_constraints,
)

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Project Data for Model Building
# ---------------------------------------------------------------------------


@dataclass
class ProjectData:
    """Aggregated data for a single project used in model building."""

    project_id: str
    name: str
    npv: float = 0.0
    capex_by_year: Dict[int, float] = field(default_factory=dict)
    production_by_year: Dict[int, float] = field(default_factory=dict)
    revenue_by_year: Dict[int, float] = field(default_factory=dict)
    emissions_by_year: Dict[int, float] = field(default_factory=dict)
    is_independent: bool = True  # True if no interdependencies
    has_temporal_state: bool = False  # True if needs state variables


@dataclass
class OptimizationConfig:
    """Configuration for the MILP model."""

    planning_horizon_years: int = 30
    discount_rate: float = 0.10
    objective: str = "NPV"  # NPV, PRODUCTION, EMISSIONS, CUSTOM
    sense: str = "maximize"
    solver: str = "highs"
    time_limit_seconds: Optional[int] = None
    mip_gap: float = 0.001


# ---------------------------------------------------------------------------
# MILP Model Builder
# ---------------------------------------------------------------------------


class MILPModelBuilder:
    """
    Builds a Pyomo ConcreteModel for portfolio optimization.

    Follows the hybrid pre-computation pattern from CLAUDE.md:
    - Independent projects (70-90% typical): pre-computed NPV as scalar
    - Interdependent projects: full state variable treatment

    Usage:
        builder = MILPModelBuilder(config)
        builder.add_projects(project_data)
        builder.add_constraints(...)
        model = builder.build()
    """

    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.projects: Dict[str, ProjectData] = {}
        self.independent_projects: Set[str] = set()
        self.interdependent_projects: Set[str] = set()
        self.years: List[int] = list(range(config.planning_horizon_years))

        # Constraint data (populated via add_* methods)
        self._selection_constraints: List[SelectionConstraintData] = []
        self._dependencies: List[SelectionDependencyData] = []
        self._groups: List[SelectionGroupData] = []
        self._metric_constraints: List[MetricConstraintData] = []
        self._synergy_pairs: List[tuple[str, str, float]] = []
        self._infrastructure: List[Dict[str, Any]] = []

        # Pre-computed metric values for metric constraints
        self._metric_values: Dict[str, Dict[str, Dict[int, float]]] = {}

        logger.info(
            "milp_builder_initialized",
            planning_horizon=config.planning_horizon_years,
            discount_rate=config.discount_rate,
            objective=config.objective,
        )

    def add_projects(self, projects: List[ProjectData]) -> None:
        """
        Add projects to the model.

        Automatically classifies projects as independent or interdependent
        based on whether they have temporal state requirements.
        """
        for proj in projects:
            self.projects[proj.project_id] = proj

            if proj.is_independent and not proj.has_temporal_state:
                self.independent_projects.add(proj.project_id)
            else:
                self.interdependent_projects.add(proj.project_id)

        logger.info(
            "projects_added",
            total=len(projects),
            independent=len(self.independent_projects),
            interdependent=len(self.interdependent_projects),
        )

    def add_selection_constraints(
        self, constraints: List[SelectionConstraintData]
    ) -> None:
        """Add per-project selection constraints."""
        self._selection_constraints.extend(constraints)

    def add_dependencies(self, dependencies: List[SelectionDependencyData]) -> None:
        """Add inter-project dependencies."""
        self._dependencies.extend(dependencies)

        # Mark affected projects as interdependent
        for dep in dependencies:
            self.interdependent_projects.add(dep.independent_opportunity_id)
            self.interdependent_projects.add(dep.dependent_opportunity_id)
            self.independent_projects.discard(dep.independent_opportunity_id)
            self.independent_projects.discard(dep.dependent_opportunity_id)

    def add_groups(self, groups: List[SelectionGroupData]) -> None:
        """Add selection groups."""
        self._groups.extend(groups)

    def add_metric_constraints(
        self,
        constraints: List[MetricConstraintData],
        metric_values: Dict[str, Dict[str, Dict[int, float]]],
    ) -> None:
        """
        Add portfolio-level metric constraints.

        Args:
            constraints: Metric constraint definitions
            metric_values: Pre-computed values: metric_name -> project_id -> year -> value
        """
        self._metric_constraints.extend(constraints)
        self._metric_values.update(metric_values)

    def add_synergies(self, synergy_pairs: List[tuple[str, str, float]]) -> None:
        """Add synergy pairs (project_a, project_b, synergy_npv)."""
        self._synergy_pairs.extend(synergy_pairs)

    def add_infrastructure(self, infrastructure: List[Dict[str, Any]]) -> None:
        """Add shared infrastructure capacity constraints."""
        self._infrastructure.extend(infrastructure)

    def build(self) -> ConcreteModel:
        """
        Build and return the complete Pyomo ConcreteModel.

        Steps:
        1. Create model with sets and indices
        2. Create decision variables (select, instances, start_year)
        3. Create objective function
        4. Add all constraints
        5. Return ready-to-solve model
        """
        logger.info("milp_model_build_started")

        model = ConcreteModel("PortfolioOptimization")

        # Step 1: Sets and indices
        self._create_sets(model)

        # Step 2: Decision variables
        self._create_variables(model)

        # Step 3: Objective function
        self._create_objective(model)

        # Step 4: All constraints
        self._add_all_constraints(model)

        # Log model statistics
        num_vars = model.nvariables() if hasattr(model, "nvariables") else 0
        num_constraints = model.nconstraints() if hasattr(model, "nconstraints") else 0

        logger.info(
            "milp_model_built",
            num_projects=len(self.projects),
            num_years=len(self.years),
            num_variables=num_vars,
            num_constraints=num_constraints,
            independent_projects=len(self.independent_projects),
            interdependent_projects=len(self.interdependent_projects),
        )

        return model

    # ----- Internal: Set creation -----

    def _create_sets(self, model: ConcreteModel) -> None:
        """Create Pyomo sets for projects, years, and derived index sets."""
        all_project_ids = list(self.projects.keys())

        model.PROJECTS = PyomoSet(initialize=all_project_ids, doc="All project IDs")
        model.YEARS = PyomoSet(initialize=self.years, doc="Year indices")
        model.INDEPENDENT = PyomoSet(
            initialize=list(self.independent_projects),
            doc="Projects without interdependencies",
        )
        model.INTERDEPENDENT = PyomoSet(
            initialize=list(self.interdependent_projects),
            doc="Projects with interdependencies",
        )

    # ----- Internal: Variable creation -----

    def _create_variables(self, model: ConcreteModel) -> None:
        """
        Create decision variables.

        Primary decision: select[p] ∈ {0, 1} for each project
        For independent projects: this is the only needed variable (NPV is pre-computed)
        For interdependent projects: additional state variables created by TimeSeriesStateManager
        """
        # Binary selection variable for all projects
        model.select = Var(
            model.PROJECTS,
            domain=Binary,
            doc="1 if project is selected, 0 otherwise",
        )

    # ----- Internal: Objective creation -----

    def _create_objective(self, model: ConcreteModel) -> None:
        """
        Create the objective function.

        Default: maximize total portfolio NPV
        NPV[p] is pre-computed for independent projects
        For interdependent projects, NPV is also pre-computed but may need adjustment
        for synergies.
        """
        if self.config.objective == "NPV":
            self._create_npv_objective(model)
        elif self.config.objective == "PRODUCTION":
            self._create_production_objective(model)
        elif self.config.objective == "EMISSIONS":
            self._create_emissions_objective(model)
        else:
            # Default to NPV
            self._create_npv_objective(model)

    def _create_npv_objective(self, model: ConcreteModel) -> None:
        """Maximize total portfolio NPV."""
        sense = maximize if self.config.sense == "maximize" else minimize

        # Base NPV: sum(NPV[p] * select[p])
        def objective_rule(mdl):
            base_npv = sum(
                self.projects[p].npv * mdl.select[p]
                for p in mdl.PROJECTS
            )

            # Add synergy bonus terms
            synergy_bonus = 0
            for idx, (proj_a, proj_b, syn_val) in enumerate(self._synergy_pairs):
                ivar_name = f"synergy_interaction_{idx}"
                if hasattr(mdl, ivar_name):
                    synergy_bonus += syn_val * getattr(mdl, ivar_name)

            # Subtract soft constraint penalty terms
            penalty = 0
            for i, mc in enumerate(self._metric_constraints):
                if mc.is_soft:
                    weight = float(mc.penalty_weight or 1.0)
                    magnitude = float(mc.penalty_magnitude or 1.0)
                    for year in self.years:
                        slack_name = f"slack_{mc.metric_name}_{year}"
                        if hasattr(mdl, slack_name):
                            penalty += weight * getattr(mdl, slack_name) / magnitude

            return base_npv + synergy_bonus - penalty

        model.objective = Objective(rule=objective_rule, sense=sense)

    def _create_production_objective(self, model: ConcreteModel) -> None:
        """Maximize total portfolio production."""
        def objective_rule(mdl):
            return sum(
                sum(
                    self.projects[p].production_by_year.get(t, 0.0)
                    for t in self.years
                ) * mdl.select[p]
                for p in mdl.PROJECTS
            )

        model.objective = Objective(rule=objective_rule, sense=maximize)

    def _create_emissions_objective(self, model: ConcreteModel) -> None:
        """Minimize total portfolio emissions."""
        def objective_rule(mdl):
            return sum(
                sum(
                    self.projects[p].emissions_by_year.get(t, 0.0)
                    for t in self.years
                ) * mdl.select[p]
                for p in mdl.PROJECTS
            )

        model.objective = Objective(rule=objective_rule, sense=minimize)

    # ----- Internal: Constraint aggregation -----

    def _add_all_constraints(self, model: ConcreteModel) -> None:
        """Add all constraints using the constraint_generators module."""
        all_project_ids = set(self.projects.keys())

        constraint_counts = add_all_constraints(
            model=model,
            selection_constraints=self._selection_constraints,
            dependencies=self._dependencies,
            groups=self._groups,
            metric_constraints=self._metric_constraints,
            projects=all_project_ids,
            years=self.years,
            metric_values=self._metric_values,
            synergy_pairs=self._synergy_pairs if self._synergy_pairs else None,
            infrastructure=self._infrastructure if self._infrastructure else None,
        )

        logger.info("model_constraints_summary", counts=constraint_counts)


# ---------------------------------------------------------------------------
# Convenience: Build and solve in one call
# ---------------------------------------------------------------------------


def build_portfolio_model(
    projects: List[ProjectData],
    config: OptimizationConfig,
    selection_constraints: Optional[List[SelectionConstraintData]] = None,
    dependencies: Optional[List[SelectionDependencyData]] = None,
    groups: Optional[List[SelectionGroupData]] = None,
    metric_constraints: Optional[List[MetricConstraintData]] = None,
    metric_values: Optional[Dict[str, Dict[str, Dict[int, float]]]] = None,
    synergy_pairs: Optional[List[tuple[str, str, float]]] = None,
) -> ConcreteModel:
    """
    Convenience function to build a portfolio optimization model.

    Args:
        projects: List of ProjectData with NPV and metrics
        config: Optimization configuration
        selection_constraints: Per-project selection rules
        dependencies: Inter-project dependencies
        groups: Selection groups
        metric_constraints: Portfolio-level metric limits
        metric_values: Pre-computed metric values for constraints
        synergy_pairs: Project synergy pairs

    Returns:
        Built Pyomo ConcreteModel ready for solving
    """
    builder = MILPModelBuilder(config)
    builder.add_projects(projects)

    if selection_constraints:
        builder.add_selection_constraints(selection_constraints)
    if dependencies:
        builder.add_dependencies(dependencies)
    if groups:
        builder.add_groups(groups)
    if metric_constraints and metric_values:
        builder.add_metric_constraints(metric_constraints, metric_values)
    if synergy_pairs:
        builder.add_synergies(synergy_pairs)

    return builder.build()

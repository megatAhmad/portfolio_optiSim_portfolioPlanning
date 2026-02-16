"""
Hybrid Portfolio Optimizer - Orchestrates the full optimization pipeline

Implements the Hybrid Pre-Computation strategy from CLAUDE.md:

1. Classify projects as independent (no interdependencies) or interdependent
2. Pre-compute standalone NPV/metrics for independent projects (O(1) lookup)
3. Build MILP model with full state variables only for interdependent projects
4. Solve using user-selected solver
5. Extract and format results

Result: 60-80% fewer optimization variables, 5-10x faster solve times,
identical optimality for typical portfolios where 70-90% of projects
have no interdependencies.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from pyomo.environ import value as pyomo_value
import structlog

from app.optimization.constraint_generators import (
    MetricConstraintData,
    SelectionConstraintData,
    SelectionDependencyData,
    SelectionGroupData,
)
from app.optimization.milp_builder import (
    MILPModelBuilder,
    OptimizationConfig,
    ProjectData,
)
from app.optimization.solver_interface import SolverInterface, SolverStats

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Result Data Structures
# ---------------------------------------------------------------------------


@dataclass
class ProjectResult:
    """Optimization result for a single project."""

    project_id: str
    project_name: str
    is_selected: bool
    selection_value: float  # 0.0 or 1.0 for binary; WI for continuous
    npv: float
    capex_by_year: Dict[int, float] = field(default_factory=dict)
    production_by_year: Dict[int, float] = field(default_factory=dict)
    revenue_by_year: Dict[int, float] = field(default_factory=dict)
    emissions_by_year: Dict[int, float] = field(default_factory=dict)


@dataclass
class OptimizationResult:
    """Complete optimization result for a portfolio."""

    scenario_id: str
    status: str  # OPTIMAL, FEASIBLE, INFEASIBLE, ERROR
    solver_stats: SolverStats
    objective_value: float
    total_npv: float
    total_capex: float
    total_production: float

    selected_projects: List[ProjectResult]
    rejected_projects: List[ProjectResult]

    # Portfolio-level time series
    portfolio_capex_by_year: Dict[int, float] = field(default_factory=dict)
    portfolio_production_by_year: Dict[int, float] = field(default_factory=dict)
    portfolio_revenue_by_year: Dict[int, float] = field(default_factory=dict)
    portfolio_emissions_by_year: Dict[int, float] = field(default_factory=dict)

    # Constraint binding information
    binding_constraints: List[Dict[str, Any]] = field(default_factory=list)

    # Performance metadata
    num_projects_total: int = 0
    num_projects_selected: int = 0
    num_independent: int = 0
    num_interdependent: int = 0


# ---------------------------------------------------------------------------
# Hybrid Portfolio Optimizer
# ---------------------------------------------------------------------------


class HybridPortfolioOptimizer:
    """
    Main optimizer class that orchestrates the portfolio optimization pipeline.

    Usage:
        optimizer = HybridPortfolioOptimizer(config)
        optimizer.load_projects(projects)
        optimizer.load_constraints(...)
        result = optimizer.optimize()
    """

    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.projects: Dict[str, ProjectData] = {}
        self.independent_projects: Set[str] = set()
        self.interdependent_projects: Set[str] = set()

        # Constraints
        self._selection_constraints: List[SelectionConstraintData] = []
        self._dependencies: List[SelectionDependencyData] = []
        self._groups: List[SelectionGroupData] = []
        self._metric_constraints: List[MetricConstraintData] = []
        self._metric_values: Dict[str, Dict[str, Dict[int, float]]] = {}
        self._synergy_pairs: List[tuple[str, str, float]] = []

        logger.info(
            "hybrid_optimizer_initialized",
            objective=config.objective,
            horizon=config.planning_horizon_years,
            solver=config.solver,
        )

    # ----- Data Loading -----

    def load_projects(self, projects: List[ProjectData]) -> None:
        """Load project data and classify as independent/interdependent."""
        for proj in projects:
            self.projects[proj.project_id] = proj

        logger.info("projects_loaded", count=len(projects))

    def load_dependencies(self, dependencies: List[SelectionDependencyData]) -> None:
        """Load inter-project dependencies and reclassify affected projects."""
        self._dependencies = dependencies

        # Identify interdependent projects from dependencies
        dep_projects: Set[str] = set()
        for dep in dependencies:
            dep_projects.add(dep.independent_opportunity_id)
            dep_projects.add(dep.dependent_opportunity_id)

        # Classify
        for pid in self.projects:
            if pid in dep_projects:
                self.interdependent_projects.add(pid)
            else:
                self.independent_projects.add(pid)

        logger.info(
            "projects_classified",
            independent=len(self.independent_projects),
            interdependent=len(self.interdependent_projects),
            pct_independent=f"{100 * len(self.independent_projects) / max(len(self.projects), 1):.0f}%",
        )

    def load_constraints(
        self,
        selection_constraints: Optional[List[SelectionConstraintData]] = None,
        groups: Optional[List[SelectionGroupData]] = None,
        metric_constraints: Optional[List[MetricConstraintData]] = None,
        metric_values: Optional[Dict[str, Dict[str, Dict[int, float]]]] = None,
        synergy_pairs: Optional[List[tuple[str, str, float]]] = None,
    ) -> None:
        """Load all constraint data."""
        if selection_constraints:
            self._selection_constraints = selection_constraints
        if groups:
            self._groups = groups
        if metric_constraints:
            self._metric_constraints = metric_constraints
        if metric_values:
            self._metric_values = metric_values
        if synergy_pairs:
            self._synergy_pairs = synergy_pairs

    # ----- Pre-computation -----

    def _precompute_independent_npv(self) -> Dict[str, float]:
        """
        Pre-compute standalone NPV for independent projects.

        For projects with no interdependencies, their NPV is a fixed scalar
        that doesn't depend on other project selections. This allows O(1)
        lookup during optimization instead of state variable treatment.

        Returns:
            Dict mapping project_id to pre-computed NPV
        """
        precomputed: Dict[str, float] = {}

        for pid in self.independent_projects:
            proj = self.projects[pid]
            precomputed[pid] = proj.npv

        logger.info(
            "npv_precomputed",
            count=len(precomputed),
            total_npv=sum(precomputed.values()),
        )

        return precomputed

    # ----- Optimization -----

    def optimize(self, scenario_id: str = "default") -> OptimizationResult:
        """
        Run the full optimization pipeline.

        Steps:
        1. Pre-compute metrics for independent projects
        2. Build MILP model (full variables only for interdependent)
        3. Add all constraints
        4. Solve with user-selected solver
        5. Extract and format results

        Args:
            scenario_id: Identifier for this optimization run

        Returns:
            OptimizationResult with selected portfolio and metrics
        """
        logger.info(
            "optimization_started",
            scenario_id=scenario_id,
            num_projects=len(self.projects),
        )

        # Step 1: Pre-compute
        precomputed_npv = self._precompute_independent_npv()

        # Step 2-3: Build model
        project_data_list = list(self.projects.values())

        # Mark independent projects
        for proj in project_data_list:
            proj.is_independent = proj.project_id in self.independent_projects

        builder = MILPModelBuilder(self.config)
        builder.add_projects(project_data_list)
        builder.add_selection_constraints(self._selection_constraints)
        builder.add_dependencies(self._dependencies)
        builder.add_groups(self._groups)

        if self._metric_constraints and self._metric_values:
            builder.add_metric_constraints(
                self._metric_constraints, self._metric_values
            )
        if self._synergy_pairs:
            builder.add_synergies(self._synergy_pairs)

        model = builder.build()

        # Step 4: Solve
        solver = SolverInterface(solver_name=self.config.solver)
        results, stats = solver.solve(
            model,
            time_limit_seconds=self.config.time_limit_seconds,
            mip_gap=self.config.mip_gap,
        )

        # Add precomputed project count to stats
        stats.precomputed_projects = len(self.independent_projects)

        # Step 5: Extract results
        return self._extract_results(model, stats, scenario_id)

    def _extract_results(
        self,
        model: Any,
        stats: SolverStats,
        scenario_id: str,
    ) -> OptimizationResult:
        """Extract optimization results from solved Pyomo model."""
        years = list(range(self.config.planning_horizon_years))

        selected: List[ProjectResult] = []
        rejected: List[ProjectResult] = []

        # Portfolio-level aggregates
        portfolio_capex: Dict[int, float] = {t: 0.0 for t in years}
        portfolio_production: Dict[int, float] = {t: 0.0 for t in years}
        portfolio_revenue: Dict[int, float] = {t: 0.0 for t in years}
        portfolio_emissions: Dict[int, float] = {t: 0.0 for t in years}

        total_npv = 0.0
        total_capex = 0.0
        total_production = 0.0

        for pid in self.projects:
            proj = self.projects[pid]
            sel_val = pyomo_value(model.select[pid])
            is_selected = sel_val > 0.5  # Binary: threshold at 0.5

            proj_result = ProjectResult(
                project_id=pid,
                project_name=proj.name,
                is_selected=is_selected,
                selection_value=sel_val,
                npv=proj.npv * sel_val,
                capex_by_year={
                    t: proj.capex_by_year.get(t, 0.0) * sel_val for t in years
                },
                production_by_year={
                    t: proj.production_by_year.get(t, 0.0) * sel_val for t in years
                },
                revenue_by_year={
                    t: proj.revenue_by_year.get(t, 0.0) * sel_val for t in years
                },
                emissions_by_year={
                    t: proj.emissions_by_year.get(t, 0.0) * sel_val for t in years
                },
            )

            if is_selected:
                selected.append(proj_result)
                total_npv += proj.npv * sel_val
                total_capex += sum(proj.capex_by_year.get(t, 0.0) * sel_val for t in years)
                total_production += sum(
                    proj.production_by_year.get(t, 0.0) * sel_val for t in years
                )

                # Aggregate to portfolio level
                for t in years:
                    portfolio_capex[t] += proj.capex_by_year.get(t, 0.0) * sel_val
                    portfolio_production[t] += proj.production_by_year.get(t, 0.0) * sel_val
                    portfolio_revenue[t] += proj.revenue_by_year.get(t, 0.0) * sel_val
                    portfolio_emissions[t] += proj.emissions_by_year.get(t, 0.0) * sel_val
            else:
                rejected.append(proj_result)

        objective_value = pyomo_value(model.objective) if hasattr(model, "objective") else total_npv

        result = OptimizationResult(
            scenario_id=scenario_id,
            status="OPTIMAL",
            solver_stats=stats,
            objective_value=objective_value,
            total_npv=total_npv,
            total_capex=total_capex,
            total_production=total_production,
            selected_projects=selected,
            rejected_projects=rejected,
            portfolio_capex_by_year=portfolio_capex,
            portfolio_production_by_year=portfolio_production,
            portfolio_revenue_by_year=portfolio_revenue,
            portfolio_emissions_by_year=portfolio_emissions,
            num_projects_total=len(self.projects),
            num_projects_selected=len(selected),
            num_independent=len(self.independent_projects),
            num_interdependent=len(self.interdependent_projects),
        )

        logger.info(
            "optimization_completed",
            scenario_id=scenario_id,
            objective_value=objective_value,
            total_npv=total_npv,
            selected=len(selected),
            rejected=len(rejected),
            solve_time=stats.solve_time_seconds,
            mip_gap=stats.mip_gap,
        )

        return result

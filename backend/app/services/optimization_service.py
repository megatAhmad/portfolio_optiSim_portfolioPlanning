"""
Optimization Service - MILP model construction, solver dispatch, result storage

Orchestrates the optimization pipeline:
1. Load scenario configuration and project data
2. Build dependency graph and classify projects
3. Construct MILP model via MILPModelBuilder
4. Solve with user-selected solver via SolverInterface
5. Store results in TimescaleDB
6. Return optimization results
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.constraint_converter import convert_graph_to_constraints
from app.models.constraint import MetricConstraint, SelectionConstraint
from app.models.dependency import SelectionDependency, SelectionGroup
from app.models.project import Opportunity
from app.models.scenario import Scenario
from app.optimization.constraint_generators import (
    MetricConstraintData,
    SelectionConstraintData,
    SelectionDependencyData,
    SelectionGroupData,
)
from app.optimization.hybrid_optimizer import (
    HybridPortfolioOptimizer,
    OptimizationResult,
)
from app.optimization.milp_builder import OptimizationConfig, ProjectData
from app.services.data_service import DataService

logger = structlog.get_logger(__name__)


class OptimizationService:
    """Service for running portfolio optimizations.

    Bridges the API layer with the optimization engine.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.data_service = DataService(session)

    async def run_optimization(
        self,
        scenario_id: UUID,
        solver: Optional[str] = None,
        time_limit_seconds: Optional[int] = None,
        mip_gap: float = 0.001,
    ) -> OptimizationResult:
        """Run portfolio optimization for a scenario.

        Args:
            scenario_id: ID of the scenario to optimize
            solver: Solver to use (None = default from config)
            time_limit_seconds: Max solve time
            mip_gap: Target MIP gap (0.001 = 0.1%)

        Returns:
            OptimizationResult with selected portfolio
        """
        # Load scenario
        stmt = select(Scenario).where(Scenario.id == scenario_id)
        result = await self.session.execute(stmt)
        scenario = result.scalar_one_or_none()

        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        logger.info(
            "optimization_run_started",
            scenario_id=str(scenario_id),
            solver=solver,
        )

        # Build configuration
        config = OptimizationConfig(
            planning_horizon_years=scenario.planning_horizon_years or 30,
            discount_rate=scenario.discount_rate or 0.10,
            objective=scenario.objective_function or "NPV",
            solver=solver or "highs",
            time_limit_seconds=time_limit_seconds,
            mip_gap=mip_gap,
        )

        # Load project data
        projects = await self._load_project_data(config.planning_horizon_years)

        # Load constraints
        selection_constraints = await self._load_selection_constraints()
        dependencies = await self._load_dependencies()
        groups = await self._load_groups()
        metric_constraints = await self._load_metric_constraints()

        # Build and run optimizer
        optimizer = HybridPortfolioOptimizer(config)
        optimizer.load_projects(projects)
        optimizer.load_dependencies(dependencies)
        optimizer.load_constraints(
            selection_constraints=selection_constraints,
            groups=groups,
            metric_constraints=metric_constraints,
        )

        opt_result = optimizer.optimize(scenario_id=str(scenario_id))

        # Update scenario status
        scenario.status = "COMPLETED" if opt_result.status == "OPTIMAL" else "FAILED"
        await self.session.commit()

        logger.info(
            "optimization_run_completed",
            scenario_id=str(scenario_id),
            status=opt_result.status,
            objective_value=opt_result.objective_value,
            selected=opt_result.num_projects_selected,
        )

        return opt_result

    # ------------------------------------------------------------------
    # Data Loading
    # ------------------------------------------------------------------

    async def _load_project_data(
        self,
        planning_horizon: int,
    ) -> List[ProjectData]:
        """Load all projects and their pre-computed metrics."""
        opportunities = await self.data_service.get_all_opportunities()

        projects: List[ProjectData] = []
        for opp in opportunities:
            project = ProjectData(
                project_id=str(opp.id),
                name=opp.name,
                npv=0.0,  # Will be computed from metrics
                is_independent=True,
            )
            projects.append(project)

        return projects

    async def _load_selection_constraints(self) -> List[SelectionConstraintData]:
        """Load selection constraints from database."""
        stmt = select(SelectionConstraint)
        result = await self.session.execute(stmt)
        db_constraints = result.scalars().all()

        return [
            SelectionConstraintData(
                opportunity_id=str(sc.opportunity_id),
                is_integer=sc.is_integer,
                is_active=sc.is_active,
                total_wi_min=float(sc.total_wi_min),
                total_wi_max=float(sc.total_wi_max),
                total_instances_min=sc.total_instances_min,
                total_instances_max=sc.total_instances_max,
                yearly_constraints=sc.yearly_constraints,
            )
            for sc in db_constraints
        ]

    async def _load_dependencies(self) -> List[SelectionDependencyData]:
        """Load dependencies from database."""
        stmt = select(SelectionDependency).where(
            SelectionDependency.is_active == True  # noqa: E712
        )
        result = await self.session.execute(stmt)
        db_deps = result.scalars().all()

        return [
            SelectionDependencyData(
                independent_opportunity_id=str(dep.independent_opportunity_id),
                dependent_opportunity_id=str(dep.dependent_opportunity_id),
                must_or_must_not=dep.must_or_must_not,
                time_offset=dep.time_offset,
                timing_relation=dep.timing_relation,
            )
            for dep in db_deps
        ]

    async def _load_groups(self) -> List[SelectionGroupData]:
        """Load selection groups from database."""
        stmt = select(SelectionGroup).where(
            SelectionGroup.is_active == True  # noqa: E712
        )
        result = await self.session.execute(stmt)
        db_groups = result.scalars().all()

        return [
            SelectionGroupData(
                group_id=str(grp.id),
                name=grp.name,
                group_type=grp.group_type,
                member_opportunity_ids=[
                    str(m.opportunity_id) for m in grp.members
                ],
                total_instances_min=grp.total_instances_min,
                total_instances_max=grp.total_instances_max,
            )
            for grp in db_groups
        ]

    async def _load_metric_constraints(self) -> List[MetricConstraintData]:
        """Load metric constraints from database."""
        stmt = select(MetricConstraint).where(
            MetricConstraint.is_enforced == True  # noqa: E712
        )
        result = await self.session.execute(stmt)
        db_constraints = result.scalars().all()

        return [
            MetricConstraintData(
                metric_name=mc.metric_name,
                constraint_type=mc.constraint_type,
                is_soft=mc.is_soft,
                default_limit=float(mc.default_limit) if mc.default_limit else None,
                penalty_weight=float(mc.penalty_weight) if mc.penalty_weight else None,
                penalty_magnitude=float(mc.penalty_magnitude) if mc.penalty_magnitude else None,
                yearly_limits=mc.yearly_limits,
            )
            for mc in db_constraints
        ]

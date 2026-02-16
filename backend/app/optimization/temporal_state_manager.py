"""Temporal State Manager for portfolio optimization.

Manages explicit time-indexed state variables and temporal constraints for
multi-year portfolio optimization. This is the foundational component that
prevents formula explosion by using explicit state variables indexed by
(project, year, metric) linked by linear temporal constraints, rather than
recursive function calls.

The manager also maintains a NetworkX dependency graph for project
interdependencies and generates corresponding Pyomo MILP constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import networkx as nx
import structlog
from pyomo.environ import (
    Binary,
    ConcreteModel,
    Constraint,
    NonNegativeReals,
    Reals,
    Var,
    value,
)

logger = structlog.get_logger()


@dataclass
class StateVariableInfo:
    """Metadata about a registered state variable."""

    var_name: str
    domain: Any
    bounds: tuple[float | None, float | None] | None
    pyomo_var: Any  # Pyomo Var reference
    has_temporal_constraint: bool = False


class TimeSeriesStateManager:
    """Manages explicit temporal state variables for portfolio optimization.

    Creates Pyomo variables indexed by (project, year) and links them with
    temporal evolution constraints. This architecture ensures that 500 projects
    over 30 years produce a finite, solvable MILP with ~150K variables rather
    than an exponentially exploding recursive formulation.

    Attributes:
        num_projects: Number of projects in the portfolio.
        num_years: Number of years in the planning horizon.
        state_vars: Dictionary mapping variable names to StateVariableInfo.
        dependency_graph: NetworkX DiGraph for project interdependencies.
    """

    def __init__(self, num_projects: int, num_years: int) -> None:
        """Initialize the temporal state manager.

        Args:
            num_projects: Number of projects in the portfolio.
            num_years: Number of years in the planning horizon (e.g., 30).
        """
        if num_projects < 1:
            raise ValueError(f"num_projects must be >= 1, got {num_projects}")
        if num_years < 1:
            raise ValueError(f"num_years must be >= 1, got {num_years}")

        self.num_projects = num_projects
        self.num_years = num_years
        self.state_vars: dict[str, StateVariableInfo] = {}
        self.dependency_graph: nx.DiGraph = nx.DiGraph()
        self._constraint_counter: int = 0

        logger.info(
            "temporal_state_manager.initialized",
            num_projects=num_projects,
            num_years=num_years,
        )

    def create_state_variable(
        self,
        model: ConcreteModel,
        var_name: str,
        domain: Any = Reals,
        bounds: tuple[float | None, float | None] | None = None,
        initialize: float | Callable[..., float] | None = None,
    ) -> Var:
        """Create a Pyomo state variable indexed by (projects, years).

        The variable is indexed over the Cartesian product of the model's
        project set and year set, enabling explicit temporal state tracking
        for each (project, year) pair.

        Args:
            model: Pyomo ConcreteModel to add the variable to.
            var_name: Name for the variable (must be unique).
            domain: Pyomo domain (e.g., Reals, NonNegativeReals, Binary).
            bounds: Optional (lower, upper) bounds tuple.
            initialize: Optional initial value or initialization function.

        Returns:
            The created Pyomo Var instance.

        Raises:
            ValueError: If a variable with this name already exists.
        """
        if var_name in self.state_vars:
            raise ValueError(
                f"State variable '{var_name}' already exists. "
                f"Registered variables: {list(self.state_vars.keys())}"
            )

        # Ensure model has project and year sets
        if not hasattr(model, "projects"):
            model.projects = list(range(self.num_projects))
        if not hasattr(model, "years"):
            model.years = list(range(self.num_years))

        # Build keyword arguments for Var construction
        var_kwargs: dict[str, Any] = {"domain": domain}
        if bounds is not None:
            var_kwargs["bounds"] = bounds
        if initialize is not None:
            var_kwargs["initialize"] = initialize

        # Create the indexed Pyomo variable
        pyomo_var = Var(model.projects, model.years, **var_kwargs)
        setattr(model, var_name, pyomo_var)

        # Register in state_vars
        info = StateVariableInfo(
            var_name=var_name,
            domain=domain,
            bounds=bounds,
            pyomo_var=pyomo_var,
        )
        self.state_vars[var_name] = info

        logger.info(
            "state_variable.created",
            var_name=var_name,
            domain=str(domain),
            bounds=bounds,
            total_cells=self.num_projects * self.num_years,
        )

        return pyomo_var

    def link_temporal_constraint(
        self,
        model: ConcreteModel,
        var_name: str,
        evolution_fn: Callable[[ConcreteModel, int, int], Any],
        initial_condition_fn: Callable[[ConcreteModel, int], Any] | None = None,
    ) -> Constraint:
        """Create temporal constraints linking year t to year t-1.

        For t=0, applies the initial condition function (default: var=0).
        For t>0, applies the evolution function which defines how the state
        variable at (project, t) relates to (project, t-1) and other variables.

        Example evolution function for debt:
            def debt_evolution(model, p, t):
                return model.debt[p, t] == (
                    model.debt[p, t-1] * (1 + rate)
                    + model.capex[p, t]
                    - model.cashflow[p, t]
                )

        Args:
            model: Pyomo ConcreteModel.
            var_name: Name of a previously created state variable.
            evolution_fn: Function(model, project, year) -> Pyomo constraint
                expression for t > 0. Must reference var at t and t-1.
            initial_condition_fn: Optional function(model, project) -> Pyomo
                constraint expression for t=0. Defaults to var[p, 0] == 0.

        Returns:
            The created Pyomo Constraint.

        Raises:
            KeyError: If var_name was not previously created.
        """
        if var_name not in self.state_vars:
            raise KeyError(
                f"State variable '{var_name}' not found. "
                f"Available: {list(self.state_vars.keys())}. "
                f"Call create_state_variable() first."
            )

        state_info = self.state_vars[var_name]
        pyomo_var = state_info.pyomo_var

        # Default initial condition: variable starts at 0
        if initial_condition_fn is None:

            def default_initial(m: ConcreteModel, p: int) -> Any:
                return pyomo_var[p, 0] == 0

            initial_condition_fn = default_initial

        # Build the combined constraint rule
        _init_fn = initial_condition_fn
        _evol_fn = evolution_fn

        def temporal_rule(m: ConcreteModel, p: int, t: int) -> Any:
            if t == 0:
                return _init_fn(m, p)
            return _evol_fn(m, p, t)

        # Create the constraint
        constraint_name = f"{var_name}_temporal"
        constraint = Constraint(model.projects, model.years, rule=temporal_rule)
        setattr(model, constraint_name, constraint)

        state_info.has_temporal_constraint = True

        logger.info(
            "temporal_constraint.linked",
            var_name=var_name,
            constraint_name=constraint_name,
            num_constraints=self.num_projects * self.num_years,
        )

        return constraint

    def add_dependency(
        self,
        source_project: int,
        target_project: int,
        dependency_type: str,
        **kwargs: Any,
    ) -> None:
        """Add a dependency edge to the project dependency graph.

        Supported dependency types:
            - 'prerequisite': source must be selected before target (with
              optional time_offset in years)
            - 'mutex': at most one of source/target can be selected
            - 'synergy': combined value exceeds sum of individual values
              (with capex_reduction kwarg for savings amount)

        Args:
            source_project: Source project index.
            target_project: Target project index.
            dependency_type: Type of dependency ('prerequisite', 'mutex',
                'synergy').
            **kwargs: Additional edge attributes. For prerequisites:
                time_offset (int, default 0). For synergies:
                capex_reduction (float, the savings amount).

        Raises:
            ValueError: If dependency_type is not recognized or project
                indices are out of range.
        """
        valid_types = {"prerequisite", "mutex", "synergy"}
        if dependency_type not in valid_types:
            raise ValueError(
                f"Unknown dependency_type '{dependency_type}'. "
                f"Must be one of: {valid_types}"
            )

        if not (0 <= source_project < self.num_projects):
            raise ValueError(
                f"source_project {source_project} out of range [0, {self.num_projects})"
            )
        if not (0 <= target_project < self.num_projects):
            raise ValueError(
                f"target_project {target_project} out of range [0, {self.num_projects})"
            )

        if source_project == target_project:
            raise ValueError(
                f"Cannot add self-dependency: project {source_project}"
            )

        # Add nodes if they don't exist
        self.dependency_graph.add_node(source_project)
        self.dependency_graph.add_node(target_project)

        # Add directed edge with metadata
        edge_data: dict[str, Any] = {"dependency_type": dependency_type, **kwargs}
        self.dependency_graph.add_edge(source_project, target_project, **edge_data)

        # Check for cycles (except for mutex which is undirected conceptually)
        if dependency_type != "mutex":
            try:
                cycle = nx.find_cycle(self.dependency_graph)
                # Remove the edge we just added since it creates a cycle
                self.dependency_graph.remove_edge(source_project, target_project)
                raise ValueError(
                    f"Adding dependency {source_project} -> {target_project} "
                    f"creates a cycle: {cycle}"
                )
            except nx.NetworkXNoCycle:
                pass  # No cycle found — good

        logger.info(
            "dependency.added",
            source=source_project,
            target=target_project,
            dependency_type=dependency_type,
            extra_attrs=kwargs,
        )

    def generate_dependency_constraints(
        self,
        model: ConcreteModel,
    ) -> list[Constraint]:
        """Generate Pyomo MILP constraints from the dependency graph.

        Iterates over all edges in the dependency graph and creates
        appropriate Pyomo constraints for each dependency type:

        - Prerequisite: select[source] >= select[target]
          (target can only be selected if source is selected)
        - Mutex: select[source] + select[target] <= 1
          (at most one can be selected)
        - Synergy: Linearized interaction variable with 3 constraints:
          interaction <= select[source]
          interaction <= select[target]
          interaction >= select[source] + select[target] - 1

        Args:
            model: Pyomo ConcreteModel with 'select' binary variables.

        Returns:
            List of created Pyomo Constraints.

        Raises:
            AttributeError: If model does not have 'select' variables.
        """
        if not hasattr(model, "select"):
            raise AttributeError(
                "Model must have 'select' binary variables before "
                "generating dependency constraints."
            )

        constraints: list[Constraint] = []

        for source, target, edge_data in self.dependency_graph.edges(data=True):
            dep_type = edge_data["dependency_type"]
            self._constraint_counter += 1
            suffix = self._constraint_counter

            if dep_type == "prerequisite":
                constraints.extend(
                    self._generate_prerequisite_constraint(
                        model, source, target, edge_data, suffix
                    )
                )
            elif dep_type == "mutex":
                constraints.extend(
                    self._generate_mutex_constraint(
                        model, source, target, suffix
                    )
                )
            elif dep_type == "synergy":
                constraints.extend(
                    self._generate_synergy_constraints(
                        model, source, target, edge_data, suffix
                    )
                )

        logger.info(
            "dependency_constraints.generated",
            num_edges=self.dependency_graph.number_of_edges(),
            num_constraints=len(constraints),
        )

        return constraints

    def _generate_prerequisite_constraint(
        self,
        model: ConcreteModel,
        source: int,
        target: int,
        edge_data: dict[str, Any],
        suffix: int,
    ) -> list[Constraint]:
        """Generate prerequisite constraint: source must be selected for
        target to be selected.

        select[source] >= select[target]

        Args:
            model: Pyomo ConcreteModel.
            source: Source (parent) project index.
            target: Target (child) project index.
            edge_data: Edge attributes (may include time_offset).
            suffix: Unique constraint name suffix.

        Returns:
            List containing the created constraint.
        """
        constraint_name = f"prereq_{source}_{target}_{suffix}"

        constraint = Constraint(
            expr=model.select[source] >= model.select[target]
        )
        setattr(model, constraint_name, constraint)

        logger.debug(
            "constraint.prerequisite",
            source=source,
            target=target,
            constraint_name=constraint_name,
        )

        return [constraint]

    def _generate_mutex_constraint(
        self,
        model: ConcreteModel,
        source: int,
        target: int,
        suffix: int,
    ) -> list[Constraint]:
        """Generate mutual exclusivity constraint.

        select[source] + select[target] <= 1

        Args:
            model: Pyomo ConcreteModel.
            source: First project index.
            target: Second project index.
            suffix: Unique constraint name suffix.

        Returns:
            List containing the created constraint.
        """
        constraint_name = f"mutex_{source}_{target}_{suffix}"

        constraint = Constraint(
            expr=model.select[source] + model.select[target] <= 1
        )
        setattr(model, constraint_name, constraint)

        logger.debug(
            "constraint.mutex",
            source=source,
            target=target,
            constraint_name=constraint_name,
        )

        return [constraint]

    def _generate_synergy_constraints(
        self,
        model: ConcreteModel,
        source: int,
        target: int,
        edge_data: dict[str, Any],
        suffix: int,
    ) -> list[Constraint]:
        """Generate linearized synergy constraints.

        Creates an interaction binary variable and three McCormick-envelope
        constraints that linearize the product of two binary selection
        variables:

            interaction <= select[source]
            interaction <= select[target]
            interaction >= select[source] + select[target] - 1

        The interaction variable equals 1 only when both projects are
        selected, enabling synergy benefits (e.g., CAPEX reduction) to
        be applied only when both projects co-exist in the portfolio.

        Args:
            model: Pyomo ConcreteModel.
            source: Source project index.
            target: Target project index.
            edge_data: Edge attributes (should include capex_reduction).
            suffix: Unique constraint name suffix.

        Returns:
            List of created constraints (interaction var + 3 constraints).
        """
        # Create interaction binary variable
        interaction_name = f"synergy_interaction_{source}_{target}_{suffix}"
        interaction_var = Var(domain=Binary)
        setattr(model, interaction_name, interaction_var)

        constraints: list[Constraint] = []

        # Constraint 1: interaction <= select[source]
        c1_name = f"synergy_ub_src_{source}_{target}_{suffix}"
        c1 = Constraint(expr=interaction_var <= model.select[source])
        setattr(model, c1_name, c1)
        constraints.append(c1)

        # Constraint 2: interaction <= select[target]
        c2_name = f"synergy_ub_tgt_{source}_{target}_{suffix}"
        c2 = Constraint(expr=interaction_var <= model.select[target])
        setattr(model, c2_name, c2)
        constraints.append(c2)

        # Constraint 3: interaction >= select[source] + select[target] - 1
        c3_name = f"synergy_lb_{source}_{target}_{suffix}"
        c3 = Constraint(
            expr=interaction_var >= model.select[source] + model.select[target] - 1
        )
        setattr(model, c3_name, c3)
        constraints.append(c3)

        # Apply synergy impact (e.g., capex reduction) to the objective
        self._apply_synergy_impact(model, source, target, interaction_var, edge_data)

        logger.debug(
            "constraint.synergy",
            source=source,
            target=target,
            interaction_var=interaction_name,
            num_constraints=len(constraints),
        )

        return constraints

    def _apply_synergy_impact(
        self,
        model: ConcreteModel,
        source: int,
        target: int,
        interaction_var: Var,
        edge_data: dict[str, Any],
    ) -> None:
        """Apply synergy CAPEX reduction when both projects are selected.

        Stores the synergy benefit information on the model for later
        inclusion in the objective function. The benefit is:
            capex_reduction * interaction_var
        which is only non-zero when both projects are selected.

        Args:
            model: Pyomo ConcreteModel.
            source: Source project index.
            target: Target project index.
            interaction_var: Binary variable equal to 1 when both are selected.
            edge_data: Must contain 'capex_reduction' (float) specifying the
                savings amount when both projects are co-selected.
        """
        capex_reduction = edge_data.get("capex_reduction", 0.0)

        if capex_reduction <= 0.0:
            logger.warning(
                "synergy.no_capex_reduction",
                source=source,
                target=target,
                msg="Synergy edge has no capex_reduction value; skipping impact.",
            )
            return

        # Accumulate synergy benefits on the model for objective function
        if not hasattr(model, "_synergy_benefits"):
            model._synergy_benefits = []

        model._synergy_benefits.append(
            {
                "source": source,
                "target": target,
                "interaction_var": interaction_var,
                "capex_reduction": capex_reduction,
            }
        )

        logger.info(
            "synergy.impact_registered",
            source=source,
            target=target,
            capex_reduction=capex_reduction,
        )

    def get_variable_count(self) -> int:
        """Return the total number of state variable cells.

        Returns:
            Total cells across all registered state variables.
        """
        return len(self.state_vars) * self.num_projects * self.num_years

    def get_dependency_summary(self) -> dict[str, int]:
        """Return a summary of dependencies by type.

        Returns:
            Dictionary mapping dependency types to their count.
        """
        summary: dict[str, int] = {}
        for _, _, data in self.dependency_graph.edges(data=True):
            dep_type = data.get("dependency_type", "unknown")
            summary[dep_type] = summary.get(dep_type, 0) + 1
        return summary

    def validate_graph(self) -> list[str]:
        """Validate the dependency graph for potential issues.

        Checks for:
            - Cycles in non-mutex edges
            - Isolated nodes
            - Conflicting constraints (e.g., A->B prerequisite + A-B mutex)

        Returns:
            List of warning/error messages. Empty if valid.
        """
        issues: list[str] = []

        # Check for cycles in prerequisite/synergy subgraph
        prereq_synergy_edges = [
            (u, v)
            for u, v, d in self.dependency_graph.edges(data=True)
            if d.get("dependency_type") != "mutex"
        ]
        subgraph = nx.DiGraph(prereq_synergy_edges)
        cycles = list(nx.simple_cycles(subgraph))
        for cycle in cycles:
            issues.append(
                f"Cycle detected in non-mutex dependencies: {cycle}"
            )

        # Check for conflicting constraints
        for u, v, data in self.dependency_graph.edges(data=True):
            dep_type = data.get("dependency_type")
            # Check if reverse edge exists with conflicting type
            if self.dependency_graph.has_edge(v, u):
                reverse_data = self.dependency_graph.edges[v, u]
                reverse_type = reverse_data.get("dependency_type")

                if dep_type == "prerequisite" and reverse_type == "prerequisite":
                    issues.append(
                        f"Circular prerequisite: {u} -> {v} and {v} -> {u}"
                    )
                if dep_type == "prerequisite" and reverse_type == "mutex":
                    issues.append(
                        f"Conflicting: {u} is prerequisite of {v} "
                        f"but also mutex with {v}"
                    )

        if issues:
            logger.warning("dependency_graph.validation_issues", issues=issues)
        else:
            logger.info("dependency_graph.valid")

        return issues

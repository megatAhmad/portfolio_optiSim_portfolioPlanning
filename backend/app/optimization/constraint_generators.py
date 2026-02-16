"""
Constraint Generators - Convert domain constraints to Pyomo MILP constraints

Translates the 4 constraint types defined in the database into Pyomo
MILP constraints that the solver can enforce:

1. Selection Constraints — per-project: integer/continuous selection,
   working interest bounds, instance limits, yearly timing windows
2. Selection Dependencies — between projects: prerequisite (Must),
   mutual exclusivity (Must Not), instance ratios
3. Selection Groups — named groups with collective rules:
   Exclusive, Inclusive, AtLeastN, AtMostN, ExactlyN
4. Metric Constraints — portfolio-level limits on computed metrics,
   supporting hard enforcement and soft enforcement with penalty weights

Each generator function takes the Pyomo model and constraint data,
then adds the corresponding Constraint objects to the model.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from pyomo.environ import (
    Binary,
    Constraint,
    NonNegativeReals,
    Objective,
    Var,
    maximize,
    value,
)
import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Data Transfer Objects (lightweight representations of DB models)
# ---------------------------------------------------------------------------


@dataclass
class SelectionConstraintData:
    """DTO for SelectionConstraint ORM model."""

    opportunity_id: str
    is_integer: bool
    is_active: bool
    total_wi_min: float
    total_wi_max: float
    total_instances_min: int
    total_instances_max: int
    yearly_constraints: Optional[List[Dict[str, Any]]] = None


@dataclass
class SelectionDependencyData:
    """DTO for SelectionDependency ORM model."""

    independent_opportunity_id: str
    dependent_opportunity_id: str
    must_or_must_not: str  # "Must" or "Must Not"
    time_offset: int = 0
    timing_relation: Optional[str] = None  # "Before", "After", "During"


@dataclass
class SelectionGroupData:
    """DTO for SelectionGroup ORM model."""

    group_id: str
    name: str
    group_type: str  # Exclusive, Inclusive, AtLeastN, AtMostN, ExactlyN
    member_opportunity_ids: List[str]
    total_instances_min: Optional[int] = None
    total_instances_max: Optional[int] = None
    yearly_constraints: Optional[List[Dict[str, Any]]] = None


@dataclass
class MetricConstraintData:
    """DTO for MetricConstraint ORM model."""

    metric_name: str
    constraint_type: str  # Min, Max, Range, Equal
    is_soft: bool
    default_limit: Optional[float] = None
    penalty_weight: Optional[float] = None
    penalty_magnitude: Optional[float] = None
    yearly_limits: Optional[Dict[str, float]] = None


# ---------------------------------------------------------------------------
# 1. Selection Constraints (per-project)
# ---------------------------------------------------------------------------


def add_selection_constraints(
    model: Any,
    constraints: List[SelectionConstraintData],
    projects: Set[str],
    years: List[int],
) -> int:
    """
    Add per-project selection constraints to the Pyomo model.

    Creates constraints for:
    - Binary vs. continuous selection variables
    - Working interest bounds (min/max WI)
    - Instance count limits (total and per-year)
    - Yearly timing windows (earliest/latest start years)

    Args:
        model: Pyomo ConcreteModel (must have model.select[project] variable)
        constraints: List of selection constraint data
        projects: Set of project IDs
        years: List of year indices

    Returns:
        Number of constraints added
    """
    count = 0

    for sc in constraints:
        if not sc.is_active:
            continue

        pid = sc.opportunity_id
        if pid not in projects:
            logger.warning(
                "selection_constraint_skipped",
                opportunity_id=pid,
                reason="project not in optimization universe",
            )
            continue

        # --- Working Interest Bounds ---
        # select[p] represents working interest fraction (0.0 to 1.0+)
        # For integer selection: select[p] ∈ {0, 1}
        # For continuous: total_wi_min <= select[p] <= total_wi_max

        if sc.is_integer:
            # Binary selection: project is either fully selected or not
            model.select[pid].domain = Binary
        else:
            # Continuous WI: bound the selection variable
            model.select[pid].setlb(0.0)
            model.select[pid].setub(float(sc.total_wi_max))

            # Minimum WI: if selected at all, WI must be >= min
            # Linearized: select[p] == 0 OR select[p] >= wi_min
            # Using: select[p] >= wi_min * is_selected[p]
            if sc.total_wi_min > 0:
                indicator_name = f"is_selected_{pid}"
                if not hasattr(model, indicator_name):
                    setattr(model, indicator_name, Var(domain=Binary))

                indicator = getattr(model, indicator_name)
                wi_min = float(sc.total_wi_min)
                wi_max = float(sc.total_wi_max)

                # select[p] <= wi_max * indicator
                cname_ub = f"sel_wi_ub_{pid}"
                setattr(
                    model,
                    cname_ub,
                    Constraint(expr=model.select[pid] <= wi_max * indicator),
                )
                count += 1

                # select[p] >= wi_min * indicator
                cname_lb = f"sel_wi_lb_{pid}"
                setattr(
                    model,
                    cname_lb,
                    Constraint(expr=model.select[pid] >= wi_min * indicator),
                )
                count += 1

        # --- Instance Limits (total) ---
        if hasattr(model, "instances"):
            if sc.total_instances_max < 999:
                cname = f"sel_inst_max_{pid}"
                setattr(
                    model,
                    cname,
                    Constraint(
                        expr=sum(
                            model.instances[pid, t] for t in years
                        ) <= sc.total_instances_max
                    ),
                )
                count += 1

            if sc.total_instances_min > 0:
                cname = f"sel_inst_min_{pid}"
                setattr(
                    model,
                    cname,
                    Constraint(
                        expr=sum(
                            model.instances[pid, t] for t in years
                        ) >= sc.total_instances_min * model.select[pid]
                    ),
                )
                count += 1

        # --- Yearly Timing Windows ---
        if sc.yearly_constraints and hasattr(model, "instances"):
            for yc in sc.yearly_constraints:
                year = yc["year"]
                if year not in years:
                    continue

                yc_min = yc.get("min", 0)
                yc_max = yc.get("max", 999)

                if yc_max < 999:
                    cname = f"sel_yr_max_{pid}_{year}"
                    setattr(
                        model,
                        cname,
                        Constraint(expr=model.instances[pid, year] <= yc_max),
                    )
                    count += 1

                if yc_min > 0:
                    cname = f"sel_yr_min_{pid}_{year}"
                    setattr(
                        model,
                        cname,
                        Constraint(
                            expr=model.instances[pid, year] >= yc_min * model.select[pid]
                        ),
                    )
                    count += 1

    logger.info("selection_constraints_added", count=count)
    return count


# ---------------------------------------------------------------------------
# 2. Selection Dependencies (between projects)
# ---------------------------------------------------------------------------


def add_dependency_constraints(
    model: Any,
    dependencies: List[SelectionDependencyData],
    projects: Set[str],
    years: List[int],
) -> int:
    """
    Add inter-project dependency constraints to the Pyomo model.

    Converts graph edges to MILP constraints:
    - Must (prerequisite): select[child] <= select[parent]
      With time offset: start_year[child] >= start_year[parent] + offset
    - Must Not (mutual exclusivity): select[A] + select[B] <= 1

    Args:
        model: Pyomo ConcreteModel
        dependencies: List of dependency data
        projects: Set of project IDs
        years: List of year indices

    Returns:
        Number of constraints added
    """
    count = 0

    for i, dep in enumerate(dependencies):
        parent = dep.independent_opportunity_id
        child = dep.dependent_opportunity_id

        if parent not in projects or child not in projects:
            logger.warning(
                "dependency_constraint_skipped",
                parent=parent,
                child=child,
                reason="project not in optimization universe",
            )
            continue

        if dep.must_or_must_not == "Must":
            # --- Prerequisite: child can only be selected if parent is ---
            # select[child] <= select[parent]
            cname = f"dep_prereq_{i}_{parent}_{child}"
            setattr(
                model,
                cname,
                Constraint(expr=model.select[child] <= model.select[parent]),
            )
            count += 1

            # Time offset: parent must start at least `offset` years before child
            if dep.time_offset > 0 and hasattr(model, "start_year"):
                # start_year[child] >= start_year[parent] + offset
                # Only enforced when both are selected
                big_m = max(years) + 1
                cname_time = f"dep_time_{i}_{parent}_{child}"
                setattr(
                    model,
                    cname_time,
                    Constraint(
                        expr=model.start_year[child] >=
                        model.start_year[parent] + dep.time_offset -
                        big_m * (2 - model.select[parent] - model.select[child])
                    ),
                )
                count += 1

        elif dep.must_or_must_not == "Must Not":
            # --- Mutual Exclusivity: at most one can be selected ---
            # select[A] + select[B] <= 1
            cname = f"dep_mutex_{i}_{parent}_{child}"
            setattr(
                model,
                cname,
                Constraint(
                    expr=model.select[parent] + model.select[child] <= 1
                ),
            )
            count += 1

    logger.info("dependency_constraints_added", count=count)
    return count


# ---------------------------------------------------------------------------
# 3. Selection Groups (collective constraints)
# ---------------------------------------------------------------------------


def add_group_constraints(
    model: Any,
    groups: List[SelectionGroupData],
    projects: Set[str],
) -> int:
    """
    Add selection group constraints to the Pyomo model.

    Group types and their MILP formulation:
    - Exclusive:  sum(select[p] for p in group) <= 1
    - Inclusive:   select[p1] == select[p2] == ... == select[pN]
    - AtLeastN:   sum(select[p] for p in group) >= N
    - AtMostN:    sum(select[p] for p in group) <= N
    - ExactlyN:   sum(select[p] for p in group) == N

    Args:
        model: Pyomo ConcreteModel
        groups: List of selection group data
        projects: Set of project IDs

    Returns:
        Number of constraints added
    """
    count = 0

    for group in groups:
        # Filter members to only those in the optimization universe
        members = [m for m in group.member_opportunity_ids if m in projects]

        if len(members) < 2:
            logger.warning(
                "group_constraint_skipped",
                group_id=group.group_id,
                name=group.name,
                reason=f"only {len(members)} members in optimization universe",
            )
            continue

        gtype = group.group_type
        gid = group.group_id

        if gtype == "Exclusive":
            # At most 1 member selected
            cname = f"grp_exclusive_{gid}"
            setattr(
                model,
                cname,
                Constraint(
                    expr=sum(model.select[p] for p in members) <= 1
                ),
            )
            count += 1

        elif gtype == "Inclusive":
            # All or nothing: force all members to have the same selection value
            # select[p_i] == select[p_0] for all i > 0
            for i in range(1, len(members)):
                cname = f"grp_inclusive_{gid}_{i}"
                setattr(
                    model,
                    cname,
                    Constraint(
                        expr=model.select[members[i]] == model.select[members[0]]
                    ),
                )
                count += 1

        elif gtype == "AtLeastN":
            n = group.total_instances_min or 1
            cname = f"grp_atleast_{gid}"
            setattr(
                model,
                cname,
                Constraint(
                    expr=sum(model.select[p] for p in members) >= n
                ),
            )
            count += 1

        elif gtype == "AtMostN":
            n = group.total_instances_max or 1
            cname = f"grp_atmost_{gid}"
            setattr(
                model,
                cname,
                Constraint(
                    expr=sum(model.select[p] for p in members) <= n
                ),
            )
            count += 1

        elif gtype == "ExactlyN":
            n = group.total_instances_min or group.total_instances_max or 1
            cname = f"grp_exactly_{gid}"
            setattr(
                model,
                cname,
                Constraint(
                    expr=sum(model.select[p] for p in members) == n
                ),
            )
            count += 1

        else:
            logger.warning(
                "unknown_group_type",
                group_id=gid,
                group_type=gtype,
            )

    logger.info("group_constraints_added", count=count)
    return count


# ---------------------------------------------------------------------------
# 4. Metric Constraints (portfolio-level)
# ---------------------------------------------------------------------------


def add_metric_constraints(
    model: Any,
    constraints: List[MetricConstraintData],
    projects: Set[str],
    years: List[int],
    metric_values: Dict[str, Dict[str, Dict[int, float]]],
) -> tuple[int, float]:
    """
    Add portfolio-level metric constraints to the Pyomo model.

    Supports both hard and soft enforcement:
    - Hard: standard MILP constraint, model infeasible if violated
    - Soft: slack variable + penalty in objective
      penalty_term = weight * (slack / magnitude)

    Args:
        model: Pyomo ConcreteModel
        constraints: List of metric constraint data
        projects: Set of project IDs
        years: List of year indices
        metric_values: Nested dict of metric_name -> project_id -> year -> value
            Pre-computed metric values for each project-year combination

    Returns:
        tuple of (num_constraints_added, total_penalty_terms_added_to_objective)
    """
    count = 0
    total_penalty = 0.0

    for i, mc in enumerate(constraints):
        mname = mc.metric_name

        if mname not in metric_values:
            logger.warning(
                "metric_constraint_skipped",
                metric_name=mname,
                reason="metric not found in computed values",
            )
            continue

        for year in years:
            # Get the limit for this year
            limit = _get_yearly_limit(mc, year)
            if limit is None:
                continue

            # Build the portfolio metric expression for this year
            # sum over all projects: select[p] * metric_value[p][year]
            portfolio_metric = sum(
                model.select[p] * metric_values[mname].get(p, {}).get(year, 0.0)
                for p in projects
                if p in metric_values[mname]
            )

            if mc.is_soft:
                # --- Soft Constraint: add slack variable and penalty ---
                slack_name = f"slack_{mname}_{year}"
                if not hasattr(model, slack_name):
                    setattr(
                        model,
                        slack_name,
                        Var(domain=NonNegativeReals, doc=f"Slack for {mname} at year {year}"),
                    )

                slack = getattr(model, slack_name)
                weight = float(mc.penalty_weight or 1.0)
                magnitude = float(mc.penalty_magnitude or 1.0)

                # Add constraint with slack
                if mc.constraint_type == "Max":
                    cname = f"mc_soft_max_{i}_{mname}_{year}"
                    setattr(
                        model,
                        cname,
                        Constraint(expr=portfolio_metric <= limit + slack),
                    )
                elif mc.constraint_type == "Min":
                    cname = f"mc_soft_min_{i}_{mname}_{year}"
                    setattr(
                        model,
                        cname,
                        Constraint(expr=portfolio_metric >= limit - slack),
                    )
                elif mc.constraint_type == "Equal":
                    cname = f"mc_soft_eq_{i}_{mname}_{year}"
                    setattr(
                        model,
                        cname,
                        Constraint(expr=portfolio_metric == limit + slack),
                    )
                else:
                    continue

                # Record penalty for adding to objective later
                # penalty = weight * (slack / magnitude)
                total_penalty += weight / magnitude
                count += 1

            else:
                # --- Hard Constraint: standard MILP constraint ---
                if mc.constraint_type == "Max":
                    cname = f"mc_hard_max_{i}_{mname}_{year}"
                    setattr(
                        model,
                        cname,
                        Constraint(expr=portfolio_metric <= limit),
                    )
                elif mc.constraint_type == "Min":
                    cname = f"mc_hard_min_{i}_{mname}_{year}"
                    setattr(
                        model,
                        cname,
                        Constraint(expr=portfolio_metric >= limit),
                    )
                elif mc.constraint_type == "Equal":
                    cname = f"mc_hard_eq_{i}_{mname}_{year}"
                    setattr(
                        model,
                        cname,
                        Constraint(expr=portfolio_metric == limit),
                    )
                elif mc.constraint_type == "Range":
                    # Range needs both min and max from yearly_limits
                    logger.debug(
                        "range_constraint_placeholder",
                        metric_name=mname,
                        year=year,
                    )
                    continue

                count += 1

    logger.info(
        "metric_constraints_added",
        count=count,
        has_soft_constraints=total_penalty > 0,
    )
    return count, total_penalty


def _get_yearly_limit(mc: MetricConstraintData, year: int) -> Optional[float]:
    """Get the effective limit for a specific year, with override support."""
    # Check for year-specific override
    if mc.yearly_limits and str(year) in mc.yearly_limits:
        return float(mc.yearly_limits[str(year)])

    # Fall back to default
    if mc.default_limit is not None:
        return float(mc.default_limit)

    return None


# ---------------------------------------------------------------------------
# 5. Synergy Constraints (interaction between selected projects)
# ---------------------------------------------------------------------------


def add_synergy_constraints(
    model: Any,
    synergy_pairs: List[tuple[str, str, float]],
    projects: Set[str],
) -> int:
    """
    Add synergy interaction constraints for project pairs.

    When two projects are both selected, their combined value includes
    a synergy bonus (e.g., shared facilities reduce CAPEX by $50M).

    Linearized interaction:
        interaction[A,B] <= select[A]
        interaction[A,B] <= select[B]
        interaction[A,B] >= select[A] + select[B] - 1

    The interaction variable is 1 only when both A and B are selected.
    Synergy value is then: synergy_bonus * interaction[A,B]

    Args:
        model: Pyomo ConcreteModel
        synergy_pairs: List of (project_A, project_B, synergy_value) tuples
        projects: Set of project IDs in optimization universe

    Returns:
        Number of constraints added
    """
    count = 0

    for idx, (proj_a, proj_b, synergy_val) in enumerate(synergy_pairs):
        if proj_a not in projects or proj_b not in projects:
            continue

        # Create interaction binary variable
        ivar_name = f"synergy_interaction_{idx}"
        setattr(model, ivar_name, Var(domain=Binary))
        ivar = getattr(model, ivar_name)

        # interaction <= select[A]
        cname_a = f"synergy_ub_a_{idx}"
        setattr(model, cname_a, Constraint(expr=ivar <= model.select[proj_a]))
        count += 1

        # interaction <= select[B]
        cname_b = f"synergy_ub_b_{idx}"
        setattr(model, cname_b, Constraint(expr=ivar <= model.select[proj_b]))
        count += 1

        # interaction >= select[A] + select[B] - 1
        cname_lb = f"synergy_lb_{idx}"
        setattr(
            model,
            cname_lb,
            Constraint(
                expr=ivar >= model.select[proj_a] + model.select[proj_b] - 1
            ),
        )
        count += 1

    logger.info("synergy_constraints_added", count=count, num_pairs=len(synergy_pairs))
    return count


# ---------------------------------------------------------------------------
# 6. Shared Infrastructure Constraints
# ---------------------------------------------------------------------------


def add_shared_infrastructure_constraints(
    model: Any,
    infrastructure: List[Dict[str, Any]],
    projects: Set[str],
    years: List[int],
) -> int:
    """
    Add shared infrastructure capacity constraints.

    Multiple projects may compete for limited physical capacity
    (e.g., platform slots, pipeline throughput, power supply).

    For each shared resource:
        sum(usage[p] * select[p] for p in competing_projects) <= capacity

    Args:
        model: Pyomo ConcreteModel
        infrastructure: List of dicts with keys:
            - name: resource name
            - capacity: total capacity
            - projects: dict of project_id -> usage_per_year
        projects: Set of project IDs
        years: List of year indices

    Returns:
        Number of constraints added
    """
    count = 0

    for idx, infra in enumerate(infrastructure):
        capacity = infra["capacity"]
        infra_projects = infra["projects"]

        for year in years:
            # Sum usage across all competing projects for this year
            usage_expr = sum(
                model.select[pid] * infra_projects[pid].get(year, 0.0)
                for pid in infra_projects
                if pid in projects
            )

            cname = f"infra_{idx}_{infra['name']}_{year}"
            setattr(
                model,
                cname,
                Constraint(expr=usage_expr <= capacity),
            )
            count += 1

    logger.info("infrastructure_constraints_added", count=count)
    return count


# ---------------------------------------------------------------------------
# Aggregate: Add All Constraints
# ---------------------------------------------------------------------------


def add_all_constraints(
    model: Any,
    selection_constraints: List[SelectionConstraintData],
    dependencies: List[SelectionDependencyData],
    groups: List[SelectionGroupData],
    metric_constraints: List[MetricConstraintData],
    projects: Set[str],
    years: List[int],
    metric_values: Dict[str, Dict[str, Dict[int, float]]],
    synergy_pairs: Optional[List[tuple[str, str, float]]] = None,
    infrastructure: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, int]:
    """
    Add all constraint types to the Pyomo model.

    Convenience function that calls all individual constraint generators.

    Returns:
        Dict mapping constraint type to count of constraints added
    """
    counts: Dict[str, int] = {}

    counts["selection"] = add_selection_constraints(
        model, selection_constraints, projects, years
    )

    counts["dependency"] = add_dependency_constraints(
        model, dependencies, projects, years
    )

    counts["group"] = add_group_constraints(model, groups, projects)

    mc_count, penalty_total = add_metric_constraints(
        model, metric_constraints, projects, years, metric_values
    )
    counts["metric"] = mc_count

    if synergy_pairs:
        counts["synergy"] = add_synergy_constraints(
            model, synergy_pairs, projects
        )

    if infrastructure:
        counts["infrastructure"] = add_shared_infrastructure_constraints(
            model, infrastructure, projects, years
        )

    total = sum(counts.values())
    logger.info("all_constraints_added", total=total, breakdown=counts)

    return counts

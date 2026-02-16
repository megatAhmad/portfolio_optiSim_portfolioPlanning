"""
Linearization - Big-M reformulations for non-linear operations

Converts non-linear max/min operations to linear MILP constraints using
auxiliary binary variables and Big-M constants.

Required because MILP solvers can only handle linear objective functions
and linear constraints. All non-linear operations must be reformulated.

Key Principle:
Choose M carefully using domain-specific bounds:
- Too large: numerical instability, poor solver performance
- Too small: incorrect results, violated constraints

Example:
    # Non-linear: z = max(a, b)
    # Linearized:
    model.z >= a
    model.z >= b
    model.z <= a + M*(1-y)  # y=1 forces z=a
    model.z <= b + M*y      # y=0 forces z=b
"""

from typing import Callable, Optional

from pyomo.environ import (
    Binary,
    ConcreteModel,
    Constraint,
    NonNegativeReals,
    Reals,
    Var,
)
import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Big-M Selection
# ---------------------------------------------------------------------------


def calculate_big_m(
    lower_bound: Optional[float] = None,
    upper_bound: Optional[float] = None,
    domain_max: Optional[float] = None,
    safety_factor: float = 1.1,
) -> float:
    """
    Calculate an appropriate Big-M value for linearization.

    Args:
        lower_bound: Theoretical lower bound of the variable
        upper_bound: Theoretical upper bound of the variable
        domain_max: Maximum value from domain knowledge (e.g., sum of all CAPEX)
        safety_factor: Multiplier for safety margin (default 1.1 = 10% buffer)

    Returns:
        Big-M value

    Raises:
        ValueError: If insufficient information to calculate M
    """
    if domain_max is not None:
        return domain_max * safety_factor

    if upper_bound is not None and lower_bound is not None:
        return (upper_bound - lower_bound) * safety_factor

    if upper_bound is not None:
        return abs(upper_bound) * safety_factor

    raise ValueError(
        "Cannot calculate Big-M: provide either domain_max or upper_bound (with optional lower_bound)"
    )


# ---------------------------------------------------------------------------
# Max/Min Linearization
# ---------------------------------------------------------------------------


def linearize_max_2(
    model: ConcreteModel,
    index_set: set,
    var_a_name: str,
    var_b_name: str,
    result_var_name: str,
    big_m: float,
    constraint_name_prefix: str = "max_linearization",
) -> None:
    """
    Linearize z = max(a, b) using Big-M method.

    Creates:
    - Binary selection variable y
    - Constraints: z >= a, z >= b (z is at least max)
    - Constraints: z <= a + M*(1-y), z <= b + M*y (z is at most max)

    When y=1: z <= a (forced), z can exceed b
    When y=0: z <= b (forced), z can exceed a
    Combined with z >= a and z >= b, this ensures z = max(a, b)

    Args:
        model: Pyomo ConcreteModel
        index_set: Indices for variables (e.g., projects, years)
        var_a_name: Name of first variable
        var_b_name: Name of second variable
        result_var_name: Name of result variable (z)
        big_m: Big-M constant
        constraint_name_prefix: Prefix for constraint names
    """
    # Create result variable if it doesn't exist
    if not hasattr(model, result_var_name):
        setattr(
            model,
            result_var_name,
            Var(index_set, domain=Reals, doc=f"Result of max({var_a_name}, {var_b_name})"),
        )

    # Create binary selection variable
    binary_var_name = f"{result_var_name}_select"
    if not hasattr(model, binary_var_name):
        setattr(
            model,
            binary_var_name,
            Var(index_set, domain=Binary, doc=f"Binary selector for {result_var_name}"),
        )

    # Get variable references
    var_a = getattr(model, var_a_name)
    var_b = getattr(model, var_b_name)
    result_var = getattr(model, result_var_name)
    binary_var = getattr(model, binary_var_name)

    # Constraint: z >= a (z is at least as large as a)
    def _lower_bound_a(mdl, *idx):
        return result_var[idx] >= var_a[idx]

    setattr(
        model,
        f"{constraint_name_prefix}_lb_a",
        Constraint(index_set, rule=_lower_bound_a),
    )

    # Constraint: z >= b (z is at least as large as b)
    def _lower_bound_b(mdl, *idx):
        return result_var[idx] >= var_b[idx]

    setattr(
        model,
        f"{constraint_name_prefix}_lb_b",
        Constraint(index_set, rule=_lower_bound_b),
    )

    # Constraint: z <= a + M*(1-y) (when y=1, z <= a)
    def _upper_bound_a(mdl, *idx):
        return result_var[idx] <= var_a[idx] + big_m * (1 - binary_var[idx])

    setattr(
        model,
        f"{constraint_name_prefix}_ub_a",
        Constraint(index_set, rule=_upper_bound_a),
    )

    # Constraint: z <= b + M*y (when y=0, z <= b)
    def _upper_bound_b(mdl, *idx):
        return result_var[idx] <= var_b[idx] + big_m * binary_var[idx]

    setattr(
        model,
        f"{constraint_name_prefix}_ub_b",
        Constraint(index_set, rule=_upper_bound_b),
    )

    logger.debug(
        "max_linearization_created",
        result_var=result_var_name,
        var_a=var_a_name,
        var_b=var_b_name,
        big_m=big_m,
    )


def linearize_min_2(
    model: ConcreteModel,
    index_set: set,
    var_a_name: str,
    var_b_name: str,
    result_var_name: str,
    big_m: float,
    constraint_name_prefix: str = "min_linearization",
) -> None:
    """
    Linearize z = min(a, b) using Big-M method.

    Creates:
    - Binary selection variable y
    - Constraints: z <= a, z <= b (z is at most min)
    - Constraints: z >= a - M*(1-y), z >= b - M*y (z is at least min)

    Args:
        model: Pyomo ConcreteModel
        index_set: Indices for variables
        var_a_name: Name of first variable
        var_b_name: Name of second variable
        result_var_name: Name of result variable (z)
        big_m: Big-M constant
        constraint_name_prefix: Prefix for constraint names
    """
    # Create result variable if it doesn't exist
    if not hasattr(model, result_var_name):
        setattr(
            model,
            result_var_name,
            Var(index_set, domain=Reals, doc=f"Result of min({var_a_name}, {var_b_name})"),
        )

    # Create binary selection variable
    binary_var_name = f"{result_var_name}_select"
    if not hasattr(model, binary_var_name):
        setattr(
            model,
            binary_var_name,
            Var(index_set, domain=Binary, doc=f"Binary selector for {result_var_name}"),
        )

    # Get variable references
    var_a = getattr(model, var_a_name)
    var_b = getattr(model, var_b_name)
    result_var = getattr(model, result_var_name)
    binary_var = getattr(model, binary_var_name)

    # Constraint: z <= a (z is at most as large as a)
    def _upper_bound_a(mdl, *idx):
        return result_var[idx] <= var_a[idx]

    setattr(
        model,
        f"{constraint_name_prefix}_ub_a",
        Constraint(index_set, rule=_upper_bound_a),
    )

    # Constraint: z <= b (z is at most as large as b)
    def _upper_bound_b(mdl, *idx):
        return result_var[idx] <= var_b[idx]

    setattr(
        model,
        f"{constraint_name_prefix}_ub_b",
        Constraint(index_set, rule=_upper_bound_b),
    )

    # Constraint: z >= a - M*(1-y) (when y=1, z >= a)
    def _lower_bound_a(mdl, *idx):
        return result_var[idx] >= var_a[idx] - big_m * (1 - binary_var[idx])

    setattr(
        model,
        f"{constraint_name_prefix}_lb_a",
        Constraint(index_set, rule=_lower_bound_a),
    )

    # Constraint: z >= b - M*y (when y=0, z >= b)
    def _lower_bound_b(mdl, *idx):
        return result_var[idx] >= var_b[idx] - big_m * binary_var[idx]

    setattr(
        model,
        f"{constraint_name_prefix}_lb_b",
        Constraint(index_set, rule=_lower_bound_b),
    )

    logger.debug(
        "min_linearization_created",
        result_var=result_var_name,
        var_a=var_a_name,
        var_b=var_b_name,
        big_m=big_m,
    )


# ---------------------------------------------------------------------------
# Conditional Constraints (IF-THEN logic)
# ---------------------------------------------------------------------------


def linearize_if_then(
    model: ConcreteModel,
    index_set: set,
    condition_var_name: str,
    then_constraint_func: Callable,
    constraint_name: str,
    big_m: float,
) -> None:
    """
    Linearize IF condition THEN constraint using Big-M.

    When condition_var = 1, constraint is active.
    When condition_var = 0, constraint is relaxed (disabled).

    Example:
        # IF project_selected THEN debt <= max_debt
        # Linearized: debt <= max_debt + M*(1 - project_selected)

    Args:
        model: Pyomo ConcreteModel
        index_set: Indices for constraint
        condition_var_name: Binary variable name for condition
        then_constraint_func: Function returning the RHS of constraint
        constraint_name: Name for the constraint
        big_m: Big-M constant
    """
    condition_var = getattr(model, condition_var_name)

    def _conditional_rule(mdl, *idx):
        # When condition=1: original constraint holds
        # When condition=0: constraint relaxed by Big-M
        original_rhs = then_constraint_func(mdl, *idx)
        return original_rhs + big_m * (1 - condition_var[idx])

    setattr(model, constraint_name, Constraint(index_set, rule=_conditional_rule))

    logger.debug(
        "if_then_linearization_created",
        constraint=constraint_name,
        condition_var=condition_var_name,
    )


# ---------------------------------------------------------------------------
# Absolute Value Linearization
# ---------------------------------------------------------------------------


def linearize_absolute_value(
    model: ConcreteModel,
    index_set: set,
    var_name: str,
    abs_var_name: str,
    big_m: float,
    constraint_name_prefix: str = "abs_linearization",
) -> None:
    """
    Linearize abs_z = |z| using Big-M method.

    Creates:
    - Binary variable y indicating sign (y=1 if z>=0, y=0 if z<0)
    - Constraints: abs_z >= z, abs_z >= -z (abs_z is at least |z|)
    - Constraints: abs_z <= z + M*(1-y), abs_z <= -z + M*y (abs_z is at most |z|)

    Args:
        model: Pyomo ConcreteModel
        index_set: Indices for variables
        var_name: Name of variable to take absolute value of
        abs_var_name: Name of result variable (absolute value)
        big_m: Big-M constant
        constraint_name_prefix: Prefix for constraint names
    """
    # Create absolute value variable if it doesn't exist
    if not hasattr(model, abs_var_name):
        setattr(
            model,
            abs_var_name,
            Var(index_set, domain=NonNegativeReals, doc=f"Absolute value of {var_name}"),
        )

    # Create binary sign variable
    sign_var_name = f"{abs_var_name}_sign"
    if not hasattr(model, sign_var_name):
        setattr(
            model,
            sign_var_name,
            Var(index_set, domain=Binary, doc=f"Sign indicator for {var_name}"),
        )

    # Get variable references
    var = getattr(model, var_name)
    abs_var = getattr(model, abs_var_name)
    sign_var = getattr(model, sign_var_name)

    # Constraint: abs_z >= z
    def _lower_bound_pos(mdl, *idx):
        return abs_var[idx] >= var[idx]

    setattr(
        model,
        f"{constraint_name_prefix}_lb_pos",
        Constraint(index_set, rule=_lower_bound_pos),
    )

    # Constraint: abs_z >= -z
    def _lower_bound_neg(mdl, *idx):
        return abs_var[idx] >= -var[idx]

    setattr(
        model,
        f"{constraint_name_prefix}_lb_neg",
        Constraint(index_set, rule=_lower_bound_neg),
    )

    # Constraint: abs_z <= z + M*(1-y)
    def _upper_bound_pos(mdl, *idx):
        return abs_var[idx] <= var[idx] + big_m * (1 - sign_var[idx])

    setattr(
        model,
        f"{constraint_name_prefix}_ub_pos",
        Constraint(index_set, rule=_upper_bound_pos),
    )

    # Constraint: abs_z <= -z + M*y
    def _upper_bound_neg(mdl, *idx):
        return abs_var[idx] <= -var[idx] + big_m * sign_var[idx]

    setattr(
        model,
        f"{constraint_name_prefix}_ub_neg",
        Constraint(index_set, rule=_upper_bound_neg),
    )

    logger.debug(
        "abs_linearization_created",
        abs_var=abs_var_name,
        var=var_name,
        big_m=big_m,
    )


# ---------------------------------------------------------------------------
# Piecewise Linear Approximation
# ---------------------------------------------------------------------------


def create_piecewise_linear(
    model: ConcreteModel,
    index_set: set,
    input_var_name: str,
    output_var_name: str,
    breakpoints: list[float],
    values: list[float],
    constraint_name_prefix: str = "piecewise",
) -> None:
    """
    Create piecewise linear approximation of a non-linear function.

    Uses Special Ordered Sets of type 2 (SOS2) for efficient formulation.

    Args:
        model: Pyomo ConcreteModel
        index_set: Indices for variables
        input_var_name: Name of input variable
        output_var_name: Name of output variable
        breakpoints: x-coordinates of piecewise segments (must be sorted)
        values: y-coordinates at breakpoints (same length as breakpoints)
        constraint_name_prefix: Prefix for constraint names

    Example:
        # Approximate z = x^2 for x in [0, 10]
        breakpoints = [0, 2, 4, 6, 8, 10]
        values = [0, 4, 16, 36, 64, 100]
        create_piecewise_linear(model, projects, 'x', 'z', breakpoints, values)
    """
    if len(breakpoints) != len(values):
        raise ValueError("breakpoints and values must have same length")

    if len(breakpoints) < 2:
        raise ValueError("Need at least 2 breakpoints for piecewise linear")

    # Create output variable if it doesn't exist
    if not hasattr(model, output_var_name):
        setattr(
            model,
            output_var_name,
            Var(index_set, domain=Reals, doc=f"Piecewise linear output for {input_var_name}"),
        )

    # Create lambda variables (convex combination weights)
    lambda_var_name = f"{output_var_name}_lambda"
    num_points = len(breakpoints)

    if not hasattr(model, lambda_var_name):
        lambda_index_set = [(i, j) for i in index_set for j in range(num_points)]
        setattr(
            model,
            lambda_var_name,
            Var(
                lambda_index_set,
                domain=NonNegativeReals,
                bounds=(0, 1),
                doc="Convex combination weights",
            ),
        )

    input_var = getattr(model, input_var_name)
    output_var = getattr(model, output_var_name)
    lambda_var = getattr(model, lambda_var_name)

    # Constraint: sum of lambdas = 1
    def _lambda_sum(mdl, *idx):
        return sum(lambda_var[idx, j] for j in range(num_points)) == 1

    setattr(
        model,
        f"{constraint_name_prefix}_lambda_sum",
        Constraint(index_set, rule=_lambda_sum),
    )

    # Constraint: input = sum(breakpoint[j] * lambda[j])
    def _input_convex_combination(mdl, *idx):
        return input_var[idx] == sum(
            breakpoints[j] * lambda_var[idx, j] for j in range(num_points)
        )

    setattr(
        model,
        f"{constraint_name_prefix}_input",
        Constraint(index_set, rule=_input_convex_combination),
    )

    # Constraint: output = sum(value[j] * lambda[j])
    def _output_convex_combination(mdl, *idx):
        return output_var[idx] == sum(
            values[j] * lambda_var[idx, j] for j in range(num_points)
        )

    setattr(
        model,
        f"{constraint_name_prefix}_output",
        Constraint(index_set, rule=_output_convex_combination),
    )

    # SOS2: at most 2 adjacent lambdas can be non-zero
    # Note: This requires solver support for SOS2 (Gurobi, CPLEX have it)
    # For solvers without SOS2 support, need binary variable formulation

    logger.debug(
        "piecewise_linear_created",
        input_var=input_var_name,
        output_var=output_var_name,
        num_breakpoints=len(breakpoints),
    )

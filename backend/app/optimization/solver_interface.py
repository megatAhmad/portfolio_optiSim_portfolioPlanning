"""
Solver Interface - Pluggable MILP solver abstraction

Provides a unified interface for multiple optimization solvers (open-source and commercial).
Users can select their preferred solver via configuration without code changes.

Supported solvers:
- HiGHS (open-source, recommended default)
- Google OR-Tools (open-source)
- GLPK (open-source)
- CBC/CLP (COIN-OR, open-source)
- Gurobi (commercial)
- CPLEX (commercial)

All solvers accessed via Pyomo's SolverFactory for consistency.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from pyomo.environ import SolverFactory, SolverStatus, TerminationCondition
from pyomo.opt import SolverResults
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Solver Registry
# ---------------------------------------------------------------------------


class SolverType(str, Enum):
    """Supported optimization solvers."""

    HIGHS = "highs"
    ORTOOLS = "or-tools"
    GLPK = "glpk"
    CBC = "cbc"
    GUROBI = "gurobi"
    CPLEX = "cplex"


SOLVER_DISPLAY_NAMES: Dict[str, str] = {
    "highs": "HiGHS",
    "or-tools": "Google OR-Tools",
    "glpk": "GLPK",
    "cbc": "COIN-OR CBC",
    "gurobi": "Gurobi",
    "cplex": "CPLEX",
}


# Open-source solvers that should work without license
OPEN_SOURCE_SOLVERS = {
    SolverType.HIGHS,
    SolverType.ORTOOLS,
    SolverType.GLPK,
    SolverType.CBC,
}

# Commercial solvers requiring license
COMMERCIAL_SOLVERS = {
    SolverType.GUROBI,
    SolverType.CPLEX,
}


@dataclass
class SolverStats:
    """Statistics and metadata from a solver run."""

    solver_name: str
    solver_version: str | None
    status: str
    termination_condition: str
    solve_time_seconds: float
    mip_gap: float | None
    objective_value: float | None
    num_variables: int
    num_constraints: int
    num_binary_variables: int | None = None
    num_integer_variables: int | None = None
    iterations: int | None = None
    nodes_explored: int | None = None
    precomputed_projects: int | None = None
    optimization_method: str = "MILP"


# ---------------------------------------------------------------------------
# Solver Detection and Availability
# ---------------------------------------------------------------------------


def detect_available_solvers() -> list[str]:
    """
    Auto-detect which solvers are installed and functional.

    Tests each solver by attempting to create a SolverFactory instance.
    Returns list of available solver names.
    """
    available = []

    for solver in SolverType:
        try:
            opt = SolverFactory(solver.value)
            if opt.available():
                available.append(solver.value)
                logger.debug("solver_detected", solver=solver.value)
        except Exception as e:
            logger.debug("solver_not_available", solver=solver.value, error=str(e))

    return available


def get_default_solver() -> str:
    """
    Get the default solver from config, falling back to best available.

    Priority:
    1. User-configured DEFAULT_SOLVER (if available)
    2. HiGHS (recommended open-source default)
    3. OR-Tools
    4. CBC
    5. GLPK
    6. First available solver

    Raises ValueError if no solvers are available.
    """
    available = detect_available_solvers()

    if not available:
        raise ValueError(
            "No MILP solvers available. Install at least one: "
            "HiGHS (pip install highspy), OR-Tools (pip install ortools), "
            "GLPK (pip install glpk), or CBC (pip install coinor.cbc)"
        )

    # Try configured default first
    if settings.DEFAULT_SOLVER and settings.DEFAULT_SOLVER in available:
        return settings.DEFAULT_SOLVER

    # Fall back to priority order
    priority_order = [
        SolverType.HIGHS.value,
        SolverType.ORTOOLS.value,
        SolverType.CBC.value,
        SolverType.GLPK.value,
    ]

    for solver in priority_order:
        if solver in available:
            logger.info(
                "default_solver_selected",
                solver=solver,
                reason=f"Configured solver '{settings.DEFAULT_SOLVER}' not available"
                if settings.DEFAULT_SOLVER
                else "Using recommended default",
            )
            return solver

    # Last resort: first available
    return available[0]


# ---------------------------------------------------------------------------
# Solver Interface
# ---------------------------------------------------------------------------


class SolverInterface:
    """
    Unified interface for solving Pyomo MILP models with multiple solvers.

    Handles:
    - Solver selection and validation
    - Solver-specific option mapping
    - Result extraction and normalization
    - Error handling and reporting
    - Performance statistics collection
    """

    def __init__(self, solver_name: str | None = None):
        """
        Initialize solver interface.

        Args:
            solver_name: Solver to use. If None, uses get_default_solver().
        """
        self.solver_name = solver_name or get_default_solver()
        self._validate_solver()

        # Create solver instance
        try:
            self.solver = SolverFactory(self.solver_name)
        except Exception as e:
            raise ValueError(
                f"Failed to create solver '{self.solver_name}': {str(e)}"
            ) from e

        if not self.solver.available():
            raise ValueError(
                f"Solver '{self.solver_name}' is not available. "
                f"Available solvers: {', '.join(detect_available_solvers())}"
            )

        logger.info(
            "solver_initialized",
            solver=self.solver_name,
            display_name=SOLVER_DISPLAY_NAMES.get(self.solver_name, self.solver_name),
        )

    def _validate_solver(self) -> None:
        """Validate that the requested solver exists and is available."""
        available = detect_available_solvers()

        if self.solver_name not in available:
            raise ValueError(
                f"Solver '{self.solver_name}' is not available. "
                f"Available solvers: {', '.join(available)}"
            )

    def solve(
        self,
        model: Any,
        time_limit_seconds: Optional[int] = None,
        mip_gap: Optional[float] = None,
        verbose: bool = False,
        **solver_options: Any,
    ) -> tuple[SolverResults, SolverStats]:
        """
        Solve a Pyomo MILP model.

        Args:
            model: Pyomo ConcreteModel to solve
            time_limit_seconds: Maximum solve time (solver-specific default if None)
            mip_gap: Target MIP gap (0.001 = 0.1% = 99.9% optimal)
            verbose: Enable solver output to console
            **solver_options: Additional solver-specific options

        Returns:
            tuple of (SolverResults, SolverStats)

        Raises:
            RuntimeError: If solver fails or model is infeasible
        """
        # Build solver options based on solver type
        options = self._build_solver_options(
            time_limit_seconds=time_limit_seconds,
            mip_gap=mip_gap,
            verbose=verbose,
            **solver_options,
        )

        logger.info(
            "optimization_started",
            solver=self.solver_name,
            time_limit=time_limit_seconds,
            mip_gap=mip_gap,
        )

        # Solve the model
        try:
            results: SolverResults = self.solver.solve(
                model,
                tee=verbose,
                options=options,
            )
        except Exception as e:
            logger.error("solver_failed", solver=self.solver_name, error=str(e))
            raise RuntimeError(f"Solver failed: {str(e)}") from e

        # Extract statistics
        stats = self._extract_stats(model, results)

        logger.info(
            "optimization_completed",
            solver=self.solver_name,
            status=stats.status,
            termination=stats.termination_condition,
            solve_time=stats.solve_time_seconds,
            mip_gap=stats.mip_gap,
            objective=stats.objective_value,
        )

        # Check for infeasibility or errors
        if results.solver.status != SolverStatus.ok:
            raise RuntimeError(
                f"Solver status: {results.solver.status}. "
                f"Termination: {results.solver.termination_condition}"
            )

        if results.solver.termination_condition == TerminationCondition.infeasible:
            raise RuntimeError(
                "Model is infeasible. Check constraints for conflicts."
            )

        return results, stats

    def _build_solver_options(
        self,
        time_limit_seconds: Optional[int],
        mip_gap: Optional[float],
        verbose: bool,
        **extra_options: Any,
    ) -> Dict[str, Any]:
        """
        Build solver-specific options dictionary.

        Different solvers use different option names for the same concept.
        This method normalizes common options across solvers.
        """
        options: Dict[str, Any] = {}

        # Time limit (solver-specific names)
        if time_limit_seconds is not None:
            if self.solver_name == SolverType.HIGHS.value:
                options["time_limit"] = time_limit_seconds
            elif self.solver_name == SolverType.GUROBI.value:
                options["TimeLimit"] = time_limit_seconds
            elif self.solver_name == SolverType.CPLEX.value:
                options["timelimit"] = time_limit_seconds
            elif self.solver_name in [SolverType.CBC.value, SolverType.GLPK.value]:
                options["sec"] = time_limit_seconds
            # OR-Tools uses different mechanism, handle separately if needed

        # MIP gap (solver-specific names)
        if mip_gap is not None:
            if self.solver_name == SolverType.HIGHS.value:
                options["mip_rel_gap"] = mip_gap
            elif self.solver_name == SolverType.GUROBI.value:
                options["MIPGap"] = mip_gap
            elif self.solver_name == SolverType.CPLEX.value:
                options["mip_tolerances_mipgap"] = mip_gap
            elif self.solver_name == SolverType.CBC.value:
                options["ratio"] = mip_gap
            # GLPK has limited MIP gap control

        # Verbosity
        if not verbose:
            if self.solver_name == SolverType.HIGHS.value:
                options["log_to_console"] = False
            elif self.solver_name == SolverType.GUROBI.value:
                options["OutputFlag"] = 0
            elif self.solver_name == SolverType.CPLEX.value:
                options["mip_display"] = 0

        # Merge with user-provided options (user options override defaults)
        options.update(extra_options)

        return options

    def _extract_stats(self, model: Any, results: SolverResults) -> SolverStats:
        """
        Extract solver statistics from results.

        Normalizes across different solver result formats.
        """
        # Basic stats available from all solvers
        stats = SolverStats(
            solver_name=self.solver_name,
            solver_version=getattr(results.solver, "version", None),
            status=str(results.solver.status),
            termination_condition=str(results.solver.termination_condition),
            solve_time_seconds=results.solver.time or 0.0,
            mip_gap=None,
            objective_value=None,
            num_variables=model.nvariables() if hasattr(model, "nvariables") else 0,
            num_constraints=model.nconstraints()
            if hasattr(model, "nconstraints")
            else 0,
        )

        # Extract objective value
        if hasattr(results.problem, "upper_bound") and results.problem.upper_bound is not None:
            stats.objective_value = results.problem.upper_bound
        elif hasattr(results.problem, "lower_bound") and results.problem.lower_bound is not None:
            stats.objective_value = results.problem.lower_bound

        # Extract MIP gap (solver-specific)
        if hasattr(results, "problem") and hasattr(results.problem, "upper_bound") and hasattr(results.problem, "lower_bound"):
            ub = results.problem.upper_bound
            lb = results.problem.lower_bound
            if ub is not None and lb is not None and ub != 0:
                stats.mip_gap = abs((ub - lb) / ub)

        return stats


# ---------------------------------------------------------------------------
# Convenience Functions
# ---------------------------------------------------------------------------


def list_available_solvers() -> Dict[str, Dict[str, Any]]:
    """
    List all available solvers with metadata.

    Returns:
        Dict mapping solver name to metadata (display_name, is_commercial, available)
    """
    available_solvers = detect_available_solvers()

    return {
        solver.value: {
            "display_name": SOLVER_DISPLAY_NAMES.get(solver.value, solver.value),
            "is_commercial": solver in COMMERCIAL_SOLVERS,
            "available": solver.value in available_solvers,
        }
        for solver in SolverType
    }


def solve_model(
    model: Any,
    solver: Optional[str] = None,
    **solve_kwargs: Any,
) -> tuple[SolverResults, SolverStats]:
    """
    Convenience function to solve a model with automatic solver selection.

    Args:
        model: Pyomo ConcreteModel
        solver: Solver name (uses default if None)
        **solve_kwargs: Passed to SolverInterface.solve()

    Returns:
        tuple of (SolverResults, SolverStats)
    """
    interface = SolverInterface(solver_name=solver)
    return interface.solve(model, **solve_kwargs)

"""Formula Compiler for PlanningSpace-compatible expressions.

Transforms PlanningSpace formula syntax into secure, executable Python callables.
The compilation pipeline is:

1. **Transform** -- Convert PlanningSpace syntax (``[Metric Name]``, ``PT``,
   built-in functions) into valid Python expression strings.
2. **Parse** -- Parse the Python string into an ``ast.AST`` tree.
3. **Validate** -- Walk the AST to block dangerous constructs (``eval``,
   ``exec``, ``import``, attribute access on unsafe objects).
4. **Compile** -- Compile the validated AST to a Python code object.
5. **Wrap** -- Return a callable that accepts a metrics context, master data,
   time period index, and optional project/outcome/level identifiers.

Compiled callables are cached by ``(formula_type, formula_text)`` for reuse.
"""

from __future__ import annotations

import ast
import math
import re
from typing import Any, Optional

import numpy as np
import structlog

logger = structlog.get_logger(__name__)

# Type alias for the compiled formula callable signature.
FormulaCallable = Any  # Callable[[dict, dict, int, Optional[str], Optional[str], str], float]

# Pre-compiled regex for [Metric Name] references.
_METRIC_REF_PATTERN: re.Pattern[str] = re.compile(r"\[([^\]]+)\]")

# Regex to match standalone PT that is not part of a larger identifier.
# Matches PT preceded by a non-alphanumeric character (or start of string)
# and followed by a non-alphanumeric character (or end of string).
_PT_PATTERN: re.Pattern[str] = re.compile(r"(?<![A-Za-z0-9_])PT(?![A-Za-z0-9_])")


class FormulaCompiler:
    """Compile PlanningSpace formulas into safe, executable Python callables.

    The compiler supports the standard PlanningSpace built-in functions and
    enforces a security sandbox by blocking dangerous AST nodes.

    Usage::

        compiler = FormulaCompiler()
        fn = compiler.compile_formula(
            "[Production Rate - Oil] * [MD - Price - Oil] * 365.25 / 1e6",
            formula_type="CT",
        )
        value = fn(metrics_ctx, master_data, t=3, project="Alpha", outcome="Base")
    """

    # Built-in function names recognised in PlanningSpace formulas.
    BUILTIN_FUNCTIONS: frozenset[str] = frozenset({
        "Total",
        "TotalDisc",
        "TotalInf",
        "Disc",
        "CumDisc",
        "GetCumulative",
        "IF",
        "MAX",
        "MIN",
        "SUM",
        "ABS",
    })

    # Names that are forbidden inside formula ASTs for security.
    FORBIDDEN_NAMES: frozenset[str] = frozenset({
        "eval",
        "exec",
        "compile",
        "import",
        "__import__",
        "open",
        "file",
        "input",
        "raw_input",
        "globals",
        "locals",
        "getattr",
        "setattr",
        "delattr",
        "__builtins__",
    })

    # Attribute names that must never be accessed via dot notation.
    _FORBIDDEN_ATTRIBUTES: frozenset[str] = frozenset({
        "__class__",
        "__subclasses__",
        "__bases__",
        "__mro__",
        "__globals__",
        "__code__",
        "__func__",
        "__self__",
        "__module__",
        "__dict__",
        "__init__",
        "__new__",
        "__del__",
        "__reduce__",
        "__reduce_ex__",
    })

    def __init__(self) -> None:
        self.compiled_cache: dict[str, FormulaCallable] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compile_formula(
        self,
        formula: str,
        formula_type: str = "CT",
    ) -> FormulaCallable:
        """Compile a PlanningSpace formula string into an executable callable.

        Args:
            formula: The raw formula string in PlanningSpace syntax.
            formula_type: One of ``"FYF"`` (first-year), ``"CT"`` (current-time),
                ``"Total"``, ``"TotalDisc"``.

        Returns:
            A callable with signature
            ``(metrics_context, master_data, t, project, outcome, level) -> float``.

        Raises:
            ValueError: If the formula contains forbidden constructs or has
                invalid syntax.
        """
        cache_key = f"{formula_type}:{formula}"
        if cache_key in self.compiled_cache:
            return self.compiled_cache[cache_key]

        # Step 1: Transform PlanningSpace syntax to Python.
        python_expr = self._transform_to_python(formula, formula_type)

        # Step 2: Parse to AST.
        try:
            tree = ast.parse(python_expr, mode="eval")
        except SyntaxError as exc:
            logger.error(
                "formula_syntax_error",
                formula=formula,
                formula_type=formula_type,
                transformed=python_expr,
                error=str(exc),
            )
            raise ValueError(
                f"Invalid formula syntax: {formula}\n"
                f"Transformed to: {python_expr}\n"
                f"Error: {exc}"
            ) from exc

        # Step 3: Security validation.
        self._validate_ast(tree)

        # Step 4: Compile to code object.
        code = compile(tree, f"<formula:{formula_type}>", "eval")

        # Step 5: Wrap in a callable with the expected signature.
        def formula_function(
            metrics_context: dict[str, Any],
            master_data: dict[str, np.ndarray],
            t: int,
            project: Optional[str] = None,
            outcome: Optional[str] = None,
            level: str = "S",
        ) -> float:
            evaluation_namespace: dict[str, Any] = {
                "metrics": metrics_context,
                "master_data": master_data,
                "t": t,
                "project": project,
                "outcome": outcome,
                "level": level,
                "_prior_value": metrics_context.get("_prior_value", 0.0),
                # Built-in functions
                "Total": FormulaCompiler._builtin_total,
                "TotalDisc": FormulaCompiler._builtin_total_disc,
                "TotalInf": FormulaCompiler._builtin_total_inf,
                "Disc": FormulaCompiler._builtin_disc,
                "CumDisc": FormulaCompiler._builtin_cum_disc,
                "GetCumulative": FormulaCompiler._builtin_get_cumulative,
                "IF": FormulaCompiler._builtin_if,
                "MAX": FormulaCompiler._builtin_max,
                "MIN": FormulaCompiler._builtin_min,
                "SUM": FormulaCompiler._builtin_sum,
                "ABS": abs,
                # Math constants and helpers available to formulas.
                "math": math,
                "pi": math.pi,
                "e": math.e,
            }

            try:
                result = eval(code, {"__builtins__": {}}, evaluation_namespace)  # noqa: S307
                return float(result) if result is not None else 0.0
            except ZeroDivisionError:
                logger.warning(
                    "formula_division_by_zero",
                    formula=formula,
                    t=t,
                    project=project,
                    outcome=outcome,
                )
                return 0.0
            except Exception as exc:
                logger.error(
                    "formula_evaluation_error",
                    formula=formula,
                    formula_type=formula_type,
                    t=t,
                    project=project,
                    outcome=outcome,
                    error=str(exc),
                )
                raise RuntimeError(
                    f"Error evaluating formula '{formula}' at t={t} "
                    f"for project={project}, outcome={outcome}: {exc}"
                ) from exc

        # Cache the compiled function.
        self.compiled_cache[cache_key] = formula_function

        logger.debug(
            "formula_compiled",
            formula=formula,
            formula_type=formula_type,
            cache_size=len(self.compiled_cache),
        )

        return formula_function

    # ------------------------------------------------------------------
    # Syntax transformation
    # ------------------------------------------------------------------

    def _transform_to_python(self, formula: str, formula_type: str) -> str:
        """Transform PlanningSpace formula syntax into a Python expression string.

        Transformations applied:
        - ``[Metric Name]`` where name starts with ``"MD -"`` or ``"OMD"``
          becomes ``master_data['Metric Name'][t]``.
        - ``[Metric Name]`` (other) becomes ``metrics['Metric Name']``.
        - Standalone ``PT`` becomes ``_prior_value`` (the current metric's
          value at ``t-1``, injected by the ExecutionEngine).

        For ``formula_type='FYF'``, any remaining ``PT`` reference after
        transformation is treated as an error because the first year has
        no prior period.

        Args:
            formula: Raw PlanningSpace formula string.
            formula_type: ``"FYF"``, ``"CT"``, ``"Total"``, or ``"TotalDisc"``.

        Returns:
            A valid Python expression string.

        Raises:
            ValueError: If a FYF formula contains a ``PT`` reference.
        """
        python_code = formula

        # 1. Replace [Metric Name] references.
        def _replace_metric_ref(match: re.Match[str]) -> str:
            metric_name = match.group(1)
            # Master Data metrics are keyed differently in the context.
            if metric_name.startswith("MD -") or metric_name.startswith("OMD"):
                return f"master_data['{metric_name}'][t]"
            return f"metrics['{metric_name}']"

        python_code = _METRIC_REF_PATTERN.sub(_replace_metric_ref, python_code)

        # 2. Handle PT (Prior Time).
        if formula_type == "FYF":
            # FYF formulas must not reference prior time.
            if _PT_PATTERN.search(python_code):
                raise ValueError(
                    f"First Year Formula (FYF) cannot reference PT (prior time): "
                    f"{formula}"
                )
        else:
            # Replace standalone PT with the prior-value variable injected
            # by the ExecutionEngine into the metrics context.
            python_code = _PT_PATTERN.sub("_prior_value", python_code)

        return python_code

    # ------------------------------------------------------------------
    # AST security validation
    # ------------------------------------------------------------------

    def _validate_ast(self, tree: ast.AST) -> None:
        """Walk the AST and block dangerous constructs.

        Checks for:
        - References to forbidden names (``eval``, ``exec``, etc.).
        - Import statements.
        - Attribute access on unsafe dunder attributes.

        Args:
            tree: The parsed AST to validate.

        Raises:
            ValueError: If any forbidden construct is found.
        """
        for node in ast.walk(tree):
            # Block forbidden names used as bare identifiers or function calls.
            if isinstance(node, ast.Name):
                if node.id in self.FORBIDDEN_NAMES:
                    raise ValueError(
                        f"Forbidden name in formula: '{node.id}'"
                    )

            # Block import statements (these would be ast.Import or
            # ast.ImportFrom in statement mode; in expression mode they
            # shouldn't appear, but we check defensively).
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                raise ValueError("Import statements are not allowed in formulas")

            # Block attribute access on dangerous dunder names.
            if isinstance(node, ast.Attribute):
                if node.attr in self._FORBIDDEN_ATTRIBUTES:
                    raise ValueError(
                        f"Forbidden attribute access in formula: '.{node.attr}'"
                    )

            # Block calls to forbidden names (e.g. ``eval(...)``).
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in self.FORBIDDEN_NAMES:
                    raise ValueError(
                        f"Forbidden function call in formula: '{node.func.id}(...)'"
                    )

    # ------------------------------------------------------------------
    # Built-in function implementations
    # ------------------------------------------------------------------

    @staticmethod
    def _builtin_total(values: np.ndarray | list[float]) -> float:
        """Undiscounted sum across all time periods.

        Args:
            values: Array or list of time-series values.

        Returns:
            Sum of all values.
        """
        return float(np.sum(values))

    @staticmethod
    def _builtin_total_disc(
        values: np.ndarray | list[float],
        rate: float = 0.10,
    ) -> float:
        """Net Present Value (NPV) calculation.

        Discounts each value by ``(1 + rate)^t`` where *t* is the zero-based
        time index.

        Args:
            values: Array or list of time-series values.
            rate: Annual discount rate (default 10%).

        Returns:
            Discounted sum (NPV).
        """
        arr = np.asarray(values, dtype=np.float64)
        periods = np.arange(len(arr), dtype=np.float64)
        discount_factors = (1.0 + rate) ** periods
        return float(np.sum(arr / discount_factors))

    @staticmethod
    def _builtin_total_inf(
        values: np.ndarray | list[float],
        inflation_rate: float = 0.02,
    ) -> float:
        """Inflation-adjusted sum across all time periods.

        Each value is multiplied by ``(1 + inflation_rate)^t``.

        Args:
            values: Array or list of time-series values.
            inflation_rate: Annual inflation rate (default 2%).

        Returns:
            Inflation-adjusted sum.
        """
        arr = np.asarray(values, dtype=np.float64)
        periods = np.arange(len(arr), dtype=np.float64)
        inflation_factors = (1.0 + inflation_rate) ** periods
        return float(np.sum(arr * inflation_factors))

    @staticmethod
    def _builtin_disc(value: float, rate: float, period: int) -> float:
        """Discount a single value to present value.

        Args:
            value: The future value.
            rate: Discount rate.
            period: Number of periods from present.

        Returns:
            Present value.
        """
        return float(value / (1.0 + rate) ** period)

    @staticmethod
    def _builtin_cum_disc(
        values: np.ndarray | list[float],
        rate: float,
        up_to: int,
    ) -> float:
        """Cumulative discounted value up to (and including) a given period.

        Args:
            values: Array or list of time-series values.
            rate: Discount rate.
            up_to: Period index (inclusive) up to which to accumulate.

        Returns:
            Cumulative discounted sum from period 0 to *up_to*.
        """
        arr = np.asarray(values, dtype=np.float64)
        end = min(up_to + 1, len(arr))
        sliced = arr[:end]
        periods = np.arange(end, dtype=np.float64)
        discount_factors = (1.0 + rate) ** periods
        return float(np.sum(sliced / discount_factors))

    @staticmethod
    def _builtin_get_cumulative(
        values: np.ndarray | list[float],
        start: int = 0,
        end: Optional[int] = None,
    ) -> float:
        """Sum of values over a sub-range of the time horizon.

        Args:
            values: Array or list of time-series values.
            start: Start index (inclusive, default 0).
            end: End index (exclusive). If ``None``, sums to the end of the array.

        Returns:
            Sum of values in ``[start, end)``.
        """
        arr = np.asarray(values, dtype=np.float64)
        return float(np.sum(arr[start:end]))

    @staticmethod
    def _builtin_if(
        condition: Any,
        true_value: float,
        false_value: float,
    ) -> float:
        """Conditional expression (ternary).

        Args:
            condition: Boolean-like condition.
            true_value: Value returned when condition is truthy.
            false_value: Value returned when condition is falsy.

        Returns:
            *true_value* if *condition* is truthy, otherwise *false_value*.
        """
        return float(true_value) if condition else float(false_value)

    @staticmethod
    def _builtin_max(*args: float) -> float:
        """Return the maximum of one or more values.

        Accepts either multiple positional arguments or a single iterable.
        """
        if len(args) == 1 and hasattr(args[0], "__iter__"):
            return float(max(args[0]))
        return float(max(args))

    @staticmethod
    def _builtin_min(*args: float) -> float:
        """Return the minimum of one or more values.

        Accepts either multiple positional arguments or a single iterable.
        """
        if len(args) == 1 and hasattr(args[0], "__iter__"):
            return float(min(args[0]))
        return float(min(args))

    @staticmethod
    def _builtin_sum(values: Any) -> float:
        """Sum an iterable of values.

        Args:
            values: Iterable of numeric values.

        Returns:
            Sum as a float.
        """
        return float(sum(values))

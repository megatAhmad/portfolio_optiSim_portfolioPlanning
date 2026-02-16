"""
Execution Engine for PlanningSpace-compatible metric evaluation.

Evaluates all registered metrics in topological order using the
ExpressionRegistry's dependency graph and the FormulaCompiler's
compiled callables.

Evaluation Pipeline:
1. Registry provides topological execution order (dependencies first)
2. For each metric in order:
   a. Input / Master Data metrics: look up raw values directly
   b. Computed metrics: evaluate compiled FYF at t=0, CT for t>0
3. Results cached by (metric_name, opportunity, outcome, year, level)

The engine supports filtering by opportunity, outcome, attribute, and
characteristic, and aggregation at Outcome (O), Project (P), and
Scenario (S) levels.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

import numpy as np
import structlog

from app.expression_engine.compiler import FormulaCompiler
from app.expression_engine.registry import ExpressionRegistry, MetricDefinition

logger = structlog.get_logger(__name__)

# Type alias for the results cache key
CacheKey = tuple[str, Optional[str], Optional[str], int, str]


class ExecutionEngine:
    """Evaluate all registered metrics for a set of opportunities.

    Usage::

        registry = ExpressionRegistry()
        # ... register metrics ...

        engine = ExecutionEngine(registry)
        engine.load_input_data(opportunities, outcomes, metrics_data, master_data)
        results = engine.evaluate_all_metrics(planning_horizon=30)

        # Access a specific result
        value = results[("Revenue - Oil", "ProjectAlpha", "Base", 5, "O")]
    """

    def __init__(self, registry: ExpressionRegistry) -> None:
        self.registry = registry
        self.compiler = FormulaCompiler()

        # Input data (loaded via load_input_data)
        self._input_metrics: Dict[str, Dict[str, Dict[str, np.ndarray]]] = {}
        # Structure: metric_name -> opportunity -> outcome -> time_series array

        self._master_data: Dict[str, np.ndarray] = {}
        # Structure: metric_name -> time_series array

        self._opportunities: List[str] = []
        self._outcomes: Dict[str, List[str]] = {}
        # opportunity -> list of outcome names

        self._outcome_weights: Dict[str, Dict[str, float]] = {}
        # opportunity -> outcome -> probability weight

        # Results cache: (metric_name, opportunity, outcome, year, level) -> value
        self._cache: Dict[CacheKey, float] = {}

    # ------------------------------------------------------------------
    # Data Loading
    # ------------------------------------------------------------------

    def load_input_data(
        self,
        opportunities: List[str],
        outcomes: Dict[str, List[str]],
        outcome_weights: Dict[str, Dict[str, float]],
        input_metrics: Dict[str, Dict[str, Dict[str, np.ndarray]]],
        master_data: Dict[str, np.ndarray],
    ) -> None:
        """Load all input data needed for evaluation.

        Args:
            opportunities: List of opportunity/project IDs or names.
            outcomes: Mapping of opportunity -> list of outcome names.
            outcome_weights: Mapping of opportunity -> outcome -> probability weight.
            input_metrics: Nested dict:
                metric_name -> opportunity -> outcome -> numpy array of values.
            master_data: Mapping of master data metric name -> numpy array.
        """
        self._opportunities = opportunities
        self._outcomes = outcomes
        self._outcome_weights = outcome_weights
        self._input_metrics = input_metrics
        self._master_data = master_data
        self._cache.clear()

        logger.info(
            "input_data_loaded",
            num_opportunities=len(opportunities),
            num_input_metrics=len(input_metrics),
            num_master_data=len(master_data),
        )

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate_all_metrics(
        self,
        planning_horizon: int,
        discount_rate: float = 0.10,
    ) -> Dict[CacheKey, float]:
        """Evaluate all registered metrics in topological order.

        For each metric in execution order:
        - Input metrics: copy from loaded input data
        - Master Data metrics: already available in _master_data
        - Computed metrics: evaluate FYF at t=0, CT for t>0

        Args:
            planning_horizon: Number of years in the planning horizon.
            discount_rate: Discount rate for TotalDisc calculations.

        Returns:
            Dict mapping (metric_name, opportunity, outcome, year, level) -> value
        """
        self._cache.clear()
        execution_order = self.registry.get_execution_order()

        logger.info(
            "evaluation_started",
            num_metrics=len(execution_order),
            planning_horizon=planning_horizon,
        )

        for metric_name in execution_order:
            metric = self.registry.get_metric(metric_name)

            if metric.metric_type == "Input":
                self._evaluate_input_metric(metric, planning_horizon)
            elif metric.metric_type == "Master Data":
                self._evaluate_master_data_metric(metric, planning_horizon)
            elif metric.metric_type == "Computed":
                self._evaluate_computed_metric(metric, planning_horizon, discount_rate)

        logger.info(
            "evaluation_completed",
            cache_size=len(self._cache),
        )

        return dict(self._cache)

    def get_result(
        self,
        metric_name: str,
        opportunity: Optional[str] = None,
        outcome: Optional[str] = None,
        year: int = 0,
        level: str = "S",
    ) -> float:
        """Retrieve a single cached result.

        Args:
            metric_name: Name of the metric.
            opportunity: Opportunity/project ID (None for scenario-level).
            outcome: Outcome name (None for project or scenario-level).
            year: Year index.
            level: Aggregation level ("O", "P", "S").

        Returns:
            Cached metric value, or 0.0 if not found.
        """
        key: CacheKey = (metric_name, opportunity, outcome, year, level)
        return self._cache.get(key, 0.0)

    def get_time_series(
        self,
        metric_name: str,
        opportunity: Optional[str] = None,
        outcome: Optional[str] = None,
        level: str = "S",
        planning_horizon: int = 30,
    ) -> np.ndarray:
        """Retrieve a full time series for a metric.

        Args:
            metric_name: Name of the metric.
            opportunity: Opportunity/project ID (None for scenario-level).
            outcome: Outcome name (None for project or scenario-level).
            level: Aggregation level.
            planning_horizon: Number of years.

        Returns:
            Numpy array of values for all years.
        """
        return np.array([
            self.get_result(metric_name, opportunity, outcome, t, level)
            for t in range(planning_horizon)
        ])

    # ------------------------------------------------------------------
    # Internal: Input Metric Evaluation
    # ------------------------------------------------------------------

    def _evaluate_input_metric(
        self,
        metric: MetricDefinition,
        planning_horizon: int,
    ) -> None:
        """Copy input metric values into the cache at Outcome level."""
        mname = metric.metric_name

        if mname not in self._input_metrics:
            return

        for opp in self._opportunities:
            if opp not in self._input_metrics[mname]:
                continue

            for outcome in self._outcomes.get(opp, []):
                if outcome not in self._input_metrics[mname][opp]:
                    continue

                values = self._input_metrics[mname][opp][outcome]

                for t in range(min(planning_horizon, len(values))):
                    self._cache[(mname, opp, outcome, t, "O")] = float(values[t])

            # Project-level aggregation: weighted average across outcomes
            self._aggregate_to_project_level(mname, opp, planning_horizon)

        # Scenario-level aggregation: sum across projects
        self._aggregate_to_scenario_level(mname, planning_horizon)

    # ------------------------------------------------------------------
    # Internal: Master Data Evaluation
    # ------------------------------------------------------------------

    def _evaluate_master_data_metric(
        self,
        metric: MetricDefinition,
        planning_horizon: int,
    ) -> None:
        """Master Data metrics are shared across opportunities."""
        mname = metric.metric_name

        if mname not in self._master_data:
            return

        values = self._master_data[mname]

        for t in range(min(planning_horizon, len(values))):
            # Master Data is the same for all opportunities (scenario-level)
            self._cache[(mname, None, None, t, "S")] = float(values[t])

    # ------------------------------------------------------------------
    # Internal: Computed Metric Evaluation
    # ------------------------------------------------------------------

    def _evaluate_computed_metric(
        self,
        metric: MetricDefinition,
        planning_horizon: int,
        discount_rate: float,
    ) -> None:
        """Evaluate a computed metric using FYF/CT formulas.

        For each opportunity and outcome:
        - t=0: evaluate FYF formula
        - t>0: evaluate CT formula with PT = value at t-1
        """
        mname = metric.metric_name
        level = metric.level

        # Compile formulas
        fyf_fn = None
        ct_fn = None

        if metric.formula_fyf:
            fyf_fn = self.compiler.compile_formula(metric.formula_fyf, "FYF")
        if metric.formula_ct:
            ct_fn = self.compiler.compile_formula(metric.formula_ct, "CT")

        # If no formulas, nothing to compute
        if fyf_fn is None and ct_fn is None:
            return

        # Determine scope based on metric level
        if level == "O":
            # Evaluate at Outcome level for each opportunity-outcome pair
            for opp in self._opportunities:
                if not self._matches_filter(metric, opp):
                    continue
                for outcome in self._outcomes.get(opp, []):
                    self._evaluate_formula_series(
                        metric, fyf_fn, ct_fn, opp, outcome,
                        planning_horizon, discount_rate, "O",
                    )
                # Aggregate up
                self._aggregate_to_project_level(mname, opp, planning_horizon)
            self._aggregate_to_scenario_level(mname, planning_horizon)

        elif level == "P":
            # Evaluate at Project level (no outcome dimension)
            for opp in self._opportunities:
                if not self._matches_filter(metric, opp):
                    continue
                self._evaluate_formula_series(
                    metric, fyf_fn, ct_fn, opp, None,
                    planning_horizon, discount_rate, "P",
                )
            self._aggregate_to_scenario_level(mname, planning_horizon)

        elif level == "S":
            # Evaluate at Scenario level (no project or outcome dimension)
            self._evaluate_formula_series(
                metric, fyf_fn, ct_fn, None, None,
                planning_horizon, discount_rate, "S",
            )

    def _evaluate_formula_series(
        self,
        metric: MetricDefinition,
        fyf_fn: Any,
        ct_fn: Any,
        opportunity: Optional[str],
        outcome: Optional[str],
        planning_horizon: int,
        discount_rate: float,
        level: str,
    ) -> None:
        """Evaluate FYF + CT formula across all time periods."""
        mname = metric.metric_name

        for t in range(planning_horizon):
            # Build metrics context for this evaluation point
            metrics_ctx = self._build_metrics_context(
                opportunity, outcome, t, level
            )

            # Inject prior-time value
            if t > 0:
                prior_key: CacheKey = (mname, opportunity, outcome, t - 1, level)
                metrics_ctx["_prior_value"] = self._cache.get(prior_key, 0.0)
            else:
                metrics_ctx["_prior_value"] = 0.0

            # Evaluate formula
            if t == 0 and fyf_fn is not None:
                val = fyf_fn(metrics_ctx, self._master_data, t, opportunity, outcome, level)
            elif t > 0 and ct_fn is not None:
                val = ct_fn(metrics_ctx, self._master_data, t, opportunity, outcome, level)
            elif fyf_fn is not None:
                # Fall back to FYF if no CT formula
                val = fyf_fn(metrics_ctx, self._master_data, t, opportunity, outcome, level)
            else:
                val = 0.0

            self._cache[(mname, opportunity, outcome, t, level)] = val

    def _build_metrics_context(
        self,
        opportunity: Optional[str],
        outcome: Optional[str],
        year: int,
        level: str,
    ) -> Dict[str, Any]:
        """Build the metrics context dictionary for formula evaluation.

        Contains all previously computed metric values that formulas may reference.
        """
        context: Dict[str, Any] = {}

        for (mname, opp, out, t, lvl), val in self._cache.items():
            if t != year:
                continue

            # Match the scope of evaluation
            if level == "O" and opp == opportunity and out == outcome:
                context[mname] = val
            elif level == "P" and opp == opportunity and out is None:
                context[mname] = val
            elif level == "S" and opp is None and out is None:
                context[mname] = val
            # Also include master data metrics (always scenario-level)
            elif opp is None and out is None and lvl == "S":
                if mname not in context:
                    context[mname] = val

        return context

    # ------------------------------------------------------------------
    # Internal: Aggregation
    # ------------------------------------------------------------------

    def _aggregate_to_project_level(
        self,
        metric_name: str,
        opportunity: str,
        planning_horizon: int,
    ) -> None:
        """Aggregate outcome-level values to project level (weighted by probability)."""
        outcomes = self._outcomes.get(opportunity, [])
        weights = self._outcome_weights.get(opportunity, {})

        for t in range(planning_horizon):
            weighted_sum = 0.0
            total_weight = 0.0

            for outcome in outcomes:
                key: CacheKey = (metric_name, opportunity, outcome, t, "O")
                if key in self._cache:
                    w = weights.get(outcome, 1.0 / max(len(outcomes), 1))
                    weighted_sum += self._cache[key] * w
                    total_weight += w

            if total_weight > 0:
                self._cache[(metric_name, opportunity, None, t, "P")] = weighted_sum

    def _aggregate_to_scenario_level(
        self,
        metric_name: str,
        planning_horizon: int,
    ) -> None:
        """Aggregate project-level values to scenario level (sum across projects)."""
        for t in range(planning_horizon):
            total = 0.0
            found = False

            for opp in self._opportunities:
                key: CacheKey = (metric_name, opp, None, t, "P")
                if key in self._cache:
                    total += self._cache[key]
                    found = True

            if found:
                self._cache[(metric_name, None, None, t, "S")] = total

    # ------------------------------------------------------------------
    # Internal: Filtering
    # ------------------------------------------------------------------

    def _matches_filter(
        self,
        metric: MetricDefinition,
        opportunity: str,
    ) -> bool:
        """Check if an opportunity matches the metric's filters."""
        if metric.opportunity_filter and metric.opportunity_filter != opportunity:
            return False

        # Attribute and characteristic filters would check against
        # opportunity attributes loaded from the database.
        # For now, accept all if no specific opportunity filter is set.
        return True

"""Expression Registry for PlanningSpace-compatible metric definitions.

Central registry that stores all metric definitions (Input, Master Data, Computed),
extracts inter-metric dependencies from formula references, builds a dependency graph
using NetworkX, and provides topological execution ordering for the ExecutionEngine.

Metric formulas follow the PlanningSpace FYF/PT/CT pattern:
  - FYF (First Year Formula): evaluated at t=0, cannot reference PT
  - PT  (Prior Time): value of the current metric at t-1
  - CT  (Current Time): evaluated at t>0, may reference PT and other metrics
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

import networkx as nx
import structlog

logger = structlog.get_logger(__name__)

# Pre-compiled regex for extracting [Metric Name] references from formulas.
_METRIC_REF_PATTERN: re.Pattern[str] = re.compile(r"\[([^\]]+)\]")


@dataclass
class MetricDefinition:
    """Definition of a single metric within the expression system.

    Attributes:
        metric_name: Unique name identifying the metric (e.g. "Revenue - Oil").
        metric_type: One of "Input", "Master Data", or "Computed".
        unit: Engineering/financial unit (e.g. "$M", "bbl/d", "tCO2e").
        formula_fyf: First Year Formula evaluated at t=0 (no PT references allowed).
        formula_pt: Prior Time reference formula (rarely used standalone; PT is
            typically embedded in formula_ct via the ``PT`` keyword).
        formula_ct: Current Time formula evaluated at t>0. May reference ``PT``
            for the metric's own prior-year value.
        formula_total: Aggregation formula across the full time horizon
            (e.g. ``Total([Revenue - Oil])``).
        formula_total_disc: Discounted aggregation formula
            (e.g. ``TotalDisc([BTAX Cash Flow], 0.10)``).
        level: Aggregation level -- "O" (Outcome), "P" (Project), "S" (Scenario).
        attribute_filter: Optional attribute name to filter applicable opportunities.
        characteristic_filter: Optional characteristic value paired with attribute_filter.
        opportunity_filter: Optional specific opportunity name filter.
        outcome_filter: Optional specific outcome name filter.
        is_fixture: True if this metric comes from a Master Data Set (fixture).
        is_indicator: True if this metric is a single scalar value, not a time series.
        depends_on: Set of metric names this metric depends on (auto-populated by
            the registry from formula references).
    """

    metric_name: str
    metric_type: str  # "Input", "Master Data", "Computed"
    unit: str

    # Formulas (PlanningSpace FYF/PT/CT pattern)
    formula_fyf: Optional[str] = None
    formula_pt: Optional[str] = None
    formula_ct: Optional[str] = None
    formula_total: Optional[str] = None
    formula_total_disc: Optional[str] = None

    # Filtering / aggregation
    level: str = "S"
    attribute_filter: Optional[str] = None
    characteristic_filter: Optional[str] = None
    opportunity_filter: Optional[str] = None
    outcome_filter: Optional[str] = None

    # Flags
    is_fixture: bool = False
    is_indicator: bool = False

    # Dependencies (auto-populated by ExpressionRegistry._extract_dependencies)
    depends_on: set[str] = field(default_factory=set)


class ExpressionRegistry:
    """Central registry of all metric expressions.

    Maintains a mapping of metric names to their definitions, a NetworkX
    directed graph of inter-metric dependencies, and a topologically-sorted
    execution order so the ExecutionEngine can evaluate computed metrics in
    the correct sequence.

    Usage::

        registry = ExpressionRegistry()
        registry.register_metric(MetricDefinition(
            metric_name="Production Rate - Oil",
            metric_type="Input",
            unit="bbl/d",
        ))
        registry.register_metric(MetricDefinition(
            metric_name="Revenue - Oil",
            metric_type="Computed",
            unit="$M",
            formula_ct="[Production Rate - Oil] * [MD - Price - Oil] * 365.25 / 1e6",
        ))
        order = registry.get_execution_order()
    """

    def __init__(self) -> None:
        self.metrics: dict[str, MetricDefinition] = {}
        self.dependency_graph: nx.DiGraph = nx.DiGraph()
        self.execution_order: list[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register_metric(self, metric: MetricDefinition) -> None:
        """Register a single metric definition and rebuild the execution order.

        Args:
            metric: The metric definition to register.

        Raises:
            ValueError: If the dependency graph contains cycles after adding
                this metric.
        """
        self.metrics[metric.metric_name] = metric

        # Ensure the metric itself is a node in the graph, even if it has
        # no formula dependencies (Input / Master Data metrics).
        self.dependency_graph.add_node(metric.metric_name)

        self._extract_dependencies(metric)
        self._build_execution_order()

        logger.info(
            "metric_registered",
            metric_name=metric.metric_name,
            metric_type=metric.metric_type,
            depends_on=sorted(metric.depends_on),
        )

    def register_metrics_batch(self, metrics: list[MetricDefinition]) -> None:
        """Register multiple metrics and rebuild the execution order once at the end.

        This is more efficient than calling :meth:`register_metric` in a loop
        because the expensive topological sort is performed only once.

        Args:
            metrics: List of metric definitions to register.

        Raises:
            ValueError: If the dependency graph contains cycles after adding
                all metrics.
        """
        for metric in metrics:
            self.metrics[metric.metric_name] = metric
            self.dependency_graph.add_node(metric.metric_name)
            self._extract_dependencies(metric)

        self._build_execution_order()

        logger.info(
            "metrics_batch_registered",
            count=len(metrics),
            total_metrics=len(self.metrics),
        )

    def get_metric(self, name: str) -> MetricDefinition:
        """Retrieve a metric definition by name.

        Args:
            name: The metric name to look up.

        Returns:
            The corresponding MetricDefinition.

        Raises:
            KeyError: If *name* is not found in the registry.
        """
        if name not in self.metrics:
            raise KeyError(f"Metric '{name}' not found in registry")
        return self.metrics[name]

    def get_execution_order(self) -> list[str]:
        """Return the topologically-sorted execution order.

        Metrics with no dependencies appear first; metrics that depend on
        other metrics appear after their dependencies.

        Returns:
            Ordered list of metric names.
        """
        return list(self.execution_order)

    def validate_dependencies(self) -> list[str]:
        """Validate that all metrics referenced in formulas are registered.

        Returns:
            A list of human-readable error messages. An empty list means all
            dependencies are satisfied.
        """
        errors: list[str] = []

        for metric in self.metrics.values():
            for dep in sorted(metric.depends_on):
                if dep not in self.metrics:
                    errors.append(
                        f"Metric '{metric.metric_name}' references undefined "
                        f"metric '{dep}'"
                    )

        if errors:
            logger.warning(
                "dependency_validation_failed",
                error_count=len(errors),
                errors=errors,
            )
        else:
            logger.debug("dependency_validation_passed", metric_count=len(self.metrics))

        return errors

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_dependencies(self, metric: MetricDefinition) -> None:
        """Extract ``[Metric Name]`` references from all formula fields.

        Populates ``metric.depends_on`` and adds directed edges to the
        dependency graph from the *current* metric to each referenced metric.
        The edge direction is ``metric -> dependency``, meaning "metric depends
        on dependency".

        Args:
            metric: The metric whose formulas should be scanned.
        """
        # Reset dependencies for this metric (idempotent re-registration).
        metric.depends_on = set()

        # Scan every formula field that may contain metric references.
        formula_fields: list[Optional[str]] = [
            metric.formula_fyf,
            metric.formula_pt,
            metric.formula_ct,
            metric.formula_total,
            metric.formula_total_disc,
        ]

        for formula in formula_fields:
            if formula is None:
                continue

            matches = _METRIC_REF_PATTERN.findall(formula)
            for referenced_name in matches:
                # A metric does not "depend on" itself -- self-references are
                # handled via the PT mechanism rather than graph edges.
                if referenced_name == metric.metric_name:
                    continue

                metric.depends_on.add(referenced_name)

                # Ensure the referenced metric node exists in the graph even
                # if it hasn't been registered yet (will be validated later).
                self.dependency_graph.add_node(referenced_name)

                # Edge: this metric depends on referenced_name.
                self.dependency_graph.add_edge(metric.metric_name, referenced_name)

        logger.debug(
            "dependencies_extracted",
            metric_name=metric.metric_name,
            depends_on=sorted(metric.depends_on),
        )

    def _build_execution_order(self) -> None:
        """Compute topological execution order from the dependency graph.

        The dependency graph has edges from *dependent* to *dependency*
        (``A -> B`` means "A depends on B"). A topological sort of the
        *reversed* graph yields an order where dependencies come before the
        metrics that need them.

        Raises:
            ValueError: If the dependency graph contains one or more cycles,
                with details about which metrics form the cycle(s).
        """
        if len(self.dependency_graph) == 0:
            self.execution_order = []
            return

        try:
            reversed_graph: nx.DiGraph = self.dependency_graph.reverse()
            self.execution_order = list(nx.topological_sort(reversed_graph))

            logger.debug(
                "execution_order_built",
                order=self.execution_order,
            )

        except nx.NetworkXUnfeasible:
            # Cycle detected -- provide actionable error information.
            cycles: list[list[str]] = list(nx.simple_cycles(self.dependency_graph))
            cycle_descriptions = [" -> ".join(c + [c[0]]) for c in cycles]

            logger.error(
                "circular_dependency_detected",
                cycles=cycle_descriptions,
            )

            raise ValueError(
                "Circular dependencies detected in metric formulas. "
                f"Cycles: {cycle_descriptions}"
            )

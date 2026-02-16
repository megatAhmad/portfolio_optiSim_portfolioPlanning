"""Cycle detection and graph validation for dependency graphs.

Detects circular dependencies that would make topological ordering
(and therefore optimization constraint generation) impossible.
Provides actionable reporting with affected projects and fix suggestions.
"""

from __future__ import annotations

from typing import Any

import networkx as nx
import structlog

logger = structlog.get_logger(__name__)


class CycleDetector:
    """Detects cycles and validates dependency graphs.

    Operates on a NetworkX ``DiGraph`` to find circular dependencies,
    orphaned nodes, and other structural issues that would prevent
    correct optimization constraint generation.
    """

    def __init__(self) -> None:
        self._log = logger.bind(component="CycleDetector")

    def detect_cycles(self, graph: nx.DiGraph) -> list[list[Any]]:
        """Find all simple cycles in the directed graph.

        A simple cycle is a closed path where no node appears twice.
        Uses Johnson's algorithm via ``nx.simple_cycles``.

        Parameters
        ----------
        graph:
            The NetworkX DiGraph to analyze.

        Returns
        -------
        list[list]
            List of cycles, where each cycle is a list of node IDs
            forming a closed loop. Returns an empty list if no cycles
            are found.
        """
        cycles: list[list[Any]] = list(nx.simple_cycles(graph))

        if cycles:
            self._log.warning(
                "cycles_detected",
                cycle_count=len(cycles),
                first_cycle=[str(n) for n in cycles[0]],
            )
        else:
            self._log.debug("no_cycles_detected")

        return cycles

    def has_cycles(self, graph: nx.DiGraph) -> bool:
        """Check whether the graph contains any cycles.

        This is faster than ``detect_cycles`` when you only need a
        boolean result, as it short-circuits on the first cycle found.

        Parameters
        ----------
        graph:
            The NetworkX DiGraph to analyze.

        Returns
        -------
        bool
            ``True`` if at least one cycle exists.
        """
        try:
            nx.find_cycle(graph)
        except nx.NetworkXNoCycle:
            return False
        return True

    def get_cycle_report(self, graph: nx.DiGraph) -> dict[str, Any]:
        """Generate a detailed report of all cycles in the graph.

        Parameters
        ----------
        graph:
            The NetworkX DiGraph to analyze.

        Returns
        -------
        dict
            Cycle report with the following keys:

            - ``has_cycles`` (bool): Whether any cycles exist.
            - ``cycles`` (list[list]): All simple cycles found.
            - ``affected_projects`` (set): All project IDs involved in cycles.
            - ``suggestions`` (list[str]): Actionable suggestions for resolving
              each cycle.
        """
        cycles = self.detect_cycles(graph)
        affected_projects: set[Any] = set()
        suggestions: list[str] = []

        for cycle in cycles:
            for node in cycle:
                affected_projects.add(node)

            # Build a human-readable cycle description
            cycle_labels = [str(node) for node in cycle]
            cycle_str = " -> ".join(cycle_labels) + f" -> {cycle_labels[0]}"
            suggestions.append(
                f"Cycle detected: {cycle_str}. "
                f"Remove or reverse one dependency in this chain to break the cycle."
            )

        report: dict[str, Any] = {
            "has_cycles": len(cycles) > 0,
            "cycles": cycles,
            "affected_projects": affected_projects,
            "suggestions": suggestions,
        }

        self._log.info(
            "cycle_report_generated",
            has_cycles=report["has_cycles"],
            cycle_count=len(cycles),
            affected_project_count=len(affected_projects),
        )
        return report

    def validate_graph(self, graph: nx.DiGraph) -> list[str]:
        """Validate the dependency graph for structural issues.

        Checks for:
        1. Circular dependencies (cycles).
        2. Self-loops (a project depending on itself).
        3. Orphaned nodes (nodes with no edges at all).
        4. Isolated subgraphs (disconnected components) -- informational, not an error.

        Parameters
        ----------
        graph:
            The NetworkX DiGraph to validate.

        Returns
        -------
        list[str]
            List of validation error messages. An empty list means the
            graph is valid.
        """
        errors: list[str] = []

        # 1. Self-loops
        self_loops = list(nx.selfloop_edges(graph))
        for source, target in self_loops:
            errors.append(
                f"Self-loop detected: project '{source}' depends on itself. "
                f"Remove this dependency."
            )

        # 2. Cycles (excluding self-loops which are already reported)
        # Build a copy without self-loops for cycle detection
        graph_no_self = graph.copy()
        graph_no_self.remove_edges_from(self_loops)

        cycles = self.detect_cycles(graph_no_self)
        for cycle in cycles:
            cycle_labels = [str(node) for node in cycle]
            cycle_str = " -> ".join(cycle_labels) + f" -> {cycle_labels[0]}"
            errors.append(
                f"Circular dependency: {cycle_str}. "
                f"Break this cycle by removing or reversing one dependency."
            )

        # 3. Orphaned nodes (no in-edges and no out-edges, excluding virtual nodes)
        for node in graph.nodes():
            node_str = str(node)
            if node_str.startswith("__infra__") or node_str.startswith("__resource__"):
                continue
            in_degree = graph.in_degree(node)
            out_degree = graph.out_degree(node)
            if in_degree == 0 and out_degree == 0:
                errors.append(
                    f"Orphaned node: project '{node}' has no dependencies "
                    f"(neither incoming nor outgoing). This project is in the "
                    f"dependency graph but is not connected to any other project."
                )

        # 4. Disconnected components (informational logging, not an error)
        if graph.number_of_nodes() > 0:
            undirected = graph.to_undirected()
            components = list(nx.connected_components(undirected))
            if len(components) > 1:
                self._log.info(
                    "disconnected_components",
                    component_count=len(components),
                    component_sizes=[len(c) for c in components],
                )

        self._log.info(
            "graph_validation_complete",
            error_count=len(errors),
            node_count=graph.number_of_nodes(),
            edge_count=graph.number_of_edges(),
        )
        return errors

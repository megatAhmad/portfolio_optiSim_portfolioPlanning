"""
Graph-to-MILP Constraint Converter

Converts NetworkX dependency graph edges into Pyomo MILP constraints.

This module bridges Phase 1 (graph analysis) and Phase 2 (optimization):
- Phase 1: DependencyGraphBuilder creates a NetworkX DiGraph with project
  interdependencies (prerequisites, mutex, synergies, shared infra, resources)
- Phase 2: This converter reads the graph and produces
  SelectionDependencyData / synergy_pairs / infrastructure data that
  the constraint_generators module can consume

Architecture pattern from CLAUDE.md Key Decision #2:
  Two-phase approach — graph algorithms for analysis + MILP constraints for optimization.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
import structlog

from app.optimization.constraint_generators import (
    SelectionDependencyData,
    SelectionGroupData,
)

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Edge Type Constants
# ---------------------------------------------------------------------------

EDGE_TYPE_PREREQUISITE = "prerequisite"
EDGE_TYPE_MUTEX = "mutex"
EDGE_TYPE_SYNERGY = "synergy"
EDGE_TYPE_SHARED_INFRA = "shared_infrastructure"
EDGE_TYPE_RESOURCE = "resource_constraint"


# ---------------------------------------------------------------------------
# Conversion Results
# ---------------------------------------------------------------------------


class ConversionResult:
    """Container for converted graph data ready for MILP constraint generation."""

    def __init__(self) -> None:
        self.dependencies: List[SelectionDependencyData] = []
        self.synergy_pairs: List[Tuple[str, str, float]] = []
        self.infrastructure: List[Dict[str, Any]] = []
        self.warnings: List[str] = []

    @property
    def total_constraints(self) -> int:
        return len(self.dependencies) + len(self.synergy_pairs) + len(self.infrastructure)


# ---------------------------------------------------------------------------
# Converter
# ---------------------------------------------------------------------------


class GraphToMILPConverter:
    """Convert a NetworkX dependency graph into MILP constraint data.

    Usage::

        from app.graph.dependency_graph import DependencyGraphBuilder

        builder = DependencyGraphBuilder()
        builder.add_prerequisite("A", "B", time_offset=2)
        builder.add_mutex("C", "D")
        graph = builder.graph

        converter = GraphToMILPConverter(graph)
        result = converter.convert()

        # Pass to constraint generators
        add_dependency_constraints(model, result.dependencies, projects, years)
        add_synergy_constraints(model, result.synergy_pairs, projects)
    """

    def __init__(
        self,
        graph: nx.DiGraph,
        project_universe: Optional[Set[str]] = None,
    ) -> None:
        """
        Args:
            graph: NetworkX DiGraph with edge metadata (type, time_offset, etc.)
            project_universe: If provided, only convert edges where both
                endpoints are in this set (optimization universe filtering)
        """
        self.graph = graph
        self.project_universe = project_universe

    def convert(self) -> ConversionResult:
        """Convert all graph edges to MILP constraint data.

        Returns:
            ConversionResult with dependencies, synergy_pairs, and infrastructure data.
        """
        result = ConversionResult()

        for u, v, data in self.graph.edges(data=True):
            # Filter to optimization universe
            if self.project_universe:
                if u not in self.project_universe or v not in self.project_universe:
                    continue

            edge_type = data.get("type", EDGE_TYPE_PREREQUISITE)

            if edge_type == EDGE_TYPE_PREREQUISITE:
                self._convert_prerequisite(u, v, data, result)
            elif edge_type == EDGE_TYPE_MUTEX:
                self._convert_mutex(u, v, data, result)
            elif edge_type == EDGE_TYPE_SYNERGY:
                self._convert_synergy(u, v, data, result)
            elif edge_type == EDGE_TYPE_SHARED_INFRA:
                self._convert_shared_infrastructure(u, v, data, result)
            elif edge_type == EDGE_TYPE_RESOURCE:
                self._convert_resource_constraint(u, v, data, result)
            else:
                result.warnings.append(
                    f"Unknown edge type '{edge_type}' between {u} and {v}"
                )

        logger.info(
            "graph_converted_to_milp",
            num_dependencies=len(result.dependencies),
            num_synergy_pairs=len(result.synergy_pairs),
            num_infrastructure=len(result.infrastructure),
            num_warnings=len(result.warnings),
        )

        return result

    def _convert_prerequisite(
        self,
        parent: str,
        child: str,
        data: Dict[str, Any],
        result: ConversionResult,
    ) -> None:
        """Convert a prerequisite edge to a SelectionDependencyData."""
        result.dependencies.append(
            SelectionDependencyData(
                independent_opportunity_id=parent,
                dependent_opportunity_id=child,
                must_or_must_not="Must",
                time_offset=data.get("time_offset", 0),
                timing_relation=data.get("timing_relation", "Before"),
            )
        )

    def _convert_mutex(
        self,
        project_a: str,
        project_b: str,
        data: Dict[str, Any],
        result: ConversionResult,
    ) -> None:
        """Convert a mutual exclusivity edge to a SelectionDependencyData."""
        result.dependencies.append(
            SelectionDependencyData(
                independent_opportunity_id=project_a,
                dependent_opportunity_id=project_b,
                must_or_must_not="Must Not",
                time_offset=0,
            )
        )

    def _convert_synergy(
        self,
        project_a: str,
        project_b: str,
        data: Dict[str, Any],
        result: ConversionResult,
    ) -> None:
        """Convert a synergy edge to a synergy pair tuple."""
        synergy_value = data.get("synergy_value", 0.0)
        if synergy_value != 0.0:
            result.synergy_pairs.append((project_a, project_b, synergy_value))
        else:
            result.warnings.append(
                f"Synergy edge between {project_a} and {project_b} has zero value"
            )

    def _convert_shared_infrastructure(
        self,
        project_a: str,
        project_b: str,
        data: Dict[str, Any],
        result: ConversionResult,
    ) -> None:
        """Convert shared infrastructure edge to infrastructure constraint data.

        Shared infrastructure edges represent projects competing for the same
        physical capacity (platform slots, pipeline throughput, etc.).
        """
        infra_name = data.get("infrastructure_name", f"infra_{project_a}_{project_b}")
        capacity = data.get("capacity", 0.0)
        usage_a = data.get("usage_a", {})  # year -> usage amount
        usage_b = data.get("usage_b", {})  # year -> usage amount

        # Check if we already have an entry for this infrastructure
        existing = None
        for infra in result.infrastructure:
            if infra["name"] == infra_name:
                existing = infra
                break

        if existing:
            existing["projects"][project_a] = usage_a
            existing["projects"][project_b] = usage_b
        else:
            result.infrastructure.append({
                "name": infra_name,
                "capacity": capacity,
                "projects": {
                    project_a: usage_a,
                    project_b: usage_b,
                },
            })

    def _convert_resource_constraint(
        self,
        project_a: str,
        project_b: str,
        data: Dict[str, Any],
        result: ConversionResult,
    ) -> None:
        """Convert resource constraint edge (drilling rigs, personnel, budget).

        Resource constraints are modeled similarly to shared infrastructure
        but may have different capacity types (counts vs. rates).
        """
        resource_name = data.get("resource_name", f"resource_{project_a}_{project_b}")
        capacity = data.get("capacity", 0.0)
        demand_a = data.get("demand_a", {})
        demand_b = data.get("demand_b", {})

        existing = None
        for infra in result.infrastructure:
            if infra["name"] == resource_name:
                existing = infra
                break

        if existing:
            existing["projects"][project_a] = demand_a
            existing["projects"][project_b] = demand_b
        else:
            result.infrastructure.append({
                "name": resource_name,
                "capacity": capacity,
                "projects": {
                    project_a: demand_a,
                    project_b: demand_b,
                },
            })


# ---------------------------------------------------------------------------
# Convenience Function
# ---------------------------------------------------------------------------


def convert_graph_to_constraints(
    graph: nx.DiGraph,
    project_universe: Optional[Set[str]] = None,
) -> ConversionResult:
    """Convert a dependency graph to MILP constraint data.

    Args:
        graph: NetworkX DiGraph with typed edges and metadata
        project_universe: Optional set of project IDs to filter to

    Returns:
        ConversionResult with all constraint data ready for MILP
    """
    converter = GraphToMILPConverter(graph, project_universe)
    return converter.convert()

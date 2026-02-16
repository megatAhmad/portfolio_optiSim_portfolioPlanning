"""Dependency graph builder using NetworkX DiGraph.

Constructs a directed graph of project interdependencies from selection
dependency records and additional synergy/shared-infrastructure/resource
constraint definitions. Provides graph analysis utilities (predecessors,
successors, critical path, centrality) and exports visualization data
for frontend D3.js / React Flow rendering.
"""

from __future__ import annotations

from typing import Any

import networkx as nx
import structlog

logger = structlog.get_logger(__name__)

# Edge type constants
EDGE_TYPE_PREREQUISITE = "prerequisite"
EDGE_TYPE_MUTEX = "mutex"
EDGE_TYPE_SYNERGY = "synergy"
EDGE_TYPE_SHARED_INFRA = "shared_infra"
EDGE_TYPE_RESOURCE = "resource"


class DependencyGraphBuilder:
    """Builds and queries a NetworkX DiGraph of project interdependencies.

    The graph stores projects as nodes (keyed by their UUID or string ID)
    and dependency relationships as directed edges with typed metadata.

    Edge types
    ----------
    - ``prerequisite`` -- Project A must complete before Project B can start.
    - ``mutex`` -- At most one of {A, B} can be selected.
    - ``synergy`` -- Combined value exceeds the sum of individual values.
    - ``shared_infra`` -- Projects share physical infrastructure capacity.
    - ``resource`` -- Projects compete for limited resources.
    """

    def __init__(self) -> None:
        self._graph: nx.DiGraph = nx.DiGraph()
        self._log = logger.bind(component="DependencyGraphBuilder")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def graph(self) -> nx.DiGraph:
        """Return the underlying NetworkX DiGraph."""
        return self._graph

    @property
    def node_count(self) -> int:
        """Return the number of nodes in the graph."""
        return self._graph.number_of_nodes()

    @property
    def edge_count(self) -> int:
        """Return the number of edges in the graph."""
        return self._graph.number_of_edges()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def build_from_dependencies(self, dependencies: list[dict[str, Any]]) -> nx.DiGraph:
        """Build the dependency graph from a list of selection dependency dicts.

        Each dependency dict is expected to contain at minimum:

        - ``independent_opportunity_id`` -- source node ID
        - ``dependent_opportunity_id`` -- target node ID
        - ``must_or_must_not`` -- ``"Must"`` (prerequisite) or ``"Must Not"`` (mutex)
        - ``time_offset`` -- integer year offset (default 0)
        - ``timing_relation`` -- ``"Before"``, ``"After"``, or ``"During"`` (default ``"Before"``)

        Parameters
        ----------
        dependencies:
            List of dependency dictionaries.

        Returns
        -------
        nx.DiGraph
            The constructed directed graph.
        """
        for dep in dependencies:
            source_id = dep["independent_opportunity_id"]
            target_id = dep["dependent_opportunity_id"]
            must_type: str = dep.get("must_or_must_not", "Must")
            time_offset: int = dep.get("time_offset", 0)
            timing_relation: str = dep.get("timing_relation", "Before")
            is_active: bool = dep.get("is_active", True)

            if not is_active:
                self._log.debug(
                    "skipping_inactive_dependency",
                    source=str(source_id),
                    target=str(target_id),
                )
                continue

            # Ensure nodes exist
            if not self._graph.has_node(source_id):
                self._graph.add_node(source_id)
            if not self._graph.has_node(target_id):
                self._graph.add_node(target_id)

            if must_type.lower() == "must":
                self._graph.add_edge(
                    source_id,
                    target_id,
                    type=EDGE_TYPE_PREREQUISITE,
                    time_offset=time_offset,
                    timing_relation=timing_relation,
                )
                self._log.debug(
                    "added_prerequisite_edge",
                    source=str(source_id),
                    target=str(target_id),
                    time_offset=time_offset,
                    timing_relation=timing_relation,
                )
            elif must_type.lower() == "must not":
                self._graph.add_edge(
                    source_id,
                    target_id,
                    type=EDGE_TYPE_MUTEX,
                    time_offset=time_offset,
                    timing_relation=timing_relation,
                )
                self._log.debug(
                    "added_mutex_edge",
                    source=str(source_id),
                    target=str(target_id),
                )
            else:
                self._log.warning(
                    "unknown_dependency_type",
                    must_or_must_not=must_type,
                    source=str(source_id),
                    target=str(target_id),
                )

        self._log.info(
            "graph_built",
            nodes=self._graph.number_of_nodes(),
            edges=self._graph.number_of_edges(),
        )
        return self._graph

    def add_synergy(
        self,
        source_id: Any,
        target_id: Any,
        capex_reduction: float = 0.0,
        opex_reduction: float = 0.0,
    ) -> None:
        """Add a synergy edge between two projects.

        A synergy means the combined value of selecting both projects exceeds
        the sum of their individual values (e.g., shared facilities reduce CAPEX).

        Parameters
        ----------
        source_id:
            First project identifier.
        target_id:
            Second project identifier.
        capex_reduction:
            CAPEX savings when both projects are selected (in currency units).
        opex_reduction:
            OPEX savings when both projects are selected (in currency units).
        """
        if not self._graph.has_node(source_id):
            self._graph.add_node(source_id)
        if not self._graph.has_node(target_id):
            self._graph.add_node(target_id)

        self._graph.add_edge(
            source_id,
            target_id,
            type=EDGE_TYPE_SYNERGY,
            capex_reduction=capex_reduction,
            opex_reduction=opex_reduction,
        )
        self._log.debug(
            "added_synergy_edge",
            source=str(source_id),
            target=str(target_id),
            capex_reduction=capex_reduction,
            opex_reduction=opex_reduction,
        )

    def add_shared_infrastructure(
        self,
        project_ids: list[Any],
        infra_id: str,
        capacity: float,
        requirements: dict[Any, float],
    ) -> None:
        """Add shared infrastructure constraints between projects.

        All listed projects share a physical infrastructure resource (e.g.,
        platform slots, pipeline throughput) with a finite total capacity.

        Parameters
        ----------
        project_ids:
            List of project identifiers that share the infrastructure.
        infra_id:
            Unique identifier for the infrastructure resource.
        capacity:
            Total available capacity of the infrastructure.
        requirements:
            Mapping of ``project_id -> capacity_required`` for each project.
        """
        # Create a virtual infrastructure node
        infra_node = f"__infra__{infra_id}"
        self._graph.add_node(
            infra_node,
            node_type="infrastructure",
            infra_id=infra_id,
            capacity=capacity,
        )

        for project_id in project_ids:
            if not self._graph.has_node(project_id):
                self._graph.add_node(project_id)

            requirement = requirements.get(project_id, 0.0)
            self._graph.add_edge(
                project_id,
                infra_node,
                type=EDGE_TYPE_SHARED_INFRA,
                infra_id=infra_id,
                capacity=capacity,
                requirement=requirement,
            )

        self._log.debug(
            "added_shared_infra",
            infra_id=infra_id,
            capacity=capacity,
            project_count=len(project_ids),
        )

    def add_resource_constraint(
        self,
        project_ids: list[Any],
        resource_name: str,
        available: float,
        requirements: dict[Any, float],
    ) -> None:
        """Add a resource constraint across multiple projects.

        Projects compete for a limited resource (e.g., drilling rigs,
        personnel, annual budget).

        Parameters
        ----------
        project_ids:
            List of project identifiers that require the resource.
        resource_name:
            Human-readable resource name.
        available:
            Total available resource quantity.
        requirements:
            Mapping of ``project_id -> resource_required``.
        """
        resource_node = f"__resource__{resource_name}"
        self._graph.add_node(
            resource_node,
            node_type="resource",
            resource_name=resource_name,
            available=available,
        )

        for project_id in project_ids:
            if not self._graph.has_node(project_id):
                self._graph.add_node(project_id)

            requirement = requirements.get(project_id, 0.0)
            self._graph.add_edge(
                project_id,
                resource_node,
                type=EDGE_TYPE_RESOURCE,
                resource_name=resource_name,
                available=available,
                requirement=requirement,
            )

        self._log.debug(
            "added_resource_constraint",
            resource_name=resource_name,
            available=available,
            project_count=len(project_ids),
        )

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def get_independent_projects(self, all_project_ids: set[Any]) -> set[Any]:
        """Return the set of project IDs that have no dependencies.

        Independent projects are those that do not appear in the
        dependency graph at all. They can be pre-computed as standalone
        NPV scalars for faster optimization.

        Parameters
        ----------
        all_project_ids:
            Complete set of project IDs in the portfolio.

        Returns
        -------
        set
            Project IDs with no interdependencies.
        """
        # Filter out virtual nodes (infrastructure / resource)
        graph_project_ids = {
            node
            for node in self._graph.nodes()
            if not self._is_virtual_node(node)
        }
        independent = all_project_ids - graph_project_ids
        self._log.debug(
            "independent_projects",
            total=len(all_project_ids),
            independent=len(independent),
            interdependent=len(graph_project_ids),
        )
        return independent

    def get_interdependent_projects(self) -> set[Any]:
        """Return the set of project IDs that participate in dependencies.

        Returns
        -------
        set
            Project IDs that appear as nodes in the dependency graph
            (excluding virtual infrastructure/resource nodes).
        """
        return {
            node
            for node in self._graph.nodes()
            if not self._is_virtual_node(node)
        }

    def get_predecessors(self, project_id: Any) -> list[Any]:
        """Return direct predecessors (parents) of a project.

        Parameters
        ----------
        project_id:
            The project to query.

        Returns
        -------
        list
            Predecessor project IDs (excluding virtual nodes).
        """
        if not self._graph.has_node(project_id):
            return []
        return [
            pred
            for pred in self._graph.predecessors(project_id)
            if not self._is_virtual_node(pred)
        ]

    def get_successors(self, project_id: Any) -> list[Any]:
        """Return direct successors (children) of a project.

        Parameters
        ----------
        project_id:
            The project to query.

        Returns
        -------
        list
            Successor project IDs (excluding virtual nodes).
        """
        if not self._graph.has_node(project_id):
            return []
        return [
            succ
            for succ in self._graph.successors(project_id)
            if not self._is_virtual_node(succ)
        ]

    def get_critical_path(self) -> list[Any]:
        """Compute the critical path through prerequisite edges.

        The critical path is the longest path through the subgraph of
        prerequisite edges only (weighted by ``1 + abs(time_offset)``).

        Returns
        -------
        list
            Ordered list of project IDs forming the critical path.
            Returns an empty list if the prerequisite subgraph is empty
            or contains cycles.
        """
        # Build a subgraph of prerequisite edges only
        prereq_edges = [
            (u, v, data)
            for u, v, data in self._graph.edges(data=True)
            if data.get("type") == EDGE_TYPE_PREREQUISITE
        ]
        if not prereq_edges:
            return []

        subgraph = nx.DiGraph()
        for u, v, data in prereq_edges:
            weight = 1 + abs(data.get("time_offset", 0))
            subgraph.add_edge(u, v, weight=weight)

        # Critical path requires a DAG
        if not nx.is_directed_acyclic_graph(subgraph):
            self._log.warning("critical_path_has_cycles")
            return []

        try:
            path = nx.dag_longest_path(subgraph, weight="weight")
        except nx.NetworkXUnfeasible:
            self._log.warning("critical_path_unfeasible")
            return []

        self._log.debug("critical_path", path=[str(n) for n in path], length=len(path))
        return list(path)

    def get_centrality_scores(self) -> dict[Any, float]:
        """Compute betweenness centrality for all project nodes.

        Higher centrality means a project is more important as a bridge
        between other interdependent projects.

        Returns
        -------
        dict
            Mapping of project_id to betweenness centrality score (0.0 -- 1.0).
        """
        if self._graph.number_of_nodes() == 0:
            return {}

        centrality: dict[Any, float] = nx.betweenness_centrality(self._graph)
        # Filter out virtual nodes
        return {
            node: score
            for node, score in centrality.items()
            if not self._is_virtual_node(node)
        }

    def to_visualization_data(self) -> dict[str, Any]:
        """Export graph data for frontend D3.js / React Flow rendering.

        Returns
        -------
        dict
            Dictionary with ``nodes`` and ``edges`` lists suitable for
            frontend consumption::

                {
                    "nodes": [
                        {"id": "...", "label": "...", "type": "project"|"infrastructure"|"resource"},
                        ...
                    ],
                    "edges": [
                        {"source": "...", "target": "...", "type": "prerequisite"|..., "data": {...}},
                        ...
                    ],
                    "stats": {
                        "node_count": int,
                        "edge_count": int,
                        "has_cycles": bool,
                    }
                }
        """
        nodes: list[dict[str, Any]] = []
        for node_id, node_data in self._graph.nodes(data=True):
            node_type = node_data.get("node_type", "project")
            label = str(node_id)
            if node_type == "infrastructure":
                label = f"Infra: {node_data.get('infra_id', node_id)}"
            elif node_type == "resource":
                label = f"Resource: {node_data.get('resource_name', node_id)}"

            nodes.append({
                "id": str(node_id),
                "label": label,
                "type": node_type,
                "data": {k: v for k, v in node_data.items() if k != "node_type"},
            })

        edges: list[dict[str, Any]] = []
        for source, target, edge_data in self._graph.edges(data=True):
            edge_type = edge_data.get("type", "unknown")
            edge_metadata = {k: v for k, v in edge_data.items() if k != "type"}
            edges.append({
                "source": str(source),
                "target": str(target),
                "type": edge_type,
                "data": edge_metadata,
            })

        # Check for cycles without raising
        has_cycles = not nx.is_directed_acyclic_graph(self._graph)

        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "node_count": self._graph.number_of_nodes(),
                "edge_count": self._graph.number_of_edges(),
                "has_cycles": has_cycles,
            },
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_virtual_node(node: Any) -> bool:
        """Return True if the node is a virtual infrastructure/resource node."""
        node_str = str(node)
        return node_str.startswith("__infra__") or node_str.startswith("__resource__")

# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import logging
from typing import Generator

import rustworkx as rx
from rustworkx import NoEdgeBetweenNodes
from rustworkx.visit import BFSVisitor, PruneSearch, StopSearch

from power_grid_model_ds._core.model.graphs.errors import MissingBranchError, MissingNodeError, NoPathBetweenNodes
from power_grid_model_ds._core.model.graphs.models._rustworkx_search import find_fundamental_cycles_rustworkx
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel

_logger = logging.getLogger(__name__)


class RustworkxGraphModel(BaseGraphModel):
    """A wrapper around the graph from the 'rustworkx' package"""

    def __init__(self, active_only=False) -> None:
        super().__init__(active_only=active_only)
        self._graph: rx.PyGraph = rx.PyGraph()
        self._internal_to_external: dict[int, int] = {}
        self._external_to_internal: dict[int, int] = {}

    @property
    def nr_nodes(self):
        return self._graph.num_nodes()

    @property
    def nr_branches(self):
        return self._graph.num_edges()

    @property
    def external_ids(self) -> list[int]:
        return list(self._external_to_internal.keys())

    # pylint: disable=duplicate-code
    def external_to_internal(self, ext_node_id: int):
        try:
            return self._external_to_internal[ext_node_id]
        except KeyError as error:
            raise MissingNodeError(f"External node id '{ext_node_id}' does NOT exist!") from error

    def internal_to_external(self, int_node_id: int):
        return self._internal_to_external[int_node_id]

    def _add_node(self, ext_node_id: int):
        graph_node_id = self._graph.add_node(ext_node_id)
        self._external_to_internal[ext_node_id] = graph_node_id
        self._internal_to_external[graph_node_id] = ext_node_id

    def _add_nodes(self, ext_node_ids: list[int]) -> None:
        graph_node_ids = self._graph.add_nodes_from(ext_node_ids)
        for ext_node_id, graph_node_id in zip(ext_node_ids, graph_node_ids):
            self._external_to_internal[ext_node_id] = graph_node_id
            self._internal_to_external[graph_node_id] = ext_node_id

    def _delete_node(self, node_id: int):
        self._graph.remove_node(node_id)
        external_node_id = self._internal_to_external.pop(node_id)
        self._external_to_internal.pop(external_node_id)

    def _has_branch(self, from_node_id: int, to_node_id: int) -> bool:
        return self._graph.has_edge(from_node_id, to_node_id)

    def _has_node(self, node_id: int) -> bool:
        return self._graph.has_node(node_id)

    def _add_branch(self, from_node_id: int, to_node_id: int):
        self._graph.add_edge(from_node_id, to_node_id, None)

    def _add_branches(self, from_node_ids: list[int], to_node_ids: list[int]):
        edge_list = [(from_node_id, to_node_id, None) for from_node_id, to_node_id in zip(from_node_ids, to_node_ids)]
        self._graph.add_edges_from(edge_list)

    def _delete_branch(self, from_node_id: int, to_node_id: int) -> None:
        try:
            self._graph.remove_edge(from_node_id, to_node_id)
        except NoEdgeBetweenNodes as error:
            raise MissingBranchError(f"No edge between (internal) nodes {from_node_id} and {to_node_id}") from error

    def _get_shortest_path(self, source: int, target: int) -> tuple[list[int], int]:
        path_mapping = rx.dijkstra_shortest_paths(self._graph, source, target)

        if target not in path_mapping:
            raise NoPathBetweenNodes(f"No path between internal nodes {source} and {target}")

        path_nodes = list(path_mapping[target])
        return path_nodes, len(path_nodes) - 1

    def _get_all_paths(self, source: int, target: int) -> list[list[int]]:
        return list(rx.all_simple_paths(self._graph, source, target))

    def _get_components(self) -> list[list[int]]:
        components = rx.connected_components(self._graph)
        return [list(component) for component in components]

    def _get_connected(self, node_id: int, nodes_to_ignore: list[int], inclusive: bool = False) -> list[int]:
        visitor = _NodeVisitor(nodes_to_ignore)
        rx.bfs_search(self._graph, [node_id], visitor)
        connected_nodes = visitor.nodes
        if not inclusive:
            connected_nodes.remove(node_id)

        return connected_nodes

    def _in_branches(self, int_node_id: int) -> Generator[tuple[int, int], None, None]:
        return ((source, target) for source, target, _ in self._graph.in_edges(int_node_id))

    def _find_first_connected(self, node_id: int, candidate_node_ids: list[int]) -> int:
        visitor = _NodeFinder(candidate_nodes=candidate_node_ids)
        rx.bfs_search(self._graph, [node_id], visitor)
        if visitor.found_node is None:
            raise MissingNodeError(f"node {node_id} is not connected to any of the candidate nodes")
        return visitor.found_node

    def _find_fundamental_cycles(self) -> list[list[int]]:
        """Find all fundamental cycles in the graph using Rustworkx.

        Returns:
            list[list[int]]: A list of cycles, each cycle is a list of node IDs.
        """
        return find_fundamental_cycles_rustworkx(self._graph)

    def _all_branches(self) -> Generator[tuple[int, int], None, None]:
        return ((source, target) for source, target in self._graph.edge_list())


class _NodeVisitor(BFSVisitor):
    def __init__(self, nodes_to_ignore: list[int]):
        self.nodes_to_ignore = nodes_to_ignore
        self.nodes: list[int] = []

    def discover_vertex(self, v):
        if v in self.nodes_to_ignore:
            raise PruneSearch
        self.nodes.append(v)


class _NodeFinder(BFSVisitor):
    """Visitor that stops the search when a candidate node is found"""

    def __init__(self, candidate_nodes: list[int]):
        self.candidate_nodes = candidate_nodes
        self.found_node: int | None = None

    def discover_vertex(self, v):
        if v in self.candidate_nodes:
            self.found_node = v
            raise StopSearch

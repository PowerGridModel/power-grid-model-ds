# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from abc import ABC, abstractmethod

import numpy as np
from numpy._typing import NDArray

from power_grid_model_ds._core.model.arrays.pgm_arrays import Branch3Array, BranchArray, NodeArray
from power_grid_model_ds._core.model.containers.grid_protocol import MinimalGridArrays
from power_grid_model_ds._core.model.graphs.errors import (
    GraphError,
    MissingBranchError,
    MissingNodeError,
    NoPathBetweenNodes,
)


# pylint: disable=too-many-public-methods
class BaseGraphModel(ABC):
    """Base class for graph models"""

    def __init__(self, active_only=False) -> None:
        self.active_only = active_only

    @property
    @abstractmethod
    def nr_nodes(self):
        """Returns the number of nodes in the graph"""

    @property
    @abstractmethod
    def nr_branches(self):
        """Returns the number of branches in the graph"""

    @abstractmethod
    def external_to_internal(self, ext_node_id: int) -> int:
        """Convert external node id to internal node id (internal)

        Raises:
            MissingNodeError: if the external node id does not exist in the graph
        """

    @abstractmethod
    def internal_to_external(self, int_node_id: int) -> int:
        """Convert internal id (internal) to external node id"""

    @property
    @abstractmethod
    def external_ids(self) -> list[int]:
        """Return all external node ids

        Warning: Depending on graph engine, performance could be slow for large graphs
        """

    def has_node(self, node_id: int) -> bool:
        """Check if a node exists."""
        try:
            internal_node_id = self.external_to_internal(ext_node_id=node_id)
        except MissingNodeError:
            return False

        return self._has_node(node_id=internal_node_id)

    def add_node(self, ext_node_id: int, raise_on_fail: bool = True) -> None:
        """Add a node to the graph."""
        if self.has_node(ext_node_id):
            if raise_on_fail:
                raise GraphError(f"External node id '{ext_node_id}' already exists!")
            return

        self._add_node(ext_node_id)

    def delete_node(self, ext_node_id: int, raise_on_fail: bool = True) -> None:
        """Remove a node from the graph.

        Args:
            ext_node_id(int): id of the node to remove
            raise_on_fail(bool): whether to raise an error if the node does not exist. Defaults to True

        Raises:
            MissingNodeError: if the node does not exist in the graph and ``raise_on_fail=True``
        """
        try:
            internal_node_id = self.external_to_internal(ext_node_id)
        except MissingNodeError as error:
            if raise_on_fail:
                raise error
            return

        self._delete_node(node_id=internal_node_id)

    def add_node_array(self, node_array: NodeArray, raise_on_fail: bool = True) -> None:
        """Add all nodes in the node array to the graph."""
        for node in node_array:
            self.add_node(ext_node_id=node.id.item(), raise_on_fail=raise_on_fail)

    def delete_node_array(self, node_array: NodeArray, raise_on_fail: bool = True) -> None:
        """Delete all nodes in node_array from the graph"""
        for node in node_array:
            self.delete_node(node.id.item(), raise_on_fail=raise_on_fail)

    def has_branch(self, from_ext_node_id: int, to_ext_node_id: int) -> bool:
        """Check if a branch exists between two nodes."""
        try:
            int_from_node_id = self.external_to_internal(from_ext_node_id)
            int_to_node_id = self.external_to_internal(to_ext_node_id)
        except MissingNodeError:
            return False

        return self._has_branch(from_node_id=int_from_node_id, to_node_id=int_to_node_id)

    def add_branch(self, from_ext_node_id: int, to_ext_node_id: int) -> None:
        """Add a new branch to the graph."""
        self._add_branch(
            from_node_id=self.external_to_internal(from_ext_node_id),
            to_node_id=self.external_to_internal(to_ext_node_id),
        )

    def delete_branch(self, from_ext_node_id: int, to_ext_node_id: int, raise_on_fail: bool = True) -> None:
        """Remove an existing branch from the graph.

        Args:
            from_ext_node_id: id of the from node
            to_ext_node_id: id of the to node
            raise_on_fail: whether to raise an error if the branch does not exist

        Raises:
            MissingBranchError: if branch does not exist in the graph and ``raise_on_fail=True``
        """
        try:
            self._delete_branch(
                from_node_id=self.external_to_internal(from_ext_node_id),
                to_node_id=self.external_to_internal(to_ext_node_id),
            )
        except (MissingNodeError, MissingBranchError) as error:
            if raise_on_fail:
                raise MissingBranchError(
                    f"Branch between nodes {from_ext_node_id} and {to_ext_node_id} does NOT exist!"
                ) from error

    def add_branch_array(self, branch_array: BranchArray) -> None:
        """Add all branches in the branch array to the graph."""
        for branch in branch_array:
            if self._branch_is_relevant(branch):
                self.add_branch(branch.from_node.item(), branch.to_node.item())

    def add_branch3_array(self, branch3_array: Branch3Array) -> None:
        """Add all branch3s in the branch3 array to the graph."""
        for branch3 in branch3_array:
            branches = _get_branch3_branches(branch3)
            self.add_branch_array(branches)

    def delete_branch_array(self, branch_array: BranchArray, raise_on_fail: bool = True) -> None:
        """Delete all branches in branch_array from the graph."""
        for branch in branch_array:
            if self._branch_is_relevant(branch):
                self.delete_branch(branch.from_node.item(), branch.to_node.item(), raise_on_fail=raise_on_fail)

    def delete_branch3_array(self, branch_array: Branch3Array, raise_on_fail: bool = True) -> None:
        """Delete all branch3s in the branch3 array from the graph."""
        for branch3 in branch_array:
            branches = _get_branch3_branches(branch3)
            self.delete_branch_array(branches, raise_on_fail=raise_on_fail)

    def get_shortest_path(self, ext_start_node_id: int, ext_end_node_id: int) -> tuple[list[int], int]:
        """Calculate the shortest path between two nodes

        Example:
            given this graph: [1] - [2] - [3] - [4]

            >>> graph.get_shortest_path(1, 4) == [1, 2, 3, 4], 3
            >>> graph.get_shortest_path(1, 1) == [1], 0

        Returns:
            tuple[list[int], int]: a tuple where the first element is a list of external nodes from start to end.
            The second element is the distance of the path in number of edges.

        Raises:
            NoPathBetweenNodes: if no path exists between the given nodes
        """
        if ext_start_node_id == ext_end_node_id:
            return [ext_start_node_id], 0

        try:
            internal_path, distance = self._get_shortest_path(
                source=self.external_to_internal(ext_start_node_id), target=self.external_to_internal(ext_end_node_id)
            )
            return self._internals_to_externals(internal_path), distance
        except NoPathBetweenNodes as e:
            raise NoPathBetweenNodes(f"No path between nodes {ext_start_node_id} and {ext_end_node_id}") from e

    def get_all_paths(self, ext_start_node_id: int, ext_end_node_id: int) -> list[list[int]]:
        """Retrieves all paths between two (external) nodes.
        Returns a list of paths, each path containing a list of external nodes.
        """
        if ext_start_node_id == ext_end_node_id:
            return []

        internal_paths = self._get_all_paths(
            source=self.external_to_internal(ext_start_node_id),
            target=self.external_to_internal(ext_end_node_id),
        )

        if internal_paths == []:
            raise NoPathBetweenNodes(f"No path between nodes {ext_start_node_id} and {ext_end_node_id}")

        return [self._internals_to_externals(path) for path in internal_paths]

    def get_components(self, substation_nodes: NDArray[np.int32]) -> list[list[int]]:
        """Returns all separate components when the substation_nodes are removed of the graph as lists"""
        internal_components = self._get_components(substation_nodes=self._externals_to_internals(substation_nodes))
        return [self._internals_to_externals(component) for component in internal_components]

    def get_connected(
        self, node_id: int, nodes_to_ignore: list[int] | None = None, inclusive: bool = False
    ) -> list[int]:
        """Find all nodes connected to the node_id

        Args:
            node_id: node id to start the search from
            inclusive: whether to include the given node id in the result
            nodes_to_ignore: list of node ids to ignore while traversing the graph.
                              Any nodes connected to `node_id` (solely) through these nodes will
                              not be included in the result
        Returns:
            nodes: list of node ids sorted by distance, connected to the node id
        """
        if nodes_to_ignore is None:
            nodes_to_ignore = []

        nodes = self._get_connected(
            node_id=self.external_to_internal(node_id),
            nodes_to_ignore=self._externals_to_internals(nodes_to_ignore),
            inclusive=inclusive,
        )
        return self._internals_to_externals(nodes)

    def find_fundamental_cycles(self) -> list[list[int]]:
        """Find all fundamental cycles in the graph.
        Returns:
            list[list[int]]: list of cycles, each cycle is a list of (external) node ids
        """
        internal_cycles = self._find_fundamental_cycles()
        return [self._internals_to_externals(nodes) for nodes in internal_cycles]

    @classmethod
    def from_arrays(cls, arrays: MinimalGridArrays, active_only=False) -> "BaseGraphModel":
        """Build from arrays"""
        new_graph = cls(active_only=active_only)

        new_graph.add_node_array(node_array=arrays.node)
        new_graph.add_branch_array(arrays.branches)
        new_graph.add_branch3_array(arrays.three_winding_transformer)

        return new_graph

    def _internals_to_externals(self, internal_nodes: list[int]) -> list[int]:
        """Convert a list of internal nodes to external nodes"""
        return [self.internal_to_external(node_id) for node_id in internal_nodes]

    def _externals_to_internals(self, external_nodes: list[int] | NDArray) -> list[int]:
        """Convert a list of external nodes to internal nodes"""
        return [self.external_to_internal(node_id) for node_id in external_nodes]

    def _branch_is_relevant(self, branch: BranchArray) -> bool:
        """Check if a branch is relevant"""
        if self.active_only:
            return branch.is_active.item()
        return True

    @abstractmethod
    def _get_connected(self, node_id: int, nodes_to_ignore: list[int], inclusive: bool = False) -> list[int]: ...

    @abstractmethod
    def _has_branch(self, from_node_id, to_node_id) -> bool: ...

    @abstractmethod
    def _has_node(self, node_id) -> bool: ...

    @abstractmethod
    def _add_node(self, ext_node_id: int) -> None: ...

    @abstractmethod
    def _delete_node(self, node_id: int): ...

    @abstractmethod
    def _add_branch(self, from_node_id, to_node_id) -> None: ...

    @abstractmethod
    def _delete_branch(self, from_node_id, to_node_id) -> None:
        """
        Raises:
            MissingBranchError: if the branch does not exist
        """

    @abstractmethod
    def _get_shortest_path(self, source, target): ...

    @abstractmethod
    def _get_all_paths(self, source, target) -> list[list[int]]: ...

    @abstractmethod
    def _get_components(self, substation_nodes: list[int]) -> list[list[int]]: ...

    @abstractmethod
    def _find_fundamental_cycles(self) -> list[list[int]]: ...


def _get_branch3_branches(branch3: Branch3Array) -> BranchArray:
    node_1 = branch3.node_1.item()
    node_2 = branch3.node_2.item()
    node_3 = branch3.node_3.item()

    status_1 = branch3.status_1.item()
    status_2 = branch3.status_2.item()
    status_3 = branch3.status_3.item()

    branches = BranchArray.zeros(3)
    branches.from_node = [node_1, node_1, node_2]
    branches.to_node = [node_2, node_3, node_3]
    branches.from_status = [status_1, status_1, status_2]
    branches.to_status = [status_2, status_3, status_3]

    return branches
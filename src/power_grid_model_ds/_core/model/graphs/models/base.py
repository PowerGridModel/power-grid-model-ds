# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator

from numpy._typing import NDArray

from power_grid_model_ds._core.model.arrays.pgm_arrays import Branch3Array, BranchArray, NodeArray
from power_grid_model_ds._core.model.graphs.errors import (
    GraphError,
    MissingBranchError,
    MissingNodeError,
    NoPathBetweenNodes,
)

if TYPE_CHECKING:
    from power_grid_model_ds._core.model.grids.base import Grid


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

    @property
    def all_branches(self) -> Generator[tuple[int, int], None, None]:
        """Returns all branches in the graph."""
        return (
            (self.internal_to_external(source), self.internal_to_external(target))
            for source, target in self._all_branches()
        )

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

    def in_branches(self, node_id: int) -> Generator[tuple[int, int], None, None]:
        """Return all branches that have the node as an endpoint."""
        int_node_id = self.external_to_internal(node_id)
        internal_edges = self._in_branches(int_node_id=int_node_id)
        return (
            (self.internal_to_external(source), self.internal_to_external(target)) for source, target in internal_edges
        )

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
        if raise_on_fail and any(self.has_node(x) for x in node_array["id"]):
            raise GraphError("At least one node id already exists in the Graph.")
        self._add_nodes(node_array["id"].tolist())

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
        if self.active_only:
            branch_array = branch_array[branch_array.is_active]
            if not branch_array.size:
                return

        from_node_ids = self._externals_to_internals(branch_array["from_node"].tolist())
        to_node_ids = self._externals_to_internals(branch_array["to_node"].tolist())
        self._add_branches(from_node_ids, to_node_ids)

    def add_branch3_array(self, branch3_array: Branch3Array) -> None:
        """Add all branch3s in the branch3 array to the graph."""
        for branch3 in branch3_array:
            self.add_branch_array(branch3.as_branches())

    def delete_branch_array(self, branch_array: BranchArray, raise_on_fail: bool = True) -> None:
        """Delete all branches in branch_array from the graph."""
        for branch in branch_array:
            if self._branch_is_relevant(branch):
                self.delete_branch(branch.from_node.item(), branch.to_node.item(), raise_on_fail=raise_on_fail)

    def delete_branch3_array(self, branch3_array: Branch3Array, raise_on_fail: bool = True) -> None:
        """Delete all branch3s in the branch3 array from the graph."""
        for branch3 in branch3_array:
            self.delete_branch_array(branch3.as_branches(), raise_on_fail=raise_on_fail)

    @contextmanager
    def tmp_remove_nodes(self, nodes: list[int]) -> Generator:
        """Context manager that temporarily removes nodes and their branches from the graph.
        Example:
            >>> with graph.tmp_remove_nodes([1, 2, 3]):
            >>>    assert not graph.has_node(1)
            >>> assert graph.has_node(1)
        In practice, this is useful when you want to e.g. calculate the shortest path between two nodes without
        considering certain nodes.
        """
        edge_list = []
        for node in nodes:
            edge_list += list(self.in_branches(node))
            self.delete_node(node)

        yield

        for node in nodes:
            self.add_node(int(node))  # convert to int to avoid type issues when input is e.g. a numpy array
        for source, target in edge_list:
            self.add_branch(source, target)

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

        return [self._internals_to_externals(path) for path in internal_paths]

    def get_components(self) -> list[list[int]]:
        """Returns all separate components when the substation_nodes are removed of the graph as lists

        If you want to get the components of the graph without certain nodes,
        use the `tmp_remove_nodes` context manager.

        Example:
        >>> with graph.tmp_remove_nodes(substation_nodes):
        >>>    components = graph.get_components()
        """
        internal_components = self._get_components()
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

    def find_first_connected(self, node_id: int, candidate_node_ids: list[int]) -> int:
        """Find the first connected node to the node_id from the candidate_node_ids

        Note:
            If multiple candidate nodes are connected to the node, the first one found is returned.
            There is no guarantee that the same candidate node will be returned each time.

        Raises:
            MissingNodeError: if no connected node is found
            ValueError: if the node_id is in candidate_node_ids
        """
        internal_node_id = self.external_to_internal(node_id)
        internal_candidates = self._externals_to_internals(candidate_node_ids)
        if internal_node_id in internal_candidates:
            raise ValueError("node_id cannot be in candidate_node_ids")
        return self.internal_to_external(self._find_first_connected(internal_node_id, internal_candidates))

    def get_downstream_nodes(self, node_id: int, start_node_ids: list[int], inclusive: bool = False) -> list[int]:
        """Find all nodes downstream of the node_id with respect to the start_node_ids

        Example:
            given this graph: [1] - [2] - [3] - [4]
            >>> graph.get_downstream_nodes(2, [1]) == [3, 4]
            >>> graph.get_downstream_nodes(2, [1], inclusive=True) == [2, 3, 4]

        args:
            node_id: node id to start the search from
            start_node_ids: list of node ids considered 'above' the node_id
            inclusive: whether to include the given node id in the result
        returns:
            list of node ids sorted by distance, downstream of to the node id
        """
        connected_node = self.find_first_connected(node_id, start_node_ids)
        path, _ = self.get_shortest_path(node_id, connected_node)
        _, upstream_node, *_ = (
            path  # path is at least 2 elements long or find_first_connected would have raised an error
        )

        return self.get_connected(node_id, [upstream_node], inclusive)

    def find_fundamental_cycles(self) -> list[list[int]]:
        """Find all fundamental cycles in the graph.
        Returns:
            list[list[int]]: list of cycles, each cycle is a list of (external) node ids
        """
        internal_cycles = self._find_fundamental_cycles()
        return [self._internals_to_externals(nodes) for nodes in internal_cycles]

    @classmethod
    def from_arrays(cls, arrays: "Grid", active_only=False) -> "BaseGraphModel":
        """Build from arrays"""
        new_graph = cls(active_only=active_only)

        new_graph.add_node_array(node_array=arrays.node, raise_on_fail=False)
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
    def _in_branches(self, int_node_id: int) -> Generator[tuple[int, int], None, None]: ...

    @abstractmethod
    def _get_connected(self, node_id: int, nodes_to_ignore: list[int], inclusive: bool = False) -> list[int]: ...

    @abstractmethod
    def _find_first_connected(self, node_id: int, candidate_node_ids: list[int]) -> int: ...

    @abstractmethod
    def _has_branch(self, from_node_id, to_node_id) -> bool: ...

    @abstractmethod
    def _has_node(self, node_id) -> bool: ...

    @abstractmethod
    def _add_node(self, ext_node_id: int) -> None: ...

    @abstractmethod
    def _add_nodes(self, ext_node_ids: list[int]) -> None: ...

    @abstractmethod
    def _delete_node(self, node_id: int): ...

    @abstractmethod
    def _add_branch(self, from_node_id: int, to_node_id: int) -> None: ...

    @abstractmethod
    def _add_branches(self, from_node_ids: list[int], to_node_ids: list[int]) -> None: ...

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
    def _get_components(self) -> list[list[int]]: ...

    @abstractmethod
    def _find_fundamental_cycles(self) -> list[list[int]]: ...

    @abstractmethod
    def _all_branches(self) -> Generator[tuple[int, int], None, None]: ...

# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Base grid classes"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self, Type, TypeVar

import numpy as np
import numpy.typing as npt

from power_grid_model_ds._core.model.arrays import (
    AsymCurrentSensorArray,
    AsymLineArray,
    AsymPowerSensorArray,
    AsymVoltageSensorArray,
    Branch3Array,
    BranchArray,
    GenericBranchArray,
    LineArray,
    LinkArray,
    NodeArray,
    SourceArray,
    SymCurrentSensorArray,
    SymGenArray,
    SymLoadArray,
    SymPowerSensorArray,
    SymVoltageSensorArray,
    ThreeWindingTransformerArray,
    TransformerArray,
    TransformerTapRegulatorArray,
)
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.containers.base import FancyArrayContainer
from power_grid_model_ds._core.model.containers.helpers import container_equal
from power_grid_model_ds._core.model.graphs.container import GraphContainer
from power_grid_model_ds._core.model.graphs.models import RustworkxGraphModel
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel
from power_grid_model_ds._core.model.grids._feeders import set_feeder_ids
from power_grid_model_ds._core.model.grids._helpers import (
    create_empty_grid,
    create_grid_from_extended_grid,
    merge_grids,
)
from power_grid_model_ds._core.model.grids._modify import (
    add_array_to_grid,
    add_branch,
    add_node,
    delete_branch,
    delete_branch3,
    delete_node,
    make_active,
    make_inactive,
    reverse_branches,
)
from power_grid_model_ds._core.model.grids._search import (
    get_branch_arrays,
    get_branches,
    get_downstream_nodes,
    get_nearest_substation_node,
    get_typed_branches,
)
from power_grid_model_ds._core.model.grids.serialization.pickle import load_grid_from_pickle, save_grid_to_pickle
from power_grid_model_ds._core.model.grids.serialization.string import (
    deserialize_from_str,
    deserialize_from_txt_file,
    serialize_to_str,
)

G = TypeVar("G", bound="Grid")

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods


@dataclass
class Grid(FancyArrayContainer):
    """Grid object containing the entire network and interface to interact with it.

    Examples:

        >>> from power_grid_model_ds import Grid
        >>> grid = Grid.empty()
        >>> grid
    """

    graphs: GraphContainer
    """The graph representations of the grid."""

    # nodes
    node: NodeArray

    # branches
    transformer: TransformerArray
    three_winding_transformer: ThreeWindingTransformerArray
    line: LineArray
    link: LinkArray
    generic_branch: GenericBranchArray
    asym_line: AsymLineArray

    source: SourceArray
    sym_load: SymLoadArray
    sym_gen: SymGenArray

    # regulators
    transformer_tap_regulator: TransformerTapRegulatorArray

    # sensors
    sym_power_sensor: SymPowerSensorArray
    sym_voltage_sensor: SymVoltageSensorArray
    sym_current_sensor: SymCurrentSensorArray
    asym_power_sensor: AsymPowerSensorArray
    asym_voltage_sensor: AsymVoltageSensorArray
    asym_current_sensor: AsymCurrentSensorArray

    def __str__(self) -> str:
        """Serialize grid to a string.
        Compatible with https://csacademy.com/app/graph_editor/
        """
        return serialize_to_str(self)

    def __eq__(self, other: Any) -> bool:
        """Check if two grids are equal.

        Note: differences in graphs are ignored in this comparison.
        """
        if not isinstance(other, self.__class__):
            return False
        return container_equal(self, other, ignore_extras=False, early_exit=True, fields_to_ignore=["graphs"])

    @classmethod
    def empty(cls: Type[G], graph_model: type[BaseGraphModel] = RustworkxGraphModel) -> G:
        """Create an empty grid

        Args:
            graph_model (type[BaseGraphModel], optional): The graph model to use. Defaults to RustworkxGraphModel.

        Returns:
            Grid: An empty grid
        """
        return create_empty_grid(cls, graph_model=graph_model)

    @classmethod
    # pylint: disable=arguments-differ
    def from_cache(cls: Type[Self], cache_path: Path, load_graphs: bool = True) -> Self:
        """Read from cache and build .graphs from arrays

        Args:
            cache_path (Path): The path to the cache
            load_graphs (bool, optional): Whether to load the graphs. Defaults to True.

        Returns:
            G: The grid loaded from cache
        """
        return load_grid_from_pickle(cls, cache_path=cache_path, load_graphs=load_graphs)

    @classmethod
    def from_txt(cls: Type[G], *args: str) -> G:
        """Build a grid from a list of strings

        See the documentation for the expected format of the txt_lines

        Args:
            *args (str): The lines of the grid

        Examples:
            >>> Grid.from_txt("1 2", "2 3", "3 4 transformer", "4 5", "S1 6")
            alternative: Grid.from_txt("1 2\n2 3\n3 4 transformer\n4 5\nS1 6")
        """
        return deserialize_from_str(cls, *args)

    @classmethod
    # pylint: disable=arguments-differ
    def from_txt_file(cls: Type[G], txt_file_path: Path) -> G:
        """Load grid from txt file

        Args:
            txt_file_path (Path): The path to the txt file
        """
        return deserialize_from_txt_file(cls, txt_file_path)

    @classmethod
    def from_extended(cls: Type[G], extended: G) -> G:
        """Create a grid from an extended Grid object."""
        return create_grid_from_extended_grid(cls, extended=extended)

    @property
    def branches(self) -> BranchArray:
        """Converts all branch arrays into a single BranchArray."""
        return get_branches(self)

    @property
    def branch_arrays(self) -> list[BranchArray]:
        """Returns all branch arrays"""
        return get_branch_arrays(self)

    def append(self, array: FancyArray, check_max_id: bool = True):
        """Append an array to the grid. Both 'grid arrays' and 'grid.graphs' will be updated.

        Args:
            array (FancyArray): The array to append.
            check_max_id (bool, optional): Whether to check if the array id is the maximum id. Defaults to True.
        """
        return add_array_to_grid(self, array=array, check_max_id=check_max_id)

    def add_branch(self, branch: BranchArray) -> None:
        """Add a branch to the grid

        Args:
            branch (BranchArray): The branch to add
        """
        return add_branch(self, branch)

    def delete_branch(self, branch: BranchArray) -> None:
        """Remove a branch from the grid

        Args:
            branch (BranchArray): The branch to remove
        """
        return delete_branch(self, branch=branch)

    def delete_branch3(self, branch: Branch3Array) -> None:
        """Remove a branch3 from the grid

        Args:
            branch (Branch3Array): The branch3 to remove
        """
        return delete_branch3(self, branch=branch)

    def add_node(self, node: NodeArray) -> None:
        """Add a new node to the grid

        Args:
            node (NodeArray): The node to add
        """
        return add_node(self, node=node)

    def delete_node(self, node: NodeArray) -> None:
        """Remove a node from the grid

        Args:
            node (NodeArray): The node to remove
        """
        return delete_node(self, node=node)

    def make_active(self, branch: BranchArray) -> None:
        """Make a branch active

        Args:
            branch (BranchArray): The branch to make active
        """
        return make_active(self, branch=branch)

    def make_inactive(self, branch: BranchArray, at_to_side: bool = True) -> None:
        """Make a branch inactive. This is done by setting from or to status to 0.

        Args:
            branch (BranchArray): The branch to make inactive
            at_to_side (bool, optional): Whether to deactivate the to_status instead of the from_status.
            Defaults to True.
        """
        return make_inactive(self, branch=branch, at_to_side=at_to_side)

    def set_feeder_ids(self):
        """Determines all feeder groups in the network and gives them a feeder identifier

        feeder_branch_id := All assets being connected through the same feeding branch(es) on the substation
        feeder_node_id := All assets connected to the same feeder node (substation)

        Example:
        Nodes Topology
        (SUBSTATION) 101 --- 102 --- 103 -|- 104 --- 105 --- 101 (SUBSTATION)
                             {-}
                             106

        Branches Topology:
        (SUBSTATION) *** 201 *** 202 *** 203 *** 601 *** 204 *** (SUBSTATION)
                             301
                             ***

             Substation ID | Feeder ID
        101 | -1           | -1
        102 | 101          | 201
        103 | 101          | 201
        104 | 101          | 204
        105 | 101          | 204
        106 | 101          | 201
        201 | 101          | 201
        202 | 101          | 201
        203 | 101          | -1
        204 | 101          | 204
        301 | 101          | 201
        601 | 101          | 204
        """
        return set_feeder_ids(grid=self)

    def get_typed_branches(self, branch_ids: list[int] | npt.NDArray[np.int32]) -> BranchArray:
        """Find a matching LineArray, LinkArray or TransformerArray for the given branch_ids

        Raises:
            ValueError:
                - If no branch_ids are provided.
                - If not all branch_ids are of the same type.
        """
        return get_typed_branches(self, branch_ids)

    def reverse_branches(self, branches: BranchArray):
        """Reverse the direction of the branches."""
        return reverse_branches(self, branches)

    def get_branches_in_path(self, nodes_in_path: list[int]) -> BranchArray:
        """Returns all branches within a path of nodes

        Args:
            nodes_in_path (list[int]): The nodes in the path

        Returns:
            BranchArray: The branches in the path
        """
        return self.branches.filter(from_node=nodes_in_path, to_node=nodes_in_path, from_status=1, to_status=1)

    def get_nearest_substation_node(self, node_id: int):
        """Find the nearest substation node.

        Args:
            node_id(int): The id of the node to find the nearest substation node for.

        Returns:
            NodeArray: The nearest substation node.

        Raises:
            RecordDoesNotExist: If no substation node is connected to the input node.
        """
        return get_nearest_substation_node(self, node_id=node_id)

    def get_downstream_nodes(self, node_id: int, inclusive: bool = False):
        """Get the downstream nodes from a node.
        Assuming each node has a single feeding substation and the grid is radial

        Example:
            given this graph: [1] - [2] - [3] - [4], with 1 being a substation node

            >>> graph.get_downstream_nodes(2) == [3, 4]
            >>> graph.get_downstream_nodes(3) == [4]
            >>> graph.get_downstream_nodes(3, inclusive=True) == [3, 4]

        Args:
            node_id(int): The id of the node to get the downstream nodes from.
            inclusive(bool): Whether to include the input node in the result.

        Raises:
            NotImplementedError: If the input node is a substation node.

        Returns:
            list[int]: The downstream nodes.
        """
        return get_downstream_nodes(self, node_id=node_id, inclusive=inclusive)

    def cache(self, cache_dir: Path, cache_name: str, compress: bool = True):
        """Cache Grid to a folder

        Args:
            cache_dir (Path): The directory to save the cache to.
            cache_name (str): The name of the cache.
            compress (bool, optional): Whether to compress the cache. Defaults to True.
        """
        return save_grid_to_pickle(self, cache_dir=cache_dir, cache_name=cache_name, compress=compress)

    def merge(self, other_grid: G, mode: str) -> G:
        """Merge another grid into this grid. When ids overlap, ids of other_grid are offset to avoid conflicts.

        Args:
            other_grid (G): The grid to merge into this grid.
            mode (str): The merge mode:
                - "recalculate_ids": Recalculate ids of other_grid to avoid conflicts.
                - "keep_ids": Keep ids of other_grid. Raises an error if grids contain overlapping indices.
        """

        merged_grid = merge_grids(self, other_grid, mode)

        return merged_grid

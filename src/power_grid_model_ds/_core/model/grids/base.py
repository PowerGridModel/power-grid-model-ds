# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Base grid classes"""

import dataclasses
import itertools
import logging
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Type, TypeVar

import numpy as np
import numpy.typing as npt

from power_grid_model_ds._core import fancypy as fp
from power_grid_model_ds._core.model.arrays import (
    AsymVoltageSensorArray,
    Branch3Array,
    BranchArray,
    LineArray,
    LinkArray,
    NodeArray,
    SourceArray,
    SymGenArray,
    SymLoadArray,
    SymPowerSensorArray,
    SymVoltageSensorArray,
    ThreeWindingTransformerArray,
    TransformerArray,
    TransformerTapRegulatorArray,
)
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.arrays.base.errors import RecordDoesNotExist
from power_grid_model_ds._core.model.containers.base import FancyArrayContainer
from power_grid_model_ds._core.model.enums.nodes import NodeType
from power_grid_model_ds._core.model.graphs.container import GraphContainer
from power_grid_model_ds._core.model.graphs.models import RustworkxGraphModel
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel
from power_grid_model_ds._core.model.grids._text_sources import TextSource
from power_grid_model_ds._core.model.grids.helpers import set_feeder_ids, set_is_feeder
from power_grid_model_ds._core.utils.pickle import get_pickle_path, load_from_pickle, save_to_pickle
from power_grid_model_ds._core.utils.zip import file2gzip

Self = TypeVar("Self", bound="Grid")

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

    source: SourceArray
    sym_load: SymLoadArray
    sym_gen: SymGenArray

    # regulators
    transformer_tap_regulator: TransformerTapRegulatorArray

    # sensors
    sym_power_sensor: SymPowerSensorArray
    sym_voltage_sensor: SymVoltageSensorArray
    asym_voltage_sensor: AsymVoltageSensorArray

    def __str__(self) -> str:
        """String representation of the grid.

        Compatible with https://csacademy.com/app/graph_editor/
        """
        grid_str = ""

        for transformer3 in self.three_winding_transformer:
            nodes = [transformer3.node_1.item(), transformer3.node_2.item(), transformer3.node_3.item()]
            for combo in itertools.combinations(nodes, 2):
                grid_str += f"S{combo[0]} S{combo[1]} {transformer3.id.item()},3-transformer\n"

        for branch in self.branches:
            from_node = self.node.get(id=branch.from_node).record
            to_node = self.node.get(id=branch.to_node).record

            from_node_str = f"S{from_node.id}" if from_node.node_type == NodeType.SUBSTATION_NODE else str(from_node.id)
            to_node_str = f"S{to_node.id}" if to_node.node_type == NodeType.SUBSTATION_NODE else str(to_node.id)

            suffix_str = str(branch.id.item())
            if branch.from_status.item() == 0 or branch.to_status.item() == 0:
                suffix_str = f"{suffix_str},open"

            if branch.id in self.transformer.id:
                suffix_str = f"{suffix_str},transformer"
            elif branch.id in self.link.id:
                suffix_str = f"{suffix_str},link"
            elif branch.id in self.line.id:
                pass  # no suffix needed
            else:
                raise ValueError(f"Branch {branch.id} is not a transformer, link or line")

            grid_str += f"{from_node_str} {to_node_str} {suffix_str}\n"
        return grid_str

    @property
    def branches(self) -> BranchArray:
        """Converts all branch arrays into a single BranchArray."""
        branch_dtype = BranchArray.get_dtype()
        branches = BranchArray()
        for array in self.branch_arrays:
            new_branch = BranchArray(data=array.data[list(branch_dtype.names)])
            branches = fp.concatenate(branches, new_branch)
        return branches

    @property
    def branch_arrays(self) -> list[BranchArray]:
        """Returns all branch arrays"""
        branch_arrays = []
        for field in dataclasses.fields(self):
            array = getattr(self, field.name)
            if isinstance(array, BranchArray):
                branch_arrays.append(array)
        return branch_arrays

    def get_typed_branches(self, branch_ids: list[int] | npt.NDArray[np.int32]) -> BranchArray:
        """Find a matching LineArray, LinkArray or TransformerArray for the given branch_ids

        Raises:
            ValueError:
                - If no branch_ids are provided.
                - If not all branch_ids are of the same type.
        """
        if not np.any(branch_ids):
            raise ValueError("No branch_ids provided.")
        for branch_array in self.branch_arrays:
            array = branch_array.filter(branch_ids)
            if 0 < array.size != len(branch_ids):
                raise ValueError("Branches are not of the same type.")
            if array.size:
                return array
        raise RecordDoesNotExist(f"Branches {branch_ids} not found in grid.")

    def reverse_branches(self, branches: BranchArray):
        """Reverse the direction of the branches."""
        if not branches.size:
            return
        if not isinstance(branches, (LineArray, LinkArray, TransformerArray)):
            try:
                branches = self.get_typed_branches(branches.id)
            except ValueError:
                # If the branches are not of the same type, reverse them per type (though this is slower)
                for array in self.branch_arrays:
                    self.reverse_branches(array.filter(branches.id))
                return

        from_nodes = branches.from_node
        to_nodes = branches.to_node

        array_field = self.find_array_field(branches.__class__)
        array = getattr(self, array_field.name)
        array.update_by_id(branches.id, from_node=to_nodes, to_node=from_nodes)

    @classmethod
    def empty(cls: Type[Self], graph_model: type[BaseGraphModel] = RustworkxGraphModel) -> Self:
        """Create an empty grid

        Args:
            graph_model (type[BaseGraphModel], optional): The graph model to use. Defaults to RustworkxGraphModel.

        Returns:
            Grid: An empty grid
        """
        empty_fields = cls._get_empty_fields()
        empty_fields["graphs"] = GraphContainer.empty(graph_model=graph_model)
        return cls(**empty_fields)

    def append(self, array: FancyArray, check_max_id: bool = True):
        """Append an array to the grid. Both 'grid arrays' and 'grid.graphs' will be updated.

        Args:
            array (FancyArray): The array to append.
            check_max_id (bool, optional): Whether to check if the array id is the maximum id. Defaults to True.
        """
        self._append(array, check_max_id=check_max_id)  # noqa

        # pylint: disable=protected-access
        self.graphs._append(array)

    def add_branch(self, branch: BranchArray) -> None:
        """Add a branch to the grid

        Args:
            branch (BranchArray): The branch to add
        """
        self._append(array=branch)
        self.graphs.add_branch_array(branch_array=branch)

        logging.debug(f"added branch {branch.id} from {branch.from_node} to {branch.to_node}")

    def delete_branch(self, branch: BranchArray) -> None:
        """Remove a branch from the grid

        Args:
            branch (BranchArray): The branch to remove
        """
        _add_branch_array(branch=branch, grid=self)
        self.graphs.delete_branch(branch=branch)
        logging.debug(
            f"""deleted branch {branch.id.item()} from {branch.from_node.item()} to {branch.to_node.item()}"""
        )

    def delete_branch3(self, branch: Branch3Array) -> None:
        """Remove a branch3 from the grid

        Args:
            branch (Branch3Array): The branch3 to remove
        """
        _add_branch_array(branch=branch, grid=self)
        self.graphs.delete_branch3(branch=branch)

    def add_node(self, node: NodeArray) -> None:
        """Add a new node to the grid

        Args:
            node (NodeArray): The node to add
        """
        self._append(array=node)
        self.graphs.add_node_array(node_array=node)
        logging.debug(f"added rail {node.id}")

    def delete_node(self, node: NodeArray) -> None:
        """Remove a node from the grid

        Args:
            node (NodeArray): The node to remove
        """
        self.node = self.node.exclude(id=node.id)
        self.sym_load = self.sym_load.exclude(node=node.id)
        self.source = self.source.exclude(node=node.id)

        for branch_array in self.branch_arrays:
            matching_branches = branch_array.filter(from_node=node.id, to_node=node.id, mode_="OR")
            for branch in matching_branches:
                self.delete_branch(branch)

        self.graphs.delete_node(node=node)
        logging.debug(f"deleted rail {node.id}")

    def make_active(self, branch: BranchArray) -> None:
        """Make a branch active

        Args:
            branch (BranchArray): The branch to make active
        """
        array_field = self.find_array_field(branch.__class__)
        array_attr = getattr(self, array_field.name)
        branch_mask = array_attr.id == branch.id
        array_attr.from_status[branch_mask] = 1
        array_attr.to_status[branch_mask] = 1
        setattr(self, array_field.name, array_attr)

        self.graphs.make_active(branch=branch)
        logging.debug(f"activated branch {branch.id}")

    def make_inactive(self, branch: BranchArray, at_to_side: bool = True) -> None:
        """Make a branch inactive. This is done by setting from or to status to 0.

        Args:
            branch (BranchArray): The branch to make inactive
            at_to_side (bool, optional): Whether to deactivate the to_status instead of the from_status.
            Defaults to True.
        """
        array_field = self.find_array_field(branch.__class__)
        array_attr = getattr(self, array_field.name)
        branch_mask = array_attr.id == branch.id
        status_side = "to_status" if at_to_side else "from_status"
        array_attr[status_side][branch_mask] = 0
        setattr(self, array_field.name, array_attr)

        self.graphs.make_inactive(branch=branch)
        logging.debug(f"deactivated branch {branch.id}")

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
        connected_nodes = self.graphs.active_graph.get_connected(node_id=node_id, inclusive=True)
        substation_nodes = self.node.filter(node_type=NodeType.SUBSTATION_NODE.value)

        for node in connected_nodes:
            if node in substation_nodes.id:
                return substation_nodes.get(node)
        raise RecordDoesNotExist(f"No {NodeType.SUBSTATION_NODE.name} connected to node {node_id}")

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
        substation_nodes = self.node.filter(node_type=NodeType.SUBSTATION_NODE.value)

        if node_id in substation_nodes.id:
            raise NotImplementedError("get_downstream_nodes is not implemented for substation nodes!")

        return self.graphs.active_graph.get_downstream_nodes(
            node_id=node_id, start_node_ids=list(substation_nodes.id), inclusive=inclusive
        )

    def cache(self, cache_dir: Path, cache_name: str, compress: bool = True):
        """Cache Grid to a folder

        Args:
            cache_dir (Path): The directory to save the cache to.
            cache_name (str): The name of the cache.
            compress (bool, optional): Whether to compress the cache. Defaults to True.
        """
        tmp_graphs = copy(self.graphs)
        self.graphs = None  # noqa
        cache_dir.mkdir(parents=True, exist_ok=True)

        pickle_path = cache_dir / f"{cache_name}.pickle"
        save_to_pickle(path=pickle_path, python_object=self)

        if compress:
            gzip_path = file2gzip(pickle_path)
            pickle_path.unlink()
            return gzip_path

        self.graphs = tmp_graphs
        return pickle_path

    @classmethod
    # pylint: disable=arguments-differ
    def from_cache(cls: Type[Self], cache_path: Path, load_graphs: bool = True) -> Self:
        """Read from cache and build .graphs from arrays

        Args:
            cache_path (Path): The path to the cache
            load_graphs (bool, optional): Whether to load the graphs. Defaults to True.

        Returns:
            Self: The grid loaded from cache
        """
        pickle_path = get_pickle_path(cache_path)

        grid = cls._from_pickle(pickle_path=pickle_path)
        if load_graphs:
            grid.graphs = GraphContainer.from_arrays(grid)
        return grid

    @classmethod
    def _from_pickle(cls, pickle_path: Path):
        grid = load_from_pickle(path=pickle_path)
        if not isinstance(grid, Grid):
            raise TypeError(f"{pickle_path.name} is not a valid {cls.__name__} cache.")
        return grid

    @classmethod
    def from_txt(cls, *args: str):
        """Build a grid from a list of strings

        See the documentation for the expected format of the txt_lines

        Args:
            *args (str): The lines of the grid

        Examples:
            >>> Grid.from_txt("1 2", "2 3", "3 4 transformer", "4 5", "S1 6")
            alternative: Grid.from_txt("1 2\n2 3\n3 4 transformer\n4 5\nS1 6")
        """
        return TextSource(grid_class=cls).load_from_txt(*args)

    @classmethod
    # pylint: disable=arguments-differ
    def from_txt_file(cls, txt_file_path: Path):
        """Load grid from txt file

        Args:
            txt_file_path (Path): The path to the txt file
        """
        with open(txt_file_path, "r", encoding="utf-8") as f:
            txt_lines = f.readlines()
        return TextSource(grid_class=cls).load_from_txt(*txt_lines)

    def set_feeder_ids(self):
        """Sets feeder and substation id properties in the grids arrays"""
        set_is_feeder(grid=self)
        set_feeder_ids(grid=self)

    @classmethod
    def from_extended(cls, extended: "Grid") -> "Grid":
        """Create a grid from an extended Grid object."""
        new_grid = cls.empty()

        # Add nodes first, so that branches can reference them
        new_grid.append(new_grid.node.__class__.from_extended(extended.node))

        for field in dataclasses.fields(cls):
            if field.name == "node":
                continue  # already added
            if isinstance(field.type, type) and issubclass(field.type, FancyArray):
                extended_array = getattr(extended, field.name)
                new_array = field.type.from_extended(extended_array)
                new_grid.append(new_array, check_max_id=False)

        return new_grid


def _add_branch_array(branch: BranchArray | Branch3Array, grid: Grid):
    """Add a branch array to the grid"""
    array_field = grid.find_array_field(branch.__class__)
    array_attr = getattr(grid, array_field.name)
    setattr(grid, array_field.name, array_attr.exclude(id=branch.id))

    grid.transformer_tap_regulator = grid.transformer_tap_regulator.exclude(regulated_object=branch.id)

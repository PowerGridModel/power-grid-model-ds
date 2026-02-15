# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dataclasses
from collections import defaultdict
from typing import TYPE_CHECKING, Iterator

import numpy as np
import numpy.typing as npt

from power_grid_model_ds._core import fancypy as fp
from power_grid_model_ds._core.model.arrays import BranchArray, ThreeWindingTransformerArray
from power_grid_model_ds._core.model.arrays.base.errors import RecordDoesNotExist
from power_grid_model_ds._core.model.enums.nodes import NodeType
from power_grid_model_ds._core.model.graphs.errors import MissingBranchError

if TYPE_CHECKING:
    from power_grid_model_ds._core.model.grids.base import Grid


def get_branches(grid: "Grid") -> BranchArray:
    """see Grid.get_branches()"""
    branch_dtype = BranchArray.get_dtype()
    branches = BranchArray()
    for array in grid.branch_arrays:
        new_branch = BranchArray(data=array.data[list(branch_dtype.names)])
        branches = fp.concatenate(branches, new_branch)
    return branches


def get_branch_arrays(grid: "Grid") -> list[BranchArray]:
    """see Grid.get_branch_arrays()"""
    branch_arrays = []
    for field in dataclasses.fields(grid):
        array = getattr(grid, field.name)
        if isinstance(array, BranchArray):
            branch_arrays.append(array)
    return branch_arrays


def get_typed_branches(grid: "Grid", branch_ids: list[int] | npt.NDArray[np.int32]) -> BranchArray:
    """see Grid.get_typed_branches()"""
    if not np.any(branch_ids):
        raise ValueError("No branch_ids provided.")
    for branch_array in grid.branch_arrays:
        array = branch_array.filter(branch_ids)
        if 0 < array.size != len(branch_ids):
            raise ValueError("Branches are not of the same type.")
        if array.size:
            return array
    raise RecordDoesNotExist(f"Branches {branch_ids} not found in grid.")


def get_nearest_substation_node(grid: "Grid", node_id: int):
    """See Grid.get_nearest_substation_node()"""
    connected_nodes = grid.graphs.active_graph.get_connected(node_id=node_id, inclusive=True)
    substation_nodes = grid.node.filter(node_type=NodeType.SUBSTATION_NODE.value)

    for node in connected_nodes:
        if node in substation_nodes.id:
            return substation_nodes.get(node)
    raise RecordDoesNotExist(f"No {NodeType.SUBSTATION_NODE.name} connected to node {node_id}")


def get_downstream_nodes(grid: "Grid", node_id: int, inclusive: bool = False):
    """See Grid.get_downstream_nodes()"""
    substation_nodes = grid.node.filter(node_type=NodeType.SUBSTATION_NODE.value)

    if node_id in substation_nodes.id:
        raise NotImplementedError("get_downstream_nodes is not implemented for substation nodes!")

    return grid.graphs.active_graph.get_downstream_nodes(
        node_id=node_id, start_node_ids=list(substation_nodes.id), inclusive=inclusive
    )


_THREE_WINDING_BRANCH_CONFIGS = (
    ("node_1", "node_2", "status_1", "status_2"),
    ("node_1", "node_3", "status_1", "status_3"),
    ("node_2", "node_3", "status_2", "status_3"),
)


def _lookup_three_winding_branch(grid: "Grid", node_a: int, node_b: int) -> ThreeWindingTransformerArray:
    """Return the first active transformer that connects the node pair or raise if none exist."""

    three_winding_array = grid.three_winding_transformer
    error_message = f"No active three-winding transformer connects nodes {node_a} -> {node_b}."
    if not three_winding_array.size:
        raise MissingBranchError(error_message)

    for node_col_a, node_col_b, status_col_a, status_col_b in _THREE_WINDING_BRANCH_CONFIGS:
        transformer = three_winding_array.filter(
            **{
                node_col_a: [node_a, node_b],
                node_col_b: [node_a, node_b],
                status_col_a: 1,
                status_col_b: 1,
            }  # type: ignore[arg-type]
        )
        if transformer.size:
            return transformer
    raise MissingBranchError(error_message)


def _active_branches_for_path(
    grid: "Grid", path_nodes: list[int]
) -> tuple[BranchArray, dict[tuple[int, int], list[int]]]:
    """Return active branch records and an index filtered to the requested path nodes."""

    active = grid.branches.filter(from_status=1, to_status=1).filter(
        from_node=path_nodes, to_node=path_nodes, mode_="AND"
    )
    if grid.three_winding_transformer.size:
        three_winding_active = (
            grid.three_winding_transformer.as_branches()
            .filter(from_status=1, to_status=1)
            .filter(from_node=path_nodes, to_node=path_nodes, mode_="AND")
        )
        if three_winding_active.size:
            active = fp.concatenate(active, three_winding_active)

    index: dict[tuple[int, int], list[int]] = defaultdict(list)
    for position, (source, target) in enumerate(zip(active.from_node, active.to_node)):
        index[(int(source), int(target))].append(position)

    return active, index


def iter_branches_in_shortest_path(
    grid: "Grid", from_node_id: int, to_node_id: int, typed: bool = False
) -> Iterator[BranchArray]:
    """See Grid.iter_branches_in_shortest_path()."""

    path, _ = grid.graphs.active_graph.get_shortest_path(from_node_id, to_node_id)
    active_branches, index = _active_branches_for_path(grid, path)

    for current_node, next_node in zip(path[:-1], path[1:]):
        positions = index.get((current_node, next_node))
        if not positions:
            raise MissingBranchError(
                f"No active branch connects nodes {current_node} -> {next_node} even though a path exists."
            )
        branch_records = active_branches[positions]
        if typed:
            branch_ids = branch_records.id.tolist()
            try:
                typed_branches = grid.get_typed_branches(branch_ids)
            except RecordDoesNotExist:
                typed_branches = _lookup_three_winding_branch(grid, current_node, next_node)
            yield typed_branches
        else:
            yield branch_records

# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dataclasses
from collections.abc import Iterator
from itertools import pairwise
from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from power_grid_model_ds._core import fancypy as fp
from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.arrays.base.errors import RecordDoesNotExist
from power_grid_model_ds._core.model.enums.nodes import NodeType
from power_grid_model_ds._core.model.graphs.errors import MissingBranchError
from power_grid_model_ds._core.utils.misc import find_diff_masks_with_equal_nan
from power_grid_model_ds.arrays import Branch3Array, BranchArray

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


def _get_branches(grid: "Grid", from_node: int, to_node: int) -> BranchArray:
    """Return active branch records and an index filtered to the requested path nodes."""

    active_branches = grid.branches.filter(from_status=1, to_status=1).filter(
        from_node=from_node, to_node=to_node, mode_="AND"
    )
    if grid.three_winding_transformer.size:
        three_winding_active = grid.three_winding_transformer.as_branches().filter(
            from_status=1, to_status=1, from_node=from_node, to_node=to_node, mode_="AND"
        )
        if three_winding_active.size:
            active_branches = fp.concatenate(active_branches, three_winding_active)

    return active_branches


def iter_branches_in_shortest_path(
    grid: "Grid", from_node_id: int, to_node_id: int
) -> Iterator[BranchArray | Branch3Array]:
    """See Grid.iter_branches_in_shortest_path()."""

    path, _ = grid.graphs.active_graph.get_shortest_path(from_node_id, to_node_id)

    for current_node, next_node in pairwise(path):
        branches = _get_branches(grid, current_node, next_node)
        if branches.size == 0:
            raise MissingBranchError(
                f"No active branch connects nodes {current_node} -> {next_node} even though a path exists."
            )
        branch_ids = branches.id.tolist()
        try:
            typed_branches = grid.get_typed_branches(branch_ids)
        except RecordDoesNotExist:
            typed_branches = grid.three_winding_transformer.filter(branch_ids)
        yield typed_branches


def find_differences_between_grids(
    grid1: "Grid", grid2: "Grid", print_diff: bool = False
) -> dict[str, dict[str, object]]:
    """See Grid.find_differences()"""
    if not isinstance(grid1, grid2.__class__) or not isinstance(grid2, grid1.__class__):
        raise TypeError("Both grids should be of the same class (to ensure they have the same attributes)")

    differences = {}
    for field in dataclasses.fields(grid1):
        attr1 = getattr(grid1, field.name)
        attr2 = getattr(grid2, field.name)

        if attr_diff := _compare_attr(attr1, attr2):
            differences[field.name] = attr_diff

    if print_diff:
        _print_differences(differences)
    return differences


def _compare_attr(attr1: object, attr2: object) -> dict[str, object]:
    if isinstance(attr1, FancyArray) and isinstance(attr2, FancyArray):
        mask1, mask2 = find_diff_masks_with_equal_nan(attr1.data, attr2.data)
        if mask1.any() or mask2.any():
            return {"grid1": attr1[mask1], "grid2": attr2[mask2]}
        return {}
    if attr1 != attr2:
        return {"grid1": attr1, "grid2": attr2}
    return {}


def _print_differences(differences: dict[str, dict[str, object]]) -> None:
    for attr, diff in differences.items():
        title = f"There are differences in 'grid.{attr}'"
        print(f"\n{title}")
        print("-" * len(title))

        if attr in ["_ids", "graphs"]:
            continue  # more info is not relevant for these attributes

        print(diff["grid1"])
        print("\nvs.\n")
        print(diff["grid2"])

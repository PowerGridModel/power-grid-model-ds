# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
"""Contains utility functions for PGM-DS"""

from typing import TYPE_CHECKING

from power_grid_model_ds._core.model.arrays.pgm_arrays import (
    AsymLineArray,
    BranchArray,
    GenericBranchArray,
    LineArray,
    LinkArray,
    SourceArray,
    TransformerArray,
)
from power_grid_model_ds._core.model.graphs.errors import GraphError

if TYPE_CHECKING:
    from .base import Grid


def reverse_branches(grid: "Grid", branches: BranchArray) -> None:
    """See Grid.reverse_branches()"""
    if not branches.size:
        return
    if not isinstance(branches, (LineArray, LinkArray, TransformerArray, GenericBranchArray, AsymLineArray)):
        try:
            branches = grid.get_typed_branches(branches.id)
        except ValueError:
            # If the branches are not of the same type, reverse them per type (though this is slower)
            for array in grid.branch_arrays:
                grid.reverse_branches(array.filter(branches.id))
            return

    from_nodes = branches.from_node
    from_states = branches.from_status
    to_nodes = branches.to_node
    to_states = branches.to_status

    array_field = grid.find_array_field(branches.__class__)
    array = getattr(grid, array_field.name)
    array.update_by_id(branches.id, from_node=to_nodes, to_node=from_nodes)
    array.update_by_id(
        branches.id, from_node=to_nodes, from_status=to_states, to_node=from_nodes, to_status=from_states
    )


def set_branch_orientations(grid: "Grid") -> BranchArray:
    """See grid.set_branch_orientations()."""
    reversed_branches = get_reversed_branches(grid)
    grid.reverse_branches(reversed_branches)
    return reversed_branches


def get_reversed_branches(grid: "Grid") -> BranchArray:
    """See grid.get_reversed_branches()."""
    reverse_branch_ids = []
    branches = grid.branches
    for source in grid.source:
        reverse_branch_ids += _get_reverted_branches_for_source(grid=grid, source=source, branches=branches)

    return grid.branches.filter(reverse_branch_ids)


def _get_reverted_branches_for_source(grid: "Grid", source: SourceArray, branches: BranchArray) -> list[int]:

    nodes_in_order = grid.graphs.active_graph.get_connected(source.node.item(), inclusive=True)

    other_source_nodes = grid.source.exclude(source.id).node.tolist()
    if set(nodes_in_order) & set(other_source_nodes):
        raise GraphError("Cannot set branch orientations if source is connected to other sources")

    connected_branches = branches.filter(
        from_status=1, to_status=1, from_node=nodes_in_order, to_node=nodes_in_order
    )
    reverted_branch_ids = []
    node_rank = {node: index for index, node in enumerate(nodes_in_order)}
    for branch in connected_branches:
        from_node = branch.from_node.item()
        to_node = branch.to_node.item()
        if node_rank[from_node] > node_rank[to_node]:
            reverted_branch_ids.append(branch.id.item())

    # also add for reversed open_branches
    reversed_open_branches = branches.filter(from_status=0, to_status=1, to_node=nodes_in_order).exclude(
        from_node=nodes_in_order
    )
    reverted_branch_ids += reversed_open_branches.id.tolist()
    return reverted_branch_ids

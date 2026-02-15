# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
"""Contains utility functions for PGM-DS"""

from power_grid_model_ds._core.model.arrays.pgm_arrays import SourceArray
from power_grid_model_ds._core.model.graphs.errors import GraphError
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel
from power_grid_model_ds._core.model.grids.base import Grid


def fix_branch_orientations(grid: Grid, dry_run: bool = False) -> list[int]:
    """
    Fix branch orientations in the grid so that all branches are oriented away from the sources.

    Orientation is determined by the distance of the branch's from_node and to_node to the source node.
    The node that is closer to the source is considered the "from_node".
    Note that this might not reflect the actual power flow direction in the grid.

    Other notes:
    - Sources should not be connected to other sources. If a source is connected to another source,
      a GraphError is raised.
    - Parallel edges (multiple edges between the same two nodes) and cycles are supported.

    Args:
        grid (Grid): The grid to fix branch orientations for.
        dry_run (bool): If True, do not actually modify the grid, just return the branch IDs that would be reverted
            (default: False).

    Returns:
        list[int]: A list of branch IDs that were reverted (or would be reverted in case of ``dry_run=True``).
    """
    reverse_branch_ids = []
    for source in grid.source:
        reverse_branch_ids += _get_reverted_branches_for_source(grid, source)

    if not dry_run:
        grid.reverse_branches(grid.branches.filter(id=reverse_branch_ids))
    return reverse_branch_ids


def _get_reverted_branches_for_source(grid: Grid, source: SourceArray) -> list[int]:

    nodes_in_order = grid.graphs.active_graph.get_connected(source.node.item(), inclusive=True)

    other_source_nodes = grid.source.exclude(source.id).node.tolist()
    if set(nodes_in_order) & set(other_source_nodes):
        raise GraphError("Cannot fix branch orientations if source is connected to other sources")

    connected_branches = grid.branches.filter(
        from_status=1, to_status=1, from_node=nodes_in_order, to_node=nodes_in_order
    )

    reverted_branch_ids = []
    for branch in connected_branches:
        from_node = branch.from_node.item()
        to_node = branch.to_node.item()
        from_index = nodes_in_order.index(from_node)
        to_index = nodes_in_order.index(to_node)
        if from_index > to_index:
            reverted_branch_ids.append(branch.id.item())
    return reverted_branch_ids

"""Contains utility functions for PGM-DS"""

from power_grid_model_ds._core.model.arrays.pgm_arrays import BranchArray, SourceArray
from power_grid_model_ds._core.model.grids.base import Grid


def fix_branch_orientations(grid: Grid) -> BranchArray:
    """ToDo"""
    cycles = grid.graphs.active_graph.find_fundamental_cycles()

    if any(cycles):
        # ToDo: support parallel lines.
        raise NotImplementedError("Cannot fix branch orientations on graph with cycles")
    # ToDo: check that source is not connected to other sources.

    reverted_branch_ids = []
    for source in grid.source:
        reverted_branch_ids += _get_reverted_branches_for_source(grid, source)

    _revert_branches(grid, reverted_branch_ids)
    return grid.branches.filter(reverted_branch_ids)


def _get_reverted_branches_for_source(grid: Grid, source: SourceArray) -> list[int]:

    nodes_in_order = grid.graphs.active_graph.get_connected(source.node.item(), inclusive=True)
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


def _revert_branches(grid: Grid, branch_ids: list[int]):
    for branch_id in branch_ids:
        branch = grid.get_typed_branches([branch_id])
        grid.delete_branch(branch)
        from_node = branch.from_node.item()
        branch.from_node = branch.to_node.item()
        branch.to_node = from_node
        grid.append(branch, check_max_id=False)

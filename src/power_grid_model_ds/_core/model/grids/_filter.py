# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import TYPE_CHECKING

from power_grid_model_ds._core.model.constants import EMPTY_ID
from power_grid_model_ds._core.model.grids._search import get_downstream_nodes as _get_downstream_nodes

if TYPE_CHECKING:
    from power_grid_model_ds._core.model.grids.base import Grid


def filter_grid(
    grid: "Grid",
    feeder_ids: list[int],
    *,
    include_adjacent_nodes: bool = False,
) -> "Grid":
    """Create a new Grid containing only the components belonging to the given feeders.

    All nodes and branches belonging to the specified feeder_ids are included, as well
    as the feeding substation node for each feeder. All branch types whose endpoints are
    both in the visible node set are included. All appliances (loads, generators, sources,
    shunts) whose connected node is visible are included. Three-winding transformers are
    included only when all three of their nodes are visible.

    Requires set_feeder_ids() to have been called on the grid first.

    Args:
        grid: The source Grid to filter.
        feeder_ids: IDs of feeder branches (feeder_branch_id values set by
            set_feeder_ids()). All nodes and branches belonging to these feeders are
            included, as well as the feeding substation node for each feeder.
        include_adjacent_nodes: When True, also include nodes one hop away from any
            visible node (via any branch or three-winding transformer).

    Returns:
        A new Grid containing the filtered subset, with graphs rebuilt.

    Example:
        >>> grid.set_feeder_ids()
        >>> subset = filter_grid(grid, feeder_ids=[201])
        >>> subset = filter_grid(grid, feeder_ids=[201, 204])
        >>> subset = filter_grid(grid, feeder_ids=[201], include_adjacent_nodes=True)
    """
    visible_nodes = _resolve_visible_nodes(grid, feeder_ids)
    if include_adjacent_nodes:
        visible_nodes = _expand_adjacent_nodes(grid, visible_nodes)
    return _build_grid_subset(grid, visible_nodes)


def filter_path(
    grid: "Grid",
    start_node_id: int,
    end_node_id: int,
    *,
    include_adjacent_nodes: bool = False,
) -> "Grid":
    """Create a new Grid containing only the components along the shortest path between two nodes.

    Uses the active graph (active branches only) to find the shortest path. All nodes along
    the path are included, as well as all branches connecting consecutive path nodes.

    Args:
        grid: The source Grid to filter.
        start_node_id: The starting node ID.
        end_node_id: The ending node ID.
        include_adjacent_nodes: When True, also include nodes one hop away from any
            visible node (via any branch or three-winding transformer).

    Returns:
        A new Grid containing the filtered subset, with graphs rebuilt.

    Raises:
        NoPathBetweenNodes: if no path exists between the two nodes in the active graph.

    Example:
        >>> subset = filter_path(grid, start_node_id=102, end_node_id=106)
        >>> subset = filter_path(grid, start_node_id=102, end_node_id=106, include_adjacent_nodes=True)
    """
    path_nodes, _ = grid.graphs.active_graph.get_shortest_path(start_node_id, end_node_id)
    visible_nodes = set(path_nodes)
    if include_adjacent_nodes:
        visible_nodes = _expand_adjacent_nodes(grid, visible_nodes)
    return _build_grid_subset(grid, visible_nodes)


def filter_nodes(
    grid: "Grid",
    node_ids: list[int],
    *,
    include_adjacent_nodes: bool = False,
) -> "Grid":
    """Create a new Grid containing only the specified nodes and their connecting components.

    All branches whose both endpoints are in the given node list are included. All
    appliances connected to any of the given nodes are included. Three-winding transformers
    are included only when all three of their nodes are in the list.

    Args:
        grid: The source Grid to filter.
        node_ids: List of node IDs to include.
        include_adjacent_nodes: When True, also include nodes one hop away from any
            visible node (via any branch or three-winding transformer).

    Returns:
        A new Grid containing the filtered subset, with graphs rebuilt.

    Example:
        >>> subset = filter_nodes(grid, node_ids=[102, 103])
        >>> subset = filter_nodes(grid, node_ids=[102, 103], include_adjacent_nodes=True)
    """
    visible_nodes = set(node_ids)
    if include_adjacent_nodes:
        visible_nodes = _expand_adjacent_nodes(grid, visible_nodes)
    return _build_grid_subset(grid, visible_nodes)


def filter_downstream(
    grid: "Grid",
    node_id: int,
    *,
    include_adjacent_nodes: bool = False,
) -> "Grid":
    """Create a new Grid containing only the nodes downstream of the given node.

    Uses the active graph and the grid's substation nodes to determine the downstream
    direction. The given node itself is always included.

    Args:
        grid: The source Grid to filter.
        node_id: The node ID from which to start the downstream traversal.
        include_adjacent_nodes: When True, also include nodes one hop away from any
            visible node (including upstream-adjacent nodes).

    Returns:
        A new Grid containing the filtered subset, with graphs rebuilt.

    Raises:
        NotImplementedError: if node_id is a substation node.

    Example:
        >>> subset = filter_downstream(grid, node_id=102)
        >>> subset = filter_downstream(grid, node_id=102, include_adjacent_nodes=True)
    """
    downstream = _get_downstream_nodes(grid, node_id=node_id, inclusive=True)
    visible_nodes = set(downstream)
    if include_adjacent_nodes:
        visible_nodes = _expand_adjacent_nodes(grid, visible_nodes)
    return _build_grid_subset(grid, visible_nodes)


def _resolve_visible_nodes(grid: "Grid", feeder_ids: list[int]) -> set[int]:
    feeder_nodes = grid.node.filter(feeder_branch_id=feeder_ids)
    visible: set[int] = set(feeder_nodes.id.tolist())
    substation_ids = {nid for nid in feeder_nodes.feeder_node_id.tolist() if nid != EMPTY_ID}
    return visible | substation_ids


def _expand_adjacent_nodes(grid: "Grid", visible_nodes: set[int]) -> set[int]:
    seed = list(visible_nodes)
    expanded = set(visible_nodes)

    branches = grid.branches
    expanded |= set(branches.filter(from_node=seed).to_node.tolist())
    expanded |= set(branches.filter(to_node=seed).from_node.tolist())

    twt = grid.three_winding_transformer
    for node_field in ("node_1", "node_2", "node_3"):
        matches = twt.filter(**{node_field: seed})  # type: ignore[arg-type]
        if matches.size:
            for other_field in ("node_1", "node_2", "node_3"):
                if other_field != node_field:
                    expanded |= set(getattr(matches, other_field).tolist())

    return expanded


def _build_grid_subset(grid: "Grid", visible_nodes: set[int]) -> "Grid":
    node_list = list(visible_nodes)
    result = type(grid).empty()

    result.append(grid.node.filter(id=node_list))

    for branch_array in grid.branch_arrays:
        subset = branch_array.filter(from_node=node_list, to_node=node_list, mode_="AND")
        if subset.size:
            result.append(subset)

    twt_subset = grid.three_winding_transformer.filter(
        node_1=node_list, node_2=node_list, node_3=node_list, mode_="AND"
    )
    if twt_subset.size:
        result.append(twt_subset)

    for appliance_array in (
        grid.sym_load,
        grid.sym_gen,
        grid.source,
        grid.asym_load,
        grid.asym_gen,
        grid.shunt,
    ):
        subset = appliance_array.filter(node=node_list)
        if subset.size:
            result.append(subset)

    return result

# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import TYPE_CHECKING

import numpy as np

from power_grid_model_ds._core.model.arrays.pgm_arrays import BranchArray
from power_grid_model_ds._core.model.enums.nodes import NodeType

if TYPE_CHECKING:
    from .base import Grid


def set_feeder_ids(grid: "Grid"):
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
    _reset_feeder_ids(grid)
    feeder_node_ids = grid.node.filter(node_type=NodeType.SUBSTATION_NODE)["id"]
    with grid.graphs.active_graph.tmp_remove_nodes(feeder_node_ids.tolist()):
        components = grid.graphs.active_graph.get_components()
    for component_node_ids in components:
        component_branches = _get_active_component_branches(grid, component_node_ids)

        feeder_branch = _get_feeder_branch(component_branches)

        if feeder_branch.size == 0:
            continue  # early exit

        feeder_node_id = _get_feeder_node_id(feeder_branch, feeder_node_ids)

        for array in grid.branch_arrays:
            array.update_by_id(
                component_branches.id,
                feeder_branch_id=feeder_branch.id.item(),
                feeder_node_id=feeder_node_id,
                allow_missing=True,
            )

        grid.node.update_by_id(
            component_node_ids,
            feeder_branch_id=feeder_branch.id.item(),
            feeder_node_id=feeder_node_id,
            allow_missing=True,
        )


def set_is_feeder(grid: "Grid") -> None:
    "Set the is_feeder property for all branches in the network."
    feeder_node_ids = grid.node.filter(node_type=NodeType.SUBSTATION_NODE).id
    array: BranchArray
    for array in [grid.link, grid.line, grid.transformer]:
        array.is_feeder = np.logical_xor(
            np.isin(array.from_node, feeder_node_ids), np.isin(array.to_node, feeder_node_ids)
        )


def _reset_feeder_ids(grid: "Grid"):
    # Resets all feeder ids to EMPTY_ID
    for array in grid.branch_arrays:
        array.set_empty("feeder_branch_id")
        array.set_empty("feeder_node_id")

    grid.node.set_empty("feeder_branch_id")
    grid.node.set_empty("feeder_node_id")


def _get_active_component_branches(grid: "Grid", component_node_ids: list[int]) -> BranchArray:
    # a component is a set of actively connected nodes (ids)
    # returns all active branches in the component

    branches = grid.branches
    branches_in_component = branches.filter(from_node=component_node_ids, to_node=component_node_ids, mode_="OR")
    active_branches = branches_in_component.filter(from_status=1, to_status=1)
    return active_branches


def _get_feeder_branch(component_branches: BranchArray) -> BranchArray:
    feeder_branches = component_branches.filter(is_feeder=True)

    if feeder_branches.size == 1:
        return feeder_branches

    if feeder_branches.size > 1:
        # Cannot point to multiple branches, so just pick the first one
        return feeder_branches[0]

    return BranchArray()


def _get_feeder_node_id(feeder_branch: BranchArray, feeder_node_ids: np.ndarray) -> int:
    # intersect to retrieve the feeder node id
    feeder_node_id = np.intersect1d(feeder_branch.node_ids, feeder_node_ids)
    return feeder_node_id.item()

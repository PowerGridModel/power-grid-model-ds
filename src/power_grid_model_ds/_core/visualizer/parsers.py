# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any, Literal

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds.arrays import BranchArray, NodeArray


def parse_node_array(nodes: NodeArray) -> list[dict[str, Any]]:
    """Parse the nodes."""
    parsed_nodes = []

    with_coords = "x" in nodes.columns and "y" in nodes.columns

    columns = nodes.columns
    for node in nodes:
        cyto_elements = {"data": _array_to_dict(node, columns)}
        cyto_elements["data"]["id"] = str(node.id.item())
        cyto_elements["data"]["group"] = "node"
        if with_coords:
            cyto_elements["position"] = {"x": node.x.item(), "y": -node.y.item()}  # invert y-axis for visualization
        parsed_nodes.append(cyto_elements)
    return parsed_nodes


def parse_branches(grid: Grid) -> list[dict[str, Any]]:
    """Parse the branches."""
    parsed_branches = []
    parsed_branches.extend(parse_branch_array(grid.line, "line"))
    parsed_branches.extend(parse_branch_array(grid.link, "link"))
    parsed_branches.extend(parse_branch_array(grid.transformer, "transformer"))
    return parsed_branches


def parse_branch_array(branches: BranchArray, group: Literal["line", "link", "transformer"]) -> list[dict[str, Any]]:
    """Parse the branch array."""
    parsed_branches = []
    columns = branches.columns
    for branch in branches:
        cyto_elements = {"data": _array_to_dict(branch, columns)}
        cyto_elements["data"].update(
            {
                "id": str(branch.id.item()),
                "source": str(branch.from_node.item()),
                "target": str(branch.to_node.item()),
                "group": group,
            }
        )
        parsed_branches.append(cyto_elements)
    return parsed_branches


def _array_to_dict(array_record: FancyArray, columns: list[str]) -> dict[str, Any]:
    """Stringify the record (required by Dash)."""
    return dict(zip(columns, array_record.tolist().pop()))

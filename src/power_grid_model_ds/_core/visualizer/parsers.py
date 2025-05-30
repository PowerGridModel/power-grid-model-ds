# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any, Literal

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds.arrays import Branch3Array, BranchArray, NodeArray


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
    parsed_branches.extend(parse_branch3_array(grid.three_winding_transformer, "transformer"))
    return parsed_branches


def parse_branch3_array(branches: Branch3Array, group: Literal["transformer"]) -> list[dict[str, Any]]:
    """Parse the three-winding transformer array."""
    parsed_branches = []
    columns = branches.columns
    for branch in branches:
        for branch_ in _branch3_to_branches(branch):
            cyto_elements = {"data": _array_to_dict(branch_, columns)}
            cyto_elements["data"].update(
                {
                    "id": str(branch.id.item()) + f"_{branch_.from_node.item()}_{branch_.to_node.item()}",
                    "source": str(branch_.from_node.item()),
                    "target": str(branch_.to_node.item()),
                    "group": group,
                }
            )
            parsed_branches.append(cyto_elements)
    return parsed_branches


def _branch3_to_branches(branch3: Branch3Array) -> BranchArray:
    node_1 = branch3.node_1.item()
    node_2 = branch3.node_2.item()
    node_3 = branch3.node_3.item()

    status_1 = branch3.status_1.item()
    status_2 = branch3.status_2.item()
    status_3 = branch3.status_3.item()

    branches = BranchArray.zeros(3)
    branches.from_node = [node_1, node_1, node_2]
    branches.to_node = [node_2, node_3, node_3]
    branches.from_status = [status_1, status_1, status_2]
    branches.to_status = [status_2, status_3, status_3]

    return branches


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

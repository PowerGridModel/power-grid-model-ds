# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Literal

from power_grid_model import ComponentType

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.parsing_utils import array_to_dict
from power_grid_model_ds._core.visualizer.styling_classification import (
    get_branch_classification,
    get_node_classification,
)
from power_grid_model_ds._core.visualizer.typing import VizToComponentElements
from power_grid_model_ds.arrays import Branch3Array, BranchArray, NodeArray


def parse_element_data(grid: Grid) -> VizToComponentElements:
    """
    Parse grid element data and organize by node ID as string.

    Args:
        grid (Grid): The power grid model.
    Returns:
        VizToComponentElements: A dict of elements for visualization
            A mapping from node or edge IDs used in visualization to their associated component data.
    """

    elements: VizToComponentElements = {}

    elements.update(parse_node_array(grid.node))

    # Parse branches
    elements.update(parse_branch_array(grid.asym_line, ComponentType.asym_line))
    elements.update(parse_branch_array(grid.line, ComponentType.line))
    elements.update(parse_branch_array(grid.generic_branch, ComponentType.generic_branch))
    elements.update(parse_branch_array(grid.link, ComponentType.link))
    elements.update(parse_branch_array(grid.transformer, ComponentType.transformer))

    # Parse branch3
    elements.update(parse_branch3_array(grid.three_winding_transformer, ComponentType.three_winding_transformer))
    return elements


def parse_node_array(nodes: NodeArray) -> VizToComponentElements:
    """Parse the nodes. Fills node data to viz_to_comp."""
    parsed_nodes: VizToComponentElements = {}

    with_coords = "x" in nodes.columns and "y" in nodes.columns

    for node in nodes:
        node_id_str = str(node.id.item())

        parsed_nodes[node_id_str] = {
            "data": {"id": node_id_str, "group": "node"},
            "classes": get_node_classification(node),
        }
        parsed_nodes[node_id_str]["data"].update(array_to_dict(node, nodes.columns))

        if with_coords:
            parsed_nodes[node_id_str]["position"] = {
                "x": node.x.item(),
                "y": -node.y.item(),
            }  # invert y-axis for visualization
    return parsed_nodes


def parse_branch3_array(
    branches: Branch3Array, group: Literal[ComponentType.three_winding_transformer]
) -> VizToComponentElements:
    """Parse the three-winding transformer array. Fills branch3 data to viz_to_comp."""
    parsed_branches: VizToComponentElements = {}
    for branch3 in branches:
        branch3_component_data = array_to_dict(branch3, branches.columns)  # Same for all three branches
        for count, branch in enumerate(branch3.as_branches()):
            branch_id_str = f"{branch3.id.item()}_{count}"
            parsed_branches[branch_id_str] = {
                "data": {
                    # IDs need to be unique, so we combine the branch ID with 0,1,2
                    "id": branch_id_str,
                    "source": str(branch.from_node.item()),
                    "target": str(branch.to_node.item()),
                    "group": group.value,
                },
                "classes": get_branch_classification(branch, group),
            }
            parsed_branches[branch_id_str]["data"].update(branch3_component_data)
    return parsed_branches


def parse_branch_array(
    branches: BranchArray,
    group: Literal[
        ComponentType.line,
        ComponentType.asym_line,
        ComponentType.generic_branch,
        ComponentType.link,
        ComponentType.transformer,
    ],
) -> VizToComponentElements:
    """Parse the branch array. Fills branch data to viz_to_comp."""
    parsed_branches: VizToComponentElements = {}
    for branch in branches:
        branch_id_str = str(branch.id.item())
        parsed_branches[branch_id_str] = {
            "data": {
                "id": branch_id_str,
                "source": str(branch.from_node.item()),
                "target": str(branch.to_node.item()),
                "group": group.value,
            },
            "classes": get_branch_classification(branch, group),
        }
        parsed_branches[branch_id_str]["data"].update(array_to_dict(branch, branches.columns))
    return parsed_branches

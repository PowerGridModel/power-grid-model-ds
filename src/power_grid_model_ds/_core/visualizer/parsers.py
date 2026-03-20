# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Literal

from power_grid_model import ComponentType, MeasuredTerminalType

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.parsing_utils import (
    append_component_list_parsed_elements,
    array_to_dict,
)
from power_grid_model_ds._core.visualizer.styling_classification import (
    StyleClass,
    get_appliance_edge_classification,
    get_branch_classification,
    get_node_classification,
)
from power_grid_model_ds._core.visualizer.typing import (
    ComponentTypeAppliance,
    ComponentTypeBranch,
    VizToComponentElements,
)
from power_grid_model_ds.arrays import (
    ApplianceArray,
    Branch3Array,
    BranchArray,
    NodeArray,
)

_NODE_BRANCH_TERMINAL_TYPE = [
    MeasuredTerminalType.branch_from,
    MeasuredTerminalType.branch_to,
    MeasuredTerminalType.node,
]
_APPLIANCE_TERMINAL_TYPE = [
    MeasuredTerminalType.load,
    MeasuredTerminalType.generator,
    MeasuredTerminalType.source,
    MeasuredTerminalType.shunt,
]
_BRANCH3_TERMINAL_TYPE = [
    MeasuredTerminalType.branch3_1,
    MeasuredTerminalType.branch3_2,
    MeasuredTerminalType.branch3_3,
]


def parse_element_data(grid: Grid) -> VizToComponentElements:
    """
    Parse grid element data and organize by node ID as string.

    Args:
        grid (Grid): The power grid model.
    Returns:
        VizToComponentElements: A dict of elements for visualization.
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

    # Parse appliances
    _parse_appliances(elements, grid.sym_load, ComponentType.sym_load)
    _parse_appliances(elements, grid.sym_gen, ComponentType.sym_gen)
    _parse_appliances(elements, grid.source, ComponentType.source)
    _parse_appliances(elements, grid.asym_load, ComponentType.asym_load)
    _parse_appliances(elements, grid.asym_gen, ComponentType.asym_gen)
    _parse_appliances(elements, grid.shunt, ComponentType.shunt)

    return elements


def parse_node_array(nodes: NodeArray) -> VizToComponentElements:
    """Parse the nodes. Fills node data to viz_to_comp."""
    parsed_nodes: VizToComponentElements = {}

    with_coords = "x" in nodes.columns and "y" in nodes.columns

    for node in nodes:
        node_id_str = str(node.id.item())

        parsed_nodes[node_id_str] = {
            "data": {"id": node_id_str, "group": "node", "associated_ids": {"node": [node.id.item()]}},
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
                    "associated_ids": {group.value: [branch3.id.item()]},
                },
                "classes": get_branch_classification(branch, group),
            }
            parsed_branches[branch_id_str]["data"].update(branch3_component_data)
    return parsed_branches


def parse_branch_array(branches: BranchArray, group: ComponentTypeBranch) -> VizToComponentElements:
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
                "associated_ids": {group.value: [branch.id.item()]},
            },
            "classes": get_branch_classification(branch, group),
        }
        parsed_branches[branch_id_str]["data"].update(array_to_dict(branch, branches.columns))
    return parsed_branches


def _parse_appliances(elements: VizToComponentElements, array: ApplianceArray, group: ComponentTypeAppliance) -> None:
    """Parse appliances and associate them with nodes."""
    for appliance in array:
        appliance_id_str = str(appliance.id.item())
        appliance_ghost_id_str = f"{appliance_id_str}_ghost_node"
        node_id_str = str(appliance.node.item())

        # Add appliance to node
        elements[appliance_ghost_id_str] = {
            "data": {
                "id": appliance_ghost_id_str,
                "group": f"{group.value}_ghost_node",
                "associated_ids": {group.value: [appliance.id.item()]},
            },
            "selectable": False,
            "classes": StyleClass.APPLIANCE_GHOST_NODE.value,
        }

        elements[appliance_id_str] = {
            "data": {
                "id": appliance_id_str,
                "source": node_id_str,
                "target": appliance_ghost_id_str,
                "group": group.value,
                "associated_ids": {group.value: [appliance.id.item()]},
            },
            "selectable": False,
            "classes": get_appliance_edge_classification(appliance, group),
        }

        append_component_list_parsed_elements(elements, appliance.id.item(), node_id_str, group.value)

# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any, Literal

from power_grid_model import ComponentType

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.typing import VizToComponentData
from power_grid_model_ds.arrays import Branch3Array, BranchArray, NodeArray


def parse_element_data(grid: Grid) -> tuple[list[dict[str, Any]], VizToComponentData]:
    """
    Parse grid element data and organize by node ID as string.

    Args:
        grid (Grid): The power grid model.
    Returns:
        tuple[list[dict[str, Any]], VizToComponentData]: A tuple containing
            a list of elements for visualization
            A mapping from node or edge IDs used in visualization to their associated component data.
    """
    viz_to_comp: VizToComponentData = {}

    elements = []
    elements += parse_node_array(grid.node, viz_to_comp)
    elements += parse_branches(grid, viz_to_comp)

    return elements, viz_to_comp


def parse_node_array(nodes: NodeArray, viz_to_comp: VizToComponentData) -> list[dict[str, Any]]:
    """Parse the nodes. Fills node data to viz_to_comp."""
    parsed_nodes = []

    with_coords = "x" in nodes.columns and "y" in nodes.columns

    for node in nodes:
        node_id_str = str(node.id.item())

        _ensure_component_list(viz_to_comp, node_id_str, ComponentType.node)
        viz_to_comp[node_id_str][ComponentType.node].append(_array_to_dict(node, nodes.columns))

        cyto_elements = {"data": {"id": node_id_str, "group": ComponentType.node.value}}
        if with_coords:
            cyto_elements["position"] = {"x": node.x.item(), "y": -node.y.item()}  # invert y-axis for visualization
        parsed_nodes.append(cyto_elements)
    return parsed_nodes


def parse_branches(grid: Grid, viz_to_comp: VizToComponentData) -> list[dict[str, Any]]:
    """Parse the branches. Fills branch data to viz_to_comp."""
    parsed_branches = []
    parsed_branches.extend(parse_branch_array(grid.line, ComponentType.line, viz_to_comp))
    parsed_branches.extend(parse_branch_array(grid.link, ComponentType.link, viz_to_comp))
    parsed_branches.extend(parse_branch_array(grid.transformer, ComponentType.transformer, viz_to_comp))

    parsed_branches.extend(
        parse_branch3_array(
            grid.three_winding_transformer,
            component_type=ComponentType.three_winding_transformer,
            group=ComponentType.transformer.value,
            viz_to_comp=viz_to_comp,
        )
    )
    return parsed_branches


def parse_branch3_array(
    branches: Branch3Array,
    component_type: Literal[ComponentType.three_winding_transformer],
    group: Literal["transformer"],
    viz_to_comp: VizToComponentData,
) -> list[dict[str, Any]]:
    """Parse the three-winding transformer array. Fills branch3 data to viz_to_comp."""
    parsed_branches = []
    for branch3 in branches:
        branch3_component_data = _array_to_dict(branch3, branches.columns)  # Same for all three branches
        for count, branch1 in enumerate(branch3.as_branches()):
            branch3_id_str = f"{str(branch3.id.item())}_{count}"

            _ensure_component_list(viz_to_comp, branch3_id_str, component_type)
            viz_to_comp[branch3_id_str][component_type].append(branch3_component_data)

            cyto_elements = {
                "data": {
                    # IDs need to be unique, so we combine the branch ID with the from and to nodes
                    "id": branch3_id_str,
                    "source": str(branch1.from_node.item()),
                    "target": str(branch1.to_node.item()),
                    "group": group,
                }
            }
            parsed_branches.append(cyto_elements)
    return parsed_branches


def parse_branch_array(
    branches: BranchArray,
    group: Literal[ComponentType.line, ComponentType.link, ComponentType.transformer],
    viz_to_comp: VizToComponentData,
) -> list[dict[str, Any]]:
    """Parse the branch array. Fills branch data to viz_to_comp."""
    parsed_branches = []
    for branch in branches:
        _ensure_component_list(viz_to_comp, str(branch.id.item()), group)
        viz_to_comp[str(branch.id.item())][group].append(_array_to_dict(branch, branches.columns))

        cyto_elements = {
            "data": {
                "id": str(branch.id.item()),
                "source": str(branch.from_node.item()),
                "target": str(branch.to_node.item()),
                "group": group.value,
            }
        }
        parsed_branches.append(cyto_elements)
    return parsed_branches


def _array_to_dict(array_record: FancyArray, columns: list[str]) -> dict[str, Any]:
    """Stringify the record (required by Dash)."""
    return dict(zip(columns, array_record.tolist().pop()))


def _ensure_component_list(viz_to_comp: VizToComponentData, node_id: str, component_type: ComponentType) -> None:
    """Ensure that the component list exists for a given node and component type."""
    if node_id not in viz_to_comp:
        viz_to_comp[node_id] = {}
    if component_type not in viz_to_comp[node_id]:
        viz_to_comp[node_id][component_type] = []

# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any, Literal

from power_grid_model import MeasuredTerminalType

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.typing import ListArrayData, VizToComponentData
from power_grid_model_ds.arrays import Branch3Array, BranchArray, NodeArray

_NODE_OR_EDGE_POWER_SENSORS = [
    MeasuredTerminalType.branch_from,
    MeasuredTerminalType.branch_to,
    MeasuredTerminalType.node,
]
_BRANCH3_POWER_SENSORS = [
    MeasuredTerminalType.branch3_1,
    MeasuredTerminalType.branch3_2,
    MeasuredTerminalType.branch3_3,
]
_APPLIANCE_POWER_SENSORS = [
    MeasuredTerminalType.load,
    MeasuredTerminalType.generator,
    MeasuredTerminalType.source,
]


def parse_node_array(nodes: NodeArray, viz_to_comp: VizToComponentData) -> list[dict[str, Any]]:
    """Parse the nodes. Fills node data to viz_to_comp."""
    parsed_nodes = []

    with_coords = "x" in nodes.columns and "y" in nodes.columns

    for node in nodes:
        node_id_str = str(node.id.item())

        _ensure_component_list(viz_to_comp, node_id_str, "node")
        viz_to_comp[node_id_str]["node"].append(_array_to_dict(node, nodes.columns))

        cyto_elements = {"data": {"id": node_id_str, "group": "node"}}
        if with_coords:
            cyto_elements["position"] = {"x": node.x.item(), "y": -node.y.item()}  # invert y-axis for visualization
        parsed_nodes.append(cyto_elements)
    return parsed_nodes


def parse_branches(grid: Grid, viz_to_comp: VizToComponentData) -> list[dict[str, Any]]:
    """Parse the branches. Fills branch data to viz_to_comp."""
    parsed_branches = []
    parsed_branches.extend(parse_branch_array(grid.line, "line", viz_to_comp))
    parsed_branches.extend(parse_branch_array(grid.link, "link", viz_to_comp))
    parsed_branches.extend(parse_branch_array(grid.transformer, "transformer", viz_to_comp))
    
    # TODO (nitbharambe) Remove ambiguity of group
    parsed_branches.extend(
        parse_branch3_array(
            grid.three_winding_transformer,
            component_type="three_winding_transformer",
            group="transformer",
            viz_to_comp=viz_to_comp,
        )
    )
    return parsed_branches


def parse_branch3_array(
    branches: Branch3Array,
    component_type: Literal["three_winding_transformer"],
    group: Literal["transformer"],
    viz_to_comp: VizToComponentData,
) -> list[dict[str, Any]]:
    """Parse the three-winding transformer array. Fills branch3 data to viz_to_comp."""
    parsed_branches = []
    for branch3 in branches:
        branch3_component_data = _array_to_dict(branches[0], branches.columns)  # Same for all three branches
        for count, branch1 in enumerate(branch3.as_branches()):
            branch3_id_str = str(branch3.id.item())

            _ensure_component_list(viz_to_comp, branch3_id_str, component_type)
            viz_to_comp[branch3_id_str][component_type].append(branch3_component_data)

            cyto_elements = {
                "data": {
                    # IDs need to be unique, so we combine the branch ID with the from and to nodes
                    "id": f"{branch3_id_str}_{count}",
                    "source": str(branch1.from_node.item()),
                    "target": str(branch1.to_node.item()),
                    "group": group,
                }
            }
            parsed_branches.append(cyto_elements)
    return parsed_branches


def parse_branch_array(
    branches: BranchArray, group: Literal["line", "link", "transformer"], viz_to_comp: VizToComponentData
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
                "group": group,
            }
        }
        parsed_branches.append(cyto_elements)
    return parsed_branches


def _array_to_dict(array_record: FancyArray, columns: list[str]) -> dict[str, Any]:
    """Stringify the record (required by Dash)."""
    return dict(zip(columns, array_record.tolist().pop()))


def _ensure_component_list(viz_to_comp: VizToComponentData, node_id: str, component_type: str) -> None:
    """Ensure that the component list exists for a given node and component type."""
    if node_id not in viz_to_comp:
        viz_to_comp[node_id] = {}
    if component_type not in viz_to_comp[node_id]:
        viz_to_comp[node_id][component_type] = []


def _parse_power_sensors(grid: Grid, viz_to_comp: VizToComponentData) -> dict[str, ListArrayData]:
    """Parse power sensors and return appliance-to-power-sensor mapping."""
    indirect_connections: dict[str, ListArrayData] = {}

    for power_sensor in grid.sym_power_sensor:
        measured_object_id = str(power_sensor.measured_object.item())
        measured_terminal_type = power_sensor.measured_terminal_type.item()
        sensor_dict = _array_to_dict(power_sensor, grid.sym_power_sensor.columns)

        if measured_terminal_type in _NODE_OR_EDGE_POWER_SENSORS:
            _ensure_component_list(viz_to_comp, measured_object_id, "sym_power_sensor")
            viz_to_comp[measured_object_id]["sym_power_sensor"].append(sensor_dict)
        elif measured_terminal_type in _BRANCH3_POWER_SENSORS:
            for count in range(3):
                branch1_id = f"{measured_object_id}_{count}"
                _ensure_component_list(viz_to_comp, branch1_id, "sym_power_sensor")
                viz_to_comp[branch1_id]["sym_power_sensor"].append(sensor_dict)
        elif measured_terminal_type in _APPLIANCE_POWER_SENSORS:
            # Collect sensors related to appliances
            if measured_object_id not in indirect_connections:
                indirect_connections[measured_object_id] = []
            indirect_connections[measured_object_id].append(sensor_dict)

    return indirect_connections


def _parse_appliances(
    grid: Grid, viz_to_comp: VizToComponentData, indirect_connections: dict[str, ListArrayData]
) -> None:
    """Parse appliances and associate them with nodes."""
    for appliance_type in ["sym_load", "sym_gen", "source"]:
        appliance_array = getattr(grid, appliance_type)

        for appliance in appliance_array:
            node_id_str = str(appliance.node.item())

            # Add appliance to node
            _ensure_component_list(viz_to_comp, node_id_str, appliance_type)
            viz_to_comp[node_id_str][appliance_type].append(_array_to_dict(appliance, appliance_array.columns))

            # Add associated power sensors if any
            appliance_id = str(appliance.id.item())
            if appliance_id in indirect_connections:
                _ensure_component_list(viz_to_comp, node_id_str, "sym_power_sensor")
                viz_to_comp[node_id_str]["sym_power_sensor"].extend(indirect_connections[appliance_id])


def _parse_voltage_sensors(grid: Grid, viz_to_comp: VizToComponentData) -> None:
    """Parse voltage sensors and associate them with nodes."""
    for voltage_sensor in grid.sym_voltage_sensor:
        node_id_str = str(voltage_sensor.measured_object.item())
        _ensure_component_list(viz_to_comp, node_id_str, "sym_voltage_sensor")
        viz_to_comp[node_id_str]["sym_voltage_sensor"].append(
            _array_to_dict(voltage_sensor, grid.sym_voltage_sensor.columns)
        )


def _parse_transformer_tap_regulators(grid: Grid, viz_to_comp: VizToComponentData) -> None:
    """Parse transformer tap regulators and associate them with transformers."""
    for tap_regulator in grid.transformer_tap_regulator:
        regulated_object_str = str(tap_regulator.regulated_object.item())
        _ensure_component_list(viz_to_comp, regulated_object_str, "transformer_tap_regulator")
        viz_to_comp[regulated_object_str]["transformer_tap_regulator"].append(
            _array_to_dict(tap_regulator, grid.transformer_tap_regulator.columns)
        )


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

    indirect_connections = _parse_power_sensors(grid, viz_to_comp)

    _parse_appliances(grid, viz_to_comp, indirect_connections)
    _parse_voltage_sensors(grid, viz_to_comp)
    _parse_transformer_tap_regulators(grid, viz_to_comp)

    return elements, viz_to_comp
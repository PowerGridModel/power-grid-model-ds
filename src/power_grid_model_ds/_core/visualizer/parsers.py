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


def parse_node_array(nodes: NodeArray) -> ListArrayData:
    """Parse the nodes."""
    parsed_nodes = []

    with_coords = "x" in nodes.columns and "y" in nodes.columns

    for node in nodes:
        cyto_elements = {"data": {"id": str(node.id.item()), "group": "node"}}
        if with_coords:
            cyto_elements["position"] = {"x": node.x.item(), "y": -node.y.item()}  # invert y-axis for visualization
        parsed_nodes.append(cyto_elements)
    return parsed_nodes


def parse_branches(grid: Grid) -> ListArrayData:
    """Parse the branches."""
    parsed_branches = []
    parsed_branches.extend(parse_branch_array(grid.line, "line"))
    parsed_branches.extend(parse_branch_array(grid.link, "link"))
    parsed_branches.extend(parse_branch_array(grid.transformer, "transformer"))
    parsed_branches.extend(parse_branch3_array(grid.three_winding_transformer, "transformer"))
    return parsed_branches


def parse_branch3_array(branches: Branch3Array, group: Literal["transformer"]) -> ListArrayData:
    """Parse the three-winding transformer array."""
    parsed_branches = []
    for branch3 in branches:
        for count, branch1 in enumerate(branch3.as_branches()):
            cyto_elements = {
                "data": {
                    # IDs need to be unique, so we combine the branch ID with the from and to nodes
                    "id": f"{branch3.id.item()}_{count}",
                    "source": str(branch1.from_node.item()),
                    "target": str(branch1.to_node.item()),
                    "group": group,
                }
            }
            parsed_branches.append(cyto_elements)
    return parsed_branches


def parse_branch_array(branches: BranchArray, group: Literal["line", "link", "transformer"]) -> ListArrayData:
    """Parse the branch array."""
    parsed_branches = []
    for branch in branches:
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


def _parse_component_data(grid: Grid, component_type: str, viz_to_comp: VizToComponentData) -> None:
    """Parse node data and populate viz_to_comp mapping."""
    columns = getattr(grid, component_type).columns
    for component in getattr(grid, component_type):
        component_id_str = str(component.id.item())
        _ensure_component_list(viz_to_comp, component_id_str, component_type)
        viz_to_comp[component_id_str][component_type].append(_array_to_dict(component, columns))


def _parse_branch3_data(grid: Grid, component_type: str, viz_to_comp: VizToComponentData) -> None:
    """Parse three-winding transformer data and populate viz_to_comp mapping."""
    columns = getattr(grid, component_type).columns
    for branch3 in getattr(grid, component_type):
        for count in range(3):
            branch1_id_str = f"{branch3.id.item()}_{count}"
            _ensure_component_list(viz_to_comp, branch1_id_str, component_type)
            viz_to_comp[branch1_id_str][component_type].append(_array_to_dict(branch3, columns))


def _parse_transformer_tap_regulators(grid: Grid, viz_to_comp: VizToComponentData) -> None:
    """Parse transformer tap regulators and associate them with transformers."""
    for tap_regulator in grid.transformer_tap_regulator:
        regulated_object_str = str(tap_regulator.regulated_object.item())
        _ensure_component_list(viz_to_comp, regulated_object_str, "transformer_tap_regulator")
        viz_to_comp[regulated_object_str]["transformer_tap_regulator"].append(
            _array_to_dict(tap_regulator, grid.transformer_tap_regulator.columns)
        )


def parse_element_data(grid: Grid) -> VizToComponentData:
    """
    Parse grid element data and organize by node ID as string.

    Args:
        grid (Grid): The power grid model.
    Returns:
        VizToComponentData: A mapping from node or edge IDs to their associated component data.
    """
    viz_to_comp: VizToComponentData = {}

    _parse_component_data(grid, "node", viz_to_comp)
    _parse_component_data(grid, "line", viz_to_comp)
    _parse_component_data(grid, "link", viz_to_comp)
    _parse_component_data(grid, "transformer", viz_to_comp)
    _parse_branch3_data(grid, "three_winding_transformer", viz_to_comp)

    indirect_connections = _parse_power_sensors(grid, viz_to_comp)

    _parse_appliances(grid, viz_to_comp, indirect_connections)
    _parse_voltage_sensors(grid, viz_to_comp)
    _parse_transformer_tap_regulators(grid, viz_to_comp)

    return viz_to_comp

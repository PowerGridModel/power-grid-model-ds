# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any, Literal

from power_grid_model import MeasuredTerminalType

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.arrays.pgm_arrays import (
    AsymVoltageSensorArray,
    Branch3Array,
    BranchArray,
    NodeArray,
    SourceArray,
    SymGenArray,
    SymLoadArray,
    SymPowerSensorArray,
    SymVoltageSensorArray,
    TransformerTapRegulatorArray,
)
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.typing import VizToComponentData, VizToComponentElements

_NODE_EDGE_APPLIANCE_POWER_SENSORS = [
    MeasuredTerminalType.branch_from,
    MeasuredTerminalType.branch_to,
    MeasuredTerminalType.node,
    MeasuredTerminalType.load,
    MeasuredTerminalType.generator,
    MeasuredTerminalType.source,
]
_BRANCH3_POWER_SENSORS = [
    MeasuredTerminalType.branch3_1,
    MeasuredTerminalType.branch3_2,
    MeasuredTerminalType.branch3_3,
]


def parse_element_data(grid: Grid) -> tuple[list[dict[str, Any]], VizToComponentElements]:
    """
    Parse grid element data and organize by node ID as string.

    Args:
        grid (Grid): The power grid model.
    Returns:
        tuple[list[dict[str, Any]], VizToComponentDataNew]: A tuple containing
            a list of elements for visualization
            A mapping from node or edge IDs used in visualization to their associated component data.
    """

    elements = {}
    elements.update(parse_node_array(grid.node))

    elements.update(parse_branch_array(grid.line, "line"))
    elements.update(parse_branch_array(grid.link, "link"))
    elements.update(parse_branch_array(grid.transformer, "transformer"))

    elements.update(parse_branch3_array(grid.three_winding_transformer, group="three_winding_transformer"))

    elements.update(_parse_appliances(grid.sym_load, "sym_load"))
    elements.update(_parse_appliances(grid.source, "source"))
    elements.update(_parse_appliances(grid.sym_gen, "sym_gen"))

    # These are not visualized directly, but their data is linked to nodes/edges of elements
    viz_to_comp: VizToComponentData = {}
    viz_to_comp.update(_parse_power_sensors(grid.sym_power_sensor, "sym_power_sensor"))
    viz_to_comp.update(_parse_voltage_sensors(grid.sym_voltage_sensor, "sym_voltage_sensor"))
    viz_to_comp.update(_parse_voltage_sensors(grid.asym_voltage_sensor, "asym_voltage_sensor"))
    viz_to_comp.update(_parse_transformer_tap_regulators(grid.transformer_tap_regulator, elements))

    viz_elements = list(elements.values())

    return viz_elements, viz_to_comp


def parse_node_array(nodes: NodeArray) -> VizToComponentElements:
    """Parse the nodes. Fills node data to viz_to_comp."""
    parsed_nodes = {}

    with_coords = "x" in nodes.columns and "y" in nodes.columns

    for node in nodes:
        node_id_str = str(node.id.item())

        parsed_nodes[node_id_str] = {"data": {"id": node_id_str, "group": "node"}}
        parsed_nodes[node_id_str]["data"].update(_array_to_dict(node, nodes.columns))

        if with_coords:
            parsed_nodes[node_id_str]["position"] = {
                "x": node.x.item(),
                "y": -node.y.item(),
            }  # invert y-axis for visualization
    return parsed_nodes


def parse_branch3_array(branches: Branch3Array, group: Literal["three_winding_transformer"]) -> VizToComponentElements:
    """Parse the three-winding transformer array. Fills branch3 data to viz_to_comp."""
    parsed_branches = {}
    for branch3 in branches:
        branch3_component_data = _array_to_dict(branch3, branches.columns)  # Same for all three branches
        for count, branch in enumerate(branch3.as_branches()):
            branch_id_str = f"{branch3.id.item()}_{count}"
            parsed_branches[branch_id_str] = {
                "data": {
                    # IDs need to be unique, so we combine the branch ID with 0,1,2
                    "id": branch_id_str,
                    "source": str(branch.from_node.item()),
                    "target": str(branch.to_node.item()),
                    "group": group,
                }
            }
            parsed_branches[branch_id_str]["data"].update(branch3_component_data)
    return parsed_branches


def parse_branch_array(branches: BranchArray, group: Literal["line", "link", "transformer"]) -> VizToComponentElements:
    """Parse the branch array. Fills branch data to viz_to_comp."""
    parsed_branches = {}
    for branch in branches:
        branch_id_str = str(branch.id.item())
        parsed_branches[branch_id_str] = {
            "data": {
                "id": branch_id_str,
                "source": str(branch.from_node.item()),
                "target": str(branch.to_node.item()),
                "group": group,
            }
        }
        parsed_branches[branch_id_str]["data"].update(_array_to_dict(branch, branches.columns))
    return parsed_branches


def _parse_appliances(
    appliances: SymLoadArray | SymGenArray | SourceArray, group: Literal["sym_load", "sym_gen", "source"]
) -> VizToComponentElements:
    """Parse appliances and associate them with nodes."""
    parsed_appliances: VizToComponentElements = {}
    for appliance in appliances:
        appliance_id_str = str(appliance.id.item())
        appliance_ghost_id_str = f"{appliance_id_str}_ghost_node"

        # Add appliance to node
        parsed_appliances[appliance_ghost_id_str] = {
            "data": {
                "id": appliance_ghost_id_str,
                "label": appliance_id_str,
                "group": f"{group}_ghost_node",
            },
            "selectable": False,
        }

        parsed_appliances[appliance_id_str] = {
            "data": {
                "id": appliance_id_str,
                "source": f"{str(appliance.node.item())}",
                "target": appliance_ghost_id_str,
                "group": group,
                "status": appliance.status.item(),
            },
        }

        parsed_appliances[appliance_id_str]["data"].update(_array_to_dict(appliance, appliances.columns))
        parsed_appliances[appliance_ghost_id_str]["data"].update(_array_to_dict(appliance, appliances.columns))
    return parsed_appliances


def _parse_power_sensors(power_sensors: SymPowerSensorArray, group) -> VizToComponentData:
    """Parse power sensors and return appliance-to-power-sensor mapping."""
    viz_to_comp: VizToComponentData = {}

    power_sensor_array = power_sensors
    for power_sensor in power_sensor_array:
        measured_object_id = str(power_sensor.measured_object.item())
        measured_terminal_type = power_sensor.measured_terminal_type.item()
        sensor_dict = _array_to_dict(power_sensor, power_sensor_array.columns)

        if measured_terminal_type in _NODE_EDGE_APPLIANCE_POWER_SENSORS:
            _ensure_component_list(viz_to_comp, measured_object_id, group)
            viz_to_comp[measured_object_id][group].append(sensor_dict)
        elif measured_terminal_type in _BRANCH3_POWER_SENSORS:
            for count in range(3):
                branch1_id = f"{measured_object_id}_{count}"
                _ensure_component_list(viz_to_comp, branch1_id, group)
                viz_to_comp[branch1_id][group].append(sensor_dict)
        else:
            raise ValueError(f"Unknown measured_terminal_type: {measured_terminal_type}")

    return viz_to_comp


def _parse_voltage_sensors(
    voltage_sensors: SymVoltageSensorArray | AsymVoltageSensorArray,
    sensor_type: Literal["sym_voltage_sensor", "asym_voltage_sensor"],
) -> VizToComponentData:
    """Parse voltage sensors and associate them with nodes."""
    viz_to_comp: VizToComponentData = {}
    for voltage_sensor in voltage_sensors:
        node_id_str = str(voltage_sensor.measured_object.item())
        sym_voltage_sensor_data = _array_to_dict(voltage_sensor, voltage_sensors.columns)
        _ensure_component_list(viz_to_comp, node_id_str, sensor_type)
        viz_to_comp[node_id_str][sensor_type].append(sym_voltage_sensor_data)
    return viz_to_comp


def _parse_transformer_tap_regulators(
    transformer_tap_regulators: TransformerTapRegulatorArray, elements: VizToComponentElements
) -> VizToComponentData:
    """Parse transformer tap regulators and associate them with transformers."""
    viz_to_comp: VizToComponentData = {}
    for tap_regulator in transformer_tap_regulators:
        regulated_object_str = str(tap_regulator.regulated_object.item())
        tap_regulator_data = _array_to_dict(tap_regulator, transformer_tap_regulators.columns)
        if regulated_object_str in elements:
            _ensure_component_list(viz_to_comp, regulated_object_str, "transformer_tap_regulator")
            viz_to_comp[regulated_object_str]["transformer_tap_regulator"].append(tap_regulator_data)
        else:
            for count in range(3):
                branch3_id_str = f"{regulated_object_str}_{count}"
                if branch3_id_str in elements:
                    _ensure_component_list(viz_to_comp, branch3_id_str, "transformer_tap_regulator")
                    viz_to_comp[branch3_id_str]["transformer_tap_regulator"].append(tap_regulator_data)
    return viz_to_comp


def _array_to_dict(array_record: FancyArray, columns: list[str]) -> dict[str, Any]:
    """Stringify the record (required by Dash)."""
    return {
        ("pgm_id" if column == "id" else column): value for column, value in zip(columns, array_record.tolist().pop())
    }


def _ensure_component_list(viz_to_comp: VizToComponentData, node_id: str, component_type: str) -> None:
    """Ensure that the component list exists for a given node and component type."""
    if node_id not in viz_to_comp:
        viz_to_comp[node_id] = {}
    if component_type not in viz_to_comp[node_id]:
        viz_to_comp[node_id][component_type] = []

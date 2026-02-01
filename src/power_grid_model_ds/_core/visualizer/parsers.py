# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Literal

from power_grid_model import ComponentType, MeasuredTerminalType

from power_grid_model_ds._core.model.arrays.pgm_arrays import (
    AsymCurrentSensorArray,
    AsymPowerSensorArray,
    AsymVoltageSensorArray,
    Branch3Array,
    BranchArray,
    NodeArray,
    SourceArray,
    SymCurrentSensorArray,
    SymGenArray,
    SymLoadArray,
    SymPowerSensorArray,
    SymVoltageSensorArray,
    TransformerTapRegulatorArray,
)
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.parsing_utils import (
    append_component_list,
    array_to_dict,
    map_appliance_to_nodes,
    merge_viz_to_comp,
)
from power_grid_model_ds._core.visualizer.styling_classification import (
    StyleClass,
    get_appliance_edge_classification,
    get_branch_classification,
    get_node_classification,
)
from power_grid_model_ds._core.visualizer.typing import VizToComponentData, VizToComponentElements

_NODE_BRANCH_TERMINAL_TYPE = [
    MeasuredTerminalType.branch_from,
    MeasuredTerminalType.branch_to,
    MeasuredTerminalType.node,
]
_APPLIANCE_TERMINAL_TYPE = [
    MeasuredTerminalType.load,
    MeasuredTerminalType.generator,
    MeasuredTerminalType.source,
]
_BRANCH3_TERMINAL_TYPE = [
    MeasuredTerminalType.branch3_1,
    MeasuredTerminalType.branch3_2,
    MeasuredTerminalType.branch3_3,
]


def parse_element_data(grid: Grid) -> tuple[VizToComponentElements, VizToComponentData]:
    """
    Parse grid element data and organize by node ID as string.

    Args:
        grid (Grid): The power grid model.
    Returns:
        tuple[VizToComponentElements, VizToComponentElements]: A tuple containing
            a dict of elements for visualization
            A mapping from node or edge IDs used in visualization to their associated component data.
    """

    elements: VizToComponentElements = {}
    viz_to_comp: VizToComponentData = {}

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
    for appliance_name in (ComponentType.sym_load, ComponentType.sym_gen, ComponentType.source):
        parsed, viz_to_comp_appliance = _parse_appliances(
            getattr(grid, appliance_name),
            appliance_name,
        )
        elements.update(parsed)
        merge_viz_to_comp(viz_to_comp, viz_to_comp_appliance)

    appliance_to_node = map_appliance_to_nodes(grid)

    # Parse sensors
    merge_viz_to_comp(
        viz_to_comp, _parse_flow_sensors(grid.sym_power_sensor, ComponentType.sym_power_sensor, appliance_to_node)
    )
    merge_viz_to_comp(
        viz_to_comp, _parse_flow_sensors(grid.asym_power_sensor, ComponentType.asym_power_sensor, appliance_to_node)
    )
    merge_viz_to_comp(
        viz_to_comp, _parse_flow_sensors(grid.sym_current_sensor, ComponentType.sym_current_sensor, appliance_to_node)
    )
    merge_viz_to_comp(
        viz_to_comp, _parse_flow_sensors(grid.asym_current_sensor, ComponentType.asym_current_sensor, appliance_to_node)
    )
    merge_viz_to_comp(viz_to_comp, _parse_voltage_sensors(grid.sym_voltage_sensor, ComponentType.sym_voltage_sensor))
    merge_viz_to_comp(viz_to_comp, _parse_voltage_sensors(grid.asym_voltage_sensor, ComponentType.asym_voltage_sensor))

    # Parse regulators
    merge_viz_to_comp(viz_to_comp, _parse_transformer_tap_regulators(grid.transformer_tap_regulator, elements))

    return elements, viz_to_comp


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


def _parse_appliances(
    appliances: SymLoadArray | SymGenArray | SourceArray,
    group: Literal[ComponentType.sym_load, ComponentType.sym_gen, ComponentType.source],
) -> tuple[VizToComponentElements, VizToComponentData]:
    """Parse appliances and associate them with nodes."""
    parsed_appliances: VizToComponentElements = {}
    viz_to_comp_appliance: VizToComponentData = {}

    for appliance in appliances:
        appliance_id_str = str(appliance.id.item())
        appliance_ghost_id_str = f"{appliance_id_str}_ghost_node"
        node_id_str = str(appliance.node.item())

        # Add appliance to node
        parsed_appliances[appliance_ghost_id_str] = {
            "data": {
                "id": appliance_ghost_id_str,
                "group": f"{group.value}_ghost_node",
            },
            "selectable": False,
            "classes": StyleClass.APPLIANCE_GHOST_NODE.value,
        }

        parsed_appliances[appliance_id_str] = {
            "data": {
                "id": appliance_id_str,
                "source": node_id_str,
                "target": appliance_ghost_id_str,
                "group": group.value,
                "status": appliance.status.item(),
            },
            "classes": get_appliance_edge_classification(appliance, group),
        }
        parsed_appliances[appliance_id_str]["data"].update(array_to_dict(appliance, appliances.columns))
        append_component_list(viz_to_comp_appliance, array_to_dict(appliance, appliances.columns), node_id_str, group)
    return parsed_appliances, viz_to_comp_appliance


def _parse_flow_sensors(
    sensors: SymPowerSensorArray | SymCurrentSensorArray | AsymPowerSensorArray | AsymCurrentSensorArray,
    group: Literal[
        ComponentType.sym_power_sensor,
        ComponentType.sym_current_sensor,
        ComponentType.asym_power_sensor,
        ComponentType.asym_current_sensor,
    ],
    appliance_to_node: dict[str, str],
) -> VizToComponentData:
    """Parse power sensors and return appliance-to-power-sensor mapping."""
    viz_to_comp: VizToComponentData = {}
    for power_sensor in sensors:
        measured_object_id_str = str(power_sensor.measured_object.item())
        measured_terminal_type = power_sensor.measured_terminal_type.item()
        sensor_dict = array_to_dict(power_sensor, sensors.columns)

        if measured_terminal_type in _NODE_BRANCH_TERMINAL_TYPE:
            append_component_list(viz_to_comp, sensor_dict, measured_object_id_str, group)
        elif measured_terminal_type in _BRANCH3_TERMINAL_TYPE:
            for count in range(3):
                branch1_id = f"{measured_object_id_str}_{count}"
                append_component_list(viz_to_comp, sensor_dict, branch1_id, group)
        elif measured_terminal_type in _APPLIANCE_TERMINAL_TYPE:
            append_component_list(viz_to_comp, sensor_dict, measured_object_id_str, group)
            # Map appliance to both appliance and its node as both can be unvisualized
            append_component_list(viz_to_comp, sensor_dict, appliance_to_node[measured_object_id_str], group)
        else:
            raise ValueError(f"Unknown measured_terminal_type: {measured_terminal_type}")

    return viz_to_comp


def _parse_voltage_sensors(
    voltage_sensors: SymVoltageSensorArray | AsymVoltageSensorArray,
    sensor_type: Literal[ComponentType.sym_voltage_sensor, ComponentType.asym_voltage_sensor],
) -> VizToComponentData:
    """Parse voltage sensors and associate them with nodes."""
    viz_to_comp: VizToComponentData = {}
    for voltage_sensor in voltage_sensors:
        node_id_str = str(voltage_sensor.measured_object.item())
        sym_voltage_sensor_data = array_to_dict(voltage_sensor, voltage_sensors.columns)
        append_component_list(viz_to_comp, sym_voltage_sensor_data, node_id_str, sensor_type)
    return viz_to_comp


def _parse_transformer_tap_regulators(
    transformer_tap_regulators: TransformerTapRegulatorArray, elements: VizToComponentElements
) -> VizToComponentData:
    """Parse transformer tap regulators and associate them with transformers."""
    viz_to_comp: VizToComponentData = {}
    for tap_regulator in transformer_tap_regulators:
        regulated_object_str = str(tap_regulator.regulated_object.item())
        tap_regulator_data = array_to_dict(tap_regulator, transformer_tap_regulators.columns)
        if regulated_object_str in elements:
            append_component_list(
                viz_to_comp, tap_regulator_data, regulated_object_str, ComponentType.transformer_tap_regulator
            )
        else:
            for count in range(3):
                branch3_id_str = f"{regulated_object_str}_{count}"
                if branch3_id_str in elements:
                    append_component_list(
                        viz_to_comp, tap_regulator_data, branch3_id_str, ComponentType.transformer_tap_regulator
                    )
    return viz_to_comp

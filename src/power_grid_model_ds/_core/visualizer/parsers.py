# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Literal

from power_grid_model import ComponentType, MeasuredTerminalType

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.parsing_utils import (
    append_component_list_parsed_elements,
    map_appliance_to_nodes,
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
    ComponentTypeFlowSensor,
    VizToComponentElements,
)
from power_grid_model_ds.arrays import (
    ApplianceArray,
    AsymCurrentSensorArray,
    AsymPowerSensorArray,
    AsymVoltageSensorArray,
    Branch3Array,
    BranchArray,
    FaultArray,
    NodeArray,
    SymCurrentSensorArray,
    SymPowerSensorArray,
    SymVoltageSensorArray,
    TransformerTapRegulatorArray,
    VoltageRegulatorArray,
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

    # Parse sensors
    appliance_to_node = map_appliance_to_nodes(grid)
    _parse_flow_sensors(elements, grid.sym_power_sensor, ComponentType.sym_power_sensor, appliance_to_node)
    _parse_flow_sensors(elements, grid.asym_power_sensor, ComponentType.asym_power_sensor, appliance_to_node)
    _parse_flow_sensors(elements, grid.sym_current_sensor, ComponentType.sym_current_sensor, appliance_to_node)
    _parse_flow_sensors(elements, grid.asym_current_sensor, ComponentType.asym_current_sensor, appliance_to_node)
    _parse_voltage_sensors(elements, grid.sym_voltage_sensor, ComponentType.sym_voltage_sensor)
    _parse_voltage_sensors(elements, grid.asym_voltage_sensor, ComponentType.asym_voltage_sensor)
    _parse_voltage_regulators(elements, grid.voltage_regulator)
    _parse_faults(elements, grid.fault)

    # Parse regulators
    _parse_transformer_tap_regulators(elements, grid.transformer_tap_regulator)

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
    return parsed_branches


def _parse_appliances(elements: VizToComponentElements, array: ApplianceArray, group: ComponentTypeAppliance) -> None:
    """Parse appliances and associate them with nodes."""
    with_coords = any("position" in element for element in elements.values())

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

        if with_coords:
            elements[appliance_ghost_id_str]["style"] = {"z-index": -1}

        elements[appliance_id_str] = {
            "data": {
                "id": appliance_id_str,
                "source": node_id_str,
                "target": appliance_ghost_id_str,
                "group": group.value,
                "associated_ids": {group.value: [appliance.id.item()]},
            },
            "classes": get_appliance_edge_classification(appliance, group),
        }

        if with_coords:
            elements[appliance_ghost_id_str]["position"] = {
                "x": elements[node_id_str]["position"]["x"],
                "y": elements[node_id_str]["position"]["y"],
            }  # invert y-axis for visualization

        append_component_list_parsed_elements(elements, appliance.id.item(), node_id_str, group.value)


def _parse_flow_sensors(
    elements: VizToComponentElements,
    array: SymPowerSensorArray | SymCurrentSensorArray | AsymPowerSensorArray | AsymCurrentSensorArray,
    group: ComponentTypeFlowSensor,
    appliance_to_node: dict[str, str],
):
    """Parse power sensors and return appliance-to-power-sensor mapping."""
    for power_sensor in array:
        measured_object_id_str = str(power_sensor.measured_object.item())
        measured_terminal_type = power_sensor.measured_terminal_type.item()

        if measured_terminal_type in _NODE_BRANCH_TERMINAL_TYPE:
            mapping_id_strs = [measured_object_id_str]
        elif measured_terminal_type in _BRANCH3_TERMINAL_TYPE:
            mapping_id_strs = [f"{measured_object_id_str}_{count}" for count in range(3)]
        elif measured_terminal_type in _APPLIANCE_TERMINAL_TYPE:
            mapping_id_strs = [measured_object_id_str]
            # Map appliance to both appliance and its node as both can be unvisualized
            if measured_object_id_str in appliance_to_node:
                mapping_id_strs.append(appliance_to_node[measured_object_id_str])
        else:
            raise ValueError(f"Unknown measured_terminal_type: {measured_terminal_type}")

        for id_str in mapping_id_strs:
            append_component_list_parsed_elements(elements, power_sensor.id.item(), id_str, group.value)


def _parse_voltage_sensors(
    elements: VizToComponentElements,
    array: SymVoltageSensorArray | AsymVoltageSensorArray,
    group: Literal[ComponentType.sym_voltage_sensor, ComponentType.asym_voltage_sensor],
):
    """Parse voltage sensors and associate them with nodes."""
    for voltage_sensor in array:
        node_id_str = str(voltage_sensor.measured_object.item())
        append_component_list_parsed_elements(elements, voltage_sensor.id.item(), node_id_str, group.value)


def _parse_transformer_tap_regulators(elements: VizToComponentElements, array: TransformerTapRegulatorArray):
    """Parse transformer tap regulators and associate them with transformers."""
    for tap_regulator in array:
        regulated_object_str = str(tap_regulator.regulated_object.item())
        if regulated_object_str in elements:
            mapping_id_strs = [regulated_object_str]
        else:
            mapping_id_strs = [
                f"{regulated_object_str}_{count}" for count in range(3) if f"{regulated_object_str}_{count}" in elements
            ]

        for id_str in mapping_id_strs:
            append_component_list_parsed_elements(
                elements, tap_regulator.id.item(), id_str, ComponentType.transformer_tap_regulator.value
            )


def _parse_voltage_regulators(elements: VizToComponentElements, array: VoltageRegulatorArray):
    """Parse voltage regulators and associate them with nodes."""
    for voltage_regulator in array:
        regulated_object_str = str(voltage_regulator.regulated_object.item())
        append_component_list_parsed_elements(
            elements, voltage_regulator.id.item(), regulated_object_str, ComponentType.voltage_regulator.value
        )


def _parse_faults(elements: VizToComponentElements, array: FaultArray):
    """Parse faults and associate them with nodes."""
    for fault in array:
        fault_object_str = str(fault.fault_object.item())
        append_component_list_parsed_elements(elements, fault.id.item(), fault_object_str, ComponentType.fault.value)

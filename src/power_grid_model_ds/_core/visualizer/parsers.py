# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any, Literal

from power_grid_model import ComponentType, MeasuredTerminalType

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

_NODE_BRANCH_POWER_SENSORS = [
    MeasuredTerminalType.branch_from,
    MeasuredTerminalType.branch_to,
    MeasuredTerminalType.node,
]
_APPLIANCE_POWER_SENSORS = [
    MeasuredTerminalType.load,
    MeasuredTerminalType.generator,
    MeasuredTerminalType.source,
]
_BRANCH3_POWER_SENSORS = [
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
    # These are not visualized directly, but their data is linked to nodes/edges of elements
    viz_to_comp: VizToComponentData = {}

    elements.update(parse_node_array(grid.node))

    elements.update(parse_branch_array(grid.line, ComponentType.line))
    elements.update(parse_branch_array(grid.generic_branch, ComponentType.generic_branch))
    elements.update(parse_branch_array(grid.link, ComponentType.link))
    elements.update(parse_branch_array(grid.transformer, ComponentType.transformer))

    elements.update(parse_branch3_array(grid.three_winding_transformer, ComponentType.three_winding_transformer))

    for appliance_name in [ComponentType.sym_load, ComponentType.sym_gen, ComponentType.source]:
        parsed, viz_to_comp_appliance = _parse_appliances(
            getattr(grid, appliance_name),
            appliance_name,  # type: ignore[arg-type]
        )
        elements.update(parsed)
        _merge_viz_to_comp(viz_to_comp, viz_to_comp_appliance)

    appliance_to_node = map_appliance_to_nodes(grid)

    _merge_viz_to_comp(
        viz_to_comp, _parse_power_sensors(grid.sym_power_sensor, ComponentType.sym_power_sensor, appliance_to_node)
    )
    _merge_viz_to_comp(viz_to_comp, _parse_voltage_sensors(grid.sym_voltage_sensor, ComponentType.sym_voltage_sensor))
    _merge_viz_to_comp(viz_to_comp, _parse_voltage_sensors(grid.asym_voltage_sensor, ComponentType.asym_voltage_sensor))
    _merge_viz_to_comp(viz_to_comp, _parse_transformer_tap_regulators(grid.transformer_tap_regulator, elements))

    return elements, viz_to_comp


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


def parse_branch3_array(
    branches: Branch3Array, group: Literal[ComponentType.three_winding_transformer]
) -> VizToComponentElements:
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
                    "group": group.value,
                }
            }
            parsed_branches[branch_id_str]["data"].update(branch3_component_data)
    return parsed_branches


def parse_branch_array(
    branches: BranchArray,
    group: Literal[ComponentType.line, ComponentType.generic_branch, ComponentType.link, ComponentType.transformer],
) -> VizToComponentElements:
    """Parse the branch array. Fills branch data to viz_to_comp."""
    parsed_branches = {}
    for branch in branches:
        branch_id_str = str(branch.id.item())
        parsed_branches[branch_id_str] = {
            "data": {
                "id": branch_id_str,
                "source": str(branch.from_node.item()),
                "target": str(branch.to_node.item()),
                "group": group.value,
            }
        }
        parsed_branches[branch_id_str]["data"].update(_array_to_dict(branch, branches.columns))
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
                "label": appliance_id_str,
                "group": f"{group.value}_ghost_node",
            },
            "selectable": False,
        }

        parsed_appliances[appliance_id_str] = {
            "data": {
                "id": appliance_id_str,
                "source": node_id_str,
                "target": appliance_ghost_id_str,
                "group": group.value,
                "status": appliance.status.item(),
            },
        }

        parsed_appliances[appliance_id_str]["data"].update(_array_to_dict(appliance, appliances.columns))
        _append_component_list(viz_to_comp_appliance, _array_to_dict(appliance, appliances.columns), node_id_str, group)
    return parsed_appliances, viz_to_comp_appliance


def _parse_power_sensors(
    power_sensors: SymPowerSensorArray,
    group: Literal[ComponentType.sym_power_sensor],
    appliance_to_node: dict[str, str],
) -> VizToComponentData:
    """Parse power sensors and return appliance-to-power-sensor mapping."""
    viz_to_comp: VizToComponentData = {}
    for power_sensor in power_sensors:
        measured_object_id_str = str(power_sensor.measured_object.item())
        measured_terminal_type = power_sensor.measured_terminal_type.item()
        sensor_dict = _array_to_dict(power_sensor, power_sensors.columns)

        if measured_terminal_type in _NODE_BRANCH_POWER_SENSORS:
            _append_component_list(viz_to_comp, sensor_dict, measured_object_id_str, group)
        elif measured_terminal_type in _APPLIANCE_POWER_SENSORS:
            _append_component_list(viz_to_comp, sensor_dict, measured_object_id_str, group)
            _append_component_list(viz_to_comp, sensor_dict, appliance_to_node[measured_object_id_str], group)
        elif measured_terminal_type in _BRANCH3_POWER_SENSORS:
            for count in range(3):
                branch1_id = f"{measured_object_id_str}_{count}"
                _append_component_list(viz_to_comp, sensor_dict, branch1_id, group)
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
        sym_voltage_sensor_data = _array_to_dict(voltage_sensor, voltage_sensors.columns)
        _append_component_list(viz_to_comp, sym_voltage_sensor_data, node_id_str, sensor_type)
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
            _append_component_list(
                viz_to_comp, tap_regulator_data, regulated_object_str, ComponentType.transformer_tap_regulator
            )
        else:
            for count in range(3):
                branch3_id_str = f"{regulated_object_str}_{count}"
                if branch3_id_str in elements:
                    _append_component_list(
                        viz_to_comp, tap_regulator_data, branch3_id_str, ComponentType.transformer_tap_regulator
                    )
    return viz_to_comp


def _array_to_dict(array_record: FancyArray, columns: list[str]) -> dict[str, Any]:
    """Stringify the record (required by Dash)."""
    return {
        ("pgm_id" if column == "id" else column): value for column, value in zip(columns, array_record.tolist().pop())
    }


def _append_component_list(
    viz_to_comp: VizToComponentData, to_append: dict[str, Any], id_str: str, component_type: ComponentType
) -> None:
    """Append a component to the VizToComponentData structure."""
    if id_str not in viz_to_comp:
        viz_to_comp[id_str] = {}
    if component_type not in viz_to_comp[id_str]:
        viz_to_comp[id_str][component_type] = []
    viz_to_comp[id_str][component_type].append(to_append)


def _merge_viz_to_comp(viz_to_comp: VizToComponentData, to_merge: VizToComponentData) -> VizToComponentData:
    """Merge two nested dictionaries of VizToComponentData type."""
    for id_str, component_data in to_merge.items():
        if id_str not in viz_to_comp:
            viz_to_comp[id_str] = component_data
        else:
            for comp_type in component_data:
                if comp_type not in viz_to_comp[id_str]:
                    viz_to_comp[id_str][comp_type] = component_data[comp_type]
                else:
                    viz_to_comp[id_str][comp_type].extend(component_data[comp_type])
    return viz_to_comp


def map_appliance_to_nodes(grid: Grid) -> dict[str, str]:
    """Map appliance IDs to their associated node IDs."""
    appliance_to_node: dict[str, str] = {}
    for appliance_name in [ComponentType.sym_load, ComponentType.sym_gen, ComponentType.source]:
        appliance_array = getattr(grid, appliance_name)
        appliance_to_node.update(dict(zip(map(str, appliance_array.id), map(str, appliance_array.node))))
    return appliance_to_node

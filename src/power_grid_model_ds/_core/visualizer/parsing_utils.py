# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from power_grid_model import ComponentType

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.typing import VizToComponentData, VizToComponentElements


def append_component_list_parsed_elements(
    elements: VizToComponentElements, to_append: int, connected_to_id_str: str, group: str
) -> None:
    """Append a component to the VizToComponentData structure."""
    if not (
        connected_to_id_str in elements
        and "data" in elements[connected_to_id_str]
        and "associated_ids" in elements[connected_to_id_str]["data"]
    ):
        raise ValueError(f"Node ID {connected_to_id_str} or its data not found while parsing")
    elements[connected_to_id_str]["data"]["associated_ids"][group].append(to_append)


def append_component_list(
    viz_to_comp: VizToComponentData, to_append: int, id_str: str, component_type: ComponentType
) -> None:
    """Append a component to the VizToComponentData structure."""
    if id_str not in viz_to_comp:
        viz_to_comp[id_str] = {}
    if component_type not in viz_to_comp[id_str]:
        viz_to_comp[id_str][component_type] = []
    viz_to_comp[id_str][component_type].append(to_append)


def merge_viz_to_comp(viz_to_comp: VizToComponentData, to_merge: VizToComponentData) -> VizToComponentData:
    """Merge two nested dictionaries of VizToComponentData type."""
    for id_str, component_data in to_merge.items():
        if id_str not in viz_to_comp:
            viz_to_comp[id_str] = component_data
            continue
        for comp_type in component_data:
            if comp_type not in viz_to_comp[id_str]:
                viz_to_comp[id_str][comp_type] = component_data[comp_type]
                continue
            viz_to_comp[id_str][comp_type].extend(component_data[comp_type])
    return viz_to_comp


def map_appliance_to_nodes(grid: Grid) -> dict[str, str]:
    """Map appliance IDs to their associated node IDs."""
    appliance_to_node: dict[str, str] = {}
    for appliance_name in [
        ComponentType.sym_load,
        ComponentType.sym_gen,
        ComponentType.source,
        ComponentType.asym_load,
        ComponentType.asym_gen,
        ComponentType.shunt,
    ]:
        appliance_array = getattr(grid, appliance_name)
        appliance_to_node.update(dict(zip(map(str, appliance_array.id), map(str, appliance_array.node))))
    return appliance_to_node


def viz_id_to_pgm_id(id_str: str) -> int:
    """Convert a viz element ID string to a PGM ID integer."""
    for suffix in ["_0", "_1", "_2"]:
        id_str = id_str.replace(suffix, "")
    return int(id_str)


def pgm_id_to_viz_ids(pgm_id: int, component_type: ComponentType) -> list[str]:
    """Convert a PGM ID integer to a viz element ID string."""
    if component_type == ComponentType.three_winding_transformer:
        suffixes = ["_0", "_1", "_2"]
    # TODO Remove applliances if not used
    elif component_type in [
        ComponentType.sym_load,
        ComponentType.sym_gen,
        ComponentType.source,
        ComponentType.asym_load,
        ComponentType.asym_gen,
        ComponentType.shunt,
    ]:
        suffixes = ["", "_ghost_node"]
    else:
        suffixes = [""]
    return [f"{pgm_id}{suffix}" for suffix in suffixes]

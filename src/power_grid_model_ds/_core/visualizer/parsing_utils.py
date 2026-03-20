# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from typing import Any

from power_grid_model import ComponentType

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.typing import VizToComponentElements

PGM_ID_KEY = "pgm_id"

_SHOW_APPLIANCES_GROUPS = [
    "sym_load",
    "sym_load_ghost_node",
    "sym_gen",
    "sym_gen_ghost_node",
    "asym_load",
    "asym_load_ghost_node",
    "asym_gen",
    "asym_gen_ghost_node",
    "shunt",
    "shunt_ghost_node",
]


def array_to_dict(array_record: FancyArray, columns: list[str]) -> dict[str, Any]:
    """
    Stringify the record (required by Dash).
    Also, rename the "id" column to "pgm_id" to avoid conflicts with Dash's internal use of "id".
    """
    return {
        (PGM_ID_KEY if column == "id" else column): value for column, value in zip(columns, array_record.tolist().pop())
    }


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
    if group not in elements[connected_to_id_str]["data"]["associated_ids"]:
        elements[connected_to_id_str]["data"]["associated_ids"][group] = []
    elements[connected_to_id_str]["data"]["associated_ids"][group].append(to_append)


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


def filter_out_appliances(elements_iterable):
    """Filter out appliance elements from the VizToComponentElements structure."""
    return [element for element in elements_iterable if element["data"]["group"] not in _SHOW_APPLIANCES_GROUPS]

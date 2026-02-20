# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any

from power_grid_model import ComponentType

STYLESHEET = list[dict[str, Any]]
ListArrayData = list[dict[str, Any]]

VizToComponentElements = dict[str, Any | dict[str, Any]]

"""
Mapping from visualization element ID to component type to list of array data.
Purpose is to link unvisualized elements data to visualized elements id they are connected to.

For example:
    {
        "node_id_1": {
            "sym_voltage_sensor": [ sensor id, ...],
            ...
        },
        "edge_id_1": {
            "ComponentType.sym_power_sensor": [ sensor id, ...],
            "ComponentType.sym_current_sensor": [ sensor id, ...],
            ...
        },
        "branch3_id_0": {
            "ComponentType.transformer_tap_regulator": [ regulator id, ...],
            ...
        },
        "branch3_id_1": {
            "ComponentType.transformer_tap_regulator": [ regulator id, ...],
            ...
        },
        {
            "source_id_str": {
                "ComponentType.sym_power_sensor": [ sensor id, ...],
        }
        ...
    }
"""
VizToComponentData = dict[str, dict[ComponentType, ListArrayData]]

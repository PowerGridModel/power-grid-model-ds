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
Purpose is to link unvisualized elements data to visualized elements id.

For example:
    {
        "node_id_1": {
            "node": [ {"id": 0, "u_rated": 100}, {...} ],
            "sym_voltage_sensor": [ {..sensor data..}, {...}],
            ...
        },
        "edge_id_1": {
            "ComponentType.line": [ {..line data..}, {...} ],
            "ComponentType.sym_power_sensor": [ {..sensor data..}, {...}],
            ...
        },
        "branch3_id_0": {
            "ComponentType.three_winding_transformer": [ {..three_winding_transformer data..}, {...} ],
            ...
        },
        "branch3_id_1": {
            "ComponentType.three_winding_transformer": [ {..same three_winding_transformer data..}, {...} ],
            ...
        },
        {
            "source_id_str": {
                "ComponentType.sym_power_sensor": [ {..sensor data..}, {...}],
        }
        ...
    }
"""
VizToComponentData = dict[str, dict[ComponentType, ListArrayData]]

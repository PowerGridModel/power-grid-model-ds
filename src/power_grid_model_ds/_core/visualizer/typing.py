# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any

from power_grid_model import ComponentType

STYLESHEET = list[dict[str, Any]]
ListArrayData = list[dict[str, Any]]

"""
Mapping from visualization element ID to component type to list of array data.

For example:
    {
        "node_id_1": {
            "node": [ {"id": 0, "u_rated": 100}, {...} ],
            "source": [ {..source data..}, {...}],
            ...
        },
        "edge_id_1": {
            "line": [ {..line data..}, {...} ],
            "sym_power_sensor": [ {..sensor data..}, {...}],
            ...
        },
        "branch3_id_0": {
            "three_winding_transformer": [ {..three_winding_transformer data..}, {...} ],
            ...
        },
        "branch3_id_1": {
            "three_winding_transformer": [ {..same three_winding_transformer data..}, {...} ],
            ...
        },
        ...
    }
"""
VizToComponentData = dict[str, dict[ComponentType, ListArrayData]]

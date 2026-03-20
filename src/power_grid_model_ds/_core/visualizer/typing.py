# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any, Literal

from power_grid_model import ComponentType

STYLESHEET = list[dict[str, Any]]


# after removing extra data from cytoscape elements and using only VizToComponentElementsValue
VizToComponentElements = dict[str, Any | dict[str, Any]]


ComponentTypeFlowSensor = Literal[
    ComponentType.sym_power_sensor,
    ComponentType.sym_current_sensor,
    ComponentType.asym_power_sensor,
    ComponentType.asym_current_sensor,
]


ComponentTypeBranch = Literal[
    ComponentType.line,
    ComponentType.asym_line,
    ComponentType.generic_branch,
    ComponentType.link,
    ComponentType.transformer,
]


ComponentTypeAppliance = Literal[
    ComponentType.asym_gen,
    ComponentType.asym_load,
    ComponentType.sym_load,
    ComponentType.sym_gen,
    ComponentType.source,
    ComponentType.shunt,
]

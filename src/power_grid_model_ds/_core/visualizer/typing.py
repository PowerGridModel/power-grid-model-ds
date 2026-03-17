# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any, Literal, NotRequired, Required, TypedDict

from power_grid_model import ComponentType

STYLESHEET = list[dict[str, Any]]


class _VizToComponentElementsValueData(TypedDict):
    """Sub dictionary for data within VizToComponentElementsValue"""

    id: Required[str]
    source: NotRequired[str]
    target: NotRequired[str]
    group: Required[str]
    associated_ids: Required[dict[str, list[int]]]  # e.g. {"sym_load": [1, 2], "sym_gen": [3]}


class VizToComponentElementsValue(TypedDict):
    """Element data for mapping visualization elements to component types and IDs
    This is what is needed for cytoscape elements."""

    data: _VizToComponentElementsValueData
    classes: str
    position: NotRequired[dict[Literal["x", "y"], float]]
    selectable: NotRequired[bool]


VizToComponentElements = dict[str, VizToComponentElementsValue]


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

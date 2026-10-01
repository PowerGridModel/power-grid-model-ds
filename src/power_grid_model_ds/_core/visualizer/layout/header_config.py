# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
from enum import Enum

import dash_bootstrap_components as dbc
from dash import dcc, html

NODE_SCALE_HTML = [
    html.I(className="fas fa-circle pgm-control-icon pgm-node-color"),
    dbc.Input(
        id="node-scale-input",
        type="number",
        value=1,
        min=0.1,
        step=0.1,
        className="pgm-scale-input",
    ),
    html.Span(className="pgm-scale-spacer"),
]

EDGE_SCALE_HTML = [
    html.I(className="fas fa-arrow-right-long pgm-control-icon pgm-branch-color"),
    dbc.Input(
        id="edge-scale-input",
        type="number",
        value=1,
        min=0.1,
        step=0.1,
        className="pgm-scale-input",
    ),
]

_SCALING_DIV = html.Div(
    NODE_SCALE_HTML + EDGE_SCALE_HTML,
    className="pgm-scaling-controls",
)


class LayoutOptions(Enum):
    """Cytoscape layout options."""

    RANDOM = "random"
    CIRCLE = "circle"
    CONCENTRIC = "concentric"
    GRID = "grid"
    COSE = "cose"
    BREADTHFIRST = "breadthfirst"
    PRESET = "preset"  # x,y-coordinates

    @classmethod
    def dropdown_options(cls):
        """Dropdown options (without PRESET)"""
        return [option for option in cls if option is not cls.PRESET]


_LAYOUT_DROPDOWN_OPTIONS = [
    {"label": option.value, "value": option.value} for option in LayoutOptions.dropdown_options()
]
_LAYOUT_DROPDOWN = html.Div(
    dcc.Dropdown(
        id="dropdown-update-layout",
        placeholder="Select layout",
        clearable=False,
        options=_LAYOUT_DROPDOWN_OPTIONS,  # type: ignore[arg-type]
        className="pgm-layout-dropdown",
    ),
    className="pgm-layout-dropdown-container",
)


_ARROWS_CHECKBOX = dbc.Checkbox(
    id="show-arrows",
    label="Show arrows",
    value=True,
    className="pgm-config-checkbox pgm-arrows-checkbox",
)

_SHOW_APPLIANCES_CHECKBOX = dbc.Checkbox(
    id="show-appliances",
    label="Show appliances",
    value=False,
    className="pgm-config-checkbox pgm-appliances-checkbox",
)

CONFIG_ELEMENTS = [_LAYOUT_DROPDOWN, _ARROWS_CHECKBOX, _SHOW_APPLIANCES_CHECKBOX, _SCALING_DIV]

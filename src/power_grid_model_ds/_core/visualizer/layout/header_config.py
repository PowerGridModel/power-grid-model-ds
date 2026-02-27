# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from enum import Enum

import dash_bootstrap_components as dbc
from dash import dcc, html

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.styling_classification import StyleClass

NODE_SCALE_HTML = [
    html.I(className="fas fa-circle", style={"color": CYTO_COLORS[StyleClass.NODE], "margin-right": "10px"}),
    dcc.Input(
        id="node-scale-input",
        type="number",
        value=1,
        min=0.1,
        step=0.1,
        style={"width": "75px"},
    ),
    html.Span(style={"margin-right": "10px"}),
]

EDGE_SCALE_HTML = [
    html.I(
        className="fas fa-arrow-right-long", style={"color": CYTO_COLORS[StyleClass.BRANCH], "margin-right": "10px"}
    ),
    dcc.Input(
        id="edge-scale-input",
        type="number",
        value=1,
        min=0.1,
        step=0.1,
        style={"width": "75px"},
    ),
]

_SCALING_DIV = html.Div(NODE_SCALE_HTML + EDGE_SCALE_HTML, style={"margin": "0 20px 0 10px"})


class LayoutOptions(Enum):
    """Cytoscape layout options."""

    RANDOM = "random"
    CIRCLE = "circle"
    CONCENTRIC = "concentric"
    GRID = "grid"
    COSE = "cose"
    BREADTHFIRST = "breadthfirst"


_LAYOUT_DROPDOWN = html.Div(
    dcc.Dropdown(
        id="dropdown-update-layout",
        placeholder="Select layout",
        value=LayoutOptions.BREADTHFIRST.value,
        clearable=False,
        options=[{"label": option.value, "value": option.value} for option in LayoutOptions],  # type: ignore[arg-type]
        style={"width": "200px"},
    ),
    style={"margin": "0 20px 0 10px", "color": "black"},
)


_ARROWS_CHECKBOX = dbc.Checkbox(
    id="show-arrows",
    label="Show arrows",
    value=True,
    label_style={"color": "white"},
    style={"margin-top": "10px"},
)

_SHOW_APPLIANCES_CHECKBOX = dbc.Checkbox(
    id="show-appliances",
    label="Show appliances",
    value=False,
    label_style={"color": "white"},
    style={"margin-top": "10px"},
)

_SCENARIO_INPUT = html.Div(
    [
        html.Span("Scenario ", style={"color": "white", "margin-right": "5px"}),
        dcc.Input(
            id="scenario-input",
            type="number",
            value=0,
            min=0,
            step=1,
            style={"width": "60px", "margin-right": "5px"},
        ),
    ],
    style={"display": "flex", "align-items": "center", "margin": "0 20px 0 10px"},
)

CONFIG_ELEMENTS = [_SCENARIO_INPUT, _LAYOUT_DROPDOWN, _ARROWS_CHECKBOX, _SHOW_APPLIANCES_CHECKBOX, _SCALING_DIV]

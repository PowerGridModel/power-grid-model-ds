# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dash import dcc, html

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.layout.cytoscape_html import LAYOUT_OPTIONS

NODE_SCALE_HTML = [
    html.I(className="fas fa-circle", style={"color": CYTO_COLORS["node"], "margin-right": "10px"}),
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
    html.I(className="fas fa-arrow-right-long", style={"color": CYTO_COLORS["line"], "margin-right": "10px"}),
    dcc.Input(
        id="edge-scale-input",
        type="number",
        value=1,
        min=0.1,
        step=0.1,
        style={"width": "75px"},
    ),
]

SCALE_INPUTS = [
    html.Div(
        NODE_SCALE_HTML + EDGE_SCALE_HTML,
        style={"margin": "0 20px 0 10px"},
    ),
]

LAYOUT_DROPDOWN_HTML = [
    html.Div(
        dcc.Dropdown(
            id="dropdown-update-layout",
            placeholder="Select layout",
            value="",
            clearable=False,
            options=[{"label": name.capitalize(), "value": name} for name in LAYOUT_OPTIONS],
            style={"width": "200px"},
        ),
        style={"margin": "0 20px 0 10px"},
    )
]

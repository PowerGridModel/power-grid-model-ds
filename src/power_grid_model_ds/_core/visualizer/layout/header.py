# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash_bootstrap_components as dbc
from dash import html

from power_grid_model_ds._core.visualizer.layout.cytoscape_config import LAYOUT_DROPDOWN_HTML, SCALE_INPUTS
from power_grid_model_ds._core.visualizer.layout.legenda import LEGENDA_HTML
from power_grid_model_ds._core.visualizer.layout.search_form import SEARCH_FORM_HTML

SHOW_ARROWS_CHECKBOX = dbc.Checkbox(
    id="show-arrows",
    label="Show arrows",
    value=True,
    className="me-2",
    label_style={"color": "white"},
    style={"margin-top": "10px"},
)
CONFIG_DIV = html.Div(
    SCALE_INPUTS + LAYOUT_DROPDOWN_HTML + [SHOW_ARROWS_CHECKBOX],
    className="d-flex justify-content-end align-items-center",
)
SEARCH_DIV = html.Div(SEARCH_FORM_HTML)

HEADER_HTML = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Button("Legend", id="btn-legend", color="primary", className="me-2"),
                dbc.Button("Search", id="btn-search", color="secondary", className="me-2"),
                dbc.Button("Config", id="btn-config", color="success", className="me-2"),
            ],
            width=5,
            style={
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "border-right": "1px solid white",
            },
        ),
        dbc.Col(
            html.Div([LEGENDA_HTML, SEARCH_DIV, CONFIG_DIV], id="right-col-content", className="text-end"),
            width=7,
            style={
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
            },
        ),
    ],
    style={
        "background-color": "#343a40",
        "color": "white",
        "padding": "1rem 0",
        "margin": 0,
        "height": "90px",
    },
    className="g-0",
    align="center",
)

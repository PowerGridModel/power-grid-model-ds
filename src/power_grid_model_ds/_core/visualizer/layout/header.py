# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash_bootstrap_components as dbc
from dash import html

from power_grid_model_ds._core.visualizer.layout.header_config import CONFIG_ELEMENTS
from power_grid_model_ds._core.visualizer.layout.header_legenda import LEGENDA_ELEMENTS, LEGENDA_STYLE
from power_grid_model_ds._core.visualizer.layout.header_search import SEARCH_ELEMENTS

_CONTENT_COLUMN_STYLE = {
    "display": "flex",
    "align-items": "center",
    "width": "100%",
}


CONFIG_DIV = html.Div(CONFIG_ELEMENTS, style=_CONTENT_COLUMN_STYLE | {"justify-content": "space-between"})
SEARCH_DIV = html.Div(SEARCH_ELEMENTS, style=_CONTENT_COLUMN_STYLE | {"justify-content": "center"})
LEGENDA_DIV = html.Div(LEGENDA_ELEMENTS, style=_CONTENT_COLUMN_STYLE | LEGENDA_STYLE)


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
            [LEGENDA_DIV, SEARCH_DIV, CONFIG_DIV],
            id="right-col-content",
            width=7,
            style={
                "display": "flex",
                "align-items": "center",
                "justify-content": "space-between",
                # "width": "100%",
            },
        ),
    ],
    style={
        "background-color": "#343a40",
        "color": "white",
        "padding": "1rem 0",
        "margin": 0,
        "height": "90px",
        "width": "100%",
    },
    align="center",
)

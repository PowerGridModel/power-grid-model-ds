# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash_bootstrap_components as dbc
from dash import html

from power_grid_model_ds._core.visualizer.layout.header_config import CONFIG_ELEMENTS
from power_grid_model_ds._core.visualizer.layout.header_legenda import LEGENDA_ELEMENTS
from power_grid_model_ds._core.visualizer.layout.header_search import SEARCH_ELEMENTS

_MENU_BUTTON_STYLE_CLASS = "me-2 btn-outline-primary"

_LEFT_COLUMN_HTML = dbc.Col(
    [
        dbc.Button("Legend", id="btn-legend", className=_MENU_BUTTON_STYLE_CLASS),
        dbc.Button("Search", id="btn-search", className=_MENU_BUTTON_STYLE_CLASS),
        dbc.Button("Config", id="btn-config", className=_MENU_BUTTON_STYLE_CLASS),
    ],
    id="header-left-col",
    width=5,
    className="pgm-header-left",
)


CONFIG_DIV = html.Div(CONFIG_ELEMENTS, className="pgm-header-right pgm-header-config")
SEARCH_DIV = html.Div(SEARCH_ELEMENTS, className="pgm-header-right pgm-header-search")
LEGENDA_DIV = html.Div(LEGENDA_ELEMENTS, className="pgm-header-right pgm-header-legend")

_RIGHT_COLUMN_HTML = dbc.Col(
    [LEGENDA_DIV, SEARCH_DIV, CONFIG_DIV],
    id="header-right-col",
    width=7,
)

HEADER_HTML = dbc.Row(
    [
        _LEFT_COLUMN_HTML,
        _RIGHT_COLUMN_HTML,
    ],
    className="pgm-header",
    align="center",
)

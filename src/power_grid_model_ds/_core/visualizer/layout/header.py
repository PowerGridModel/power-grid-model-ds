# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash_bootstrap_components as dbc

from power_grid_model_ds._core.visualizer.layout.colors import BACKGROUND_COLOR
from power_grid_model_ds._core.visualizer.layout.cytoscape_config import LAYOUT_DROPDOWN_HTML, SCALE_INPUTS
from power_grid_model_ds._core.visualizer.layout.legenda import LEGENDA_HTML
from power_grid_model_ds._core.visualizer.layout.search_form import SEARCH_FORM_HTML

_SEARCH_FORM_CARD_STYLE = {
    "background-color": "#555555",
    "color": "white",
    "border-left": "1px solid white",
    "border-right": "1px solid white",
    "border-radius": 0,
}


HEADER_HTML = dbc.Row(
    [
        dbc.Col(LEGENDA_HTML, className="d-flex align-items-center"),
        dbc.Col(
            dbc.Card(SEARCH_FORM_HTML, style=_SEARCH_FORM_CARD_STYLE),
            className="d-flex justify-content-center align-items-center",
        ),
        dbc.Col(SCALE_INPUTS + LAYOUT_DROPDOWN_HTML, className="d-flex justify-content-end align-items-center"),
    ],
    style={"background-color": BACKGROUND_COLOR},
)

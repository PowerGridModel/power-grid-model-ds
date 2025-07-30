# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash
from dash import Input, Output, callback

from power_grid_model_ds._core.visualizer.layout.header import CONFIG_DIV, SEARCH_DIV
from power_grid_model_ds._core.visualizer.layout.legenda import LEGENDA_HTML


@callback(
    Output("right-col-content", "children"),
    [
        Input("btn-legend", "n_clicks"),
        Input("btn-search", "n_clicks"),
        Input("btn-config", "n_clicks"),
    ],
)
def update_right_col(_btn1, _btn2, _btn3):
    """Update the right column content based on the button clicked."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return LEGENDA_HTML
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    button_map = {
        "btn-legend": LEGENDA_HTML,
        "btn-search": SEARCH_DIV,
        "btn-config": CONFIG_DIV,
    }
    return button_map.get(button_id, "Right Column")

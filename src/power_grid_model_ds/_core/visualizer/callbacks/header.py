# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash
from dash import Input, Output, callback

from power_grid_model_ds._core.visualizer.layout.header import CONFIG_DIV, LEGENDA_DIV, SEARCH_DIV


@callback(
    Output("header-right-col", "children"),
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
        return LEGENDA_DIV
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    button_map = {
        "btn-legend": LEGENDA_DIV,
        "btn-search": SEARCH_DIV,
        "btn-config": CONFIG_DIV,
    }
    return button_map.get(button_id, "Right Column")

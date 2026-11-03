# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dash import Input, Output, callback, ctx

from power_grid_model_ds._core.visualizer.layout.header import (
    _HIDDEN_PANEL_STYLE,
    _RIGHT_COLUMN_STYLE,
)
from power_grid_model_ds._core.visualizer.layout.header_legenda import LEGENDA_STYLE


def get_header_panel_styles(active_button: str | None) -> tuple[dict, dict, dict]:
    """Return visibility styles for the legend, search and config panels."""
    legend_style = _HIDDEN_PANEL_STYLE.copy()
    search_style = _HIDDEN_PANEL_STYLE.copy()
    config_style = _HIDDEN_PANEL_STYLE.copy()

    if active_button == "btn-search":
        search_style = _RIGHT_COLUMN_STYLE.copy()
    elif active_button == "btn-config":
        config_style = _RIGHT_COLUMN_STYLE.copy()
    else:
        legend_style = _RIGHT_COLUMN_STYLE | LEGENDA_STYLE

    return legend_style, search_style, config_style


@callback(
    Output("header-legend-panel", "style"),
    Output("header-search-panel", "style"),
    Output("header-config-panel", "style"),
    Input("btn-legend", "n_clicks"),
    Input("btn-search", "n_clicks"),
    Input("btn-config", "n_clicks"),
)
def update_right_col(_btn1, _btn2, _btn3):
    """Show the selected header panel without unmounting its controls."""
    return get_header_panel_styles(ctx.triggered_id)

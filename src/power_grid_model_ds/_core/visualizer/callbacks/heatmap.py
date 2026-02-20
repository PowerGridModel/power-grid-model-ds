# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.visualizer.callbacks.common import _update_column_options
from power_grid_model_ds._core.visualizer.layout.colors import _map_colors_to_array
from power_grid_model_ds._core.visualizer.server_state import safe_get_grid
from power_grid_model_ds._core.visualizer.typing import STYLESHEET


@callback(
    Output("heatmap-column-input", "options"),
    Output("heatmap-column-input", "value"),
    Input("heatmap-group-input", "value"),
    Input("columns-store", "data"),
)
def update_heatmap_column_options(selected_group, columns):
    """Update the column dropdown options based on the selected group."""
    return _update_column_options(selected_group, columns)


@callback(
    Output("cytoscape-graph", "stylesheet", allow_duplicate=True),
    Input("heatmap-group-input", "value"),
    Input("heatmap-column-input", "value"),
    State("stylesheet-store", "data"),
    prevent_initial_call=True,
)
def apply_heatmap_selection(
    group: str,
    column: str,
    stylesheet: STYLESHEET,
) -> STYLESHEET:
    """Apply heatmap coloring to elements based on the selected column and range."""
    if not group or not column:
        raise PreventUpdate

    grid = safe_get_grid()

    array_ids = getattr(getattr(grid, group), "id")
    array_column = getattr(getattr(grid, group), column)
    colors = _map_colors_to_array(array_column)

    new_stylesheets = []
    if group == "three_winding_transformer":
        for elm_id, color in zip(array_ids, colors):
            for count in range(3):
                new_stylesheets.append({"selector": f"#{elm_id}_{count}", "style": _get_heatmap_style(color)})
        return stylesheet + new_stylesheets

    for elm_id, color in zip(array_ids, colors):
        new_stylesheets.append({"selector": f"#{elm_id}", "style": _get_heatmap_style(color)})
    return stylesheet + new_stylesheets


def _get_heatmap_style(color: str) -> dict:
    """Get the style dictionary for heatmap coloring."""
    return {
        "background-color": color,
        "text-background-color": color,
        "line-color": color,
        "target-arrow-color": color,
    }

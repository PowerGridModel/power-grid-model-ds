# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.typing import STYLESHEET


@callback(
    Output("heatmap-column-input", "options"),
    Output("heatmap-column-input", "value"),
    Input("heatmap-group-input", "value"),
    Input("columns-store", "data"),
)
def update_heatmap_column_options(selected_group, store_data):
    """Update the column dropdown options based on the selected group."""
    if not selected_group or not store_data:
        return [], None

    # Get columns for the selected group (node, line, link, or transformer)
    columns = store_data.get(selected_group, [])
    default_value = columns[0] if columns else "id"

    return columns, default_value


@callback(
    Output("cytoscape-graph", "stylesheet", allow_duplicate=True),
    Input("heatmap-group-input", "value"),
    Input("heatmap-column-input", "value"),
    State("heatmap-min-max-store", "data"),
    State("stylesheet-store", "data"),
    prevent_initial_call=True,
)
def apply_heatmap_selection(
    group: str,
    column: str,
    heatmap_min_max: dict,
    stylesheet: STYLESHEET,
) -> STYLESHEET:
    """Apply heatmap coloring to elements based on the selected column and range."""
    if not group or not column:
        raise PreventUpdate

    if group == "branches":
        selector = "edge[group = 'line'], edge[group = 'link'], edge[group = 'transformer']"
    else:
        selector = f"[group = '{group}']"

    new_style = {
        "selector": selector,
        "style": _get_heatmap_style(group, column, heatmap_min_max),
    }
    updated_stylesheet = stylesheet + [new_style]
    return updated_stylesheet


def _get_heatmap_style(
    group: str,
    column: str,
    heatmap_min_max: dict,
) -> dict:
    """Get the style dictionary for heatmap coloring."""
    min_key = f"{group}_{column}_min"
    max_key = f"{group}_{column}_max"

    if not heatmap_min_max or min_key not in heatmap_min_max or max_key not in heatmap_min_max:
        return {}

    min_value = heatmap_min_max[min_key]
    max_value = heatmap_min_max[max_key]

    # id column was renamed to pgm_id because of cytoscape reserved word
    search_column = column if column != "id" else "pgm_id"
    mapping_expression = (
        f"mapData({search_column}, {min_value}, {max_value}, "
        f"{CYTO_COLORS['heatmap_min']}, {CYTO_COLORS['heatmap_max']})"
    )
    return {
        "background-color": mapping_expression,
        "text-background-color": mapping_expression,
        "line-color": mapping_expression,
        "target-arrow-color": mapping_expression,
    }

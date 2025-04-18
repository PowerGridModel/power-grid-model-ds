# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
from typing import Any

from dash import Input, Output, callback

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET


@callback(
    Output("cytoscape-graph", "stylesheet"),
    Input("search-form-group-input", "value"),
    Input("search-form-column-input", "value"),
    Input("search-form-operator-input", "value"),
    Input("search-form-value-input", "value"),
)
def search_element(group: str, column: str, operator: str, value: str) -> list[dict[str, Any]]:
    """Color the specified element red based on the input values."""
    if not group or not column or not value:
        return DEFAULT_STYLESHEET

    # Determine if we're working with a node or an edge type
    if group == "node":
        style = {
            "background-color": CYTO_COLORS["highlighted"],
            "text-background-color": CYTO_COLORS["highlighted"],
        }
    else:
        style = {"line-color": CYTO_COLORS["highlighted"], "target-arrow-color": CYTO_COLORS["highlighted"]}

    if column == "id":
        selector = f'[{column} {operator} "{value}"]'
    else:
        selector = f"[{column} {operator} {value}]"

    new_style = {
        "selector": selector,
        "style": style,
    }
    return DEFAULT_STYLESHEET + [new_style]


@callback(
    Output("search-form-column-input", "options"),
    Output("search-form-column-input", "value"),
    Input("search-form-group-input", "value"),
    Input("columns-store", "data"),
)
def update_column_options(selected_group, store_data):
    """Update the column dropdown options based on the selected group."""
    if not selected_group or not store_data:
        return [], None

    # Get columns for the selected group (node, line, link, or transformer)
    columns = store_data.get(selected_group, [])
    default_value = columns[0] if columns else "id"

    return columns, default_value

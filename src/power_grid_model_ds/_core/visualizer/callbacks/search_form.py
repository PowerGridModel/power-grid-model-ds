# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import logging

from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.server_state import get_grid
from power_grid_model_ds._core.visualizer.typing import STYLESHEET

logger = logging.getLogger(__name__)
HIGHLIGHT_STYLE = {
    "background-color": CYTO_COLORS["highlighted"],
    "text-background-color": CYTO_COLORS["highlighted"],
    "line-color": CYTO_COLORS["highlighted"],
    "target-arrow-color": CYTO_COLORS["highlighted"],
}


@callback(
    Output("cytoscape-graph", "stylesheet"),
    Input("search-form-group-input", "value"),
    Input("search-form-column-input", "value"),
    Input("search-form-operator-input", "value"),
    Input("search-form-value-input", "value"),
    State("stylesheet-store", "data"),
)
def search_element(group: str, column: str, operator: str, value: str, stylesheet: STYLESHEET) -> STYLESHEET:
    """Color the specified element red based on the input values."""
    if not group or not column or not value:
        raise PreventUpdate

    # Correctly parse any backslash or quote before making is a float.
    parsed_value = float(str(value).strip().replace("\\", "\\\\").replace('"', '\\"'))

    matching_ids = _get_matching_pgm_ids(group=group, column=column, operator=operator, value=parsed_value)

    highlight_selectors = [{"selector": f"#{pgm_id}", "style": HIGHLIGHT_STYLE} for pgm_id in matching_ids]
    return stylesheet + highlight_selectors


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


def _get_matching_pgm_ids(group: str, column: str, operator: str, value: float) -> list[int]:
    """Find the ids in the grid that match with the search criteria."""
    array = getattr(get_grid(), group)
    selected_column = array[column]

    # Some columns have 3 digits in them (for asymmetic data). We do not support search on those columns for now.
    if selected_column.ndim != 1:
        logger.warning(f"Column '{column}' in group '{group}' is not 1-dimensional. Skipping search.")
        raise PreventUpdate

    match operator:
        case "=":
            mask = selected_column == value
        case "!=":
            mask = selected_column != value
        case "<":
            mask = selected_column < value
        case ">":
            mask = selected_column > value

    return array.id[mask].tolist()

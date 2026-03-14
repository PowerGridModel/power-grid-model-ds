# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.visualizer.callbacks.common import _update_column_options, _update_phase_options
from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.server_state import safe_get_grid
from power_grid_model_ds._core.visualizer.typing import STYLESHEET, VizToComponentElements

HIGHLIGHT_STYLE = {
    "background-color": CYTO_COLORS["highlighted"],
    "text-background-color": CYTO_COLORS["highlighted"],
    "line-color": CYTO_COLORS["highlighted"],
    "target-arrow-color": CYTO_COLORS["highlighted"],
}


@callback(
    Output("cytoscape-graph", "stylesheet", allow_duplicate=True),
    Input("search-form-group-input", "value"),
    Input("search-form-column-input", "value"),
    Input("search-form-operator-input", "value"),
    Input("search-form-value-input", "value"),
    Input("search-form-phase-input", "value"),
    State("cytoscape-graph", "elements"),
    State("stylesheet-store", "data"),
    prevent_initial_call=True,
)
def search_element(  #  pylint: disable=too-many-arguments, disable=too-many-positional-arguments
    group: str,
    column: str,
    operator: str,
    value: str,
    phase: str,
    elements: VizToComponentElements,
    stylesheet: STYLESHEET,
) -> STYLESHEET:
    """Color the specified element red based on the input values.

    Note: Grid object is available via get_grid() for on-demand queries.
    Example: grid = get_grid()
    """
    matching_pgm_ids = _search_query_to_pgm_ids(group, column, operator, value, phase)
    if matching_pgm_ids.size == 0:
        return stylesheet

    visualizable_pgm_ids: list[str] = []
    for element in elements:
        for associated_ids in element["data"]["associated_ids"].values():
            if any(comp_id in matching_pgm_ids for comp_id in associated_ids):
                visualizable_pgm_ids.append(element["data"]["id"])

    new_stylesheets = [{"selector": f"#{elm_id}", "style": HIGHLIGHT_STYLE} for elm_id in visualizable_pgm_ids]

    return stylesheet + new_stylesheets


@callback(
    Output("search-form-column-input", "options"),
    Output("search-form-column-input", "value"),
    Input("search-form-group-input", "value"),
    Input("columns-store", "data"),
)
def update_column_options(selected_group, columns):
    """Update the column dropdown options based on the selected group."""
    return _update_column_options(selected_group, columns)


@callback(
    Output("search-form-phase-input", "options"),
    Output("search-form-phase-input", "value"),
    Input("search-form-group-input", "value"),
    Input("search-form-column-input", "value"),
)
def update_search_form_phase_options(selected_group, selected_column):
    """Update the phase dropdown options based on the selected group."""
    return _update_phase_options(selected_group, selected_column)


def _search_query_to_pgm_ids(group: str, column: str, operator: str, value: str, phase: str):

    if not group or not column or not value:
        raise PreventUpdate

    sanitized_value = str(value).strip().replace("\\", "\\\\").replace('"', '\\"')
    try:
        numeric_value = float(sanitized_value)
    except ValueError as e:
        raise PreventUpdate from e

    grid = safe_get_grid()
    component_array = getattr(grid, group)

    if phase == "abc":
        data = component_array[column]
    else:
        phase_idx = {"a": 0, "b": 1, "c": 2}.get(phase)
        data = component_array[column][:, phase_idx]

    if operator == "=":
        mask = data == numeric_value
    elif operator == ">":
        mask = data > numeric_value
    elif operator == "<":
        mask = data < numeric_value
    elif operator == "!=":
        mask = data != numeric_value
    else:
        raise PreventUpdate

    return component_array.id[mask]

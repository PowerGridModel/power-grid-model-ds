# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer.callbacks.common import _update_column_options
from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.server_state import safe_get_grid
from power_grid_model_ds._core.visualizer.typing import STYLESHEET, VizToComponentData

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
    State("viz-to-comp-store", "data"),
    State("stylesheet-store", "data"),
    State("show-appliances-store", "data"),
    prevent_initial_call=True,
)
def search_element(  #  pylint: disable=too-many-arguments, disable=too-many-positional-arguments, disable=too-many-branches, disable=too-many-locals
    group: str,
    column: str,
    operator: str,
    value: str,
    viz_to_comp: VizToComponentData,
    stylesheet: STYLESHEET,
    show_appliances: bool,
) -> STYLESHEET:
    """Color the specified element red based on the input values.

    Note: Grid object is available via get_grid() for on-demand queries.
    Example: grid = get_grid()
    """
    matching_pgm_ids = _search_query_to_pgm_ids(group, column, operator, value)
    if matching_pgm_ids.size == 0:
        return stylesheet

    non_visible_elms = _non_visible_appliances(show_appliances)
    if group not in non_visible_elms:
        visualizable_pgm_ids = [str(pgm_id) for pgm_id in matching_pgm_ids]
    else:
        visualizable_pgm_ids = []
        for viz_id, non_visible_components in viz_to_comp.items():
            if group not in non_visible_components:
                continue
            found = any(comp_id in matching_pgm_ids for comp_id in non_visible_components[ComponentType(group)])
            if found:
                visualizable_pgm_ids.append(viz_id)

    # For three-winding transformers, we need to highlight all three connected edges with id '*_0', '*_1', '*_2'.
    if group == ComponentType.three_winding_transformer.value:
        new_stylesheets = [
            {"selector": f"#{elm_id}_{count}", "style": HIGHLIGHT_STYLE}
            for elm_id in visualizable_pgm_ids
            for count in range(3)
        ]
    else:
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


def _non_visible_appliances(show_appliances: bool):
    result = [
        ComponentType.sym_power_sensor.value,
        ComponentType.sym_voltage_sensor.value,
        ComponentType.asym_voltage_sensor.value,
        ComponentType.transformer_tap_regulator.value,
    ]
    if show_appliances:
        result += [ComponentType.sym_load.value, ComponentType.sym_gen.value]
    return result


def _search_query_to_pgm_ids(group: str, column: str, operator: str, value: str):

    if not group or not column or not value:
        raise PreventUpdate

    sanitized_value = str(value).strip().replace("\\", "\\\\").replace('"', '\\"')
    try:
        numeric_value = float(sanitized_value)
    except ValueError as e:
        raise PreventUpdate from e

    grid = safe_get_grid()
    component_array = getattr(grid, group)
    if operator == "=":
        mask = component_array[column] == numeric_value
    elif operator == ">":
        mask = component_array[column] > numeric_value
    elif operator == "<":
        mask = component_array[column] < numeric_value
    elif operator == "!=":
        mask = component_array[column] != numeric_value
    else:
        raise PreventUpdate

    return component_array.id[mask]

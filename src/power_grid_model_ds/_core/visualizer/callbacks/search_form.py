# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.typing import STYLESHEET, ListArrayData, VizToComponentData

NODE_HIGHLIGHT_STYLE = {
    "background-color": CYTO_COLORS["highlighted"],
    "text-background-color": CYTO_COLORS["highlighted"],
}

EDGE_HIGHLIGHT_STYLE = {
    "line-color": CYTO_COLORS["highlighted"],
    "target-arrow-color": CYTO_COLORS["highlighted"],
}
HIGHLIGHT_STYLE = {
    "background-color": CYTO_COLORS["highlighted"],
    "text-background-color": CYTO_COLORS["highlighted"],
    "line-color": CYTO_COLORS["highlighted"],
    "target-arrow-color": CYTO_COLORS["highlighted"],
}


NODE_GROUPS = ["node"]
EDGE_GROUPS = ["line", "link", "transformer", "three_winding_transformer", "sym_load", "sym_gen", "source"]

GROUPS_IN_BRANCH = EDGE_GROUPS

INDIRECT_SEARCH_ELEMENTS = [
    "sym_power_sensor",
    "sym_voltage_sensor",
    "asym_voltage_sensor",
    "transformer_tap_regulator",
]


@callback(
    Output("cytoscape-graph", "stylesheet"),
    Input("search-form-group-input", "value"),
    Input("search-form-column-input", "value"),
    Input("search-form-operator-input", "value"),
    Input("search-form-value-input", "value"),
    State("viz-to-comp-store", "data"),
    State("stylesheet-store", "data"),
)
def search_element(  #  pylint: disable=too-many-arguments, disable=too-many-positional-arguments
    group: str,
    column: str,
    operator: str,
    value: str,
    viz_to_comp: VizToComponentData,
    stylesheet: STYLESHEET,
) -> STYLESHEET:
    """Color the specified element red based on the input values."""
    if not group or not column or not value:
        raise PreventUpdate

    # id column was renamed to pgm_id because of cytoscape reserved word
    search_column = column if column != "id" else "pgm_id"
    search_query = f"{search_column} {operator} {value}"

    if group in NODE_GROUPS:
        selector = f"node[{search_query}][group = '{group}']"
    elif group in EDGE_GROUPS:
        selector = f"edge[{search_query}][group = '{group}']"
    elif group == "branch":
        selector = f"edge[{search_query}]" + "".join(f"[group = '{group}']" for group in GROUPS_IN_BRANCH)
    elif group in INDIRECT_SEARCH_ELEMENTS:
        found = _search_components(
            viz_to_comp=viz_to_comp, component_type=group, column=search_column, operator=operator, value=value
        )
        if found:
            selector = ", ".join([f'[id = "{node_id}"]' for node_id in found])
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate

    new_style = {
        "selector": selector,
        "style": HIGHLIGHT_STYLE,
    }
    updated_stylesheet = stylesheet + [new_style]
    return updated_stylesheet


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


def _search_components(
    viz_to_comp: VizToComponentData, component_type: str, column: str, operator: str, value: str
) -> list[str]:
    """Find node or edge IDs that have components matching the search criteria."""
    try:
        numeric_value = float(value)
    except ValueError:
        return []

    matching_nodes = []
    for node_edge_id, node_edge_data in viz_to_comp.items():
        if _find_components_node_edge(node_edge_data, component_type, column, numeric_value, operator):
            matching_nodes.append(node_edge_id)

    return matching_nodes


def _find_components_node_edge(
    node_edge_data: dict[str, ListArrayData],
    component_type: str,
    column: str,
    numeric_value: float,
    operator: str,
) -> bool:
    if component_type in node_edge_data:
        for component in node_edge_data[component_type]:
            if column in component:
                if _compare_values(numeric_value, component[column], operator):
                    return True
    return False


def _compare_values(numeric_value: float, component_value: float, operator: str) -> bool:
    """Compare component value with the numeric value based on the operator."""
    match operator:
        case "=":
            return component_value == numeric_value
        case ">":
            return component_value > numeric_value
        case "<":
            return component_value < numeric_value
        case "!=":
            return component_value != numeric_value
        case _:
            return False

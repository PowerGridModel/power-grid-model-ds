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

    selected_nodes, selected_edges = _search_components(
        viz_to_comp=viz_to_comp, group=group, column=column, operator=operator, value=value
    )

    if not selected_nodes and not selected_edges:
        raise PreventUpdate

    new_styles = []
    if selected_nodes:
        node_selector = ", ".join([f'[id = "{node_id}"]' for node_id in selected_nodes])
        new_styles.append({"selector": node_selector, "style": NODE_HIGHLIGHT_STYLE})
    if selected_edges:
        edge_selector = ", ".join([f'[id = "{edge_id}"]' for edge_id in selected_edges])
        new_styles.append({"selector": edge_selector, "style": EDGE_HIGHLIGHT_STYLE})

    updated_stylesheet = stylesheet + new_styles
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


def _find_components_node_edge(
    node_edge_data: dict[str, ListArrayData],
    component_types: list[str],
    column: str,
    numeric_value: float,
    operator: str,
) -> bool:
    for component_type in component_types:
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


def _search_components(
    viz_to_comp: VizToComponentData, group: str, column: str, operator: str, value: str
) -> tuple[list[str], list[str]]:
    """Find node or edge IDs that have components matching the search criteria."""
    try:
        numeric_value = float(value)
    except ValueError:
        return [], []

    component_types = ["line", "link", "transformer"] if group == "branch" else [group]

    matching_nodes = []
    matching_edges = []
    for node_edge_id, node_edge_data in viz_to_comp.items():
        if _find_components_node_edge(node_edge_data, component_types, column, numeric_value, operator):
            if "node" in node_edge_data:
                matching_nodes.append(node_edge_id)
            else:
                matching_edges.append(node_edge_id)
            break

    return matching_nodes, matching_edges

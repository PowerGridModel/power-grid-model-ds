# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.visualizer.layout.colors import CYTO_COLORS
from power_grid_model_ds._core.visualizer.typing import STYLESHEET, VizToComponentData


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

    node_selector, edge_selector = _create_selector_for_connected_components(
        viz_to_comp=viz_to_comp, component_type=group, column=column, operator=operator, value=value
    )

    if not node_selector and not edge_selector:
        raise PreventUpdate

    new_styles = []
    if node_selector:
        new_styles.append(_generate_node_highlight_style(node_selector))
    if edge_selector:
        new_styles.append(_generate_edge_highlight_style(edge_selector))

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


def _generate_node_highlight_style(selector: str) -> dict[str, str | dict[str, str]]:
    """Get the highlight style for a given group."""
    return {
        "selector": selector,
        "style": {
            "background-color": CYTO_COLORS["highlighted"],
            "text-background-color": CYTO_COLORS["highlighted"],
        },
    }


def _generate_edge_highlight_style(selector: str) -> dict[str, str | dict[str, str]]:
    return {
        "selector": selector,
        "style": {
            "line-color": CYTO_COLORS["highlighted"],
            "target-arrow-color": CYTO_COLORS["highlighted"],
        },
    }


def _create_selector_for_connected_components(
    viz_to_comp: VizToComponentData, component_type: str, column: str, operator: str, value: str
) -> tuple[str, str]:
    """Find node or edge IDs that have components matching the search criteria."""
    try:
        numeric_value = float(value)
    except ValueError:
        return "", ""

    matching_nodes = []
    matching_edges = []
    for node_edge_id, node_edge_data in viz_to_comp.items():
        if component_type not in node_edge_data:
            continue

        for component in node_edge_data[component_type]:
            if column not in component:
                continue

            match operator:
                case "=":
                    match = component[column] == numeric_value
                case ">":
                    match = component[column] > numeric_value
                case "<":
                    match = component[column] < numeric_value
                case "!=":
                    match = component[column] != numeric_value
                case _:
                    match = False
            if not match:
                continue

            if "node" in node_edge_data:
                matching_nodes.append(node_edge_id)
            else:
                matching_edges.append(node_edge_id)

    node_selector = ", ".join([f'[id = "{node_id}"]' for node_id in matching_nodes])
    edge_selector = ", ".join([f'[id = "{edge_id}"]' for edge_id in matching_edges])
    return node_selector, edge_selector

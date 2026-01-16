# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from dash import Input, Output, State, callback, dash_table, html

from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HTML,
)
from power_grid_model_ds._core.visualizer.typing import ListArrayData, VizToComponentData

# Keys used in the visualization elements that are not part of the component data
VISUALIZATION_KEYS = ["id", "label", "group", "x", "y", "parent", "source", "target"]


@callback(
    Output("selection-output", "children"),
    Input("cytoscape-graph", "selectedNodeData"),
    Input("cytoscape-graph", "selectedEdgeData"),
    State("viz-to-comp-store", "data"),
    State("columns-store", "data"),
)
def display_selected_element(
    node_data: ListArrayData,
    edge_data: ListArrayData,
    viz_to_comp: VizToComponentData,
    columns_data: dict[str, list[str]],
):
    """Display the tapped edge data."""
    # 0th element means data for only a single selection is shown
    if node_data:
        selected_data = node_data.pop()
    elif edge_data:
        selected_data = edge_data.pop()
    else:
        return SELECTION_OUTPUT_HTML.children

    group = selected_data["group"]
    group = group.replace("_ghost_node", "")  # Remove _ghost_node suffix for appliances

    elm_data = {k: v for k, v in selected_data.items() if k not in VISUALIZATION_KEYS}

    tables: list[html.H5 | html.Div] = []
    tables.append(html.H5(group, style={"marginTop": "15px", "textAlign": "left"}))
    tables.append(_to_multiple_entries_data_tables(list_array_data=[elm_data], columns=columns_data[group]))

    elm_id_str = selected_data["id"]
    if elm_id_str in viz_to_comp:
        for comp_type, list_array_data in viz_to_comp[elm_id_str].items():
            tables.append(html.H5(comp_type, style={"marginTop": "15px", "textAlign": "left"}))
            tables.append(
                _to_multiple_entries_data_tables(list_array_data=list_array_data, columns=columns_data[comp_type])
            )
    return html.Div(children=tables, style={"overflowX": "scroll", "margin": "10px"}).children


def _to_multiple_entries_data_tables(list_array_data: ListArrayData, columns: list[str]) -> html.Div:
    """Convert list array data to a Dash DataTable."""

    # id column was renamed to pgm_id because of cytoscape reserved word
    for elm in list_array_data:
        elm["id"] = elm["pgm_id"]
        del elm["pgm_id"]
    data_table = dash_table.DataTable(  # type: ignore[attr-defined]
        data=list_array_data, columns=[{"name": key, "id": key} for key in columns], editable=False, fill_width=False
    )
    return data_table

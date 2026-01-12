# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from dash import Input, Output, State, callback, dash_table, html

from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HTML,
)
from power_grid_model_ds._core.visualizer.typing import ListArrayData, VizToComponentData


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
        elm_id_str = node_data[0]["id"]
    elif edge_data:
        elm_id_str = edge_data[0]["id"]
    else:
        return SELECTION_OUTPUT_HTML.children

    tables: list[html.H5 | html.Div] = []
    if elm_id_str in viz_to_comp:
        for comp_type, list_array_data in viz_to_comp[elm_id_str].items():
            tables.append(html.H5(comp_type, style={"marginTop": "15px"}))
            tables.append(
                _to_multiple_entries_data_tables(list_array_data=list_array_data, columns=columns_data[comp_type])
            )
        return html.Div(children=tables, style={"overflowX": "scroll", "margin": "10px"}).children
    return SELECTION_OUTPUT_HTML.children


def _to_multiple_entries_data_tables(list_array_data: ListArrayData, columns: list[str]) -> html.Div:
    data_table = dash_table.DataTable(  # type: ignore[attr-defined]
        data=list_array_data, columns=[{"name": key, "id": key} for key in columns], editable=False, fill_width=False
    )
    return data_table

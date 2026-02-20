# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


import numpy as np
from dash import Input, Output, State, callback, dash_table, html

from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HTML,
)
from power_grid_model_ds._core.visualizer.server_state import safe_get_grid
from power_grid_model_ds._core.visualizer.typing import ListArrayData, VizToComponentData

# Keys used in the visualization elements that are not part of the component data
VISUALIZATION_KEYS = ["id", "label", "group", "position", "parent", "source", "target"]


@callback(
    Output("selection-output", "children"),
    Input("cytoscape-graph", "selectedNodeData"),
    Input("cytoscape-graph", "selectedEdgeData"),
    State("viz-to-comp-store", "data"),
)
def display_selected_element(
    node_data: ListArrayData,
    edge_data: ListArrayData,
    viz_to_comp: VizToComponentData,
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
    elm_id_str = selected_data["id"]
    to_strip = ["_0", "_1", "_2"]
    for suffix in to_strip:
        elm_id_str = elm_id_str.replace(suffix, "")
    pgm_id = np.int32(elm_id_str)

    grid = safe_get_grid()

    data = getattr(grid, group).get(id=pgm_id)
    tables: list[html.H5 | html.Div] = []
    tables.append(html.H5(group, style={"marginTop": "15px", "textAlign": "left"}))
    tables.append(_array_to_data_tables(data))

    if elm_id_str in viz_to_comp:
        for comp_type, non_visible_ids in viz_to_comp[elm_id_str].items():
            data = getattr(grid, comp_type).filter(id=non_visible_ids)
            tables.append(html.H5(comp_type, style={"marginTop": "15px", "textAlign": "left"}))
            tables.append(_array_to_data_tables(data))

    return html.Div(children=tables, style={"overflowX": "scroll", "margin": "10px"}).children


def _array_to_data_tables(array_data) -> html.Div:
    """Convert array data to a Dash DataTable."""
    list_array_data = [{col: entry[col].item() for col in array_data.columns} for entry in array_data]
    columns = [{"name": key, "id": key} for key in array_data.columns]

    data_table = dash_table.DataTable(  # type: ignore[attr-defined]
        data=list_array_data, columns=columns, editable=False, fill_width=False
    )
    return html.Div(data_table)

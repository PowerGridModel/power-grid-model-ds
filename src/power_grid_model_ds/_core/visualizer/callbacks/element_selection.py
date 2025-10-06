# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any

from dash import Input, Output, callback, dash_table

from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HTML,
)


@callback(
    Output("selection-output", "children"),
    Input("cytoscape-graph", "selectedNodeData"),
    Input("cytoscape-graph", "selectedEdgeData"),
)
def display_selected_element(node_data, edge_data):
    """Display the tapped edge data."""
    if node_data:
        return _to_data_table(node_data.pop())
    if edge_data:
        return _to_data_table(edge_data.pop())
    return SELECTION_OUTPUT_HTML


def _to_data_table(data: dict[str, Any]):
    columns = data.keys()
    data_table = dash_table.DataTable(  # type: ignore[attr-defined]
        data=[data], columns=[{"name": key, "id": key} for key in columns], editable=False
    )
    return data_table

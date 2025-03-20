from typing import Any

from dash import Input, Output, callback, dash_table, dcc

from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HEADER_STYLE,
    SELECTION_OUTPUT_HTML,
)


@callback(
    Output("search-output", "children"),
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
    # del data["timeStamp"]
    group = data.pop("group")
    header = dcc.Markdown(f"↓ A **{group}** is selected ↓", style=SELECTION_OUTPUT_HEADER_STYLE)
    columns = data.keys()
    data_table = dash_table.DataTable(
        data=[data], columns=[{"name": key, "id": key} for key in columns], editable=False
    )
    return [header, data_table]

# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any

from dash import Input, Output, State, callback, dash_table
from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HTML,
)
from power_grid_model_ds._core.visualizer.typing import VizToComponentData


@callback(
    Output("selection-output", "children"),
    Input("cytoscape-graph", "selectedNodeData"),
    Input("cytoscape-graph", "selectedEdgeData"),
    State("viz-to-comp-store", "data"),
)
def display_selected_element(
    node_data: list[dict[str, Any]], edge_data: list[dict[str, Any]], viz_to_comp: VizToComponentData
):
    """Display the tapped edge data."""
    if node_data:
        elm_id_str = node_data.pop()["id"]
        return _to_data_table(viz_to_comp[elm_id_str][ComponentType.node][0])
    if edge_data:
        elm_id_str = edge_data.pop()["id"]
        return _to_data_table(viz_to_comp[elm_id_str][ComponentType.node][0])
    return SELECTION_OUTPUT_HTML.children


def _to_data_table(data: dict[str, Any]):
    columns = data.keys()
    data_table = dash_table.DataTable(  # type: ignore[attr-defined]
        data=[data], columns=[{"name": key, "id": key} for key in columns], editable=False
    )
    return data_table

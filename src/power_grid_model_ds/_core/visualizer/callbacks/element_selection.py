# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any

from dash import Input, Output, callback, dash_table

from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HTML,
)
from power_grid_model_ds._core.visualizer.parsing_utils import PGM_ID_KEY

# Keys used in the visualization elements that are not part of the component data
VISUALIZATION_KEYS = ["id", "label", "group", "position", "parent", "source", "target"]


@callback(
    Output("selection-output", "children"),
    Input("cytoscape-graph", "selectedNodeData"),
    Input("cytoscape-graph", "selectedEdgeData"),
)
def display_selected_element(node_data: list[dict[str, Any]], edge_data: list[dict[str, Any]]):
    """Display the tapped edge data."""
    # 0th element means data for only a single selection is shown
    if node_data:
        selected_data = node_data.pop()
    elif edge_data:
        selected_data = edge_data.pop()
    else:
        return SELECTION_OUTPUT_HTML.children

    elm_data = {k: v for k, v in selected_data.items() if k not in VISUALIZATION_KEYS}

    return _to_data_table(elm_data)


def _to_data_table(data: dict[str, Any]):
    data["id"] = data[PGM_ID_KEY]
    del data[PGM_ID_KEY]
    columns = list(data.keys())

    # Ensure "id" column is first
    columns.remove("id")
    columns.insert(0, "id")

    data_table = dash_table.DataTable(  # type: ignore[attr-defined]
        data=[data], columns=[{"name": key, "id": key} for key in columns], editable=False, fill_width=False
    )
    return data_table

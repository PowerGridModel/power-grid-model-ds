# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from typing import Any

from dash import Input, Output, callback, dash_table

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HTML,
)
from power_grid_model_ds._core.visualizer.parsing_utils import viz_id_to_pgm_id
from power_grid_model_ds._core.visualizer.server_state import get_grid
from power_grid_model_ds.arrays import IdArray


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

    group = selected_data["group"]
    pgm_id = viz_id_to_pgm_id(selected_data["id"])

    grid: Grid = get_grid()
    array_data = getattr(grid, group).get(id=pgm_id)

    return _to_data_table(array_data)


def _to_data_table(array_data: IdArray):
    array_data_dict = {}
    for column in array_data.columns:
        array_data_dict[column] = array_data[column].item()

    # ignore[attr-defined] added for https://github.com/plotly/dash/issues/3226
    data_table = dash_table.DataTable(  # type: ignore[attr-defined]
        data=[array_data_dict],
        columns=[{"name": key, "id": key} for key in array_data_dict],
        editable=False,
        fill_width=False,
    )
    return data_table

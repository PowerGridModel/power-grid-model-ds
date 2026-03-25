# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from typing import Any
from venv import logger

from dash import Input, Output, callback, dash_table, html

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HTML,
)
from power_grid_model_ds._core.visualizer.server_state import get_grid
from power_grid_model_ds.arrays import IdArray


@callback(
    Output("selection-output", "children"),
    Input("cytoscape-graph", "selectedNodeData"),
    Input("cytoscape-graph", "selectedEdgeData"),
)
def display_selected_element(node_data: list[dict[str, Any]], edge_data: list[dict[str, Any]]):
    """Display the tapped edge data."""
    if not node_data and not edge_data:
        return SELECTION_OUTPUT_HTML.children

    # Extract the associated pgm_ids for all selected nodes and edges, grouped by component type
    items_to_visualize: dict[str, list[int]] = {}
    for node_edge_data in [node_data, edge_data]:
        if node_edge_data is None:
            continue
        for elm in node_edge_data:
            for group, pgm_ids in elm["associated_ids"].items():
                if group not in items_to_visualize:
                    items_to_visualize[group] = []
                items_to_visualize[group].extend(pgm_ids)

    grid: Grid = get_grid()

    tables: list[html.H5 | html.Div] = []
    for comp_type, ids in items_to_visualize.items():
        # Select unique as multiple selected elements can be connected to the same component
        # (e.g. appliance and node selected together, branch3 edges selected together)
        unique_ids = list(set(ids))
        data = getattr(grid, comp_type).filter(id=unique_ids)
        tables.append(html.H5(comp_type, style={"marginTop": "15px", "textAlign": "left"}))
        tables.append(_to_data_table(data))

    return html.Div(children=tables, style={"overflowX": "scroll", "margin": "10px"}).children


def _to_data_table(array_data: IdArray):
    list_array_data = []
    for entry in array_data:
        record_dict = {}
        for col in array_data.columns:
            if entry[col].ndim == 1:
                record_dict[col] = entry[col].item()
            else:
                logger.warning(f"Column '{col}' in group '{array_data.name}' is not 1-dimensional. Skipping search.")

        list_array_data.append(record_dict)

    # ignore[attr-defined] added for https://github.com/plotly/dash/issues/3226
    data_table = dash_table.DataTable(  # type: ignore[attr-defined]
        data=list_array_data,
        columns=[{"name": key, "id": key} for key in list_array_data[0]],
        editable=False,
        fill_width=False,
    )
    return html.Div(data_table)

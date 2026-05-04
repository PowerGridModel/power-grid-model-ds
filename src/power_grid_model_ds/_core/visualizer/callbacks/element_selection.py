# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from typing import Any

import dash_ag_grid as dag
import numpy as np
import plotly.graph_objects as go
from dash import ALL, Input, Output, callback, callback_context
from power_grid_model import ComponentType

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.grid_utils import get_attr_data_from_dataset
from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HTML,
)
from power_grid_model_ds._core.visualizer.parsing_utils import viz_id_to_pgm_id
from power_grid_model_ds._core.visualizer.server_state import get_grid, get_output_data, get_update_data
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

    return _to_data_table(array_data, group)


def _to_data_table(array_data: IdArray, group):
    data_table_headers: list[dict[str, str]] = [{"field": col, "headerName": col} for col in array_data.columns]

    list_array_data = []
    for entry in array_data:
        record_dict = {}
        for col in array_data.columns:
            if entry[col].ndim == 1:
                record_dict[col] = entry[col].item()
            else:
                record_dict[col] = entry[col].tolist().pop()

        list_array_data.append(record_dict)

    # ignore[attr-defined] added for https://github.com/plotly/dash/issues/3226
    return dag.AgGrid(  # type: ignore[attr-defined]
        id={"type": "selection-table", "group": group},
        getRowId="params.data.id",
        rowData=list_array_data,
        columnDefs=data_table_headers,
        defaultColDef={"filter": True},
        dashGridOptions={"maintainColumnOrder": True, "animateRows": False},
        columnSize="sizeToFit",
    )


@callback(
    Output("selection-graph", "figure"),
    Output("selection-graph", "style"),
    # Input({"type": "selection-table", "group": ALL}, "cellDoubleClicked"),  # Capture change
    Input({"type": "selection-table", "group": ALL}, "cellClicked"),  # Capture change
    prevent_initial_call=True,
)
def cell_selection_graph(_):
    """Update graph when a cell is clicked."""
    # Search last triggered object with cellClicked  value
    triggered_ctx = callback_context.triggered[0]
    if not (
        "selection-table" in triggered_ctx["prop_id"]
        and "cellClicked" in triggered_ctx["prop_id"]
        and triggered_ctx["value"] is not None
        and callback_context.triggered_id is not None
    ):
        return go.Figure(), {"display": "none"}

    group = callback_context.triggered_id["group"]
    pgm_id = np.int32(triggered_ctx["value"]["rowId"])
    column_id = triggered_ctx["value"]["colId"]

    x_array, y_array = _get_y_data_for_cell_selection(ComponentType(group), int(pgm_id), column_id)

    if x_array is None or y_array is None:
        return go.Figure(), {"display": "none"}

    fig = go.Figure()
    if y_array.ndim == 1:
        fig.add_trace(
            go.Scatter(
                x=x_array,
                y=y_array,
                mode="lines",
                line={"width": 2},
            )
        )
    else:
        for i, color in zip(range(y_array.shape[1]), ["red", "green", "blue"], strict=True):
            fig.add_trace(
                go.Scatter(
                    x=x_array,
                    y=y_array[:, i],
                    mode="lines",
                    line={"width": 2, "color": color},
                    name=f"{column_id}_phase_{i}",
                )
            )

    fig.update_layout(
        title=f"{group} - {column_id} - id={pgm_id}",
        xaxis_title="Scenario Index",
        yaxis_title=column_id,
        template="plotly_white",
        hovermode="x unified",
        showlegend=False,
    )

    return fig, {"display": "block"}


def _get_y_data_for_cell_selection(
    comp_type: ComponentType, pgm_id: int, attr: str
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """Extract data from update_data or output_data"""
    update_data = get_update_data()
    if update_data is not None and comp_type in update_data:
        update_names = update_data[comp_type].dtype.names
        if update_names is not None and attr in update_names:
            x_data, y_data = get_attr_data_from_dataset(update_data, comp_type, attr, pgm_id)
            return x_data, y_data
    output_data = get_output_data()
    if output_data is not None and comp_type in output_data:
        output_names = output_data[comp_type].dtype.names
        if output_names is not None and attr in output_names:
            x_data, y_data = get_attr_data_from_dataset(output_data, comp_type, attr, pgm_id)
            return x_data, y_data
    return None, None

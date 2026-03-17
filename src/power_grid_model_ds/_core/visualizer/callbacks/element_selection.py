# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


from typing import Any

import numpy as np
import plotly.graph_objects as go
from dash import ALL, Input, Output, callback, callback_context, dash_table, html
from power_grid_model import ComponentType

from power_grid_model_ds._core.model.arrays.pgm_arrays import IdArray
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.grid_utils import get_attr_data_from_dataset
from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HTML,
)
from power_grid_model_ds._core.visualizer.server_state import (
    safe_get_grid,
    safe_get_output_data,
    safe_get_update_data,
)


@callback(
    Output("selection-output", "children"),
    Input("cytoscape-graph", "selectedNodeData"),
    Input("cytoscape-graph", "selectedEdgeData"),
    Input("cytoscape-graph", "elements"),
)
def display_selected_element(
    node_data: list[dict[str, Any]],
    edge_data: list[dict[str, Any]],
    _,
):
    """Display the tapped edge data."""
    if not node_data and not edge_data:
        return SELECTION_OUTPUT_HTML.children

    # Extract the associated pgm_ids for all selected nodes and edges, grouped by component type
    selected_data: dict[str, list[int]] = {}
    for data in [node_data, edge_data]:
        if data is None:
            continue
        for elm in data:
            for group, pgm_ids in elm["associated_ids"].items():
                if group not in selected_data:
                    selected_data[group] = []
                selected_data[group].extend(pgm_ids)

    grid: Grid = safe_get_grid()

    tables: list[html.H5 | html.Div] = []
    for comp_type, ids in selected_data.items():
        # Select unique as multiple selected elements can be connected to the same component
        # (e.g. appliance and node selected together, branch3 edges selected together)
        unique_ids = list(set(ids))
        data = getattr(grid, comp_type).filter(id=unique_ids)
        tables.append(html.H5(comp_type, style={"marginTop": "15px", "textAlign": "left"}))
        tables.append(_array_to_data_tables(data, comp_type))

    return html.Div(children=tables, style={"overflowX": "scroll", "margin": "10px"}).children


def _array_to_data_tables(array_data: IdArray, group: str) -> html.Div:
    """Convert array data to a Dash DataTable.
    Makes 3 phase data into separate columns with suffix _a, _b, _c"""
    list_array_data = []
    for entry in array_data:
        record_dict = {}
        for col in array_data.columns:
            if entry[col].ndim == 1:
                record_dict[col] = entry[col].item()
            else:
                assert entry[col].ndim == 2 and entry[col].shape[1] == 3
                for phase_idx, phase in enumerate(["a", "b", "c"]):
                    col_name = f"{col}_{phase}"
                    record_dict[col_name] = entry[col][0, phase_idx]
        list_array_data.append(record_dict)

    data_table_headers = []
    for col in array_data.columns:
        if array_data[col].ndim == 1:
            data_table_headers.append({"name": col, "id": col})
        else:
            for phase in ["a", "b", "c"]:
                col_name = f"{col}_{phase}"
                data_table_headers.append({"name": col_name, "id": col_name})

    data_table = dash_table.DataTable(  # type: ignore[attr-defined]
        id={"type": "selection-table", "group": group},
        data=list_array_data,
        columns=data_table_headers,
        editable=False,
        fill_width=False,
    )
    return html.Div(data_table)


@callback(
    Output("selection-graph", "figure"),
    Output("selection-graph", "style"),
    Input({"type": "selection-table", "group": ALL}, "active_cell"),  # Capture change
    prevent_initial_call=True,
)
def handle_cell_selection(_):
    """Update graph when a cell is clicked."""
    # Search last triggered objectect with active_cell value
    triggered_ctx = callback_context.triggered[0]
    if not (
        "selection-table" in triggered_ctx["prop_id"]
        and "active_cell" in triggered_ctx["prop_id"]
        and triggered_ctx["value"] is not None
        and callback_context.triggered_id is not None
    ):
        return go.Figure(), {"display": "none"}

    group = callback_context.triggered_id["group"]
    pgm_id = triggered_ctx["value"]["row_id"]
    column_id = triggered_ctx["value"]["column_id"]

    # Address the case where column_id ends with a phase suffix (e.g. "_a", "_b", "_c")
    if any(column_id.endswith(phase_suffix) for phase_suffix in ["_a", "_b", "_c"]):
        base_column = column_id[:-2]
        phase_idx = {"_a": 0, "_b": 1, "_c": 2}[column_id[-2:]]
    else:
        base_column = column_id
        phase_idx = None

    x_array, y_array, data_type = _get_y_data_for_cell_selection(ComponentType(group), pgm_id, base_column)

    if x_array is None or y_array is None or data_type is None:
        return go.Figure(), {"display": "none"}

    y_data = y_array[:, phase_idx].tolist() if phase_idx is not None else y_array.tolist()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_array.tolist(),
            y=y_data,
            mode="lines",
            line={"width": 2},
        )
    )

    fig.update_layout(
        title=f"{data_type} - {group} - {column_id} - id={pgm_id}",
        xaxis_title="Scenario Index",
        yaxis_title=column_id,
        template="plotly_white",
        hovermode="x unified",
        showlegend=False,
    )

    return fig, {"display": "block"}


def _get_y_data_for_cell_selection(
    comp_type: ComponentType, pgm_id: int, attr: str
) -> tuple[np.ndarray | None, np.ndarray | None, str | None]:
    """Extract data from update_data or output_data"""
    update_data = safe_get_update_data()
    if update_data is not None and comp_type in update_data and attr in update_data[comp_type].dtype.names:
        x_data, y_data = get_attr_data_from_dataset(update_data, comp_type, attr, pgm_id)
        return x_data, y_data, "update_data"
    output_data = safe_get_output_data()
    if output_data is not None and comp_type in output_data and attr in output_data[comp_type].dtype.names:
        x_data, y_data = get_attr_data_from_dataset(output_data, comp_type, attr, pgm_id)
        return x_data, y_data, "output_data"
    return None, None, None

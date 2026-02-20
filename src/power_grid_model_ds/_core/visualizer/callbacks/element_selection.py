# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0


import numpy as np
import plotly.graph_objects as go
from dash import ALL, Input, Output, State, callback, callback_context, dash_table, html
from power_grid_model import ComponentType, attribute_empty_value
from power_grid_model._core.dataset_definitions import DatasetType

from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HTML,
)
from power_grid_model_ds._core.visualizer.server_state import (
    safe_get_grid,
    safe_get_output_data,
    safe_get_update_data,
)
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
    tables.append(_array_to_data_tables(data, group))

    if elm_id_str in viz_to_comp:
        for comp_type, non_visible_ids in viz_to_comp[elm_id_str].items():
            data = getattr(grid, comp_type).filter(id=non_visible_ids)
            tables.append(html.H5(comp_type, style={"marginTop": "15px", "textAlign": "left"}))
            tables.append(_array_to_data_tables(data, comp_type))

    return html.Div(children=tables, style={"overflowX": "scroll", "margin": "10px"}).children


def _array_to_data_tables(array_data, group: str) -> html.Div:
    """Convert array data to a Dash DataTable."""
    list_array_data = [{col: entry[col].item() for col in array_data.columns} for entry in array_data]
    columns = [{"name": key, "id": key} for key in array_data.columns]

    data_table = dash_table.DataTable(  # type: ignore[attr-defined]
        id={"type": "selection-table", "group": group},
        data=list_array_data,
        columns=columns,
        editable=False,
        fill_width=False,
    )
    return html.Div(data_table)


@callback(
    Output({"type": "selection-table", "group": ALL}, "active_cell"),
    Output({"type": "selection-table", "group": ALL}, "selected_cells"),
    Output("selection-graph", "figure"),
    Output("selection-graph", "style"),
    Input({"type": "selection-table", "group": ALL}, "active_cell"),
    State({"type": "selection-table", "group": ALL}, "id"),
    prevent_initial_call=True,
)
def handle_cell_selection(active_cells, table_ids):
    """Clear other selections and update graph when a cell is clicked."""
    ctx = callback_context
    triggered_table_id = ctx.triggered_id

    # Find triggered table index
    cell_number = table_ids.index(triggered_table_id)
    active_cell = active_cells[cell_number]

    # Clear other selections
    active_output = [None] * len(table_ids)
    active_output[cell_number] = active_cell

    selected_output = [[] for _ in table_ids]
    if active_cell:
        selected_output[cell_number] = [active_cell]

    empty_return = (active_output, selected_output, go.Figure(), {"display": "none"})

    if active_cell is None or "row_id" not in active_cell or "column_id" not in active_cell:
        return empty_return

    group = table_ids[cell_number]["group"]
    element_id = active_cell["row_id"]
    column_id = active_cell["column_id"]

    y_data, data_type = _get_y_data_for_cell_selection(group, element_id, column_id)
    if y_data is None or data_type is None:
        return empty_return

    # Create the graph
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(len(y_data))),
            y=y_data,
            mode="lines",
            line={"width": 2},
        )
    )

    fig.update_layout(
        title=f"{data_type.value} - {group} - {column_id} - id={element_id}",
        xaxis_title="Scenario Index",
        yaxis_title=column_id,
        template="plotly_white",
        hovermode="x unified",
        showlegend=False,
    )

    return active_output, selected_output, fig, {"display": "block"}


def _get_y_data_for_cell_selection(
    group: str, element_id: int, column_id: str
) -> tuple[list | None, DatasetType | None]:
    # Extract data from update_data or output_data
    update_data = safe_get_update_data()
    output_data = safe_get_output_data()

    if update_data is not None and group in update_data and column_id in update_data[group].dtype.names:
        data_type = DatasetType.update
        empty_val = attribute_empty_value(DatasetType.update, ComponentType(group), column_id)
        id_column = update_data[group]["id"]
        column_data = update_data[group][column_id]
    elif output_data is not None and group in output_data and column_id in output_data[group].dtype.names:
        data_type = DatasetType.sym_output
        empty_val = attribute_empty_value(DatasetType.sym_output, ComponentType(group), column_id)
        id_column = output_data[group]["id"]
        column_data = output_data[group][column_id]
    else:
        return None, None

    if np.all(column_data == empty_val) or element_id not in id_column:
        return None, None

    element_idx = np.nonzero(id_column[0] == element_id)[0][0]
    y_data = column_data[:, element_idx].tolist()
    return y_data, data_type

# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any

import dash_ag_grid as dag
import numpy as np
import plotly.graph_objects as go
from dash import ALL, Input, Output, callback, callback_context, html, no_update
from power_grid_model import ComponentType

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.grid_utils import get_attr_data_from_dataset
from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HTML,
)
from power_grid_model_ds._core.visualizer.measurement_comparison import (
    VoltageComparison,
    get_symmetric_voltage_comparison,
    get_voltage_sigma_bounds,
)
from power_grid_model_ds._core.visualizer.server_state import get_grid, get_output_data, get_update_data
from power_grid_model_ds.arrays import IdArray


@callback(
    Output("selection-output", "children"),
    Input("cytoscape-graph", "selectedNodeData"),
    Input("cytoscape-graph", "selectedEdgeData"),
)
def display_selected_elements(node_data: list[dict[str, Any]], edge_data: list[dict[str, Any]]):
    """Display the selected elements and their associated components."""
    if not node_data and not edge_data:
        return SELECTION_OUTPUT_HTML.children

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

    tables: list[html.H5 | dag.AgGrid] = []

    for comp_type, ids in items_to_visualize.items():
        unique_ids = list(set(ids))
        data = getattr(grid, comp_type).filter(id=unique_ids)

        tables.append(
            html.H5(
                comp_type,
                style={"marginTop": "15px", "textAlign": "left"},
            )
        )
        tables.append(_to_data_table(array_data=data, group=comp_type))

    return tables


def _to_data_table(array_data: IdArray, group):
    """Convert component attributes into an AG Grid table."""
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

    return dag.AgGrid(  # type: ignore[attr-defined]
        id={"type": "selection-table", "group": group},
        getRowId="params.data.id",
        rowData=list_array_data,
        columnDefs=data_table_headers,
        defaultColDef={"filter": True},
        dashGridOptions={
            "maintainColumnOrder": True,
            "animateRows": False,
        },
        columnSize="sizeToFit",
    )


def _create_voltage_comparison_figure(
    comparison: VoltageComparison,
    sensor_id: int,
    sigma_multiplier: float = 2.0,
) -> go.Figure:
    """Plot measured and calculated voltages with measurement-centred bands."""
    lower, upper = get_voltage_sigma_bounds(
        comparison,
        sigma_multiplier,
    )

    fig = go.Figure()

    # Draw the uncertainty interval behind the voltage series.
    fig.add_trace(
        go.Scatter(
            x=comparison.scenario_indices,
            y=lower,
            mode="lines",
            line={"width": 0},
            showlegend=False,
            hoverinfo="skip",
            name="Lower sigma bound",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=comparison.scenario_indices,
            y=upper,
            mode="lines",
            line={"width": 0},
            fill="tonexty",
            fillcolor="rgba(100, 149, 237, 0.20)",
            name=f"Measurement +/- {sigma_multiplier:g} sigma",
            hoverinfo="skip",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=comparison.scenario_indices,
            y=comparison.measured,
            mode="lines",
            name="Measured voltage",
            line={"width": 2, "color": "royalblue"},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=comparison.scenario_indices,
            y=comparison.estimated,
            mode="lines",
            name="Calculated voltage",
            line={"width": 2, "color": "darkorange", "dash": "dash"},
        )
    )

    fig.update_layout(
        title=f"sym_voltage_sensor - voltage comparison - id={sensor_id}",
        xaxis_title="Scenario Index",
        yaxis_title="Voltage (V)",
        template="plotly_white",
        hovermode="x unified",
        showlegend=True,
    )

    return fig


@callback(
    Output("selected-selection-cell", "data"),
    Input({"type": "selection-table", "group": ALL}, "cellClicked"),
    Input("cytoscape-graph", "selectedNodeData"),
    Input("cytoscape-graph", "selectedEdgeData"),
    prevent_initial_call=True,
)
def store_selected_cell(_, _node_data, _edge_data):
    """Remember a selected cell and clear it when network selection changes."""
    triggered_id = callback_context.triggered_id

    # The displayed component tables may change with the network selection.
    # Clear the previous cell so its graph is not shown for a new selection.
    if triggered_id == "cytoscape-graph":
        return None

    triggered = callback_context.triggered

    if (
        not triggered
        or not isinstance(triggered_id, dict)
        or "selection-table" not in triggered[0]["prop_id"]
        or "cellClicked" not in triggered[0]["prop_id"]
    ):
        return no_update

    value = triggered[0]["value"]
    group = triggered_id.get("group")

    if not isinstance(value, dict) or not isinstance(group, str):
        return no_update

    try:
        component_type = ComponentType(group)
        component_id = int(value["rowId"])
        column_id = value["colId"]
    except (KeyError, TypeError, ValueError):
        return no_update

    if not isinstance(column_id, str):
        return no_update

    return {
        "group": component_type.value,
        "id": component_id,
        "column": column_id,
    }


@callback(
    Output("selection-graph", "figure"),
    Output("selection-graph", "style"),
    Output("sigma-multiplier-controls", "style"),
    Input("selected-selection-cell", "data"),
    Input("sigma-multiplier", "value"),
    Input("cytoscape-graph", "selectedNodeData"),
    Input("cytoscape-graph", "selectedEdgeData"),
    prevent_initial_call=True,
)
def cell_selection_graph(
    selected_cell,
    sigma_multiplier,
    node_data=None,
    edge_data=None,
):
    """Render the selected attribute with optional voltage sigma bands."""
    hidden = {"display": "none"}
    visible = {"display": "block"}

    # Hide the graph when Cytoscape has no selected node or edge.
    # The default arguments preserve existing direct unit-test calls.
    if not isinstance(selected_cell, dict) or (
        (node_data is not None or edge_data is not None) and not node_data and not edge_data
    ):
        return go.Figure(), hidden, hidden

    try:
        group = selected_cell["group"]
        comp_type = ComponentType(group)
        pgm_id = int(selected_cell["id"])
        column_id = selected_cell["column"]

        if not isinstance(column_id, str):
            raise ValueError("Invalid selected column")

    except (KeyError, TypeError, ValueError):
        return go.Figure(), hidden, hidden

    if comp_type == ComponentType.sym_voltage_sensor and column_id == "u_measured":
        output_data = get_output_data()

        if output_data is not None and ComponentType.node in output_data:
            node_output = output_data[ComponentType.node]

            # Only dense, symmetric node output has one scalar voltage per node.
            is_symmetric_batch = (
                isinstance(node_output, np.ndarray)
                and node_output.ndim == len(("scenario", "component"))
                and node_output.dtype.names is not None
                and {"id", "u"}.issubset(node_output.dtype.names)
                and node_output.dtype.fields["u"][0].subdtype is None
            )

            if is_symmetric_batch:
                if (
                    not isinstance(sigma_multiplier, (int, float))
                    or not np.isfinite(sigma_multiplier)
                    or sigma_multiplier < 0
                ):
                    return go.Figure(), hidden, visible

                comparison = get_symmetric_voltage_comparison(
                    grid=get_grid(),
                    update_data=get_update_data(),
                    output_data=output_data,
                    sensor_id=pgm_id,
                )

                fig = _create_voltage_comparison_figure(
                    comparison,
                    sensor_id=pgm_id,
                    sigma_multiplier=float(sigma_multiplier),
                )

                return fig, visible, visible

    # Preserve existing behaviour for other component attributes.
    x_array, y_array = _get_y_data_for_cell_selection(
        comp_type,
        pgm_id,
        column_id,
    )

    if x_array is None or y_array is None:
        return go.Figure(), hidden, hidden

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
        for i, color in zip(
            range(y_array.shape[1]),
            ["red", "green", "blue"],
            strict=True,
        ):
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

    return fig, visible, hidden


def _get_y_data_for_cell_selection(
    comp_type: ComponentType,
    pgm_id: int,
    attr: str,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """Extract the selected attribute from update or output data."""
    update_data = get_update_data()

    if update_data is not None and comp_type in update_data:
        update_names = update_data[comp_type].dtype.names

        if update_names is not None and attr in update_names:
            x_data, y_data = get_attr_data_from_dataset(
                update_data,
                comp_type,
                attr,
                pgm_id,
            )
            return x_data, y_data

    output_data = get_output_data()

    if output_data is not None and comp_type in output_data:
        output_names = output_data[comp_type].dtype.names

        if output_names is not None and attr in output_names:
            x_data, y_data = get_attr_data_from_dataset(
                output_data,
                comp_type,
                attr,
                pgm_id,
            )
            return x_data, y_data

    return None, None

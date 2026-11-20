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
from power_grid_model_ds._core.visualizer.comparison_plot import create_measurement_comparison_figure
from power_grid_model_ds._core.visualizer.grid_utils import get_attr_data_from_dataset
from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_OUTPUT_HTML,
)
from power_grid_model_ds._core.visualizer.measurement_comparison import (
    DENSE_BATCH_NDIM,
    VoltageComparison,
    get_symmetric_power_comparison,
    get_symmetric_voltage_comparison,
)
from power_grid_model_ds._core.visualizer.server_state import get_grid, get_output_data, get_update_data
from power_grid_model_ds.arrays import IdArray

_HIDDEN_GRAPH_STYLE = {"display": "none"}
_VISIBLE_GRAPH_STYLE = {"display": "block"}


@callback(
    Output("selection-output", "children"),
    Input("cytoscape-graph", "selectedNodeData"),
    Input("cytoscape-graph", "selectedEdgeData"),
)
def display_selected_elements(node_data: list[dict[str, Any]], edge_data: list[dict[str, Any]]):
    """Display selected nodes, edges, and their associated components."""
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
    tables: list[html.H5 | dag.AgGrid] = []
    for comp_type, ids in items_to_visualize.items():
        # Select unique as multiple selected elements can be connected to the same component
        # (e.g. appliance and node selected together, branch3 edges selected together)
        unique_ids = list(set(ids))
        data = getattr(grid, comp_type).filter(id=unique_ids)
        tables.append(html.H5(comp_type, style={"marginTop": "15px", "textAlign": "left"}))
        tables.append(_to_data_table(array_data=data, group=comp_type))

    return tables


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


def _create_voltage_comparison_figure(
    comparison: VoltageComparison,
    sensor_id: int,
    sigma_multiplier: float = 2.0,
) -> go.Figure:
    """Preserve the existing voltage presentation via the shared plotter."""
    return create_measurement_comparison_figure(
        comparison,
        title=f"sym_voltage_sensor - voltage comparison - id={sensor_id}",
        quantity="voltage",
        unit="V",
        sigma_multiplier=sigma_multiplier,
    )


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


def _is_dense_batch_array(component_data: Any) -> bool:
    """Whether component data uses the dense array representation supported by the selector."""
    return isinstance(component_data, np.ndarray) and component_data.ndim == DENSE_BATCH_NDIM


def _require_explicit_ids(component_data: np.ndarray) -> None:
    """Reject dense batch arrays with unsupported implicit component IDs."""
    if component_data.dtype.names is None or "id" not in component_data.dtype.names:
        raise NotImplementedError("Batch data without explicit component IDs are not implemented.")


def _voltage_comparison_graph(sensor_id: int, sigma_multiplier: float | None):
    """Build a voltage comparison for compatible symmetric node output."""
    hidden = {"display": "none"}
    visible = {"display": "block"}
    output_data = get_output_data()
    if output_data is None or ComponentType.node not in output_data:
        return None

    node_output = output_data[ComponentType.node]
    if not _is_dense_batch_array(node_output):
        return None

    node_fields = node_output.dtype.fields
    if node_fields is None or "u" not in node_fields or node_fields["u"][0].subdtype is not None:
        return None
    _require_explicit_ids(node_output)

    update_data = get_update_data()
    if update_data is not None and ComponentType.sym_voltage_sensor in update_data:
        sensor_updates = update_data[ComponentType.sym_voltage_sensor]
        if not _is_dense_batch_array(sensor_updates):
            return None
        _require_explicit_ids(sensor_updates)

    if not isinstance(sigma_multiplier, (int, float)) or not np.isfinite(sigma_multiplier) or sigma_multiplier < 0:
        return go.Figure(), hidden, visible

    comparison = get_symmetric_voltage_comparison(
        grid=get_grid(),
        update_data=update_data,
        output_data=output_data,
        sensor_id=sensor_id,
    )
    fig = _create_voltage_comparison_figure(
        comparison,
        sensor_id=sensor_id,
        sigma_multiplier=float(sigma_multiplier),
    )
    return fig, visible, visible


def _power_comparison_graph(  # noqa: PLR0911  # pylint: disable=too-many-return-statements
    sensor_id: int, measurement_attribute: str, sigma_multiplier: float | None
):
    """Build a source-terminal power comparison when calculated output is available."""
    output_data = get_output_data()
    if output_data is None or ComponentType.source not in output_data:
        return None
    source_output = output_data[ComponentType.source]
    if not _is_dense_batch_array(source_output):
        return None
    field = measurement_attribute[0]
    if source_output.dtype.fields is None or field not in source_output.dtype.fields:
        return None
    if source_output.dtype.fields[field][0].subdtype is not None:
        return None
    _require_explicit_ids(source_output)

    update_data = get_update_data()
    if update_data is not None and ComponentType.sym_power_sensor in update_data:
        updates = update_data[ComponentType.sym_power_sensor]
        if not _is_dense_batch_array(updates):
            return None
        _require_explicit_ids(updates)

    if not isinstance(sigma_multiplier, (int, float)) or not np.isfinite(sigma_multiplier) or sigma_multiplier < 0:
        return go.Figure(), _HIDDEN_GRAPH_STYLE, _VISIBLE_GRAPH_STYLE

    try:
        comparison = get_symmetric_power_comparison(
            grid=get_grid(),
            update_data=update_data,
            output_data=output_data,
            sensor_id=sensor_id,
            measurement_attribute=measurement_attribute,
        )
    except NotImplementedError:
        # An unsupported terminal must not be displayed as source power.
        return None

    quantity = "active power" if measurement_attribute == "p_measured" else "reactive power"
    unit = "W" if measurement_attribute == "p_measured" else "var"
    figure = create_measurement_comparison_figure(
        comparison,
        title=f"sym_power_sensor - {quantity} comparison - id={sensor_id}",
        quantity=quantity,
        unit=unit,
        sigma_multiplier=float(sigma_multiplier),
    )
    controls_style = _VISIBLE_GRAPH_STYLE if comparison.sigma is not None else _HIDDEN_GRAPH_STYLE
    return figure, _VISIBLE_GRAPH_STYLE, controls_style


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
    """Render the selected attribute with optional measurement sigma bands."""

    # Hide the graph when Cytoscape has no selected node or edge.
    # The default arguments preserve existing direct unit-test calls.
    if not isinstance(selected_cell, dict) or (
        (node_data is not None or edge_data is not None) and not node_data and not edge_data
    ):
        return go.Figure(), _HIDDEN_GRAPH_STYLE, _HIDDEN_GRAPH_STYLE

    try:
        group = selected_cell["group"]
        comp_type = ComponentType(group)
        pgm_id = int(selected_cell["id"])
        column_id = selected_cell["column"]

        if not isinstance(column_id, str):
            raise ValueError("Invalid selected column")

    except (KeyError, TypeError, ValueError):
        return go.Figure(), _HIDDEN_GRAPH_STYLE, _HIDDEN_GRAPH_STYLE

    if comp_type == ComponentType.sym_voltage_sensor and column_id == "u_measured":
        voltage_result = _voltage_comparison_graph(pgm_id, sigma_multiplier)
        if voltage_result is not None:
            return voltage_result

    if comp_type == ComponentType.sym_power_sensor and column_id in ("p_measured", "q_measured"):
        power_result = _power_comparison_graph(pgm_id, column_id, sigma_multiplier)
        if power_result is not None:
            return power_result

    # Preserve existing behaviour for other component attributes.
    x_array, y_array = _get_y_data_for_cell_selection(
        comp_type,
        pgm_id,
        column_id,
    )

    if x_array is None or y_array is None:
        return go.Figure(), _HIDDEN_GRAPH_STYLE, _HIDDEN_GRAPH_STYLE

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

    return fig, _VISIBLE_GRAPH_STYLE, _HIDDEN_GRAPH_STYLE


def _get_y_data_for_cell_selection(
    comp_type: ComponentType, pgm_id: int, attr: str
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """Extract the selected attribute from supported dense update or output data."""
    for dataset in (get_update_data(), get_output_data()):
        if dataset is None or comp_type not in dataset:
            continue
        component_data = dataset[comp_type]
        if not _is_dense_batch_array(component_data):
            continue
        names = component_data.dtype.names
        if names is not None and "id" in names and attr in names:
            return get_attr_data_from_dataset(dataset, comp_type, attr, pgm_id)
    return None, None

# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Component selection, scenario-aware tables, and attribute graphs."""

from typing import Any

import dash_ag_grid as dag
import numpy as np
import plotly.graph_objects as go
from dash import ALL, Input, Output, callback, callback_context, html
from power_grid_model import ComponentType

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.grid_utils import get_attr_data_from_dataset
from power_grid_model_ds._core.visualizer.layout.selection_output import SELECTION_OUTPUT_HTML
from power_grid_model_ds._core.visualizer.scenario_selection import (
    get_component_state,
    get_effective_component_state,
    get_scenario_count,
)
from power_grid_model_ds._core.visualizer.server_state import get_grid, get_output_data, get_update_data
from power_grid_model_ds.arrays import IdArray

OUTPUT_PREFIX = "output__"
SCALAR_ARRAY_DIMENSIONS = 2
COLUMN_WIDTH = 170
OUTPUT_COLUMN_WIDTH = 200
PHASE_COLORS = ("red", "green", "blue")


def _selected_ids(
    node_data: list[dict[str, Any]] | None,
    edge_data: list[dict[str, Any]] | None,
) -> dict[str, list[int]]:
    """Resolve selections while preserving component and ID order."""
    selected: dict[str, list[int]] = {}
    for element in (node_data or []) + (edge_data or []):
        for group, ids in element.get("associated_ids", {}).items():
            selected.setdefault(group, [])
            for component_id in ids:
                if component_id not in selected[group]:
                    selected[group].append(component_id)
    return selected


def _to_python(value: Any) -> Any:
    """Convert NumPy values while preserving scalar and vector attributes."""
    array = np.asarray(value)
    if array.ndim == 0:
        return array.item()
    if array.ndim == 1 and array.size == 1:
        return array.item()
    if array.ndim >= SCALAR_ARRAY_DIMENSIONS and array.shape[0] == 1:
        return array[0].tolist()
    return array.tolist()


def _base_rows(array_data: IdArray) -> list[dict[str, Any]]:
    """Convert selected Grid records to ordinary independent dictionaries."""
    return [{column: _to_python(entry[column]) for column in array_data.columns} for entry in array_data]


def _scenario_rows(
    array_data: IdArray,
    group: str,
    scenario_index: int | None,
) -> list[dict[str, Any]]:
    """Build effective input rows and append selected calculation outputs."""
    rows = _base_rows(array_data)
    update_data = get_update_data()
    output_data = get_output_data()
    scenario_count = get_scenario_count(update_data, output_data)

    if scenario_count is None:
        return rows

    if (
        not isinstance(scenario_index, (int, np.integer))
        or isinstance(scenario_index, (bool, np.bool_))
        or not 0 <= scenario_index < scenario_count
    ):
        return rows

    component_type = ComponentType(group)

    for row in rows:
        component_id = int(row["id"])
        effective = get_effective_component_state(
            row,
            update_data,
            component_type,
            component_id,
            int(scenario_index),
        )
        output = (
            get_component_state(output_data, component_type, component_id, int(scenario_index))
            if output_data is not None
            else None
        )

        if output is not None:
            for attribute, value in output.items():
                if attribute != "id":
                    effective[f"{OUTPUT_PREFIX}{attribute}"] = value

        row.clear()
        row.update(effective)

    return rows


@callback(
    Output("selection-output", "children"),
    Input("cytoscape-graph", "selectedNodeData"),
    Input("cytoscape-graph", "selectedEdgeData"),
    Input("scenario-selector", "value", allow_optional=True),
)
def display_selected_elements(
    node_data: list[dict[str, Any]] | None,
    edge_data: list[dict[str, Any]] | None,
    scenario_index: int | None = None,
):
    """Refresh selected component tables when selection or scenario changes."""
    selected = _selected_ids(node_data, edge_data)
    if not selected:
        return SELECTION_OUTPUT_HTML.children

    grid: Grid = get_grid()
    tables: list[html.H5 | dag.AgGrid] = []

    for group, ids in selected.items():
        array_data = getattr(grid, group).filter(id=ids)
        rows = _scenario_rows(array_data, group, scenario_index)

        tables.append(html.H5(group, style={"marginTop": "15px", "textAlign": "left"}))
        tables.append(_to_data_table(array_data, group, rows))

    return tables


def _to_data_table(
    array_data: IdArray,
    group: str,
    rows: list[dict[str, Any]] | None = None,
):
    """Render input and output attributes with readable, scrollable columns."""
    if rows is None:
        rows = _base_rows(array_data)

    columns = list(array_data.columns)
    output_columns = sorted({key for row in rows for key in row if key.startswith(OUTPUT_PREFIX)})
    columns.extend(output_columns)

    headers = []
    for column in columns:
        is_output = column.startswith(OUTPUT_PREFIX)
        header_name = f"Output: {column.removeprefix(OUTPUT_PREFIX)}" if is_output else column

        headers.append(
            {
                "field": column,
                "headerName": header_name,
                "width": OUTPUT_COLUMN_WIDTH if is_output else COLUMN_WIDTH,
                "minWidth": 130,
                "resizable": True,
                "tooltipField": column,
                "headerTooltip": header_name,
            }
        )

    return dag.AgGrid(  # type: ignore[attr-defined]
        id={"type": "selection-table", "group": group},
        getRowId="params.data.id",
        rowData=rows,
        columnDefs=headers,
        defaultColDef={"filter": True, "resizable": True},
        dashGridOptions={
            "maintainColumnOrder": True,
            "animateRows": False,
            "suppressHorizontalScroll": False,
        },
        style={"width": "100%"},
    )


def _add_attribute_traces(
    fig: go.Figure,
    x_array: np.ndarray,
    y_array: np.ndarray,
    column_id: str,
) -> bool:
    """Add scalar or multi-series traces without assuming exactly three phases."""
    x_values = np.asarray(x_array)
    y_values = np.asarray(y_array)

    if x_values.ndim != 1 or x_values.size == 0:
        return False

    if y_values.ndim == 1:
        if y_values.size != x_values.size:
            return False

        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines",
                line={"width": 2},
            )
        )
        return True

    if y_values.ndim != SCALAR_ARRAY_DIMENSIONS or y_values.shape[0] != x_values.size or y_values.shape[1] == 0:
        return False

    for index in range(y_values.shape[1]):
        color = PHASE_COLORS[index % len(PHASE_COLORS)]
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values[:, index],
                mode="lines",
                line={"width": 2, "color": color},
                name=f"{column_id}_phase_{index}",
            )
        )

    return True


@callback(
    Output("selection-graph", "figure"),
    Output("selection-graph", "style"),
    Input({"type": "selection-table", "group": ALL}, "cellClicked"),
    prevent_initial_call=True,
)
def cell_selection_graph(_):
    """Update the attribute graph for the selected table cell."""
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

    x_array, y_array = _get_y_data_for_cell_selection(
        ComponentType(group),
        int(pgm_id),
        column_id,
    )

    if x_array is None or y_array is None:
        return go.Figure(), {"display": "none"}

    fig = go.Figure()
    if not _add_attribute_traces(fig, x_array, y_array, column_id):
        return go.Figure(), {"display": "none"}

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
    comp_type: ComponentType,
    pgm_id: int,
    attr: str,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    """Resolve output-prefixed columns and preserve existing input graph behavior."""
    output_data = get_output_data()
    update_data = get_update_data()

    if attr.startswith(OUTPUT_PREFIX):
        attribute = attr.removeprefix(OUTPUT_PREFIX)
        datasets = [output_data]
    else:
        attribute = attr
        datasets = [update_data, output_data]

    for candidate in datasets:
        if candidate is None or comp_type not in candidate:
            continue

        component_data = candidate[comp_type]

        # Existing graph extraction supports dense structured arrays only.
        if not isinstance(component_data, np.ndarray) or component_data.dtype.names is None:
            continue

        if attribute in component_data.dtype.names:
            return get_attr_data_from_dataset(candidate, comp_type, attribute, pgm_id)

    return None, None

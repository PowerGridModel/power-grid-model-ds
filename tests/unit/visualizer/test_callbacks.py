# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import dash_ag_grid as dag
import numpy as np
import pytest
from dash.exceptions import PreventUpdate
from plotly import graph_objs as go
from power_grid_model import ComponentType, initialize_array

from power_grid_model_ds._core.model.dtypes.typing import NDArray3
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer import server_state
from power_grid_model_ds._core.visualizer.callbacks.config import (
    scale_elements,
    update_arrows,
    update_layout,
)
from power_grid_model_ds._core.visualizer.callbacks.element_selection import (
    cell_selection_graph,
    display_selected_elements,
    store_selected_cell,
)
from power_grid_model_ds._core.visualizer.callbacks.search_form import (
    HIGHLIGHT_STYLE,
    search_element,
)
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
from power_grid_model_ds._core.visualizer.layout.selection_output import SELECTION_OUTPUT_HTML
from power_grid_model_ds.arrays import NodeArray

_EDGE_INDEX = 3

_CTX_PATH = "power_grid_model_ds._core.visualizer.callbacks.element_selection.callback_context"
_CALLBACK_PATH = "power_grid_model_ds._core.visualizer.callbacks.element_selection"

_NODE_SELECTION = {
    "group": "node",
    "id": 1,
    "column": "u_rated",
}

_VOLTAGE_SELECTION = {
    "group": "sym_voltage_sensor",
    "id": 101,
    "column": "u_measured",
}


class ThreePhaseNodeArray(NodeArray):
    three_phase_quantity: NDArray3[np.float64]


class ThreePhaseGrid(Grid):
    node: ThreePhaseNodeArray


def test_scale_elements():
    assert scale_elements(1.2, 1.3, DEFAULT_STYLESHEET)


def test_search_element_no_input():
    with pytest.raises(PreventUpdate):
        search_element(
            group="",
            column="",
            operator="",
            value="",
            stylesheet=DEFAULT_STYLESHEET,
        )


def test_search_element_with_asym_column():
    server_state.set_app_state(Grid.empty())

    with pytest.raises(PreventUpdate):
        search_element(
            group="asym_gen",
            column="p_specified",
            operator="=",
            value="100",
            stylesheet=DEFAULT_STYLESHEET,
        )


@pytest.mark.parametrize(
    ("group", "column", "operator", "value", "expected_selectors"),
    [
        pytest.param(
            "node",
            "id",
            "=",
            "1",
            [{"selector": "#1", "style": HIGHLIGHT_STYLE}],
            id="node id equal",
        ),
        pytest.param(
            "branches",
            "id",
            "!=",
            "12",
            [{"selector": "#23", "style": HIGHLIGHT_STYLE}],
            id="branch id not equal",
        ),
        pytest.param(
            "line",
            "from_node",
            ">",
            "1",
            [{"selector": "#23", "style": HIGHLIGHT_STYLE}],
            id="line from_node greater",
        ),
        pytest.param(
            "line",
            "to_node",
            "<",
            "10",
            [
                {"selector": "#12", "style": HIGHLIGHT_STYLE},
                {"selector": "#23", "style": HIGHLIGHT_STYLE},
            ],
            id="line to node smaller",
        ),
    ],
)
def test_search_element_with_input(
    group,
    column,
    operator,
    value,
    expected_selectors,
):
    server_state.set_app_state(Grid.from_txt("S1 2 12", "2 3 23"))

    result = search_element(
        group,
        column,
        operator,
        value,
        DEFAULT_STYLESHEET,
    )

    assert len(result) == len(DEFAULT_STYLESHEET) + len(expected_selectors)
    assert result[-len(expected_selectors) :] == expected_selectors


def test_show_arrows():
    stylesheet = update_arrows(
        show_arrows=True,
        current_stylesheet=DEFAULT_STYLESHEET,
    )
    assert stylesheet[_EDGE_INDEX]["style"]["target-arrow-shape"] == "triangle"


def test_hide_arrows():
    stylesheet = update_arrows(
        show_arrows=False,
        current_stylesheet=DEFAULT_STYLESHEET,
    )
    assert stylesheet[_EDGE_INDEX]["style"]["target-arrow-shape"] == "none"


def test_element_selection_callback():
    grid = ThreePhaseGrid.empty()
    grid.node = ThreePhaseNodeArray.empty(1)
    grid.node.id = [1]
    grid.node.u_rated = [100.0]
    grid.node.three_phase_quantity = [[1.0, 2.0, 3.0]]

    server_state.set_app_state(grid)

    node_data = [
        {
            "id": "1",
            "group": "node",
            "associated_ids": {"node": [1]},
        }
    ]
    edge_data = []

    result = display_selected_elements(node_data, edge_data)

    expected = dag.AgGrid(  # type: ignore[attr-defined]
        rowData=[
            {
                "u_rated": 100.0,
                "id": 1,
                "node_type": 0,
                "feeder_branch_id": -2147483648,
                "feeder_node_id": -2147483648,
                "three_phase_quantity": [1.0, 2.0, 3.0],
            }
        ],
        columnDefs=[
            {"field": "id", "headerName": "id"},
            {"field": "u_rated", "headerName": "u_rated"},
            {"field": "node_type", "headerName": "node_type"},
            {"field": "feeder_branch_id", "headerName": "feeder_branch_id"},
            {"field": "feeder_node_id", "headerName": "feeder_node_id"},
            {
                "field": "three_phase_quantity",
                "headerName": "three_phase_quantity",
            },
        ],
    )

    assert result[0].children == "node"
    assert result[1].rowData == expected.rowData
    assert result[1].columnDefs == expected.columnDefs


def test_display_selected_element_none():
    result = display_selected_elements([], [])
    assert result == SELECTION_OUTPUT_HTML.children


def test_update_layout():
    assert update_layout("circle", [0, 1, 2]) == {
        "name": "circle",
        "animate": True,
    }


def test_cell_selection_graph_invalid_trigger():
    fig, style, controls_style = cell_selection_graph(None, 2.0)

    assert style == {"display": "none"}
    assert controls_style == {"display": "none"}
    assert fig == go.Figure()


def test_cell_selection_graph_no_data():
    server_state.set_app_state(Grid.empty())

    fig, style, controls_style = cell_selection_graph(
        _NODE_SELECTION,
        2.0,
    )

    assert style == {"display": "none"}
    assert controls_style == {"display": "none"}
    assert fig == go.Figure()


def test_cell_selection_graph_with_output_data():
    dtype = np.dtype(
        [
            ("id", np.int32),
            ("u_rated", np.float64),
        ]
    )

    output_data = {
        ComponentType.node: np.array(
            [
                [(1, 400.0)],
                [(9, 99.0)],
                [(1, 410.0)],
            ],
            dtype=dtype,
        )
    }

    server_state.set_app_state(
        Grid.empty(),
        output_data=output_data,
    )

    fig, style, controls_style = cell_selection_graph(
        _NODE_SELECTION,
        2.0,
    )

    assert style == {"display": "block"}
    assert controls_style == {"display": "none"}
    assert len(fig.data) == 1

    np.testing.assert_allclose(
        fig.data[0].y,
        [400.0, 410.0],
    )
    np.testing.assert_allclose(
        fig.data[0].x,
        [0, 2],
    )


def test_cell_selection_graph_three_phase_output_data():
    dtype = np.dtype(
        [
            ("id", np.int32),
            ("u_rated", np.float64, (3,)),
        ]
    )

    output_data = {
        ComponentType.node: np.array(
            [
                [(1, [400.0, 401.0, 402.0])],
                [(9, [99.0, 99.0, 99.0])],
                [(1, [410.0, 411.0, 412.0])],
            ],
            dtype=dtype,
        )
    }

    server_state.set_app_state(
        Grid.empty(),
        output_data=output_data,
    )

    fig, style, controls_style = cell_selection_graph(
        _NODE_SELECTION,
        2.0,
    )

    assert style == {"display": "block"}
    assert controls_style == {"display": "none"}
    assert len(fig.data) == 3

    np.testing.assert_allclose(
        fig.data[0].y,
        [400.0, 410.0],
    )
    np.testing.assert_allclose(
        fig.data[1].y,
        [401.0, 411.0],
    )
    np.testing.assert_allclose(
        fig.data[2].y,
        [402.0, 412.0],
    )

    for trace in fig.data:
        np.testing.assert_allclose(
            trace.x,
            [0, 2],
        )


@pytest.fixture
def mock_voltage_sensor_ctx():
    """Simulate clicking u_measured for symmetric voltage sensor 101."""
    ctx = MagicMock()

    ctx.triggered = [
        {
            "prop_id": '{"type":"selection-table","group":"sym_voltage_sensor"}.cellClicked',
            "value": {
                "rowId": "101",
                "colId": "u_measured",
            },
        }
    ]

    ctx.triggered_id = {
        "group": "sym_voltage_sensor",
    }

    return ctx


@pytest.fixture
def voltage_sensor_grid():
    """Provide sensor attributes required by the comparison helper."""
    sensors = SimpleNamespace(
        id=np.array([101], dtype=np.int32),
        measured_object=np.array([10], dtype=np.int32),
        u_measured=np.array([230.0]),
        u_sigma=np.array([2.0]),
    )

    return SimpleNamespace(
        sym_voltage_sensor=sensors,
    )


def test_cell_selection_graph_voltage_comparison(voltage_sensor_grid):
    """Selecting u_measured displays measured and calculated voltages."""
    nodes = initialize_array(
        "sym_output",
        "node",
        (3, 1),
    )
    nodes["id"] = 10
    nodes["u"][:, 0] = [229.0, 231.0, 228.0]

    updates = initialize_array(
        "update",
        "sym_voltage_sensor",
        (3, 1),
    )
    updates["id"] = 101
    updates["u_measured"][1, 0] = 235.0

    output_data = {
        ComponentType.node: nodes,
    }

    update_data = {
        ComponentType.sym_voltage_sensor: updates,
    }

    with (
        patch(
            f"{_CALLBACK_PATH}.get_grid",
            return_value=voltage_sensor_grid,
        ),
        patch(
            f"{_CALLBACK_PATH}.get_output_data",
            return_value=output_data,
        ),
        patch(
            f"{_CALLBACK_PATH}.get_update_data",
            return_value=update_data,
        ),
    ):
        fig, style, controls_style = cell_selection_graph(
            _VOLTAGE_SELECTION,
            2.0,
        )

    assert style == {"display": "block"}
    assert controls_style == {"display": "block"}
    assert len(fig.data) == 4

    assert fig.data[2].name == "Measured voltage"
    assert fig.data[3].name == "Calculated voltage"

    np.testing.assert_array_equal(
        fig.data[2].x,
        [0, 1, 2],
    )
    np.testing.assert_array_equal(
        fig.data[2].y,
        [230.0, 235.0, 230.0],
    )
    np.testing.assert_array_equal(
        fig.data[3].y,
        [229.0, 231.0, 228.0],
    )

    np.testing.assert_array_equal(
        fig.data[0].y,
        [226.0, 231.0, 226.0],
    )
    np.testing.assert_array_equal(
        fig.data[1].y,
        [234.0, 239.0, 234.0],
    )

    assert fig.layout.showlegend is True


def test_cell_selection_graph_voltage_without_data():
    """Hide the graph when no comparison data is available."""
    with (
        patch(
            f"{_CALLBACK_PATH}.get_output_data",
            return_value=None,
        ),
        patch(
            f"{_CALLBACK_PATH}.get_update_data",
            return_value=None,
        ),
    ):
        fig, style, controls_style = cell_selection_graph(
            _VOLTAGE_SELECTION,
            2.0,
        )

    assert style == {"display": "none"}
    assert controls_style == {"display": "none"}
    assert fig == go.Figure()


def test_cell_selection_graph_voltage_falls_back_to_updates():
    """Preserve the update-series graph when node output is unavailable."""
    updates = initialize_array(
        "update",
        "sym_voltage_sensor",
        (3, 1),
    )
    updates["id"] = 101
    updates["u_measured"][:, 0] = [
        230.0,
        235.0,
        232.0,
    ]

    update_data = {
        ComponentType.sym_voltage_sensor: updates,
    }

    with (
        patch(
            f"{_CALLBACK_PATH}.get_output_data",
            return_value=None,
        ),
        patch(
            f"{_CALLBACK_PATH}.get_update_data",
            return_value=update_data,
        ),
    ):
        fig, style, controls_style = cell_selection_graph(
            _VOLTAGE_SELECTION,
            2.0,
        )

    assert style == {"display": "block"}
    assert controls_style == {"display": "none"}
    assert len(fig.data) == 1

    np.testing.assert_array_equal(
        fig.data[0].x,
        [0, 1, 2],
    )
    np.testing.assert_array_equal(
        fig.data[0].y,
        [230.0, 235.0, 232.0],
    )


def test_store_selected_voltage_sensor_cell(mock_voltage_sensor_ctx):
    """A sensor cell click is retained for subsequent graph updates."""
    with patch(
        _CTX_PATH,
        mock_voltage_sensor_ctx,
    ):
        selected_cell = store_selected_cell(None, None, None)

    assert selected_cell == {
        "group": "sym_voltage_sensor",
        "id": 101,
        "column": "u_measured",
    }


def test_changing_sigma_multiplier_updates_only_bounds(voltage_sensor_grid):
    """Changing the multiplier redraws bounds without changing voltage data."""
    nodes = initialize_array(
        "sym_output",
        "node",
        (2, 1),
    )
    nodes["id"] = 10
    nodes["u"][:, 0] = [231.0, 233.0]

    output_data = {
        ComponentType.node: nodes,
    }

    with (
        patch(
            f"{_CALLBACK_PATH}.get_grid",
            return_value=voltage_sensor_grid,
        ),
        patch(
            f"{_CALLBACK_PATH}.get_output_data",
            return_value=output_data,
        ),
        patch(
            f"{_CALLBACK_PATH}.get_update_data",
            return_value=None,
        ),
    ):
        figure_1, style_1, controls_1 = cell_selection_graph(
            _VOLTAGE_SELECTION,
            1.0,
        )

        figure_3, style_3, controls_3 = cell_selection_graph(
            _VOLTAGE_SELECTION,
            3.0,
        )

    assert style_1 == style_3 == {"display": "block"}
    assert controls_1 == controls_3 == {"display": "block"}

    # Measurement = 230 V; sigma = 2 V.
    np.testing.assert_allclose(
        figure_1.data[0].y,
        [228.0, 228.0],
    )
    np.testing.assert_allclose(
        figure_1.data[1].y,
        [232.0, 232.0],
    )

    np.testing.assert_allclose(
        figure_3.data[0].y,
        [224.0, 224.0],
    )
    np.testing.assert_allclose(
        figure_3.data[1].y,
        [236.0, 236.0],
    )

    # Neither the measured nor calculated series changes.
    for index in (2, 3):
        np.testing.assert_array_equal(
            figure_1.data[index].y,
            figure_3.data[index].y,
        )

    np.testing.assert_allclose(
        figure_1.data[2].y,
        [230.0, 230.0],
    )
    np.testing.assert_allclose(
        figure_1.data[3].y,
        [231.0, 233.0],
    )


@pytest.mark.parametrize(
    "multiplier",
    [None, -1, np.nan, np.inf],
)
def test_invalid_sigma_multiplier_hides_comparison(multiplier):
    """Reject invalid multiplier values before calculating bounds."""
    nodes = initialize_array(
        "sym_output",
        "node",
        (1, 1),
    )
    nodes["id"] = 10
    nodes["u"][0, 0] = 231.0

    with patch(
        f"{_CALLBACK_PATH}.get_output_data",
        return_value={ComponentType.node: nodes},
    ):
        figure, graph_style, controls_style = cell_selection_graph(
            _VOLTAGE_SELECTION,
            multiplier,
        )

    assert figure == go.Figure()
    assert graph_style == {"display": "none"}
    assert controls_style == {"display": "block"}


@pytest.mark.parametrize(
    "triggered_property",
    ["selectedNodeData", "selectedEdgeData"],
)
def test_store_selected_cell_clears_on_network_selection_change(
    triggered_property,
):
    """Changing the selected network elements clears the stored cell."""
    ctx = MagicMock()
    ctx.triggered_id = "cytoscape-graph"
    ctx.triggered = [
        {
            "prop_id": f"cytoscape-graph.{triggered_property}",
            "value": [],
        }
    ]

    with patch(_CTX_PATH, ctx):
        selected_cell = store_selected_cell(None, [], [])

    assert selected_cell is None


def test_voltage_comparison_hides_when_network_selection_cleared():
    selected_cell = {
        "group": ComponentType.sym_voltage_sensor.value,
        "id": 101,
        "column": "u_measured",
    }

    figure, graph_style, controls_style = cell_selection_graph(
        selected_cell,
        2.0,
        [],
        [],
    )

    assert len(figure.data) == 0
    assert graph_style == {"display": "none"}
    assert controls_style == {"display": "none"}


def test_voltage_comparison_falls_back_for_asymmetric_node_output():
    """Asymmetric node output must not enter the symmetric comparison."""
    nodes = initialize_array(
        "asym_output",
        "node",
        (2, 1),
    )
    nodes["id"] = 10
    nodes["u"][:, 0] = [
        [229.0, 230.0, 231.0],
        [232.0, 233.0, 234.0],
    ]

    updates = initialize_array(
        "update",
        "sym_voltage_sensor",
        (2, 1),
    )
    updates["id"] = 101
    updates["u_measured"][:, 0] = [230.0, 232.0]

    with (
        patch(
            f"{_CALLBACK_PATH}.get_output_data",
            return_value={ComponentType.node: nodes},
        ),
        patch(
            f"{_CALLBACK_PATH}.get_update_data",
            return_value={ComponentType.sym_voltage_sensor: updates},
        ),
    ):
        figure, graph_style, controls_style = cell_selection_graph(
            _VOLTAGE_SELECTION,
            2.0,
        )

    assert graph_style == {"display": "block"}
    assert controls_style == {"display": "none"}
    assert len(figure.data) == 1

    np.testing.assert_array_equal(
        figure.data[0].x,
        [0, 1],
    )
    np.testing.assert_array_equal(
        figure.data[0].y,
        [230.0, 232.0],
    )

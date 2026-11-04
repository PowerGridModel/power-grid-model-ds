# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from copy import deepcopy
from unittest.mock import MagicMock, patch

import dash_ag_grid as dag
import numpy as np
import pytest
from dash.exceptions import PreventUpdate
from plotly import graph_objs as go
from power_grid_model import ComponentType

from power_grid_model_ds._core.model.dtypes.typing import NDArray3
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer import server_state
from power_grid_model_ds._core.visualizer.callbacks.config import (
    scale_elements,
    update_appliances,
    update_arrows,
    update_layout,
)
from power_grid_model_ds._core.visualizer.callbacks.element_selection import (
    cell_selection_graph,
    display_selected_elements,
)
from power_grid_model_ds._core.visualizer.callbacks.search_form import HIGHLIGHT_STYLE, search_element
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
from power_grid_model_ds._core.visualizer.layout.selection_output import SELECTION_OUTPUT_HTML
from power_grid_model_ds.arrays import NodeArray

_EDGE_INDEX = 3

_CTX_PATH = "power_grid_model_ds._core.visualizer.callbacks.element_selection.callback_context"


class ThreePhaseNodeArray(NodeArray):
    three_phase_quantity: NDArray3[np.float64]


class ThreePhaseGrid(Grid):
    node: ThreePhaseNodeArray


def test_scale_elements():
    assert scale_elements(1.2, 1.3, DEFAULT_STYLESHEET)


def test_search_element_no_input():
    with pytest.raises(PreventUpdate):
        search_element(group="", column="", operator="", value="", stylesheet=DEFAULT_STYLESHEET)


def test_search_element_with_asym_column():
    server_state.set_app_state(Grid.empty())
    with pytest.raises(PreventUpdate):
        search_element(group="asym_gen", column="p_specified", operator="=", value="100", stylesheet=DEFAULT_STYLESHEET)


@pytest.mark.parametrize(
    ("group", "column", "operator", "value", "expected_selectors"),
    [
        pytest.param("node", "id", "=", "1", [{"selector": "#1", "style": HIGHLIGHT_STYLE}], id="node id equal"),
        pytest.param(
            "branches", "id", "!=", "12", [{"selector": "#23", "style": HIGHLIGHT_STYLE}], id="branch id not equal"
        ),
        pytest.param(
            "line", "from_node", ">", "1", [{"selector": "#23", "style": HIGHLIGHT_STYLE}], id="line from_node greater"
        ),
        pytest.param(
            "line",
            "to_node",
            "<",
            "10",
            [{"selector": "#12", "style": HIGHLIGHT_STYLE}, {"selector": "#23", "style": HIGHLIGHT_STYLE}],
            id="line to_node smaller",
        ),
    ],
)
def test_search_element_with_input(group, column, operator, value, expected_selectors):
    server_state.set_app_state(Grid.from_txt("S1 2 12", "2 3 23"))

    result = search_element(group, column, operator, value, DEFAULT_STYLESHEET)
    assert len(result) == len(DEFAULT_STYLESHEET) + len(expected_selectors)
    assert result[-len(expected_selectors) :] == expected_selectors


def test_show_arrows():
    stylesheet = update_arrows(show_arrows=True, current_stylesheet=DEFAULT_STYLESHEET)
    assert stylesheet[_EDGE_INDEX]["style"]["target-arrow-shape"] == "triangle"


def test_hide_arrows():
    stylesheet = update_arrows(show_arrows=False, current_stylesheet=DEFAULT_STYLESHEET)
    assert stylesheet[_EDGE_INDEX]["style"]["target-arrow-shape"] == "none"


def test_element_selection_callback():
    grid = ThreePhaseGrid.empty()
    grid.node = ThreePhaseNodeArray.empty(1)
    grid.node.id = [1]
    grid.node.u_rated = [100.0]
    grid.node.three_phase_quantity = [[1.0, 2.0, 3.0]]

    server_state.set_app_state(grid)

    node_data = [{"id": "1", "group": "node", "associated_ids": {"node": [1]}}]
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
            {"field": "three_phase_quantity", "headerName": "three_phase_quantity"},
        ],
    )
    assert result[0].children == "node"
    assert result[1].rowData == expected.rowData
    assert result[1].columnDefs == expected.columnDefs


def test_display_selected_element_none():
    result = display_selected_elements([], [])
    assert result == SELECTION_OUTPUT_HTML.children


def test_update_layout():
    assert update_layout("circle", [0, 1, 2]) == {"name": "circle", "animate": True}


@pytest.fixture
def mock_cell_clicked_ctx():
    ctx = MagicMock()
    ctx.triggered = [
        {
            "prop_id": '{"type":"selection-table","group":"node"}.cellClicked',
            "value": {"rowId": "1", "colId": "u_rated"},
        }
    ]
    ctx.triggered_id = {"group": "node"}
    return ctx


def test_cell_selection_graph_invalid_trigger():
    ctx = MagicMock()
    ctx.triggered = [{"prop_id": "some-other.input", "value": None}]
    ctx.triggered_id = None
    with patch(_CTX_PATH, ctx):
        fig, style = cell_selection_graph(None)
    assert style == {"display": "none"}
    assert fig == go.Figure()


def test_cell_selection_graph_no_data(mock_cell_clicked_ctx):
    server_state.set_app_state(Grid.empty())
    with patch(_CTX_PATH, mock_cell_clicked_ctx):
        fig, style = cell_selection_graph(None)
    assert style == {"display": "none"}
    assert fig == go.Figure()


def test_cell_selection_graph_with_output_data(mock_cell_clicked_ctx):
    dtype = np.dtype([("id", np.int32), ("u_rated", np.float64)])
    output_data = {ComponentType.node: np.array([[(1, 400.0)], [(9, 99.0)], [(1, 410.0)]], dtype=dtype)}
    server_state.set_app_state(Grid.empty(), output_data=output_data)
    with patch(_CTX_PATH, mock_cell_clicked_ctx):
        fig, style = cell_selection_graph(None)
    assert style == {"display": "block"}
    assert len(fig.data) == 1
    np.testing.assert_allclose(fig.data[0].y, np.array([400.0, 410.0]))
    np.testing.assert_allclose(fig.data[0].x, np.array([0, 2]))


def test_cell_selection_graph_three_phase_output_data(mock_cell_clicked_ctx):
    dtype = np.dtype([("id", np.int32), ("u_rated", np.float64, (3,))])
    output_data = {
        ComponentType.node: np.array(
            [[(1, [400.0, 401.0, 402.0])], [(9, [99, 99, 99])], [(1, [410.0, 411.0, 412.0])]], dtype=dtype
        )
    }
    server_state.set_app_state(Grid.empty(), output_data=output_data)
    with patch(_CTX_PATH, mock_cell_clicked_ctx):
        fig, style = cell_selection_graph(None)
    assert style == {"display": "block"}
    assert len(fig.data) == 3  # one trace per phase
    np.testing.assert_allclose(fig.data[0].y, np.array([400.0, 410.0]))
    np.testing.assert_allclose(fig.data[1].y, np.array([401.0, 411.0]))
    np.testing.assert_allclose(fig.data[2].y, np.array([402.0, 412.0]))
    np.testing.assert_allclose(fig.data[0].x, np.array([0, 2]))
    np.testing.assert_allclose(fig.data[1].x, np.array([0, 2]))
    np.testing.assert_allclose(fig.data[2].x, np.array([0, 2]))



def test_update_appliances_visibility_preserves_node_separation():
    """Appliance visibility must preserve automatically separated nodes."""
    parsed_elements = {
        "2": {
            "data": {"id": "2", "group": "node"},
            "position": {"x": 250.0, "y": -250.0},
            "classes": "node",
        },
        "3": {
            "data": {"id": "3", "group": "node"},
            "position": {"x": 250.0, "y": -250.0},
            "classes": "node",
        },
        "10_ghost_node": {
            "data": {
                "id": "10_ghost_node",
                "group": "sym_load_ghost_node",
            },
            "position": {"x": 250.0, "y": -250.0},
            "classes": "appliance-ghost-node",
            "selectable": False,
        },
        "10": {
            "data": {
                "id": "10",
                "group": "sym_load",
                "source": "2",
                "target": "10_ghost_node",
            },
            "classes": "appliance",
        },
    }

    position_state = {"scale": 1.0, "manual_positions": {}}

    hidden, hidden_state, next_state = update_appliances(
        show_appliances=False,
        node_scale=2.0,
        parsed_elements=parsed_elements,
        current_elements=None,
        position_state=position_state,
        current_layout={"name": "preset"},
    )

    visible, visible_state, _ = update_appliances(
        show_appliances=True,
        node_scale=2.0,
        parsed_elements=parsed_elements,
        current_elements=hidden,
        position_state=next_state,
        current_layout={"name": "preset"},
    )

    hidden_ids = {element["data"]["id"] for element in hidden}
    visible_ids = {element["data"]["id"] for element in visible}

    assert hidden_state is False
    assert visible_state is True
    assert hidden_ids == {"2", "3"}
    assert visible_ids == {"2", "3", "10", "10_ghost_node"}

    def node_positions(elements):
        return {
            element["data"]["id"]: element["position"]
            for element in elements
            if element["data"]["group"] == "node"
        }

    hidden_positions = node_positions(hidden)
    visible_positions = node_positions(visible)

    assert hidden_positions == visible_positions
    assert hidden_positions["2"] != hidden_positions["3"]
    assert abs(
        visible_positions["3"]["x"] - visible_positions["2"]["x"]
    ) == 175.0


def test_update_appliances_restores_positions_after_scaling():
    """Scaling 1 to 2 to 1 must restore automatic node positions."""
    parsed_elements = {
        "2": {
            "data": {"id": "2", "group": "node"},
            "position": {"x": 250.0, "y": -250.0},
            "classes": "node",
        },
        "3": {
            "data": {"id": "3", "group": "node"},
            "position": {"x": 250.0, "y": -250.0},
            "classes": "node",
        },
    }

    state = {"scale": 1.0, "manual_positions": {}}

    initial, _, state = update_appliances(
        show_appliances=False,
        node_scale=1.0,
        parsed_elements=parsed_elements,
        current_elements=None,
        position_state=state,
        current_layout={"name": "preset"},
    )

    enlarged, _, state = update_appliances(
        show_appliances=False,
        node_scale=2.0,
        parsed_elements=parsed_elements,
        current_elements=initial,
        position_state=state,
        current_layout={"name": "preset"},
    )

    restored, _, state = update_appliances(
        show_appliances=False,
        node_scale=1.0,
        parsed_elements=parsed_elements,
        current_elements=enlarged,
        position_state=state,
        current_layout={"name": "preset"},
    )

    def positions(elements):
        return {
            element["data"]["id"]: element["position"]
            for element in elements
        }

    assert positions(restored) == positions(initial)
    assert positions(enlarged) != positions(initial)

    assert state["manual_positions"] == {}
    assert parsed_elements["2"]["position"] == {
        "x": 250.0,
        "y": -250.0,
    }
    assert parsed_elements["3"]["position"] == {
        "x": 250.0,
        "y": -250.0,
    }


def test_update_appliances_preserves_dragged_node_when_scaling():
    """A manually dragged node must retain its position after scaling."""
    parsed_elements = {
        "2": {
            "data": {"id": "2", "group": "node"},
            "position": {"x": 250.0, "y": -250.0},
        },
        "3": {
            "data": {"id": "3", "group": "node"},
            "position": {"x": 250.0, "y": -250.0},
        },
    }

    state = {"scale": 1.0, "manual_positions": {}}

    initial, _, state = update_appliances(
        show_appliances=False,
        node_scale=1.0,
        parsed_elements=parsed_elements,
        current_elements=None,
        position_state=state,
        current_layout={"name": "preset"},
    )

    dragged = deepcopy(initial)
    for element in dragged:
        if element["data"]["id"] == "2":
            element["position"] = {"x": 600.0, "y": -500.0}

    enlarged, _, state = update_appliances(
        show_appliances=False,
        node_scale=2.0,
        parsed_elements=parsed_elements,
        current_elements=dragged,
        position_state=state,
        current_layout={"name": "preset"},
    )

    positions = {
        element["data"]["id"]: element["position"]
        for element in enlarged
    }

    assert positions["2"] == {"x": 600.0, "y": -500.0}
    assert positions["3"] == {"x": 337.5, "y": -250.0}
    assert state["manual_positions"]["2"] == {
        "x": 600.0,
        "y": -500.0,
    }


def test_update_appliances_preserves_dragged_node_when_toggling_appliances():
    """Changing appliance visibility must preserve manually moved nodes."""
    parsed_elements = {
        "2": {
            "data": {"id": "2", "group": "node"},
            "position": {"x": 250.0, "y": -250.0},
        },
        "3": {
            "data": {"id": "3", "group": "node"},
            "position": {"x": 250.0, "y": -250.0},
        },
        "10_ghost_node": {
            "data": {
                "id": "10_ghost_node",
                "group": "sym_load_ghost_node",
            },
            "position": {"x": 250.0, "y": -250.0},
        },
        "10": {
            "data": {
                "id": "10",
                "group": "sym_load",
                "source": "2",
                "target": "10_ghost_node",
            },
        },
    }

    state = {"scale": 1.0, "manual_positions": {}}

    initial, _, state = update_appliances(
        show_appliances=False,
        node_scale=1.0,
        parsed_elements=parsed_elements,
        current_elements=None,
        position_state=state,
        current_layout={"name": "preset"},
    )

    dragged = deepcopy(initial)
    for element in dragged:
        if element["data"]["id"] == "2":
            element["position"] = {"x": 600.0, "y": -500.0}

    visible, visible_state, state = update_appliances(
        show_appliances=True,
        node_scale=1.0,
        parsed_elements=parsed_elements,
        current_elements=dragged,
        position_state=state,
        current_layout={"name": "preset"},
    )
    positions = {
        element["data"]["id"]: element["position"]
        for element in visible
        if element["data"]["group"] == "node"
    }

    assert visible_state is True
    assert positions["2"] == {"x": 600.0, "y": -500.0}
    assert state["manual_positions"]["2"] == {
        "x": 600.0,
        "y": -500.0,
    }

    visible_ids = {element["data"]["id"] for element in visible}
    assert {"10", "10_ghost_node"}.issubset(visible_ids)


def test_update_appliances_preserves_automatic_layout_positions():
    """Scaling in breadthfirst must preserve Cytoscape's positions."""
    parsed_elements = {
        "2": {
            "data": {"id": "2", "group": "node"},
            "position": {"x": 250.0, "y": -250.0},
        },
        "3": {
            "data": {"id": "3", "group": "node"},
            "position": {"x": 250.0, "y": -250.0},
        },
    }

    current_elements = [
        {
            "data": {"id": "2", "group": "node"},
            "position": {"x": 100.0, "y": 300.0},
        },
        {
            "data": {"id": "3", "group": "node"},
            "position": {"x": 500.0, "y": 300.0},
        },
    ]

    elements, show_state, position_state = update_appliances(
        show_appliances=False,
        node_scale=2.0,
        parsed_elements=parsed_elements,
        current_elements=current_elements,
        position_state={
            "scale": 1.0,
            "manual_positions": {},
        },
        current_layout={"name": "breadthfirst"},
    )

    positions = {
        element["data"]["id"]: element["position"]
        for element in elements
    }

    assert positions["2"] == {"x": 100.0, "y": 300.0}
    assert positions["3"] == {"x": 500.0, "y": 300.0}
    assert show_state is False
    assert position_state["manual_positions"] == {}
    assert position_state["scale"] == 2.0


def test_update_appliances_initial_breadthfirst_preserves_positions():
    """Initial breadthfirst layout must not classify positions as manual moves."""
    parsed_elements = {
        "2": {
            "data": {"id": "2", "group": "node"},
            "position": {"x": 250.0, "y": -250.0},
        },
        "3": {
            "data": {"id": "3", "group": "node"},
            "position": {"x": 250.0, "y": -250.0},
        },
    }

    current_elements = [
        {
            "data": {"id": "2", "group": "node"},
            "position": {"x": 100.0, "y": 300.0},
        },
        {
            "data": {"id": "3", "group": "node"},
            "position": {"x": 500.0, "y": 300.0},
        },
    ]

    elements, show_state, position_state = update_appliances(
        show_appliances=False,
        node_scale=2.0,
        parsed_elements=parsed_elements,
        current_elements=current_elements,
        position_state={
            "scale": 1.0,
            "manual_positions": {},
        },
        current_layout={"name": "breadthfirst"},
    )

    positions = {
        element["data"]["id"]: element["position"]
        for element in elements
    }

    assert positions["2"] == {"x": 100.0, "y": 300.0}
    assert positions["3"] == {"x": 500.0, "y": 300.0}
    assert show_state is False
    assert position_state["manual_positions"] == {}
    assert position_state["scale"] == 2.0

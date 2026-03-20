# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import pytest
from dash import dash_table
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer import server_state
from power_grid_model_ds._core.visualizer.callbacks.config import scale_elements, update_arrows, update_layout
from power_grid_model_ds._core.visualizer.callbacks.element_selection import display_selected_element
from power_grid_model_ds._core.visualizer.callbacks.search_form import HIGHLIGHT_STYLE, search_element
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
from power_grid_model_ds._core.visualizer.layout.selection_output import SELECTION_OUTPUT_HTML
from power_grid_model_ds.arrays import NodeArray

_EDGE_INDEX = 3


def test_scale_elements():
    assert scale_elements(1.2, 1.3, DEFAULT_STYLESHEET)


def test_search_element_no_input():
    with pytest.raises(PreventUpdate):
        search_element(group="", column="", operator="", value="", stylesheet=DEFAULT_STYLESHEET)


def test_search_element_with_asym_column():
    server_state.set_grid(Grid.empty())
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
    server_state.set_grid(Grid.from_txt("S1 2 12", "2 3 23"))

    result = search_element(group, column, operator, value, DEFAULT_STYLESHEET)
    assert len(result) == len(DEFAULT_STYLESHEET) + len(expected_selectors)
    assert result[-len(expected_selectors) :] == expected_selectors


def test_show_arrows():
    stylesheet = update_arrows(True, DEFAULT_STYLESHEET)
    assert stylesheet[_EDGE_INDEX]["style"]["target-arrow-shape"] == "triangle"


def test_hide_arrows():
    stylesheet = update_arrows(False, DEFAULT_STYLESHEET)
    assert stylesheet[_EDGE_INDEX]["style"]["target-arrow-shape"] == "none"


def test_element_selection_callback():
    grid = Grid.empty()
    grid.node = NodeArray.empty(1)
    grid.node.id = [1]
    grid.node.u_rated = [100.0]

    server_state.set_grid(grid)

    node_data = [{"id": "1", "u_rated": 100.0, "group": "node"}]
    edge_data = []

    result = display_selected_element(node_data, edge_data)
    expected = dash_table.DataTable(  # type: ignore[attr-defined]
        data=[
            {"u_rated": 100.0, "id": 1, "node_type": 0, "feeder_branch_id": -2147483648, "feeder_node_id": -2147483648}
        ],
        columns=[
            {"name": "id", "id": "id"},
            {"name": "u_rated", "id": "u_rated"},
            {"name": "node_type", "id": "node_type"},
            {"name": "feeder_branch_id", "id": "feeder_branch_id"},
            {"name": "feeder_node_id", "id": "feeder_node_id"},
        ],
        editable=False,
    )
    assert result.data == expected.data
    assert result.columns == expected.columns


def test_display_selected_element_none():
    result = display_selected_element([], [])
    assert result == SELECTION_OUTPUT_HTML.children


def test_update_layout():
    assert update_layout("circle", [0, 1, 2]) == {"name": "circle", "animate": True}

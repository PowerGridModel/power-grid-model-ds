# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import pytest
from dash import dash_table
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.visualizer.callbacks.config import scale_elements, update_arrows, update_layout
from power_grid_model_ds._core.visualizer.callbacks.element_selection import display_selected_element
from power_grid_model_ds._core.visualizer.callbacks.search_form import search_element
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
from power_grid_model_ds._core.visualizer.layout.selection_output import SELECTION_OUTPUT_HTML

_EDGE_INDEX = 3


def test_scale_elements():
    assert scale_elements(1.2, 1.3, DEFAULT_STYLESHEET)


def test_search_element_no_input():
    with pytest.raises(PreventUpdate):
        search_element(group="", column="", operator="", value="", stylesheet=DEFAULT_STYLESHEET)


def test_search_element_with_input():
    group = "node"
    column = "id"
    operator = "="
    value = "1"

    expected_selector = f'[{column} {operator} "{value}"][group = "node"]'

    result = search_element(group, column, operator, value, DEFAULT_STYLESHEET)
    assert result[-1]["selector"] == expected_selector


def test_show_arrows():
    stylesheet = update_arrows(True, DEFAULT_STYLESHEET)
    assert stylesheet[_EDGE_INDEX]["style"]["target-arrow-shape"] == "triangle"


def test_hide_arrows():
    stylesheet = update_arrows(False, DEFAULT_STYLESHEET)
    assert stylesheet[_EDGE_INDEX]["style"]["target-arrow-shape"] == "none"


def test_element_selection_callback():
    node_data = [{"pgm_id": 1, "u_rated": 100.0, "group": "node"}]
    edge_data = []
    result = display_selected_element(node_data, edge_data)
    expected = dash_table.DataTable(  # type: ignore[attr-defined]
        data=[{"u_rated": 100.0, "id": 1}],
        columns=[{"name": "id", "id": "id"}, {"name": "u_rated", "id": "u_rated"}],
        editable=False,
    )
    assert result.data == expected.data
    assert result.columns == expected.columns


def test_display_selected_element_none():
    result = display_selected_element([], [])
    assert result == SELECTION_OUTPUT_HTML.children


def test_update_layout():
    assert update_layout("abcd", [0, 1, 2]) == {"name": "abcd", "animate": True}

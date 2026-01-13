# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import pytest
from dash import dash_table
from dash.exceptions import PreventUpdate
from power_grid_model import ComponentType

from power_grid_model_ds._core.visualizer.callbacks.config import scale_elements, update_arrows
from power_grid_model_ds._core.visualizer.callbacks.element_selection import display_selected_element
from power_grid_model_ds._core.visualizer.callbacks.search_form import search_element
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
from power_grid_model_ds._core.visualizer.layout.selection_output import SELECTION_OUTPUT_HTML

_EDGE_INDEX = 3


def test_scale_elements():
    assert scale_elements(1.2, 1.3, DEFAULT_STYLESHEET)


def test_scale_elements_default_values():
    with pytest.raises(PreventUpdate):
        scale_elements(1, 1, DEFAULT_STYLESHEET)


def test_search_element_no_input():
    with pytest.raises(PreventUpdate):
        search_element(group="", column="", operator="", value="", stylesheet=DEFAULT_STYLESHEET)


def test_search_element_with_input():
    group = "node"
    column = "id"
    operator = "="
    value = "1"

    expected_selector = f'[{column} {operator} "{value}"]'

    result = search_element(group, column, operator, value, DEFAULT_STYLESHEET)
    assert result[-1]["selector"] == expected_selector


def test_show_arrows():
    stylesheet = update_arrows(True, DEFAULT_STYLESHEET)
    assert stylesheet[_EDGE_INDEX]["style"]["target-arrow-shape"] == "triangle"


def test_hide_arrows():
    stylesheet = update_arrows(False, DEFAULT_STYLESHEET)
    assert stylesheet[_EDGE_INDEX]["style"]["target-arrow-shape"] == "none"


def test_display_selected_node():
    viz_to_comp = {
        "1": {ComponentType.node: [{"id": 1, "u_rated": 10.0}, {"id": 2, "u_rated": 20.0}]},
        "3": {ComponentType.line: [{"id": 3, "from_node": 1, "to_node": 2, "r1": 10}]},
        "4_0": {ComponentType.three_winding_transformer: [{"id": 4, "node_1": 2, "node_2": 1, "node_3": 1, "sn": 10}]},
        "4_1": {ComponentType.three_winding_transformer: [{"id": 4, "node_1": 2, "node_2": 1, "node_3": 1, "sn": 10}]},
    }

    # node
    output = display_selected_element(node_data=[{"id": "1"}], edge_data=[], viz_to_comp=viz_to_comp)
    assert isinstance(output, dash_table.DataTable)
    assert output.data == [viz_to_comp["1"][ComponentType.node][0]]

    # edge
    output = display_selected_element(node_data=[], edge_data=[{"id": "3"}], viz_to_comp=viz_to_comp)
    assert isinstance(output, dash_table.DataTable)
    assert output.data == [viz_to_comp["3"][ComponentType.line][0]]

    # branch3
    output = display_selected_element(node_data=[], edge_data=[{"id": "4_0"}], viz_to_comp=viz_to_comp)
    assert isinstance(output, dash_table.DataTable)
    assert output.data == [viz_to_comp["4_0"][ComponentType.three_winding_transformer][0]]

    # nothing selected
    output = display_selected_element(node_data=[], edge_data=[], viz_to_comp=viz_to_comp)
    assert output == SELECTION_OUTPUT_HTML.children

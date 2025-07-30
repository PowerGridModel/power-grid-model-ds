# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
import pytest
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.visualizer.callbacks.config import scale_elements, update_arrows
from power_grid_model_ds._core.visualizer.callbacks.search_form import search_element
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET

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

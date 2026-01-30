# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch
import pytest
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.visualizer.callbacks.config import scale_elements, update_arrows, update_layout
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


def test_display_selected_element_none():
    result = display_selected_element([], [])
    assert result == SELECTION_OUTPUT_HTML.children


def test_update_layout():
    assert update_layout("abcd") == {"name": "abcd", "animate": True}

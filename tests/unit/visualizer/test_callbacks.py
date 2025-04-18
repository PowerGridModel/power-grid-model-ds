# SPDX-FileCopyrightText: 2025 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from power_grid_model_ds._core.visualizer.callbacks.element_scaling import scale_elements
from power_grid_model_ds._core.visualizer.callbacks.search_form import search_element
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET


def test_scale_elements():
    assert scale_elements(1, 1)


def test_search_element_no_input():
    assert search_element(group="", column="", operator="", value="") == DEFAULT_STYLESHEET


def test_search_element_with_input():
    group = "node"
    column = "id"
    operator = "="
    value = "1"

    expected_selector = f'[{column} {operator} "{value}"]'

    result = search_element(group, column, operator, value)
    assert result[-1]["selector"] == expected_selector

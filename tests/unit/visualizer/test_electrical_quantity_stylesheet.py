# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for electrical quantity Cytoscape styling."""

from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
from power_grid_model_ds._core.visualizer.styling_classification import StyleClass


def _get_style(selector: str) -> dict:
    """Find exactly one stylesheet rule for the requested selector."""
    matching_rules = [rule["style"] for rule in DEFAULT_STYLESHEET if rule["selector"] == selector]

    assert len(matching_rules) == 1
    return matching_rules[0]


def test_electrical_node_color_uses_element_data():
    style = _get_style("node[electrical_color]")

    assert style["background-color"] == "data(electrical_color)"
    assert style["text-background-color"] == "data(electrical_color)"


def test_electrical_edge_color_uses_element_data():
    style = _get_style("edge[electrical_color]")

    assert style["line-color"] == "data(electrical_color)"
    assert style["target-arrow-color"] == "data(electrical_color)"
    assert style["source-arrow-color"] == "data(electrical_color)"


def test_open_branch_rules_follow_electrical_rules():
    """Open-branch styling must remain after electrical edge colouring."""
    selectors = [rule["selector"] for rule in DEFAULT_STYLESHEET]

    open_branch_selector = f".{StyleClass.OPEN_BRANCH.value}"
    electrical_edge_selector = "edge[electrical_color]"

    assert open_branch_selector in selectors
    assert electrical_edge_selector in selectors

    assert selectors.index(open_branch_selector) > selectors.index(electrical_edge_selector)

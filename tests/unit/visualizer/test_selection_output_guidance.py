# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for shared measurement-comparison guidance and multiplier feedback."""

import math

import pytest

from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_GRAPH_HTML,
    update_sigma_multiplier_validation,
    update_voltage_comparison_guidance,
)

VOLTAGE_CELL = {"group": "sym_voltage_sensor", "id": 101, "column": "u_measured"}
POWER_P_CELL = {"group": "sym_power_sensor", "id": 201, "column": "p_measured"}
POWER_Q_CELL = {"group": "sym_power_sensor", "id": 201, "column": "q_measured"}
VISIBLE = {"display": "block"}
HIDDEN = {"display": "none"}
NOTE_VISIBLE = {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "flex-end",
    "gap": "8px",
    "fontSize": "14px",
    "color": "#694100",
}
COMPARISON_FIGURE = {
    "data": [
        {"type": "scatter", "name": "Measured voltage"},
        {"type": "scatter", "name": "Calculated voltage"},
    ]
}
ATTRIBUTE_FIGURE = {"data": [{"type": "scatter", "name": "u_measured"}]}


def test_guidance_layout_without_timer():
    store, controls, note, graph = SELECTION_GRAPH_HTML.children
    assert store.id == "selected-selection-cell"
    assert controls.id == "sigma-multiplier-controls"
    assert controls.style == HIDDEN | {"marginBottom": "12px"}

    (header,) = controls.children
    assert header.style["display"] == "flex"
    assert header.style["justifyContent"] == "space-between"
    multiplier_field, error = header.children
    assert multiplier_field.style["flexDirection"] == "column"
    assert multiplier_field.style["alignItems"] == "flex-start"
    label, sigma_input = multiplier_field.children
    assert label.children == "Sigma multiplier"
    assert label.htmlFor == "sigma-multiplier"
    assert sigma_input.id == "sigma-multiplier"
    assert sigma_input.min == 0
    assert sigma_input.value == 3.0

    assert error.id == "sigma-multiplier-error"
    assert error.role == "alert"
    assert error.style == HIDDEN
    assert error.children[0].children == "!"
    assert error.children[0].style["backgroundColor"] == "#b42318"
    assert "finite number" in error.children[1].children

    # Guidance is outside optional sigma controls so it remains visible
    # for a comparison that has no sigma values.
    assert note.id == "voltage-comparison-uncertainty-note"
    assert note.style == HIDDEN
    assert note.children[0].role == "presentation"
    assert "do not establish result validity" in note.children[1].children
    assert graph.id == "selection-graph"


@pytest.mark.parametrize("cell", [VOLTAGE_CELL, POWER_P_CELL, POWER_Q_CELL])
@pytest.mark.parametrize("multiplier", [0, 1, 2.0, 3.0, 3.5])
def test_supported_comparison_shows_note(cell, multiplier):
    assert update_voltage_comparison_guidance(cell, VISIBLE, VISIBLE, multiplier, COMPARISON_FIGURE) == NOTE_VISIBLE


@pytest.mark.parametrize("cell", [POWER_P_CELL, POWER_Q_CELL])
def test_comparison_without_sigma_still_shows_note(cell):
    assert update_voltage_comparison_guidance(cell, VISIBLE, HIDDEN, 3.0, COMPARISON_FIGURE) == NOTE_VISIBLE


@pytest.mark.parametrize("multiplier", [None, -1, math.nan, math.inf, -math.inf, "invalid"])
def test_invalid_multiplier_hides_note_when_sigma_controls_visible(multiplier):
    assert update_voltage_comparison_guidance(VOLTAGE_CELL, VISIBLE, VISIBLE, multiplier, COMPARISON_FIGURE) == HIDDEN


@pytest.mark.parametrize("cell", [None, {}, {"group": "node", "column": "u"}])
def test_other_selection_hides_guidance(cell):
    assert update_voltage_comparison_guidance(cell, VISIBLE, VISIBLE, 3.0, COMPARISON_FIGURE) == HIDDEN


def test_hidden_graph_hides_note():
    assert update_voltage_comparison_guidance(VOLTAGE_CELL, HIDDEN, VISIBLE, 3.0, COMPARISON_FIGURE) == HIDDEN


def test_ordinary_attribute_graph_does_not_show_note():
    assert update_voltage_comparison_guidance(VOLTAGE_CELL, VISIBLE, HIDDEN, 3.0, ATTRIBUTE_FIGURE) == HIDDEN


def test_missing_figure_does_not_show_note():
    assert update_voltage_comparison_guidance(VOLTAGE_CELL, VISIBLE, VISIBLE) == HIDDEN


@pytest.mark.parametrize("cell", [VOLTAGE_CELL, POWER_P_CELL, POWER_Q_CELL])
@pytest.mark.parametrize("multiplier", [0, 1, 2.0, 3.0, 3.5])
def test_valid_multiplier_has_normal_input_and_no_error(cell, multiplier):
    error_style, input_style = update_sigma_multiplier_validation(cell, multiplier, VISIBLE)
    assert error_style == HIDDEN
    assert input_style == {"width": "100px", "padding": "6px 8px"}


@pytest.mark.parametrize("cell", [VOLTAGE_CELL, POWER_P_CELL, POWER_Q_CELL])
@pytest.mark.parametrize("multiplier", [None, -1, math.nan, math.inf, -math.inf, "invalid"])
def test_invalid_multiplier_shows_error_and_red_input(cell, multiplier):
    error_style, input_style = update_sigma_multiplier_validation(cell, multiplier, VISIBLE)
    assert error_style["display"] == "flex"
    assert error_style["color"] == "#b42318"
    assert input_style["border"] == "2px solid #b42318"
    assert input_style["color"] == "#b42318"


@pytest.mark.parametrize("cell", [None, {}, {"group": "node", "column": "u"}])
def test_other_selection_hides_multiplier_error(cell):
    error_style, input_style = update_sigma_multiplier_validation(cell, -1, VISIBLE)
    assert error_style == HIDDEN
    assert "border" not in input_style


def test_hidden_controls_hide_multiplier_error():
    error_style, input_style = update_sigma_multiplier_validation(POWER_P_CELL, -1, HIDDEN)
    assert error_style == HIDDEN
    assert "border" not in input_style

# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for voltage-comparison uncertainty guidance and multiplier feedback."""

import math

import pytest

from power_grid_model_ds._core.visualizer.layout.selection_output import (
    SELECTION_GRAPH_HTML,
    update_sigma_multiplier_validation,
    update_voltage_comparison_guidance,
)

VOLTAGE_CELL = {"group": "sym_voltage_sensor", "id": 101, "column": "u_measured"}
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


def test_guidance_layout_without_timer():
    controls = SELECTION_GRAPH_HTML.children[1]
    assert controls.id == "sigma-multiplier-controls"
    assert controls.style["display"] == "none"

    (header,) = controls.children
    assert header.style["display"] == "flex"
    assert header.style["justifyContent"] == "space-between"

    multiplier_field, message_area = header.children
    assert multiplier_field.style["flexDirection"] == "column"
    assert multiplier_field.style["alignItems"] == "flex-start"
    label, sigma_input = multiplier_field.children
    assert label.children == "Sigma multiplier"
    assert label.htmlFor == "sigma-multiplier"
    assert sigma_input.id == "sigma-multiplier"
    assert sigma_input.min == 0
    assert sigma_input.value == 3.0

    assert message_area.style["display"] == "flex"
    assert message_area.style["justifyContent"] == "flex-end"
    note, error = message_area.children

    assert note.id == "voltage-comparison-uncertainty-note"
    assert note.style == HIDDEN
    assert note.children[0].role == "presentation"
    assert "do not establish result validity" in note.children[1].children
    assert len(note.children) == 2

    assert error.id == "sigma-multiplier-error"
    assert error.role == "alert"
    assert error.style == HIDDEN
    assert error.children[0].children == "!"
    assert error.children[0].role == "presentation"
    assert error.children[0].style["backgroundColor"] == "#b42318"
    assert "finite number" in error.children[1].children
    assert len(error.children) == 2

    assert len(SELECTION_GRAPH_HTML.children) == 3
    assert SELECTION_GRAPH_HTML.children[2].id == "selection-graph"


def test_visible_voltage_comparison_shows_note():
    assert update_voltage_comparison_guidance(VOLTAGE_CELL, VISIBLE, VISIBLE) == NOTE_VISIBLE


@pytest.mark.parametrize("multiplier", [0, 1, 2.0, 3.0, 3.5])
def test_valid_multiplier_shows_note(multiplier):
    assert update_voltage_comparison_guidance(VOLTAGE_CELL, VISIBLE, VISIBLE, multiplier) == NOTE_VISIBLE


@pytest.mark.parametrize("multiplier", [None, -1, math.nan, math.inf, -math.inf, "invalid"])
def test_invalid_multiplier_hides_note(multiplier):
    assert update_voltage_comparison_guidance(VOLTAGE_CELL, VISIBLE, VISIBLE, multiplier) == HIDDEN


@pytest.mark.parametrize("cell", [None, {}, {"group": "node", "column": "u"}])
def test_other_selection_hides_guidance(cell):
    assert update_voltage_comparison_guidance(cell, VISIBLE, VISIBLE) == HIDDEN


def test_hidden_controls_hide_guidance():
    assert update_voltage_comparison_guidance(VOLTAGE_CELL, HIDDEN, HIDDEN) == HIDDEN


def test_hidden_graph_hides_note():
    assert update_voltage_comparison_guidance(VOLTAGE_CELL, HIDDEN, VISIBLE) == HIDDEN


@pytest.mark.parametrize("multiplier", [0, 1, 2.0, 3.0, 3.5])
def test_valid_multiplier_has_normal_input_and_no_error(multiplier):
    error_style, input_style = update_sigma_multiplier_validation(VOLTAGE_CELL, multiplier, VISIBLE)
    assert error_style == HIDDEN
    assert input_style == {"width": "100px", "padding": "6px 8px"}


@pytest.mark.parametrize("multiplier", [None, -1, math.nan, math.inf, -math.inf, "invalid"])
def test_invalid_multiplier_shows_error_and_red_input(multiplier):
    error_style, input_style = update_sigma_multiplier_validation(VOLTAGE_CELL, multiplier, VISIBLE)
    assert error_style["display"] == "flex"
    assert error_style["justifyContent"] == "flex-end"
    assert error_style["color"] == "#b42318"
    assert input_style["border"] == "2px solid #b42318"
    assert input_style["color"] == "#b42318"


@pytest.mark.parametrize("cell", [None, {}, {"group": "node", "column": "u"}])
def test_other_selection_hides_multiplier_error(cell):
    error_style, input_style = update_sigma_multiplier_validation(cell, -1, VISIBLE)
    assert error_style == HIDDEN
    assert "border" not in input_style


def test_hidden_controls_hide_multiplier_error():
    error_style, input_style = update_sigma_multiplier_validation(VOLTAGE_CELL, -1, HIDDEN)
    assert error_style == HIDDEN
    assert "border" not in input_style

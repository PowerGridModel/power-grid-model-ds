# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for retained graph selection callbacks."""

from types import SimpleNamespace
from unittest.mock import patch

from dash import no_update

from power_grid_model_ds._core.visualizer.callbacks.element_selection import (
    update_retained_graph_selections,
)

_CALLBACK_PATH = "power_grid_model_ds._core.visualizer.callbacks.element_selection.callback_context"

SENSOR_A = {
    "group": "sym_voltage_sensor",
    "id": 101,
    "column": "u_measured",
}

SENSOR_B = {
    "group": "sym_voltage_sensor",
    "id": 102,
    "column": "u_measured",
}


def _invoke(
    triggered_id,
    selected_cell,
    retained,
    triggered_value=None,
):
    context = SimpleNamespace(
        triggered_id=triggered_id,
        triggered=[{"value": triggered_value}],
    )

    with patch(_CALLBACK_PATH, context):
        return update_retained_graph_selections(
            selected_cell,
            0,
            [],
            retained,
        )


def test_first_selection_is_retained():
    result = _invoke(
        "selected-selection-cell",
        SENSOR_A,
        [],
    )

    assert result == [SENSOR_A]


def test_second_selection_preserves_first():
    result = _invoke(
        "selected-selection-cell",
        SENSOR_B,
        [SENSOR_A],
    )

    assert result == [SENSOR_A, SENSOR_B]


def test_duplicate_selection_is_not_added():
    result = _invoke(
        "selected-selection-cell",
        SENSOR_A,
        [SENSOR_A],
    )

    assert result == [SENSOR_A]


def test_network_selection_clear_preserves_retained_graphs():
    result = _invoke(
        "selected-selection-cell",
        None,
        [SENSOR_A, SENSOR_B],
    )

    assert result is no_update


def test_clear_all_removes_retained_graphs():
    result = _invoke(
        "clear-retained-graphs",
        SENSOR_A,
        [SENSOR_A, SENSOR_B],
    )

    assert result == []


def test_invalid_selection_does_not_change_collection():
    result = _invoke(
        "selected-selection-cell",
        {"group": "sym_voltage_sensor", "id": "invalid"},
        [SENSOR_A],
    )

    assert result is no_update


def test_unrelated_trigger_does_not_change_collection():
    result = _invoke(
        None,
        SENSOR_A,
        [SENSOR_B],
    )

    assert result is no_update


def test_remove_first_graph_preserves_second():
    result = _invoke(
        {"type": "remove-retained-graph", "index": 0},
        None,
        [SENSOR_A, SENSOR_B],
        triggered_value=1,
    )

    assert result == [SENSOR_B]


def test_remove_second_graph_preserves_first():
    result = _invoke(
        {"type": "remove-retained-graph", "index": 1},
        None,
        [SENSOR_A, SENSOR_B],
        triggered_value=1,
    )

    assert result == [SENSOR_A]


def test_newly_created_remove_button_does_not_remove_graph():
    result = _invoke(
        {"type": "remove-retained-graph", "index": 0},
        None,
        [SENSOR_A],
        triggered_value=0,
    )

    assert result is no_update


def test_invalid_remove_index_does_not_change_collection():
    result = _invoke(
        {"type": "remove-retained-graph", "index": 5},
        None,
        [SENSOR_A],
        triggered_value=1,
    )

    assert result is no_update

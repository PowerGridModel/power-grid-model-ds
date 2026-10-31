# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for retained graph selections."""

from power_grid_model_ds._core.visualizer.graph_selections import (
    add_graph_selection,
    clear_graph_selections,
    remove_graph_selection,
)

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


def test_add_first_graph():
    selections = add_graph_selection([], SENSOR_A)

    assert selections == [SENSOR_A]


def test_add_second_graph_preserves_first():
    selections = add_graph_selection([SENSOR_A], SENSOR_B)

    assert selections == [SENSOR_A, SENSOR_B]


def test_duplicate_selection_is_not_added():
    selections = add_graph_selection([SENSOR_A], SENSOR_A)

    assert selections == [SENSOR_A]


def test_remove_graph_preserves_other_graph():
    selections = remove_graph_selection(
        [SENSOR_A, SENSOR_B],
        SENSOR_A,
    )

    assert selections == [SENSOR_B]


def test_clear_graphs():
    assert clear_graph_selections() == []


def test_add_does_not_mutate_existing_collection():
    original = [SENSOR_A]

    updated = add_graph_selection(original, SENSOR_B)

    assert original == [SENSOR_A]
    assert updated == [SENSOR_A, SENSOR_B]


def test_remove_does_not_mutate_existing_collection():
    original = [SENSOR_A, SENSOR_B]

    updated = remove_graph_selection(original, SENSOR_A)

    assert original == [SENSOR_A, SENSOR_B]
    assert updated == [SENSOR_B]


def test_remove_middle_graph_preserves_order():
    sensor_c = {
        "group": "sym_voltage_sensor",
        "id": 103,
        "column": "u_measured",
    }

    selections = [SENSOR_A, SENSOR_B, sensor_c]

    result = remove_graph_selection(selections, SENSOR_B)

    assert result == [SENSOR_A, sensor_c]
    assert selections == [SENSOR_A, SENSOR_B, sensor_c]

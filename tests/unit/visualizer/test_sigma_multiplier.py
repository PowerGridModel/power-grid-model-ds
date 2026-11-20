# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Unit tests for the configurable voltage-comparison sigma multiplier."""

from copy import deepcopy

import numpy as np
import pytest
from dash.exceptions import PreventUpdate

from power_grid_model_ds._core.visualizer.callbacks.element_selection import (
    update_sigma_multiplier_visibility,
    update_voltage_sigma_bands,
)


@pytest.fixture
def comparison_figure():
    """A serialized four-trace voltage comparison with original sigma values."""
    return {
        "data": [
            {"name": "Lower sigma bound", "y": [224.0, 226.0, 224.0]},
            {"name": "Measurement +/- 3 sigma", "y": [236.0, 244.0, 236.0]},
            {"name": "Measured voltage", "y": [230.0, 235.0, 230.0]},
            {"name": "Calculated voltage", "y": [229.0, 231.0, 228.0]},
        ],
        "layout": {
            "meta": {
                "comparison_type": "sym_voltage_sensor",
                "sensor_id": 17,
                "sigma": [2.0, 3.0, 2.0],
                "measured": [230.0, 235.0, 230.0],
            }
        },
    }


@pytest.fixture
def selected_cell():
    return {"group": "sym_voltage_sensor", "id": 17, "column": "u_measured"}


def _patch_assignments(patch):
    """Return the assigned locations and values from a Dash Patch."""
    operations = patch.to_plotly_json()["operations"]
    assert all(operation["operation"] == "Assign" for operation in operations)
    return {tuple(operation["location"]): operation["params"]["value"] for operation in operations}


@pytest.mark.parametrize(
    ("multiplier", "expected_lower", "expected_upper"),
    [
        (0, [230.0, 235.0, 230.0], [230.0, 235.0, 230.0]),
        (2, [226.0, 229.0, 226.0], [234.0, 241.0, 234.0]),
        (4, [222.0, 223.0, 222.0], [238.0, 247.0, 238.0]),
        (0.5, [229.0, 233.5, 229.0], [231.0, 236.5, 231.0]),
    ],
)
def test_multiplier_updates_only_sigma_bands(
    comparison_figure, selected_cell, multiplier, expected_lower, expected_upper
):
    original = deepcopy(comparison_figure)
    assignments = _patch_assignments(update_voltage_sigma_bands(multiplier, comparison_figure, selected_cell))

    assert set(assignments) == {
        ("data", 0, "y"),
        ("data", 1, "y"),
        ("data", 1, "name"),
    }
    np.testing.assert_allclose(assignments[("data", 0, "y")], expected_lower)
    np.testing.assert_allclose(assignments[("data", 1, "y")], expected_upper)
    assert assignments[("data", 1, "name")] == f"Measurement +/- {multiplier:g} sigma"
    assert comparison_figure == original


def test_repeated_changes_use_original_sigma(comparison_figure, selected_cell):
    """A previous multiplier must not rescale the next result."""
    first = _patch_assignments(update_voltage_sigma_bands(2, comparison_figure, selected_cell))
    second = _patch_assignments(update_voltage_sigma_bands(4, comparison_figure, selected_cell))

    np.testing.assert_allclose(first[("data", 0, "y")], [226, 229, 226])
    np.testing.assert_allclose(second[("data", 0, "y")], [222, 223, 222])
    np.testing.assert_allclose(second[("data", 1, "y")], [238, 247, 238])


@pytest.mark.parametrize("invalid", [None, -1, -0.1, float("nan"), float("inf"), -float("inf"), True, "2"])
def test_invalid_multiplier_is_ignored(comparison_figure, selected_cell, invalid):
    with pytest.raises(PreventUpdate):
        update_voltage_sigma_bands(invalid, comparison_figure, selected_cell)


@pytest.mark.parametrize(
    "cell",
    [
        None,
        {"group": "sym_voltage_sensor", "id": 18, "column": "u_measured"},
        {"group": "sym_voltage_sensor", "id": 17, "column": "sigma"},
        {"group": "node", "id": 17, "column": "u_measured"},
    ],
)
def test_unrelated_selection_is_ignored(comparison_figure, cell):
    with pytest.raises(PreventUpdate):
        update_voltage_sigma_bands(2, comparison_figure, cell)


def test_non_comparison_graph_is_ignored(comparison_figure, selected_cell):
    comparison_figure["layout"].pop("meta")
    with pytest.raises(PreventUpdate):
        update_voltage_sigma_bands(2, comparison_figure, selected_cell)


def test_missing_sigma_values_remain_missing(comparison_figure, selected_cell):
    comparison_figure["layout"]["meta"]["sigma"] = [2.0, None, 2.0]
    assignments = _patch_assignments(update_voltage_sigma_bands(2, comparison_figure, selected_cell))
    assert np.isnan(assignments[("data", 0, "y")][1])
    assert np.isnan(assignments[("data", 1, "y")][1])
    assert assignments[("data", 0, "y")][0] == 226
    assert assignments[("data", 0, "y")][2] == 226


def test_visibility_only_for_visible_comparison(comparison_figure):
    assert update_sigma_multiplier_visibility(comparison_figure, {"display": "block"})["display"] == "block"
    assert update_sigma_multiplier_visibility(comparison_figure, {"display": "none"}) == {"display": "none"}
    assert update_sigma_multiplier_visibility({}, {"display": "block"}) == {"display": "none"}
    assert update_sigma_multiplier_visibility(comparison_figure, None) == {"display": "none"}


def test_visibility_hides_for_fallback_graph(comparison_figure):
    comparison_figure["layout"].pop("meta")
    assert update_sigma_multiplier_visibility(comparison_figure, {"display": "block"}) == {"display": "none"}


def test_plotly_encoded_y_values_do_not_block_multiplier(comparison_figure, selected_cell):
    """The callback uses source data, not Plotly's encoded trace arrays."""
    comparison_figure["data"][2]["y"] = {"dtype": "f8", "bdata": "opaque"}
    assignments = _patch_assignments(update_voltage_sigma_bands(2, comparison_figure, selected_cell))
    np.testing.assert_allclose(assignments[("data", 0, "y")], [226, 229, 226])
    np.testing.assert_allclose(assignments[("data", 1, "y")], [234, 241, 234])

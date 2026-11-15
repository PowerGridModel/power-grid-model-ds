# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for symmetric voltage measurement comparisons."""

from types import SimpleNamespace

import numpy as np
import pytest
from numpy.testing import assert_array_equal
from power_grid_model import ComponentType, initialize_array

from power_grid_model_ds._core.visualizer.measurement_comparison import (
    VoltageComparison,
    get_symmetric_voltage_comparison,
    get_voltage_sigma_bounds,
)


@pytest.fixture
def grid():
    """Create a minimal grid with one symmetric voltage sensor."""
    sensors = SimpleNamespace(
        id=np.array([101], dtype=np.int32),
        measured_object=np.array([10], dtype=np.int32),
        u_measured=np.array([230.0]),
        u_sigma=np.array([2.0]),
    )
    return SimpleNamespace(sym_voltage_sensor=sensors)


@pytest.fixture
def output_data():
    """Create three scenarios containing node voltage results."""
    nodes = initialize_array("sym_output", "node", (3, 1))
    nodes["id"] = 10
    nodes["u"][:, 0] = [229.0, 231.0, 228.0]
    return {ComponentType.node: nodes}


def test_base_measurements_are_repeated_across_scenarios(grid, output_data):
    """Without updates, each scenario uses the base sensor values."""
    result = get_symmetric_voltage_comparison(
        grid=grid,
        update_data=None,
        output_data=output_data,
        sensor_id=101,
    )

    assert result is not None
    assert_array_equal(result.scenario_indices, [0, 1, 2])
    assert_array_equal(result.measured, [230.0, 230.0, 230.0])
    assert_array_equal(result.estimated, [229.0, 231.0, 228.0])
    assert_array_equal(result.sigma, [2.0, 2.0, 2.0])


def test_measurement_update_affects_only_its_scenario(grid, output_data):
    """A measurement update must not change other scenarios."""
    updates = initialize_array("update", "sym_voltage_sensor", (3, 1))
    updates["id"] = 101
    updates["u_measured"][1, 0] = 235.0

    result = get_symmetric_voltage_comparison(
        grid,
        {ComponentType.sym_voltage_sensor: updates},
        output_data,
        101,
    )

    assert result is not None
    assert_array_equal(result.measured, [230.0, 235.0, 230.0])
    assert_array_equal(result.estimated, [229.0, 231.0, 228.0])
    assert_array_equal(result.sigma, [2.0, 2.0, 2.0])


def test_sigma_update_affects_only_its_scenario(grid, output_data):
    """Sigma updates must be independent of measurement updates."""
    updates = initialize_array("update", "sym_voltage_sensor", (3, 1))
    updates["id"] = 101
    updates["u_sigma"][2, 0] = 3.5

    result = get_symmetric_voltage_comparison(
        grid,
        {ComponentType.sym_voltage_sensor: updates},
        output_data,
        101,
    )

    assert result is not None
    assert_array_equal(result.measured, [230.0, 230.0, 230.0])
    assert_array_equal(result.sigma, [2.0, 2.0, 3.5])


def test_nan_updates_preserve_base_values(grid, output_data):
    """Unspecified floating-point updates retain base values."""
    updates = initialize_array("update", "sym_voltage_sensor", (3, 1))
    updates["id"] = 101

    result = get_symmetric_voltage_comparison(
        grid,
        {ComponentType.sym_voltage_sensor: updates},
        output_data,
        101,
    )

    assert result is not None
    assert_array_equal(result.measured, [230.0, 230.0, 230.0])
    assert_array_equal(result.sigma, [2.0, 2.0, 2.0])


def test_missing_node_result_preserves_scenario_position(grid, output_data):
    """A missing node result must not shift later scenarios."""
    nodes = output_data[ComponentType.node].copy()
    nodes["id"][1, 0] = 99

    result = get_symmetric_voltage_comparison(
        grid,
        None,
        {ComponentType.node: nodes},
        101,
    )

    assert result is not None
    assert_array_equal(result.scenario_indices, [0, 1, 2])
    assert_array_equal(result.estimated, [229.0, np.nan, 228.0])


def test_unknown_sensor_raises_value_error(grid, output_data):
    """An unknown sensor ID must be rejected."""
    with pytest.raises(ValueError, match="Voltage sensor with ID 999 was not found"):
        get_symmetric_voltage_comparison(grid, None, output_data, 999)


@pytest.mark.parametrize("missing_output", [None, {}])
def test_missing_node_output_returns_none(grid, missing_output):
    """Missing node output means no comparison can be prepared."""
    result = get_symmetric_voltage_comparison(
        grid,
        None,
        missing_output,
        101,
    )

    assert result is None


def test_output_without_node_component_returns_none(grid):
    """Other output components do not provide the required node voltage."""
    result = get_symmetric_voltage_comparison(
        grid,
        None,
        {ComponentType.line: initialize_array("sym_output", "line", (3, 1))},
        101,
    )

    assert result is None


def test_comparison_does_not_modify_input_data(grid, output_data):
    """Preparing a comparison must not mutate the supplied data."""
    updates = initialize_array("update", "sym_voltage_sensor", (3, 1))
    updates["id"] = 101
    updates["u_measured"][1, 0] = 235.0

    original_updates = updates.copy()
    original_nodes = output_data[ComponentType.node].copy()
    original_measurements = grid.sym_voltage_sensor.u_measured.copy()

    get_symmetric_voltage_comparison(
        grid,
        {ComponentType.sym_voltage_sensor: updates},
        output_data,
        101,
    )

    for field in updates.dtype.names:
        assert_array_equal(
            updates[field],
            original_updates[field],
        )

    for field in original_nodes.dtype.names:
        assert_array_equal(
            output_data[ComponentType.node][field],
            original_nodes[field],
        )

    assert_array_equal(
        grid.sym_voltage_sensor.u_measured,
        original_measurements,
    )


@pytest.mark.parametrize(
    ("multiplier", "expected_lower", "expected_upper"),
    [
        (0.0, [230.0, 235.0], [230.0, 235.0]),
        (1.0, [228.0, 232.0], [232.0, 238.0]),
        (2.0, [226.0, 229.0], [234.0, 241.0]),
        (3.0, [224.0, 226.0], [236.0, 244.0]),
    ],
)
def test_voltage_sigma_bounds(
    multiplier,
    expected_lower,
    expected_upper,
):
    comparison = VoltageComparison(
        scenario_indices=np.array([0, 1]),
        measured=np.array([230.0, 235.0]),
        estimated=np.array([231.0, 234.0]),
        sigma=np.array([2.0, 3.0]),
    )

    lower, upper = get_voltage_sigma_bounds(comparison, multiplier)

    np.testing.assert_allclose(lower, expected_lower)
    np.testing.assert_allclose(upper, expected_upper)


@pytest.mark.parametrize("multiplier", [-1.0, np.nan, np.inf])
def test_voltage_sigma_bounds_reject_invalid_multiplier(multiplier):
    comparison = VoltageComparison(
        scenario_indices=np.array([0]),
        measured=np.array([230.0]),
        estimated=np.array([231.0]),
        sigma=np.array([2.0]),
    )

    with pytest.raises(ValueError, match="Sigma multiplier"):
        get_voltage_sigma_bounds(comparison, multiplier)


def test_voltage_sigma_bounds_preserve_missing_sigma():
    comparison = VoltageComparison(
        scenario_indices=np.array([0, 1]),
        measured=np.array([230.0, 235.0]),
        estimated=np.array([231.0, 234.0]),
        sigma=np.array([2.0, np.nan]),
    )

    lower, upper = get_voltage_sigma_bounds(comparison, 2.0)

    np.testing.assert_allclose(lower, [226.0, np.nan])
    np.testing.assert_allclose(upper, [234.0, np.nan])


@pytest.mark.parametrize("sigma", [np.inf, -np.inf])
def test_voltage_sigma_bounds_omit_infinite_sigma(sigma):
    """Infinite sigma must not produce a drawable uncertainty band."""
    comparison = VoltageComparison(
        scenario_indices=np.array([0, 1]),
        measured=np.array([230.0, 235.0]),
        estimated=np.array([229.0, 234.0]),
        sigma=np.array([2.0, sigma]),
    )

    lower, upper = get_voltage_sigma_bounds(comparison, multiplier=2.0)

    np.testing.assert_allclose(lower, [226.0, np.nan])
    np.testing.assert_allclose(upper, [234.0, np.nan])


def test_get_voltage_sigma_bounds_accepts_nan_sigma():
    comparison = VoltageComparison(
        scenario_indices=np.array([0]),
        measured=np.array([1.0]),
        estimated=np.array([1.0]),
        sigma=np.array([np.nan]),
    )

    lower, upper = get_voltage_sigma_bounds(comparison, multiplier=2.0)

    assert np.isnan(lower[0])
    assert np.isnan(upper[0])

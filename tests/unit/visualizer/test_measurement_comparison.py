# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for symmetric voltage measurement comparisons."""

from types import SimpleNamespace

import numpy as np
import pytest
from numpy.testing import assert_array_equal
from power_grid_model import ComponentType, MeasuredTerminalType, initialize_array

from power_grid_model_ds._core.visualizer.measurement_comparison import (
    VoltageComparison,
    get_symmetric_power_comparison,
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

    assert_array_equal(result.scenario_indices, [0, 1, 2])
    assert_array_equal(result.estimated, [229.0, np.nan, 228.0])


def test_unknown_sensor_raises_value_error(grid, output_data):
    """An unknown sensor ID must be rejected."""
    with pytest.raises(ValueError, match="Voltage sensor with ID 999 was not found"):
        get_symmetric_voltage_comparison(grid, None, output_data, 999)


@pytest.mark.parametrize("missing_output", [None, {}])
def test_missing_node_output_returns_none(grid, missing_output):
    assert get_symmetric_voltage_comparison(grid, None, missing_output, 101) is None


def test_output_without_node_component_returns_none(grid):
    other = initialize_array("sym_output", "line", (3, 1))
    assert get_symmetric_voltage_comparison(grid, None, {ComponentType.line: other}, 101) is None


def test_missing_sensor_update_row_preserves_base_and_alignment(grid, output_data):
    updates = initialize_array("update", "sym_voltage_sensor", (3, 1))
    updates["id"] = 101
    updates["id"][1, 0] = 999
    updates["u_measured"][2, 0] = 237.0
    comparison = get_symmetric_voltage_comparison(grid, {ComponentType.sym_voltage_sensor: updates}, output_data, 101)
    assert comparison is not None
    assert_array_equal(comparison.scenario_indices, [0, 1, 2])
    assert_array_equal(comparison.measured, [230.0, 230.0, 237.0])


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

    # Compare structured arrays field by field so NaN values
    # are treated as equal when they occur in the same positions.
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
    comparison = VoltageComparison(
        scenario_indices=np.array([0, 1]),
        measured=np.array([230.0, 235.0]),
        estimated=np.array([229.0, 234.0]),
        sigma=np.array([2.0, sigma]),
    )
    lower, upper = get_voltage_sigma_bounds(comparison, multiplier=2.0)
    np.testing.assert_allclose(lower, [226.0, np.nan])
    np.testing.assert_allclose(upper, [234.0, np.nan])


@pytest.fixture
def power_grid():
    """One symmetric source-terminal power sensor."""
    sensors = SimpleNamespace(
        id=np.array([201], dtype=np.int32),
        measured_object=np.array([20], dtype=np.int32),
        measured_terminal_type=np.array([MeasuredTerminalType.source.value], dtype=np.int32),
        p_measured=np.array([10.0]),
        q_measured=np.array([5.0]),
        p_sigma=np.array([2.0]),
        q_sigma=np.array([1.0]),
        power_sigma=np.array([999.0]),
    )
    return SimpleNamespace(sym_power_sensor=sensors)


@pytest.fixture
def power_output():
    source = initialize_array("sym_output", "source", (3, 1))
    source["id"] = 20
    source["p"][:, 0] = [9.0, 11.0, 8.0]
    source["q"][:, 0] = [4.0, 6.0, 3.0]
    return {ComponentType.source: source}


@pytest.mark.parametrize(
    ("attribute", "estimated", "sigma"),
    [
        ("p_measured", [9.0, 11.0, 8.0], [2.0, 2.0, 2.0]),
        ("q_measured", [4.0, 6.0, 3.0], [1.0, 1.0, 1.0]),
    ],
)
def test_power_comparison_uses_individual_sigma(power_grid, power_output, attribute, estimated, sigma):
    result = get_symmetric_power_comparison(power_grid, None, power_output, 201, attribute)

    assert_array_equal(result.scenario_indices, [0, 1, 2])
    assert_array_equal(result.estimated, estimated)
    assert_array_equal(result.sigma, sigma)


def test_power_updates_preserve_other_scenarios(power_grid, power_output):
    updates = initialize_array("update", "sym_power_sensor", (3, 1))
    updates["id"] = 201
    updates["p_measured"][1, 0] = 15.0
    updates["p_sigma"][2, 0] = 4.0

    result = get_symmetric_power_comparison(
        power_grid,
        {ComponentType.sym_power_sensor: updates},
        power_output,
        201,
        "p_measured",
    )

    assert_array_equal(result.measured, [10.0, 15.0, 10.0])
    assert_array_equal(result.sigma, [2.0, 2.0, 4.0])


def test_missing_power_result_preserves_scenario(power_grid, power_output):
    source = power_output[ComponentType.source].copy()
    source["id"][1, 0] = 999

    result = get_symmetric_power_comparison(
        power_grid,
        None,
        {ComponentType.source: source},
        201,
        "p_measured",
    )

    assert_array_equal(result.estimated, [9.0, np.nan, 8.0])


def test_power_without_sigma(power_grid, power_output):
    power_grid.sym_power_sensor.p_sigma[:] = np.nan

    result = get_symmetric_power_comparison(power_grid, None, power_output, 201, "p_measured")

    assert result.sigma is None
    assert_array_equal(result.estimated, [9.0, 11.0, 8.0])


def test_power_zero_sigma_is_preserved(power_grid, power_output):
    power_grid.sym_power_sensor.p_sigma[:] = 0.0

    result = get_symmetric_power_comparison(power_grid, None, power_output, 201, "p_measured")

    assert_array_equal(result.sigma, [0.0, 0.0, 0.0])


def test_unsupported_power_terminal(power_grid, power_output):
    power_grid.sym_power_sensor.measured_terminal_type[:] = -1

    with pytest.raises(NotImplementedError, match="terminal type"):
        get_symmetric_power_comparison(power_grid, None, power_output, 201, "p_measured")


def test_duplicate_power_output_is_rejected(power_grid):
    source = initialize_array("sym_output", "source", (2, 2))
    source["id"][:, 0] = 20
    source["id"][:, 1] = 99
    source["id"][1, 1] = 20

    with pytest.raises(ValueError, match="Duplicate source ID"):
        get_symmetric_power_comparison(
            power_grid,
            None,
            {ComponentType.source: source},
            201,
            "p_measured",
        )


def test_unknown_power_sensor_is_rejected(power_grid, power_output):
    with pytest.raises(ValueError, match="Expected exactly one power sensor"):
        get_symmetric_power_comparison(power_grid, None, power_output, 999, "p_measured")


def test_invalid_power_measurement_is_rejected(power_grid, power_output):
    with pytest.raises(ValueError, match="Unsupported power measurement"):
        get_symmetric_power_comparison(power_grid, None, power_output, 201, "power_sigma")

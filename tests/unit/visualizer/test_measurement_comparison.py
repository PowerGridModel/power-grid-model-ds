# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for generic sensor measurement comparisons."""

from types import SimpleNamespace

import numpy as np
import pytest
from numpy.testing import assert_array_equal
from power_grid_model import ComponentType, MeasuredTerminalType, initialize_array

from power_grid_model_ds._core.visualizer.measurement_comparison import (
    MeasurementData,
    get_sensor_comparison,
    get_sigma_bounds,
)


def _voltage_comparison(grid, update_data, output_data, sensor_id):
    """Exercise the generic API with symmetric voltage sensor inputs."""
    return get_sensor_comparison(
        grid, ComponentType.sym_voltage_sensor, sensor_id, "u_measured", update_data, output_data
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
    result = _voltage_comparison(
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

    result = _voltage_comparison(
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

    result = _voltage_comparison(
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

    result = _voltage_comparison(
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

    result = _voltage_comparison(
        grid,
        None,
        {ComponentType.node: nodes},
        101,
    )

    assert_array_equal(result.scenario_indices, [0, 1, 2])
    assert_array_equal(result.estimated, [229.0, np.nan, 228.0])


def test_unknown_sensor_raises_value_error(grid, output_data):
    """An unknown sensor ID must be rejected."""
    with pytest.raises(ValueError, match="Expected exactly one sensor with ID 999"):
        _voltage_comparison(grid, None, output_data, 999)


@pytest.mark.parametrize("missing_output", [None, {}])
def test_missing_node_output_returns_none(grid, missing_output):
    assert _voltage_comparison(grid, None, missing_output, 101) is None


def test_output_without_node_component_returns_none(grid):
    other = initialize_array("sym_output", "line", (3, 1))
    assert _voltage_comparison(grid, None, {ComponentType.line: other}, 101) is None


def test_missing_sensor_update_row_preserves_base_and_alignment(grid, output_data):
    updates = initialize_array("update", "sym_voltage_sensor", (3, 1))
    updates["id"] = 101
    updates["id"][1, 0] = 999
    updates["u_measured"][2, 0] = 237.0
    comparison = _voltage_comparison(grid, {ComponentType.sym_voltage_sensor: updates}, output_data, 101)
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

    _voltage_comparison(
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
    comparison = MeasurementData(
        scenario_indices=np.array([0, 1]),
        measured=np.array([230.0, 235.0]),
        estimated=np.array([231.0, 234.0]),
        sigma=np.array([2.0, 3.0]),
    )

    lower, upper = get_sigma_bounds(comparison, multiplier)
    np.testing.assert_allclose(lower, expected_lower)
    np.testing.assert_allclose(upper, expected_upper)


@pytest.mark.parametrize("multiplier", [-1.0, np.nan, np.inf])
def test_voltage_sigma_bounds_reject_invalid_multiplier(multiplier):
    comparison = MeasurementData(
        scenario_indices=np.array([0]),
        measured=np.array([230.0]),
        estimated=np.array([231.0]),
        sigma=np.array([2.0]),
    )

    with pytest.raises(ValueError, match="Sigma multiplier"):
        get_sigma_bounds(comparison, multiplier)


def test_voltage_sigma_bounds_preserve_missing_sigma():
    comparison = MeasurementData(
        scenario_indices=np.array([0, 1]),
        measured=np.array([230.0, 235.0]),
        estimated=np.array([231.0, 234.0]),
        sigma=np.array([2.0, np.nan]),
    )

    lower, upper = get_sigma_bounds(comparison, 2.0)
    np.testing.assert_allclose(lower, [226.0, np.nan])
    np.testing.assert_allclose(upper, [234.0, np.nan])


@pytest.mark.parametrize("sigma", [np.inf, -np.inf])
def test_voltage_sigma_bounds_omit_infinite_sigma(sigma):
    comparison = MeasurementData(
        scenario_indices=np.array([0, 1]),
        measured=np.array([230.0, 235.0]),
        estimated=np.array([229.0, 234.0]),
        sigma=np.array([2.0, sigma]),
    )
    lower, upper = get_sigma_bounds(comparison, multiplier=2.0)
    np.testing.assert_allclose(lower, [226.0, np.nan])
    np.testing.assert_allclose(upper, [234.0, np.nan])


def test_asymmetric_sigma_broadcast():
    comparison = MeasurementData(np.array([0, 1]), np.full((2, 3), 230.0), np.full((2, 3), 229.0), np.array([2.0, 3.0]))
    lower, upper = get_sigma_bounds(comparison, 2.0)
    assert_array_equal(lower, [[226.0] * 3, [224.0] * 3])
    assert_array_equal(upper, [[234.0] * 3, [236.0] * 3])


def test_sigma_shape_mismatch():
    comparison = MeasurementData(np.array([0, 1]), np.full((2, 3), 230.0), np.full((2, 3), 229.0), np.ones(3))
    with pytest.raises(ValueError, match="scenario counts"):
        get_sigma_bounds(comparison, 1.0)


@pytest.mark.parametrize("asymmetric", [False, True])
@pytest.mark.parametrize(
    ("kind", "quantity", "component", "terminal", "output_attr"),
    [
        ("voltage", "u", "node", None, "u"),
        ("power", "p", "source", "source", "p"),
        ("power", "q", "source", "source", "q"),
        ("current", "i", "line", "branch_from", "i_from"),
        ("power", "p", "line", "branch_from", "p_from"),
        ("power", "q", "line", "branch_to", "q_to"),
        ("power", "p", "three_winding_transformer", "branch3_1", "p_1"),
        ("power", "q", "three_winding_transformer", "branch3_2", "q_2"),
        ("current", "i", "three_winding_transformer", "branch3_3", "i_3"),
    ],
)
def test_generic_sensor_comparison(asymmetric, kind, quantity, component, terminal, output_attr):  # noqa: PLR0913, PLR0917
    """Check terminal mapping, phase values, updates and missing output alignment."""
    sensor_type = ComponentType(f"{'asym' if asymmetric else 'sym'}_{kind}_sensor")
    component_type = ComponentType(component)
    measured_attr = f"{quantity}_measured"
    sigma_attr = f"{quantity}_sigma"
    sensors = initialize_array("input", sensor_type, 1)
    sensors["id"] = 101
    sensors["measured_object"] = 10
    if terminal is not None:
        sensors["measured_terminal_type"] = getattr(MeasuredTerminalType, terminal)
    base = np.array([100.0, 110.0, 120.0]) if asymmetric else np.array(100.0)
    sigma = np.array([2.0, 3.0, 4.0]) if asymmetric and kind == "power" else np.array(2.0)
    sensors[measured_attr][0] = base
    sensors[sigma_attr][0] = sigma
    grid = SimpleNamespace(
        **{sensor_type.value: SimpleNamespace(**{name: sensors[name] for name in sensors.dtype.names})}
    )
    setattr(grid, component, SimpleNamespace(id=np.array([10])))
    updates = initialize_array("update", sensor_type, (3, 1))
    updates["id"][:, 0] = [101, 999, 101]
    updates[measured_attr][2, 0] = base + 5
    output = initialize_array("asym_output" if asymmetric else "sym_output", component_type, (3, 1))
    output["id"][:, 0] = [10, 999, 10]
    output[output_attr][0, 0] = base - 1
    output[output_attr][2, 0] = base + 3
    result = get_sensor_comparison(
        grid, sensor_type, 101, measured_attr, {sensor_type: updates}, {component_type: output}
    )
    assert result is not None
    assert_array_equal(result.scenario_indices, [0, 1, 2])
    assert_array_equal(result.measured, np.stack([base, base, base + 5]))
    assert_array_equal(result.estimated, np.stack([base - 1, np.full_like(base, np.nan), base + 3]))
    assert_array_equal(result.sigma, np.stack([sigma, sigma, sigma]))
    lower, upper = get_sigma_bounds(result, 2.0)
    assert_array_equal(lower, result.measured - 2 * sigma)
    assert_array_equal(upper, result.measured + 2 * sigma)


@pytest.mark.parametrize("attribute", ["u_angle_measured", "i_angle_measured"])
def test_unsupported_angle_attribute(grid, output_data, attribute):
    """Angle comparisons remain outside this PR."""
    assert get_sensor_comparison(grid, ComponentType.sym_voltage_sensor, 101, attribute, None, output_data) is None


def test_duplicate_base_sensor(grid, output_data):
    """Reject ambiguous sensor identities."""
    grid.sym_voltage_sensor.id = np.array([101, 101])
    with pytest.raises(ValueError, match="exactly one sensor"):
        _voltage_comparison(grid, None, output_data, 101)


def test_duplicate_output_component(grid):
    """Reject ambiguous output rows in one scenario."""
    nodes = initialize_array("sym_output", "node", (3, 2))
    nodes["id"] = 10
    with pytest.raises(ValueError, match="Duplicate component"):
        _voltage_comparison(grid, None, {ComponentType.node: nodes}, 101)


def test_duplicate_sensor_updates(grid, output_data):
    """Reject ambiguous sensor updates in one scenario."""
    updates = initialize_array("update", "sym_voltage_sensor", (3, 2))
    updates["id"] = 101
    with pytest.raises(ValueError, match="Duplicate sensor"):
        _voltage_comparison(grid, {ComponentType.sym_voltage_sensor: updates}, output_data, 101)


def test_scenario_count_mismatch(grid, output_data):
    """Reject inconsistent batch lengths."""
    updates = initialize_array("update", "sym_voltage_sensor", (2, 1))
    updates["id"] = 101
    with pytest.raises(ValueError, match="scenario count"):
        _voltage_comparison(grid, {ComponentType.sym_voltage_sensor: updates}, output_data, 101)


def test_measurement_output_shape_mismatch(grid):
    """Reject scalar measurements paired with phased output."""
    nodes = initialize_array("asym_output", "node", (3, 1))
    nodes["id"] = 10
    with pytest.raises(ValueError, match="shapes differ"):
        _voltage_comparison(grid, None, {ComponentType.node: nodes}, 101)

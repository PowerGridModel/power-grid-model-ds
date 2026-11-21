# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Integration tests for voltage measurement comparison."""

from types import SimpleNamespace

import numpy as np
from power_grid_model import ComponentType, PowerGridModel, initialize_array

from power_grid_model_ds._core.visualizer.measurement_comparison import (
    get_symmetric_voltage_comparison,
)


def test_voltage_comparison_matches_real_state_estimation():
    """Compare sensor measurements with actual state-estimation output."""
    nodes = initialize_array("input", "node", 1)
    nodes["id"] = 10
    nodes["u_rated"] = 230.0

    sources = initialize_array("input", "source", 1)
    sources["id"] = 20
    sources["node"] = 10
    sources["status"] = 1
    sources["u_ref"] = 1.0

    sensors = initialize_array("input", "sym_voltage_sensor", 2)
    sensors["id"] = [101, 102]
    sensors["measured_object"] = [10, 10]
    sensors["u_measured"] = [230.0, 234.0]
    sensors["u_sigma"] = [2.0, 2.0]

    input_data = {
        ComponentType.node: nodes,
        ComponentType.source: sources,
        ComponentType.sym_voltage_sensor: sensors,
    }

    model = PowerGridModel(input_data=input_data)
    result = model.calculate_state_estimation(symmetric=True)

    node_output = result[ComponentType.node]
    sensor_output = result[ComponentType.sym_voltage_sensor]

    # The comparison helper accepts dense batch output.
    # Wrap this single calculation as a one-scenario batch.
    output_data = {ComponentType.node: node_output[np.newaxis, :]}

    # Provide the sensor fields used by the comparison helper.
    grid = SimpleNamespace(
        sym_voltage_sensor=SimpleNamespace(
            id=sensors["id"],
            measured_object=sensors["measured_object"],
            u_measured=sensors["u_measured"],
            u_sigma=sensors["u_sigma"],
        )
    )

    for sensor_id, expected_measurement in (
        (101, 230.0),
        (102, 234.0),
    ):
        comparison = get_symmetric_voltage_comparison(
            grid=grid,
            update_data=None,
            output_data=output_data,
            sensor_id=sensor_id,
        )

        np.testing.assert_array_equal(
            comparison.scenario_indices,
            [0],
        )

        np.testing.assert_allclose(
            comparison.measured,
            [expected_measurement],
        )

        np.testing.assert_allclose(
            comparison.estimated,
            [232.0],
            atol=1e-8,
        )

        np.testing.assert_allclose(
            comparison.sigma,
            [2.0],
        )

        matching_output = sensor_output[sensor_output["id"] == sensor_id]

        assert len(matching_output) == 1

        residual = float(matching_output["u_residual"][0])

        np.testing.assert_allclose(
            comparison.measured[0] - comparison.estimated[0],
            residual,
            atol=1e-8,
        )


def test_voltage_comparison_matches_batch_state_estimation():
    """Compare measurements and estimates across real batch scenarios."""
    nodes = initialize_array("input", "node", 1)
    nodes["id"] = 10
    nodes["u_rated"] = 230.0

    sources = initialize_array("input", "source", 1)
    sources["id"] = 20
    sources["node"] = 10
    sources["status"] = 1
    sources["u_ref"] = 1.0

    sensors = initialize_array("input", "sym_voltage_sensor", 2)
    sensors["id"] = [101, 102]
    sensors["measured_object"] = [10, 10]
    sensors["u_measured"] = [230.0, 234.0]
    sensors["u_sigma"] = [2.0, 2.0]

    input_data = {
        ComponentType.node: nodes,
        ComponentType.source: sources,
        ComponentType.sym_voltage_sensor: sensors,
    }

    # Change sensor 101 in two calculation scenarios.
    updates = initialize_array("update", "sym_voltage_sensor", (2, 1))
    updates["id"] = 101
    updates["u_measured"][:, 0] = [230.0, 232.0]

    update_data = {
        ComponentType.sym_voltage_sensor: updates,
    }

    model = PowerGridModel(input_data=input_data)
    result = model.calculate_state_estimation(
        symmetric=True,
        update_data=update_data,
    )

    grid = SimpleNamespace(
        sym_voltage_sensor=SimpleNamespace(
            id=sensors["id"],
            measured_object=sensors["measured_object"],
            u_measured=sensors["u_measured"],
            u_sigma=sensors["u_sigma"],
        )
    )

    comparison = get_symmetric_voltage_comparison(
        grid=grid,
        update_data=update_data,
        output_data={ComponentType.node: result[ComponentType.node]},
        sensor_id=101,
    )

    np.testing.assert_array_equal(
        comparison.scenario_indices,
        [0, 1],
    )
    np.testing.assert_allclose(
        comparison.measured,
        [230.0, 232.0],
    )
    np.testing.assert_allclose(
        comparison.sigma,
        [2.0, 2.0],
    )

    # With equal measurement uncertainties, the expected
    # node estimates are the averages of both sensor readings.
    np.testing.assert_allclose(
        comparison.estimated,
        [232.0, 233.0],
        atol=1e-8,
    )

    sensor_output = result[ComponentType.sym_voltage_sensor]

    for scenario_index in range(2):
        matches = sensor_output[scenario_index][sensor_output[scenario_index]["id"] == 101]
        assert len(matches) == 1

        np.testing.assert_allclose(
            comparison.measured[scenario_index] - comparison.estimated[scenario_index],
            matches["u_residual"][0],
            atol=1e-8,
        )

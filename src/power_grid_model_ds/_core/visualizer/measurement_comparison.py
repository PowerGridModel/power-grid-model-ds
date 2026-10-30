# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Prepare symmetric voltage measurement comparisons."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from power_grid_model import ComponentType
from power_grid_model.data_types import BatchDataset

from power_grid_model_ds import Grid

DENSE_BATCH_NDIM = 2


@dataclass(frozen=True)
class VoltageComparison:
    """Measured and calculated voltages aligned by scenario."""

    scenario_indices: NDArray[np.intp]
    measured: NDArray[np.float64]
    estimated: NDArray[np.float64]
    sigma: NDArray[np.float64]


def _get_estimated_voltages(node_output: NDArray, node_id: int) -> NDArray[np.float64]:
    """Return the calculated node voltage for each scenario.

    Missing node results remain NaN to preserve scenario alignment.
    """
    if node_output.ndim != DENSE_BATCH_NDIM:
        raise ValueError("Expected a dense batch node output array")

    if node_output.dtype.names is None or not {"id", "u"}.issubset(node_output.dtype.names):
        raise ValueError("Node output must contain 'id' and 'u' fields")

    estimated = np.full(node_output.shape[0], np.nan, dtype=np.float64)

    for scenario_index, scenario in enumerate(node_output):
        matches = scenario[scenario["id"] == node_id]

        if len(matches) > 1:
            raise ValueError(f"Duplicate node ID {node_id} in output")

        if len(matches) == 1:
            estimated[scenario_index] = matches["u"][0]

    return estimated


def _apply_sensor_update(
    sensor_updates: NDArray,
    scenario_index: int,
    sensor_id: int,
    measured: NDArray[np.float64],
    sigma: NDArray[np.float64],
) -> None:
    """Apply explicitly specified measurement and sigma updates for one scenario."""
    scenario_updates = sensor_updates[scenario_index]
    matches = scenario_updates[scenario_updates["id"] == sensor_id]

    if len(matches) > 1:
        raise ValueError(f"Duplicate sensor ID {sensor_id} in updates")

    if len(matches) == 0:
        return

    update = matches[0]

    for attribute, target in (
        ("u_measured", measured),
        ("u_sigma", sigma),
    ):
        if attribute not in sensor_updates.dtype.names:
            continue

        value = float(update[attribute])

        # Power Grid Model update arrays use NaN for unspecified
        # floating-point attributes. Preserve the base value.
        if not np.isnan(value):
            target[scenario_index] = value


def _apply_sensor_updates(
    update_data: BatchDataset | None,
    scenario_count: int,
    sensor_id: int,
    measured: NDArray[np.float64],
    sigma: NDArray[np.float64],
) -> None:
    """Apply available symmetric voltage sensor updates across scenarios."""
    if update_data is None or ComponentType.sym_voltage_sensor not in update_data:
        return

    sensor_updates = update_data[ComponentType.sym_voltage_sensor]

    if sensor_updates.ndim != DENSE_BATCH_NDIM:
        raise ValueError("Expected a dense batch sensor update array")

    if sensor_updates.shape[0] != scenario_count:
        raise ValueError("Sensor updates must match the output scenario count")

    if sensor_updates.dtype.names is None or "id" not in sensor_updates.dtype.names:
        raise ValueError("Sensor updates must contain an 'id' field")

    for scenario_index in range(scenario_count):
        _apply_sensor_update(
            sensor_updates,
            scenario_index,
            sensor_id,
            measured,
            sigma,
        )


def get_symmetric_voltage_comparison(
    grid: Grid,
    update_data: BatchDataset | None,
    output_data: BatchDataset,
    sensor_id: int,
) -> VoltageComparison:
    """Prepare measured and calculated voltage values for one sensor.

    The function supports dense batch datasets. Measurements and sigma
    values start from the base grid and are overridden by explicitly
    specified sensor updates.

    Calculated voltages are retrieved from the corresponding node
    output using the sensor's measured_object reference.

    Scenario positions are preserved. Missing node results remain NaN.

    Args:
        grid: Base grid containing the symmetric voltage sensor.
        update_data: Optional dense batch updates.
        output_data: Dense batch calculation results.
        sensor_id: ID of the symmetric voltage sensor.

    Returns:
        VoltageComparison containing aligned scenario indices,
        measured voltages, calculated voltages, and sigma values.

    Raises:
        ValueError: If the sensor is missing or duplicated, or if
            the supplied batch arrays have invalid structures.
    """
    sensors = grid.sym_voltage_sensor
    sensor_matches = np.flatnonzero(sensors.id == sensor_id)

    if sensor_matches.size != 1:
        raise ValueError(f"Expected exactly one voltage sensor with ID {sensor_id}")

    sensor_index = int(sensor_matches[0])
    node_id = int(sensors.measured_object[sensor_index])

    if ComponentType.node not in output_data:
        raise ValueError("Node output is required for voltage comparison")

    node_output = output_data[ComponentType.node]

    # Validate output and determine the number of scenarios.
    estimated = _get_estimated_voltages(node_output, node_id)
    scenario_count = len(estimated)
    scenario_indices = np.arange(scenario_count, dtype=np.intp)

    # Start with the base-grid sensor values for every scenario.
    measured = np.full(
        scenario_count,
        float(sensors.u_measured[sensor_index]),
        dtype=np.float64,
    )
    sigma = np.full(
        scenario_count,
        float(sensors.u_sigma[sensor_index]),
        dtype=np.float64,
    )

    # Apply explicitly specified scenario-specific sensor updates.
    _apply_sensor_updates(
        update_data,
        scenario_count,
        sensor_id,
        measured,
        sigma,
    )

    return VoltageComparison(
        scenario_indices=scenario_indices,
        measured=measured,
        estimated=estimated,
        sigma=sigma,
    )


def get_voltage_sigma_bounds(
    comparison: VoltageComparison,
    multiplier: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Calculate measurement-centred voltage uncertainty bounds."""
    if not np.isfinite(multiplier) or multiplier < 0:
        raise ValueError("Sigma multiplier must be finite and non-negative")

    if np.any(np.isfinite(comparison.sigma) & (comparison.sigma < 0)):
        raise ValueError("Sigma values must be non-negative")

    lower = comparison.measured - multiplier * comparison.sigma
    upper = comparison.measured + multiplier * comparison.sigma

    return lower, upper

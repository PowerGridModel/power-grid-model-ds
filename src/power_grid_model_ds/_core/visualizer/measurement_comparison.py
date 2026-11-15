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
    estimated = np.full(node_output.shape[0], np.nan, dtype=np.float64)

    for scenario_index, scenario in enumerate(node_output):
        matches = scenario[scenario["id"] == node_id]

        if len(matches) > 0:
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

        # Unspecified floating-point updates preserve the base value.
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
    output_data: BatchDataset | None,
    sensor_id: int,
) -> VoltageComparison | None:
    """Prepare measured and calculated voltage values for one sensor.

    Measurements and sigma values start from the base grid and are
    overridden by explicitly specified scenario updates.

    Calculated voltages are retrieved from the corresponding node output
    using the sensor's measured_object reference.

    Missing node results within individual scenarios remain NaN.
    If node output is unavailable entirely, no comparison is returned.

    The supplied datasets are assumed to have been validated by
    set_app_state before this function is called.

    Args:
        grid: Base grid containing the symmetric voltage sensor.
        update_data: Optional dense batch updates.
        output_data: Optional dense batch calculation results.
        sensor_id: ID of the symmetric voltage sensor.

    Returns:
        Aligned comparison data, or None if node output is unavailable.

    Raises:
        ValueError: If the requested sensor does not exist.
    """
    sensors = grid.sym_voltage_sensor
    sensor_matches = np.flatnonzero(sensors.id == sensor_id)

    if sensor_matches.size == 0:
        raise ValueError(f"Voltage sensor with ID {sensor_id} was not found")

    sensor_index = int(sensor_matches[0])
    node_id = int(sensors.measured_object[sensor_index])

    if output_data is None or ComponentType.node not in output_data:
        return None

    node_output = output_data[ComponentType.node]
    estimated = _get_estimated_voltages(node_output, node_id)

    scenario_count = len(estimated)
    scenario_indices = np.arange(scenario_count, dtype=np.intp)

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
    """Calculate measurement-centred voltage uncertainty bounds.

    Non-finite sigma values produce NaN boundaries so they cannot
    appear as valid uncertainty bands in the resulting plot.
    """
    if not np.isfinite(multiplier) or multiplier < 0:
        raise ValueError("Sigma multiplier must be finite and non-negative")

    sigma = np.where(np.isfinite(comparison.sigma), comparison.sigma, np.nan)

    lower = comparison.measured - multiplier * sigma
    upper = comparison.measured + multiplier * sigma

    return lower, upper

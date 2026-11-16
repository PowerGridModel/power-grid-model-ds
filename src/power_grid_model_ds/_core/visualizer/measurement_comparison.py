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
from power_grid_model_ds._core.visualizer.grid_utils import get_attr_data_from_dataset


@dataclass(frozen=True)
class VoltageComparison:
    """Measured and calculated voltages aligned by scenario."""

    scenario_indices: NDArray[np.intp]
    measured: NDArray[np.float64]
    estimated: NDArray[np.float64]
    sigma: NDArray[np.float64]


def _get_sensor_series(
    grid: Grid,
    update_data: BatchDataset | None,
    sensor_id: int,
    attr: str,
    scenario_count: int,
) -> NDArray[np.float64]:
    """Combine base-grid values and sparse scenario updates."""
    sensors = grid.sym_voltage_sensor
    sensor_index = int(np.flatnonzero(sensors.id == sensor_id)[0])
    base_value = float(getattr(sensors, attr)[sensor_index])

    values = np.full(scenario_count, base_value, dtype=np.float64)

    if update_data is None or ComponentType.sym_voltage_sensor not in update_data:
        return values

    sensor_updates = update_data[ComponentType.sym_voltage_sensor]
    if attr not in sensor_updates.dtype.names:
        return values

    indices, updated_values = get_attr_data_from_dataset(
        update_data,
        ComponentType.sym_voltage_sensor,
        attr,
        sensor_id,
        grid,
    )
    values[indices] = updated_values
    return values


def get_symmetric_voltage_comparison(
    grid: Grid,
    update_data: BatchDataset | None,
    output_data: BatchDataset | None,
    sensor_id: int,
) -> VoltageComparison | None:
    """Prepare measured, calculated and sigma series aligned by scenario.

    Datasets are assumed validated by set_app_state. A missing sensor update
    leaves the base-grid value unchanged. Missing node results within a
    scenario are NaN, not removed; this preserves the scenario x-axis.
    """
    sensors = grid.sym_voltage_sensor
    sensor_matches = np.flatnonzero(sensors.id == sensor_id)
    if sensor_matches.size == 0:
        raise ValueError(f"Voltage sensor with ID {sensor_id} was not found")

    if output_data is None or ComponentType.node not in output_data:
        return None

    sensor_index = int(sensor_matches[0])
    node_id = int(sensors.measured_object[sensor_index])
    node_output = output_data[ComponentType.node]
    scenario_count = node_output.shape[0]
    scenario_indices = np.arange(scenario_count, dtype=np.intp)

    estimated = np.full(scenario_count, np.nan, dtype=np.float64)
    node_indices, node_voltages = get_attr_data_from_dataset(output_data, ComponentType.node, "u", node_id)
    estimated[node_indices] = node_voltages

    measured = _get_sensor_series(
        grid,
        update_data,
        sensor_id,
        "u_measured",
        scenario_count,
    )

    sigma = _get_sensor_series(
        grid,
        update_data,
        sensor_id,
        "u_sigma",
        scenario_count,
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
    """Return measurement-centred bounds; non-finite sigma produces NaNs."""
    if not np.isfinite(multiplier) or multiplier < 0:
        raise ValueError("Sigma multiplier must be finite and non-negative")

    sigma = np.where(np.isfinite(comparison.sigma), comparison.sigma, np.nan)
    lower = comparison.measured - multiplier * sigma
    upper = comparison.measured + multiplier * sigma
    return lower, upper

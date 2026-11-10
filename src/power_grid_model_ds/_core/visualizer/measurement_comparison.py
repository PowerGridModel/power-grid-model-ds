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

DENSE_BATCH_NDIM = 2


@dataclass(frozen=True)
class VoltageComparison:
    """Measured and calculated voltages aligned by scenario."""

    scenario_indices: NDArray[np.intp]
    measured: NDArray[np.float64]
    estimated: NDArray[np.float64]
    sigma: NDArray[np.float64]


def _require_dense_ids(dataset: BatchDataset, component: ComponentType) -> NDArray:
    """Return a dense component array with explicit IDs."""
    component_data = dataset[component]

    if not isinstance(component_data, np.ndarray) or component_data.ndim != DENSE_BATCH_NDIM:
        raise NotImplementedError(
            "Voltage comparison currently supports only dense batch arrays. "
            "Sparse and columnar batch data are not implemented."
        )

    if component_data.dtype.names is None or "id" not in component_data.dtype.names:
        raise NotImplementedError(
            "Voltage comparison requires an explicit 'id' field. "
            "Batch data without explicit component IDs are not implemented."
        )

    return component_data


def _get_estimated_voltages(output_data: BatchDataset, node_id: int) -> NDArray[np.float64]:
    """Return calculated node voltages, preserving missing scenarios as NaN."""
    node_output = _require_dense_ids(output_data, ComponentType.node)
    if node_output.dtype.names is None or "u" not in node_output.dtype.names:
        raise ValueError("Node output must contain a 'u' field")

    scenario_indices, voltages = get_attr_data_from_dataset(output_data, ComponentType.node, "u", node_id)
    if len(np.unique(scenario_indices)) != len(scenario_indices):
        raise ValueError(f"Duplicate node ID {node_id} in output")

    estimated = np.full(node_output.shape[0], np.nan, dtype=np.float64)
    estimated[scenario_indices] = voltages
    return estimated


def _apply_sensor_updates(
    update_data: BatchDataset | None,
    scenario_count: int,
    sensor_id: int,
    measured: NDArray[np.float64],
    sigma: NDArray[np.float64],
) -> None:
    """Apply specified sensor updates at their original scenario positions."""
    if update_data is None or ComponentType.sym_voltage_sensor not in update_data:
        return

    sensor_updates = _require_dense_ids(update_data, ComponentType.sym_voltage_sensor)
    if sensor_updates.shape[0] != scenario_count:
        raise ValueError("Sensor updates must match the output scenario count")

    sensor_fields = sensor_updates.dtype.names
    if sensor_fields is None:
        raise NotImplementedError("Sensor updates require named fields")

    for attribute, target in (("u_measured", measured), ("u_sigma", sigma)):
        if attribute not in sensor_fields:
            continue

        scenario_indices, values = get_attr_data_from_dataset(
            update_data, ComponentType.sym_voltage_sensor, attribute, sensor_id
        )
        if len(np.unique(scenario_indices)) != len(scenario_indices):
            raise ValueError(f"Duplicate sensor ID {sensor_id} in updates")

        specified = ~np.isnan(values)
        target[scenario_indices[specified]] = values[specified]


def get_symmetric_voltage_comparison(
    grid: Grid,
    update_data: BatchDataset | None,
    output_data: BatchDataset,
    sensor_id: int,
) -> VoltageComparison:
    """Compare base or updated sensor values with calculated node voltages.

    Scenario positions are preserved, and unspecified floating-point sensor
    updates retain the base-grid values. Only dense batch arrays with explicit
    IDs are currently supported.
    """
    sensors = grid.sym_voltage_sensor
    sensor_matches = np.flatnonzero(sensors.id == sensor_id)

    if sensor_matches.size != 1:
        raise ValueError(f"Expected exactly one voltage sensor with ID {sensor_id}")

    sensor_index = int(sensor_matches[0])
    node_id = int(sensors.measured_object[sensor_index])

    if ComponentType.node not in output_data:
        raise ValueError("Node output is required for voltage comparison")

    estimated = _get_estimated_voltages(output_data, node_id)
    scenario_count = len(estimated)
    scenario_indices = np.arange(scenario_count, dtype=np.intp)

    measured = np.full(scenario_count, float(sensors.u_measured[sensor_index]), dtype=np.float64)
    sigma = np.full(scenario_count, float(sensors.u_sigma[sensor_index]), dtype=np.float64)
    _apply_sensor_updates(update_data, scenario_count, sensor_id, measured, sigma)

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

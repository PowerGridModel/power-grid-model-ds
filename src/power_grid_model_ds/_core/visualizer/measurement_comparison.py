# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Prepare symmetric voltage measurement comparisons."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from power_grid_model import ComponentType, MeasuredTerminalType
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

    Datasets are assumed validated by set_app_state. All returned series
    share the scenario indices of the node output dataset. Sparse sensor
    updates fall back to base-grid values. Missing node results are NaN,
    preserving the scenario x-axis.
    """
    sensors = grid.sym_voltage_sensor
    sensor_matches = np.flatnonzero(sensors.id == sensor_id)
    if sensor_matches.size == 0:
        raise ValueError(f"Voltage sensor with ID {sensor_id} was not found")

    if output_data is None or ComponentType.node not in output_data:
        return None

    sensor_index = int(sensor_matches[0])
    node_id = int(sensors.measured_object[sensor_index])
    scenario_count = output_data[ComponentType.node].shape[0]
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


@dataclass(frozen=True)
class MeasurementComparison:
    """Measured and calculated quantities aligned by scenario."""

    scenario_indices: NDArray[np.intp]
    measured: NDArray[np.float64]
    estimated: NDArray[np.float64]
    sigma: NDArray[np.float64] | None


def _get_source_power(
    output_data: BatchDataset,
    source_id: int,
    attribute: str,
) -> NDArray[np.float64]:
    """Return source power without shifting missing scenarios."""
    if ComponentType.source not in output_data:
        raise ValueError("Source output is required for power comparison")

    source_output = output_data[ComponentType.source]

    if not isinstance(source_output, np.ndarray) or source_output.ndim != DENSE_BATCH_NDIM:
        raise ValueError("Expected dense batch source output")

    names = source_output.dtype.names
    if names is None or not {"id", attribute}.issubset(names):
        raise ValueError(f"Source output requires 'id' and '{attribute}'")

    field_dtype = source_output.dtype.fields[attribute][0]
    if field_dtype.subdtype is not None:
        raise ValueError(f"Source output '{attribute}' must be scalar")

    estimated = np.full(source_output.shape[0], np.nan, dtype=np.float64)

    for scenario_index, scenario in enumerate(source_output):
        matches = scenario[scenario["id"] == source_id]

        if len(matches) > 1:
            raise ValueError(f"Duplicate source ID {source_id} in output")

        if len(matches) == 1:
            estimated[scenario_index] = matches[attribute][0]

    return estimated


@dataclass
class _PowerSensorValues:
    measured: NDArray[np.float64]
    sigma: NDArray[np.float64]


def _apply_power_sensor_updates(
    update_data: BatchDataset | None,
    sensor_id: int,
    values: _PowerSensorValues,
    *,
    measurement_attribute: str,
    sigma_attribute: str,
) -> None:
    """Apply explicitly specified power sensor updates by scenario."""
    if update_data is None or ComponentType.sym_power_sensor not in update_data:
        return

    updates = update_data[ComponentType.sym_power_sensor]

    if not isinstance(updates, np.ndarray) or updates.ndim != DENSE_BATCH_NDIM:
        raise ValueError("Expected dense batch power sensor updates")

    scenario_count = len(values.measured)

    if updates.shape[0] != scenario_count:
        raise ValueError("Power sensor updates must match the output scenario count")

    names = updates.dtype.names
    if names is None or "id" not in names:
        raise ValueError("Power sensor updates must contain an 'id' field")

    for scenario_index, scenario in enumerate(updates):
        matches = scenario[scenario["id"] == sensor_id]

        if len(matches) > 1:
            raise ValueError(f"Duplicate power sensor ID {sensor_id} in updates")

        if len(matches) == 0:
            continue

        update = matches[0]

        for attribute, target in (
            (measurement_attribute, values.measured),
            (sigma_attribute, values.sigma),
        ):
            if attribute not in names:
                continue

            value = float(update[attribute])
            if not np.isnan(value):
                target[scenario_index] = value


def get_symmetric_power_comparison(
    grid: Grid,
    update_data: BatchDataset | None,
    output_data: BatchDataset,
    sensor_id: int,
    measurement_attribute: str,
) -> MeasurementComparison:
    """Prepare source-terminal symmetric power measurements and results.

    Only source-terminal sensors are supported. P and Q use their
    respective measurement and sigma attributes.
    """
    if measurement_attribute not in ("p_measured", "q_measured"):
        raise ValueError(f"Unsupported power measurement: {measurement_attribute}")

    sensors = grid.sym_power_sensor
    matches = np.flatnonzero(sensors.id == sensor_id)

    if matches.size != 1:
        raise ValueError(f"Expected exactly one power sensor with ID {sensor_id}")

    sensor_index = int(matches[0])
    terminal = int(sensors.measured_terminal_type[sensor_index])

    if terminal != MeasuredTerminalType.source.value:
        raise NotImplementedError(f"Power comparison for terminal type {terminal} is not implemented")

    quantity = measurement_attribute[0]
    sigma_attribute = f"{quantity}_sigma"
    source_id = int(sensors.measured_object[sensor_index])

    estimated = _get_source_power(output_data, source_id, quantity)
    scenario_count = len(estimated)

    measured = np.full(
        scenario_count,
        float(getattr(sensors, measurement_attribute)[sensor_index]),
        dtype=np.float64,
    )
    sigma = np.full(
        scenario_count,
        float(getattr(sensors, sigma_attribute)[sensor_index]),
        dtype=np.float64,
    )

    _apply_power_sensor_updates(
        update_data,
        sensor_id,
        _PowerSensorValues(measured=measured, sigma=sigma),
        measurement_attribute=measurement_attribute,
        sigma_attribute=sigma_attribute,
    )

    if np.any(np.isfinite(sigma) & (sigma < 0)):
        raise ValueError("Sigma values must be non-negative")

    return MeasurementComparison(
        scenario_indices=np.arange(scenario_count, dtype=np.intp),
        measured=measured,
        estimated=estimated,
        sigma=sigma if np.any(np.isfinite(sigma)) else None,
    )

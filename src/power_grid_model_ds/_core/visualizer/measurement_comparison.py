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
        if sensor_updates.dtype.names is None or attribute not in sensor_updates.dtype.names:
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

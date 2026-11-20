# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Prepare scenario-aligned voltage and symmetric power comparisons."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from power_grid_model import ComponentType, MeasuredTerminalType
from power_grid_model.data_types import BatchDataset

from power_grid_model_ds import Grid
from power_grid_model_ds._core.visualizer.grid_utils import get_attr_data_from_dataset

DENSE_BATCH_NDIM = 2


@dataclass(frozen=True)
class MeasurementComparison:
    """Measured and estimated values aligned by scenario.

    Sigma is optional for comparisons without measurement uncertainty.
    """

    scenario_indices: NDArray[np.intp]
    measured: NDArray[np.float64]
    estimated: NDArray[np.float64]
    sigma: NDArray[np.float64] | None = None


# Preserve the existing public name for voltage-specific callers.
VoltageComparison = MeasurementComparison


def _require_dense_ids(dataset: BatchDataset, component: ComponentType) -> NDArray:
    """Return a dense component array with explicit IDs."""
    component_data = dataset[component]

    if not isinstance(component_data, np.ndarray) or component_data.ndim != DENSE_BATCH_NDIM:
        raise NotImplementedError(
            "Measurement comparison currently supports only dense batch arrays. "
            "Sparse and columnar batch data are not implemented."
        )

    if component_data.dtype.names is None or "id" not in component_data.dtype.names:
        raise NotImplementedError(
            "Measurement comparison requires an explicit 'id' field. "
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


def _apply_sensor_updates(  # noqa: PLR0913  # pylint: disable=too-many-arguments
    update_data: BatchDataset | None,
    scenario_count: int,
    sensor_id: int,
    measured: NDArray[np.float64],
    sigma: NDArray[np.float64],
    *,
    component: ComponentType = ComponentType.sym_voltage_sensor,
    measurement_attribute: str = "u_measured",
    sigma_attribute: str = "u_sigma",
) -> None:
    """Apply explicitly specified sensor updates at their scenario positions."""
    if update_data is None or component not in update_data:
        return

    sensor_updates = _require_dense_ids(update_data, component)
    if sensor_updates.shape[0] != scenario_count:
        raise ValueError("Sensor updates must match the output scenario count")

    field_names = sensor_updates.dtype.names
    if field_names is None:
        raise ValueError("Sensor updates require structured component data")

    for attribute, target in ((measurement_attribute, measured), (sigma_attribute, sigma)):
        if attribute not in field_names:
            continue
        scenario_indices, values = get_attr_data_from_dataset(update_data, component, attribute, sensor_id)
        if len(np.unique(scenario_indices)) != len(scenario_indices):
            raise ValueError(f"Duplicate sensor ID {sensor_id} in updates")
        specified = ~np.isnan(values)
        target[scenario_indices[specified]] = values[specified]


def _get_estimated_series(
    output_data: BatchDataset,
    component: ComponentType,
    attribute: str,
    object_id: int,
) -> NDArray[np.float64]:
    """Extract an estimated scalar quantity, retaining missing scenarios as NaN."""
    if component not in output_data:
        raise ValueError(f"{component.value} output is required for comparison")
    data = _require_dense_ids(output_data, component)
    field_names = data.dtype.names
    fields = data.dtype.fields
    if field_names is None or fields is None or attribute not in field_names:
        raise ValueError(f"{component.value} output requires scalar '{attribute}'")
    if fields[attribute][0].subdtype is not None:
        raise ValueError(f"{component.value} output requires scalar '{attribute}'")
    indices, values = get_attr_data_from_dataset(output_data, component, attribute, object_id)
    if len(np.unique(indices)) != len(indices):
        raise ValueError(f"Duplicate {component.value} ID {object_id} in output")
    estimated = np.full(data.shape[0], np.nan, dtype=np.float64)
    estimated[indices] = values
    return estimated


def get_symmetric_power_comparison(
    grid: Grid,
    update_data: BatchDataset | None,
    output_data: BatchDataset,
    sensor_id: int,
    measurement_attribute: str,
) -> MeasurementComparison:
    """Compare a source-terminal power measurement with its calculated output.

    Only the verified source-terminal mapping is supported here. Other terminal
    types must be resolved against their actual component and output schema.
    `power_sigma` is deliberately ignored: bands use p_sigma or q_sigma only.
    """
    if measurement_attribute not in ("p_measured", "q_measured"):
        raise ValueError(f"Unsupported power measurement: {measurement_attribute}")

    sensors = grid.sym_power_sensor
    matches = np.flatnonzero(sensors.id == sensor_id)
    if matches.size != 1:
        raise ValueError(f"Expected exactly one power sensor with ID {sensor_id}")
    index = int(matches[0])
    terminal = int(sensors.measured_terminal_type[index])
    if terminal != MeasuredTerminalType.source.value:
        raise NotImplementedError(f"Power comparison for terminal type {terminal} is not implemented")

    estimated_attribute = measurement_attribute[0]  # 'p' or 'q'
    sigma_attribute = f"{estimated_attribute}_sigma"
    estimated = _get_estimated_series(
        output_data, ComponentType.source, estimated_attribute, int(sensors.measured_object[index])
    )
    count = len(estimated)
    measured = np.full(count, float(getattr(sensors, measurement_attribute)[index]), dtype=np.float64)
    sigma = np.full(count, float(getattr(sensors, sigma_attribute)[index]), dtype=np.float64)
    _apply_sensor_updates(
        update_data,
        count,
        sensor_id,
        measured,
        sigma,
        component=ComponentType.sym_power_sensor,
        measurement_attribute=measurement_attribute,
        sigma_attribute=sigma_attribute,
    )
    # Missing sigma means no uncertainty bands, but comparison lines remain.
    return MeasurementComparison(
        scenario_indices=np.arange(count, dtype=np.intp),
        measured=measured,
        estimated=estimated,
        sigma=sigma if np.any(np.isfinite(sigma)) else None,
    )


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


def get_measurement_sigma_bounds(
    comparison: MeasurementComparison,
    multiplier: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Calculate measurement-centred uncertainty bounds for aligned series."""
    if not np.isfinite(multiplier) or multiplier < 0:
        raise ValueError("Sigma multiplier must be finite and non-negative")

    if comparison.sigma is None:
        raise ValueError("Measurement sigma is required to calculate bounds")

    if np.any(np.isfinite(comparison.sigma) & (comparison.sigma < 0)):
        raise ValueError("Sigma values must be non-negative")

    lower = comparison.measured - multiplier * comparison.sigma
    upper = comparison.measured + multiplier * comparison.sigma
    return lower, upper


def get_voltage_sigma_bounds(
    comparison: VoltageComparison,
    multiplier: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Compatibility wrapper for measurement-centred voltage bounds."""
    return get_measurement_sigma_bounds(comparison, multiplier)

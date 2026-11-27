# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Prepare sensor measurement comparisons."""

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray
from power_grid_model import ComponentType, MeasuredTerminalType
from power_grid_model.data_types import BatchDataset

from power_grid_model_ds import Grid
from power_grid_model_ds._core.visualizer.grid_utils import get_attr_data_from_dataset

PHASED_MEASUREMENT_NDIM = 2


_BRANCH_COMPONENT_TYPES = (
    ComponentType.line,
    ComponentType.asym_line,
    ComponentType.link,
    ComponentType.generic_branch,
    ComponentType.transformer,
)

_VOLTAGE_SENSOR_OUTPUT_ATTRIBUTES = {"u_measured": "u"}

_FLOW_SENSOR_TERMINAL_COMPONENT_TYPES: dict[MeasuredTerminalType, tuple[ComponentType, ...]] = {
    MeasuredTerminalType.branch_from: _BRANCH_COMPONENT_TYPES,
    MeasuredTerminalType.branch_to: _BRANCH_COMPONENT_TYPES,
    MeasuredTerminalType.branch3_1: (ComponentType.three_winding_transformer,),
    MeasuredTerminalType.branch3_2: (ComponentType.three_winding_transformer,),
    MeasuredTerminalType.branch3_3: (ComponentType.three_winding_transformer,),
    MeasuredTerminalType.source: (ComponentType.source,),
    MeasuredTerminalType.shunt: (ComponentType.shunt,),
    MeasuredTerminalType.load: (ComponentType.sym_load, ComponentType.asym_load),
    MeasuredTerminalType.generator: (ComponentType.sym_gen, ComponentType.asym_gen),
}

_FLOW_SENSOR_OUTPUT_ATTRIBUTES: dict[str, dict[MeasuredTerminalType, str]] = {
    "p_measured": {
        MeasuredTerminalType.branch_from: "p_from",
        MeasuredTerminalType.branch_to: "p_to",
        MeasuredTerminalType.branch3_1: "p_1",
        MeasuredTerminalType.branch3_2: "p_2",
        MeasuredTerminalType.branch3_3: "p_3",
        MeasuredTerminalType.source: "p",
        MeasuredTerminalType.shunt: "p",
        MeasuredTerminalType.load: "p",
        MeasuredTerminalType.generator: "p",
    },
    "q_measured": {
        MeasuredTerminalType.branch_from: "q_from",
        MeasuredTerminalType.branch_to: "q_to",
        MeasuredTerminalType.branch3_1: "q_1",
        MeasuredTerminalType.branch3_2: "q_2",
        MeasuredTerminalType.branch3_3: "q_3",
        MeasuredTerminalType.source: "q",
        MeasuredTerminalType.shunt: "q",
        MeasuredTerminalType.load: "q",
        MeasuredTerminalType.generator: "q",
    },
    "i_measured": {
        MeasuredTerminalType.branch_from: "i_from",
        MeasuredTerminalType.branch_to: "i_to",
        MeasuredTerminalType.branch3_1: "i_1",
        MeasuredTerminalType.branch3_2: "i_2",
        MeasuredTerminalType.branch3_3: "i_3",
        MeasuredTerminalType.source: "i",
        MeasuredTerminalType.shunt: "i",
        MeasuredTerminalType.load: "i",
        MeasuredTerminalType.generator: "i",
    },
}

_SIGMA_ATTRIBUTES = {
    "u_measured": "u_sigma",
    "p_measured": "p_sigma",
    "q_measured": "q_sigma",
    "i_measured": "i_sigma",
}

_UNSUPPORTED_ATTRIBUTES = {"u_angle_measured", "i_angle_measured"}


@dataclass(frozen=True)
class MeasurementData:
    """Measured and calculated sensor values aligned by scenario."""

    scenario_indices: NDArray[np.intp]
    measured: NDArray[np.float64]
    estimated: NDArray[np.float64]
    sigma: NDArray[np.float64]


def _dense_component(dataset: BatchDataset, component: ComponentType) -> NDArray:
    """Require dense structured batch data with explicit component IDs."""
    data = dataset[component]
    if not isinstance(data, np.ndarray) or data.ndim != PHASED_MEASUREMENT_NDIM:
        raise NotImplementedError("Comparison requires dense batch arrays")
    if data.dtype.names is None or "id" not in data.dtype.names:
        raise ValueError("Comparison requires explicit component IDs")
    return data


def _sensor_index(sensors: Any, sensor_id: int) -> int:
    """Resolve exactly one sensor."""
    matches = np.flatnonzero(sensors.id == sensor_id)
    if matches.size != 1:
        raise ValueError(f"Expected exactly one sensor with ID {sensor_id}")
    return int(matches[0])


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _sensor_series(  # noqa: PLR0913, PLR0917
    grid: Grid,
    update_data: BatchDataset | None,
    sensor_type: ComponentType,
    sensor_id: int,
    attribute: str,
    count: int,
) -> NDArray[np.float64]:
    """Repeat base values and overlay updates at their original indices."""
    sensors = getattr(grid, sensor_type.value)
    base = np.asarray(getattr(sensors, attribute)[_sensor_index(sensors, sensor_id)], dtype=np.float64)
    values = np.broadcast_to(base, (count, *base.shape)).copy()
    if update_data is None or sensor_type not in update_data:
        return values
    data = _dense_component(update_data, sensor_type)
    if data.shape[0] != count:
        raise ValueError("Sensor updates must match the output scenario count")
    if attribute not in (data.dtype.names or ()):
        return values
    indices, updates = get_attr_data_from_dataset(update_data, sensor_type, attribute, sensor_id)
    if np.unique(indices).size != indices.size:
        raise ValueError("Duplicate sensor ID in updates")
    values[indices] = np.where(np.isnan(updates), values[indices], updates)
    return values


def _estimated_series(
    output_data: BatchDataset, component: ComponentType, attribute: str, component_id: int
) -> NDArray[np.float64]:
    """Preserve missing output rows at their original scenario positions."""
    data = _dense_component(output_data, component)
    if attribute not in (data.dtype.names or ()):
        raise ValueError(f"Output attribute {attribute} is unavailable")
    indices, extracted = get_attr_data_from_dataset(output_data, component, attribute, component_id)
    if np.unique(indices).size != indices.size:
        raise ValueError("Duplicate component ID in output")
    values = np.full((data.shape[0], *data[attribute].shape[2:]), np.nan, dtype=np.float64)
    values[indices] = extracted
    return values


# pylint: disable-next=too-many-arguments,too-many-positional-arguments,too-many-locals
def get_sensor_comparison(  # noqa: PLR0913, PLR0917
    grid: Grid,
    sensor_type: ComponentType,
    sensor_id: int,
    measured_attr: str,
    update_data: BatchDataset | None,
    output_data: BatchDataset | None,
) -> MeasurementData | None:
    """Prepare aligned sensor series on the complete output scenario axis."""
    if measured_attr in _UNSUPPORTED_ATTRIBUTES:
        return None
    component_type, output_attr, component_id = get_associated_sensor_data(grid, sensor_type, sensor_id, measured_attr)
    if output_data is None or component_type not in output_data:
        return None
    estimated = _estimated_series(output_data, component_type, output_attr, component_id)
    count = len(estimated)
    measured = _sensor_series(grid, update_data, sensor_type, sensor_id, measured_attr, count)
    sigma = _sensor_series(grid, update_data, sensor_type, sensor_id, _SIGMA_ATTRIBUTES[measured_attr], count)
    if measured.shape != estimated.shape:
        raise ValueError("Measured and estimated shapes differ")
    return MeasurementData(np.arange(count, dtype=np.intp), measured, estimated, sigma)


def get_sigma_bounds(comparison: MeasurementData, multiplier: float) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Return measurement-centred bounds; non-finite sigma produces NaNs.

    Possible combinations of measured and sigma shapes:
    Sensor | measured shape | sigma shape
    Symmetric voltage, power, or current | (N,) | (N,)
    Asymmetric power | (N, 3) | (N, 3)
    Asymmetric voltage or current | (N, 3) | (N,)
    """
    if not np.isfinite(multiplier) or multiplier < 0:
        raise ValueError("Sigma multiplier must be finite and non-negative")

    sigma = np.where(np.isfinite(comparison.sigma), comparison.sigma, np.nan)
    # expand sigma for 2D measured arrays
    if sigma.ndim == 1 and comparison.measured.ndim == PHASED_MEASUREMENT_NDIM:
        if sigma.shape[0] != comparison.measured.shape[0]:
            raise ValueError("Sigma and measurement scenario counts differ")
        sigma = sigma[:, np.newaxis]
    elif sigma.shape != comparison.measured.shape:
        raise ValueError("Sigma shape does not match measured data")
    lower = comparison.measured - multiplier * sigma
    upper = comparison.measured + multiplier * sigma
    return lower, upper


def get_associated_sensor_data(
    grid: Grid, sensor_type: ComponentType, sensor_id: int, measured_attr: str
) -> tuple[ComponentType, str, int]:
    """Return the output component type, attribute and id associated with a sensor."""
    sensor_array = getattr(grid, sensor_type.value)
    index = _sensor_index(sensor_array, sensor_id)
    component_id = int(sensor_array.measured_object[index])

    if sensor_type in {ComponentType.sym_voltage_sensor, ComponentType.asym_voltage_sensor}:
        if measured_attr not in _VOLTAGE_SENSOR_OUTPUT_ATTRIBUTES:
            raise ValueError(f"Unsupported voltage attribute: {measured_attr}")
        output_attr = _VOLTAGE_SENSOR_OUTPUT_ATTRIBUTES[measured_attr]
        return ComponentType.node, output_attr, component_id

    terminal_type = MeasuredTerminalType(int(sensor_array.measured_terminal_type[index]))
    candidates = _FLOW_SENSOR_TERMINAL_COMPONENT_TYPES.get(terminal_type)
    attributes = _FLOW_SENSOR_OUTPUT_ATTRIBUTES.get(measured_attr)
    if candidates is None or attributes is None or terminal_type not in attributes:
        raise ValueError("Unsupported terminal or measured attribute")
    output_attr = attributes[terminal_type]

    for candidate_type in candidates:
        component_array = getattr(grid, candidate_type.value, None)
        if component_array is not None and np.any(component_array.id == component_id):
            return candidate_type, output_attr, component_id

    raise ValueError(f"Associated component of {component_id} not found")

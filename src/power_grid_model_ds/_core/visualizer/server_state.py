# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Server-side application state for the visualizer.

The grid and batch datasets are initialized before the Dash server starts.
The inspected visualizer callbacks read these objects without modifying
them in place.

State is stored at module scope and is not isolated between user sessions.
The application is intended for single-user use.
"""

from dataclasses import dataclass

import numpy as np
from power_grid_model import ComponentType, DatasetType, power_grid_meta_data
from power_grid_model._core.errors import PowerGridError
from power_grid_model.data_types import DenseBatchArray
from power_grid_model.utils import get_dataset_batch_size, get_dataset_type, is_columnar

from power_grid_model_ds._core.model.grids.base import Grid


@dataclass
class _AppState:
    """Container for application-level state."""

    grid: Grid | None = None
    update_data: dict[ComponentType, DenseBatchArray] | None = None
    output_data: dict[ComponentType, DenseBatchArray] | None = None


_state = _AppState()


def _validate_dataset(
    dataset: dict[ComponentType, DenseBatchArray] | None,
    name: str,
) -> int | None:
    """Validate dense PGM batch arrays against the native dataset schema."""
    if not dataset:
        return None

    for component, data in dataset.items():
        if is_columnar(data):
            raise NotImplementedError(f"{name}: columnar data is not supported for {component}")
        if not isinstance(data, np.ndarray) or data.ndim not in (1, 2):
            raise ValueError(f"{name}: {component} must be a 1D or 2D structured array")
        if data.dtype.names is None or "id" not in data.dtype.names:
            raise NotImplementedError(f"{name}: {component} requires an 'id' field")

    # Empty datasets are allowed above; non-empty datasets must be identifiable.
    try:
        dataset_type = get_dataset_type(dataset)
    except (PowerGridError, ValueError, TypeError) as exc:
        raise ValueError(f"{name}: invalid or ambiguous PGM dataset schema") from exc

    allowed_types = (
        {DatasetType.update}
        if name == "update_data"
        else {DatasetType.sym_output, DatasetType.asym_output, DatasetType.sc_output}
    )
    if dataset_type not in allowed_types:
        raise ValueError(f"{name}: unsupported dataset type {dataset_type}")

    for component, data in dataset.items():
        try:
            expected_dtype = power_grid_meta_data[dataset_type][component].dtype
        except KeyError as exc:
            raise ValueError(f"{name}: unsupported component {component} for {dataset_type}") from exc
        if data.dtype != expected_dtype:
            raise ValueError(f"{name}: {component} dtype does not match {dataset_type} metadata")

    try:
        return get_dataset_batch_size(dataset)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name}: inconsistent or invalid dataset dimensions") from exc


def _validate_component_ids(
    grid: Grid,
    dataset: dict[ComponentType, DenseBatchArray] | None,
    name: str,
) -> None:
    """Validate each supplied component against the base-grid IDs.

    Updates contain unique subsets; outputs contain all grid IDs.
    Component arrays absent from a dataset are allowed.
    """
    if not dataset:
        return

    for component, data in dataset.items():
        grid_ids = getattr(grid, component.value).id
        scenario_ids = (data["id"],) if data.ndim == 1 else data["id"]
        for scenario_index, ids in enumerate(scenario_ids):
            if name == "update_data":
                if len(np.unique(ids)) != len(ids):
                    raise ValueError(f"{name}: duplicate IDs for {component} at scenario {scenario_index}")
                if not np.all(np.isin(ids, grid_ids)):
                    raise ValueError(
                        f"{name}: IDs must be a subset of grid IDs for {component} at scenario {scenario_index}"
                    )
            elif len(ids) != len(grid_ids) or not np.array_equal(np.sort(ids), np.sort(grid_ids)):
                raise ValueError(f"{name}: IDs must match grid IDs for {component} at scenario {scenario_index}")


def _validate_datasets(
    grid: Grid,
    update_data: dict[ComponentType, DenseBatchArray] | None,
    output_data: dict[ComponentType, DenseBatchArray] | None,
) -> None:
    """Validate dataset representations, scenario counts and base-grid IDs."""
    update_count = _validate_dataset(update_data, "update_data")
    output_count = _validate_dataset(output_data, "output_data")

    if update_count is not None and output_count is not None and update_count != output_count:
        raise ValueError("Update and output datasets must have the same scenario count")

    _validate_component_ids(grid, update_data, "update_data")
    _validate_component_ids(grid, output_data, "output_data")


def set_app_state(
    grid: Grid,
    update_data: dict[ComponentType, DenseBatchArray] | None = None,
    output_data: dict[ComponentType, DenseBatchArray] | None = None,
) -> None:
    """Validate datasets before updating application state."""
    _validate_datasets(grid, update_data, output_data)

    _state.grid = grid
    _state.update_data = update_data
    _state.output_data = output_data


def get_grid() -> Grid:
    """Get the grid, raising if it has not been initialized."""
    if _state.grid is None:
        raise RuntimeError(
            "Grid state not initialized. This should not happen during normal operation. Please report this as a bug."
        )
    return _state.grid


def get_update_data() -> dict[ComponentType, DenseBatchArray] | None:
    """Get the shared update data."""
    return _state.update_data


def get_output_data() -> dict[ComponentType, DenseBatchArray] | None:
    """Get the shared output data."""
    return _state.output_data

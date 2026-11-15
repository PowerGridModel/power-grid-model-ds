# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""
Server-side state management for the visualizer.

This module provides thread-safe storage for the Grid object to avoid sending
large datasets to the client browser. The state is stored in module-level variables
protected by a lock for concurrent access safety to ensure thread-safety in Flask's threaded mode.
However this is app-scoped state for single-user visualization sessions.
As such, this state management approach is not suitable for multi-user scenarios or where immutability is required.
If multi-user support is needed in the future, consider implementing a more robust state management solution.

Note that getters can modify the returned object.
As such, callers should be careful to avoid unintended side effects on the shared state.
"""

from dataclasses import dataclass

import numpy as np
from power_grid_model import ComponentType
from power_grid_model.data_types import DenseBatchArray
from power_grid_model.utils import get_dataset_batch_size, is_columnar

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
    """Validate the supported dense dataset representation."""
    if dataset is None or not dataset:
        return None

    for component, data in dataset.items():
        if is_columnar(data):
            raise NotImplementedError(f"{name}: columnar data is not supported for {component}")

        if not isinstance(data, np.ndarray) or data.ndim not in (1, 2):
            raise ValueError(f"{name}: {component} must be a 1D or 2D structured array")

        if data.dtype.names is None or "id" not in data.dtype.names:
            raise NotImplementedError(f"{name}: {component} requires an 'id' field")

    try:
        return get_dataset_batch_size(dataset)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name}: inconsistent or invalid dataset dimensions") from exc


def set_app_state(
    grid: Grid,
    update_data: dict[ComponentType, DenseBatchArray] | None = None,
    output_data: dict[ComponentType, DenseBatchArray] | None = None,
) -> None:
    """Validate datasets before updating the application state."""
    update_count = _validate_dataset(update_data, "update_data")
    output_count = _validate_dataset(output_data, "output_data")

    if update_count is not None and output_count is not None and update_count != output_count:
        raise ValueError("Update and output datasets must have the same scenario count")

    _state.grid = grid
    _state.update_data = update_data
    _state.output_data = output_data


def get_grid() -> Grid:
    """Get the Grid instance in a thread-safe manner.

    Raises:
        RuntimeError: If state has not been initialized.
        Visualizer would not function properly if this happens, so we raise an error to catch this unexpected state.
    """
    if _state.grid is None:
        raise RuntimeError(
            "Grid state not initialized. This should not happen during normal operation. Please report this as a bug."
        )
    return _state.grid


def get_update_data() -> dict[ComponentType, DenseBatchArray] | None:
    """Get the update data in a thread-safe manner."""
    return _state.update_data


def get_output_data() -> dict[ComponentType, DenseBatchArray] | None:
    """Get the output data in a thread-safe manner."""
    return _state.output_data

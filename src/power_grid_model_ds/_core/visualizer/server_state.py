# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""
Serverside state management for the visualizer.

This module provides thread-safe storage for the Grid object to avoid sending
large datasets to the client browser. The state is stored in module-level variables
protected by a lock for concurrent access safety.
"""

import threading
from dataclasses import dataclass

from power_grid_model_ds._core.model.grids.base import Grid


@dataclass
class _AppState:
    """Container for application-level state."""

    grid: Grid | None = None
    update_data: dict | None = None
    output_data: dict | None = None


# Thread-safe serverside state management
# Protected by a lock to ensure thread-safety in Flask's threaded mode.
_STATE_LOCK = threading.Lock()
_state = _AppState()


def safe_set_grid(grid: Grid) -> None:
    """Set the Grid instance in a thread-safe manner.

    Args:
        grid: The Grid instance to store.

    Note:
        This is app-scoped state for single-user visualization sessions.
        The lock ensures thread-safety for concurrent callback execution.
    """
    with _STATE_LOCK:
        _state.grid = grid


def safe_get_grid() -> Grid:
    """Get the Grid instance in a thread-safe manner.

    Returns:
        The Grid instance.

    Raises:
        RuntimeError: If state has not been initialized.
    """
    with _STATE_LOCK:
        if _state.grid is None:
            raise RuntimeError(
                "Grid state not initialized. This should not happen during normal operation. "
                "Please report this as a bug."
            )
        return _state.grid


def safe_set_update_data(update_data: dict | None) -> None:
    """Set the update data in a thread-safe manner.

    Args:
        update_data: The update data dictionary to store, or None.

    Note:
        This is app-scoped state for single-user visualization sessions.
        The lock ensures thread-safety for concurrent callback execution.
    """
    with _STATE_LOCK:
        _state.update_data = update_data


def safe_get_update_data() -> dict | None:
    """Get the update data in a thread-safe manner.

    Returns:
        The update data dictionary, or None if not set.
    """
    with _STATE_LOCK:
        return _state.update_data


def safe_set_output_data(output_data: dict | None) -> None:
    """Set the output data in a thread-safe manner.

    Args:
        output_data: The output data dictionary to store, or None.

    Note:
        This is app-scoped state for single-user visualization sessions.
        The lock ensures thread-safety for concurrent callback execution.
    """
    with _STATE_LOCK:
        _state.output_data = output_data


def safe_get_output_data() -> dict | None:
    """Get the output data in a thread-safe manner.

    Returns:
        The output data dictionary, or None if not set.
    """
    with _STATE_LOCK:
        return _state.output_data
